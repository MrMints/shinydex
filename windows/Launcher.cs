// Windows launcher: unpack bundled static files, serve loopback only, and open the browser.
// Uses Windows' .NET Framework; no Node.js or separately installed runtime is needed.
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

[assembly: AssemblyVersion("1.1.0.0")]
[assembly: AssemblyFileVersion("1.1.0.0")]

internal static class Launcher
{
    private const string Identity = "ShinyDex Windows launcher v1.1";
    private static TcpListener listener;
    private static volatile string root;
    private static string address;
    private static UpdateManager updates;
    private static readonly ManualResetEvent shutdown = new ManualResetEvent(false);

    [STAThread]
    private static int Main(string[] args)
    {
        VerificationLog("Start " + Process.GetCurrentProcess().Id + " " + string.Join(" ", args));
        // A downloaded newer launcher waits on the existing launcher's mutex.
        // This avoids requiring rights to inspect or terminate another process.
        bool restarting = args.Length > 0 && args[0] == "--restart";
        if (restarting)
        {
            string[] remaining = new string[args.Length - 1];
            Array.Copy(args, 1, remaining, 0, remaining.Length); args = remaining;
        }
        bool verify = args.Length == 2 && args[0] == "--verify";
        int port = 5173;
        if (verify && (!int.TryParse(args[1], out port) || port < 1024 || port > 65535)) return 2;
        address = "http://localhost:" + port + "/";
        string cacheRoot = verify ? Environment.GetEnvironmentVariable("LOCALAPPDATA") : Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string executable = Assembly.GetExecutingAssembly().Location;
        string redirect = UpdateManager.Redirect(cacheRoot, executable);
        VerificationLog("Redirect=" + redirect);
        if (redirect != null)
        {
            var redirected = Process.Start(new ProcessStartInfo(redirect, verify ? "--verify " + port : "") { UseShellExecute = true });
            VerificationLog("Started redirect " + redirected.Id);
            if (verify) redirected.WaitForExit(10000);
            return 0;
        }
        bool first;
        using (var mutex = new Mutex(true, "Local\\ShinyDexLauncher-" + port, out first))
        {
            if (!first && restarting)
            {
                try { first = mutex.WaitOne(30000); }
                catch (AbandonedMutexException) { first = true; }
                if (!first) return 3;
            }
            if (!first) { if (!verify) OpenBrowser(); return 0; }
            VerificationLog("Mutex acquired");
            try
            {
                // This compiler targets legacy Framework APIs; explicitly enable TLS 1.2
                // supported by Windows 10/11 instead of their incompatible zero default.
                ServicePointManager.SecurityProtocol = (SecurityProtocolType)3072;
                updates = new UpdateManager(cacheRoot, executable, verify, next => root = next, next =>
                {
                    // Shell activation starts an independent GUI process without inheriting
                    // the old server's listening socket and redirected console handles.
                    var nextProcess = Process.Start(new ProcessStartInfo(next, "--restart" + (verify ? " --verify " + port : "")) { UseShellExecute = true });
                    VerificationLog("Started replacement " + nextProcess.Id);
                    shutdown.Set();
                    if (!verify) Application.Exit();
                });
                root = UnpackFile(updates.SelectedExecutable, Path.Combine(cacheRoot, "ShinyDex"));
                StartListener(port, restarting);
                VerificationLog("Listening " + port);
                Task.Run((Action)AcceptClients);
                if (!verify || !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("SHINYDEX_RELEASE_FIXTURE"))) updates.Check();
                if (verify) { shutdown.WaitOne(600000); return 0; }
                Application.EnableVisualStyles();
                var menu = new ContextMenuStrip();
                menu.Items.Add("Open ShinyDex", null, (sender, e) => OpenBrowser());
                menu.Items.Add("Exit ShinyDex", null, (sender, e) => Application.Exit());
                using (var tray = new NotifyIcon())
                {
                    tray.Icon = SystemIcons.Application;
                    tray.Text = "ShinyDex — right-click to open or exit";
                    tray.ContextMenuStrip = menu;
                    tray.DoubleClick += (sender, e) => OpenBrowser();
                    tray.Visible = true;
                    OpenBrowser();
                    Application.Run();
                    tray.Visible = false;
                }
                return 0;
            }
            catch (SocketException)
            {
                VerificationLog("Port conflict");
                if (!verify) MessageBox.Show("Port " + port + " is already in use. Close the previous ShinyDex server (or the app using that port), then open ShinyDex.exe again.", "ShinyDex", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return 1;
            }
            catch (Exception error)
            {
                VerificationLog(error.ToString());
                if (verify) Console.Error.WriteLine(error.ToString());
                if (!verify) MessageBox.Show("ShinyDex could not start.\n\n" + error.Message, "ShinyDex", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return 1;
            }
            finally { if (listener != null) listener.Stop(); }
        }
    }

    private static void VerificationLog(string text)
    {
        string path = Environment.GetEnvironmentVariable("SHINYDEX_VERIFY_LOG");
        if (Array.IndexOf(Environment.GetCommandLineArgs(), "--verify") < 0 || string.IsNullOrEmpty(path)) return;
        try { File.AppendAllText(path, text + Environment.NewLine); } catch (IOException) { }
    }

    private static void OpenBrowser() { Process.Start(new ProcessStartInfo(address) { UseShellExecute = true }); }

    private static void StartListener(int port, bool restarting)
    {
        var elapsed = Stopwatch.StartNew();
        // Windows can retain accepted connections after the old listener closes.
        // Reuse its address only after checking that no live listener owns it;
        // the named mutex serializes ShinyDex handoffs and ordinary launches.
        while (true)
        {
            bool occupied = false;
            using (var probe = new TcpClient())
            {
                try { probe.Connect(IPAddress.Loopback, port); occupied = true; }
                catch (SocketException) { }
            }
            if (occupied)
            {
                if (restarting && elapsed.ElapsedMilliseconds < 30000) { Thread.Sleep(100); continue; }
                throw new SocketException((int)SocketError.AddressAlreadyInUse);
            }
            listener = new TcpListener(IPAddress.Loopback, port);
            listener.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
            listener.Start();
            return;
        }
    }

    internal static string UnpackFile(string executable, string cacheRoot)
    {
        // Reflection-only loading reads embedded data without executing the downloaded app.
        Assembly sourceAssembly = Path.GetFullPath(executable).Equals(Path.GetFullPath(Assembly.GetExecutingAssembly().Location), StringComparison.OrdinalIgnoreCase)
            ? Assembly.GetExecutingAssembly() : Assembly.ReflectionOnlyLoad(File.ReadAllBytes(executable));
        using (Stream bundled = sourceAssembly.GetManifestResourceStream("ShinyDex.Web.zip"))
        using (var bytes = new MemoryStream())
        {
            if (bundled == null) throw new InvalidDataException("This version does not contain a ShinyDex app.");
            bundled.CopyTo(bytes);
            byte[] payload = bytes.ToArray();
            string hash;
            using (var sha = SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(payload)).Replace("-", "").ToLowerInvariant();
            string directory = Path.Combine(cacheRoot, "app", hash);
            // A completion marker is written only after successful extraction. Each build has its own cache.
            if (!File.Exists(Path.Combine(directory, ".complete")))
            {
                Directory.CreateDirectory(directory);
                using (var archive = new ZipArchive(new MemoryStream(payload), ZipArchiveMode.Read))
                {
                long expanded = 0;
                foreach (var entry in archive.Entries)
                {
                    expanded += entry.Length;
                    if (expanded > 250000000) throw new InvalidDataException("Bundled files are too large.");
                    string file = Path.GetFullPath(Path.Combine(directory, entry.FullName));
                    if (!file.StartsWith(directory + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Invalid bundled path.");
                    Directory.CreateDirectory(Path.GetDirectoryName(file));
                    using (var source = entry.Open())
                    using (var target = File.Create(file)) source.CopyTo(target);
                }
                }
                foreach (string required in new[] { "index.html", "main.js", "style.css", "data.json", "hunts.json" })
                    if (!File.Exists(Path.Combine(directory, required))) throw new InvalidDataException("App bundle is incomplete.");
                File.WriteAllText(Path.Combine(directory, ".complete"), hash);
            }
            return directory;
        }
    }

    private static void AcceptClients()
    {
        try { while (true) { var client = listener.AcceptTcpClient(); Task.Run(() => Serve(client)); } }
        catch (SocketException) { } // Normal shutdown unblocks AcceptTcpClient.
        catch (ObjectDisposedException) { }
    }

    private static void Serve(TcpClient client)
    {
        using (client)
        {
            client.ReceiveTimeout = 5000;
            client.SendTimeout = 10000;
            try
            {
                using (var stream = client.GetStream())
                {
                    // Bound incoming headers; accept one request per connection.
                    var header = new StringBuilder();
                    while (header.Length < 16384)
                    {
                        int value = stream.ReadByte();
                        if (value < 0) return;
                        header.Append((char)value);
                        if (header.Length >= 4 && header.ToString(header.Length - 4, 4) == "\r\n\r\n") break;
                    }
                    if (header.Length >= 16384) { Reply(stream, 431, "text/plain", Encoding.UTF8.GetBytes("Headers too large"), false); return; }
                    string[] request = header.ToString().Split(new[] { "\r\n" }, StringSplitOptions.None)[0].Split(' ');
                    if (request.Length != 3) { Reply(stream, 400, "text/plain", new byte[0], false); return; }
                    bool head = request[0] == "HEAD";
                    // Reject foreign Host headers to avoid exposing local data through DNS rebinding.
                    string expectedHost = "localhost:" + ((IPEndPoint)listener.LocalEndpoint).Port;
                    string loopbackHost = "127.0.0.1:" + ((IPEndPoint)listener.LocalEndpoint).Port;
                    bool validHost = false;
                    foreach (string line in header.ToString().Split(new[] { "\r\n" }, StringSplitOptions.None))
                    if (line.StartsWith("Host:", StringComparison.OrdinalIgnoreCase))
                    {
                        string host = line.Substring(5).Trim();
                        validHost = host.Equals(expectedHost, StringComparison.OrdinalIgnoreCase) || host == loopbackHost;
                        break;
                    }
                    if (!validHost) { Reply(stream, 403, "text/plain", new byte[0], head); return; }
                    string url = request[1].Split('?')[0];
                    for (int i = 0; i < url.Length; i++)
                    if (url[i] == '%' && (i + 2 >= url.Length || !Uri.IsHexDigit(url[i + 1]) || !Uri.IsHexDigit(url[i + 2])))
                    { Reply(stream, 400, "text/plain", new byte[0], head); return; }
                    string path = Uri.UnescapeDataString(url);
                    if (request[0] == "POST" && (path == "/__updates/install" || path == "/__updates/check"))
                    {
                        int length;
                        if (!int.TryParse(Header(header.ToString(), "Content-Length"), out length) || length < 0 || length > 250000)
                        { Reply(stream, 400, "application/json", Encoding.UTF8.GetBytes("{}"), false); return; }
                        byte[] body = new byte[length]; int read = 0;
                        while (read < length) { int count = stream.Read(body, read, length - read); if (count == 0) return; read += count; }
                        // Consume the bounded body before rejecting, so TCP close does not reset the response.
                        string origin = Header(header.ToString(), "Origin");
                        if ((origin != "http://" + expectedHost && origin != "http://" + loopbackHost) || Header(header.ToString(), "X-ShinyDex-Token") != updates.Token)
                        { Reply(stream, 403, "application/json", Encoding.UTF8.GetBytes("{}"), false); return; }
                        if (path == "/__updates/check") { updates.Check(); Reply(stream, 200, "application/json", Encoding.UTF8.GetBytes(updates.Snapshot()), false); }
                        else { bool accepted = updates.Install(Encoding.UTF8.GetString(body)); Reply(stream, accepted ? 202 : 409, "application/json", Encoding.UTF8.GetBytes(updates.Snapshot()), false); }
                        return;
                    }
                    if (request[0] != "GET" && !head) { Reply(stream, 405, "text/plain", new byte[0], false); return; }
                    if (path == "/__updates/status") { Reply(stream, 200, "application/json", Encoding.UTF8.GetBytes(updates.Snapshot()), head); return; }
                    // Always supply the current updater UI, including when old HTML lacks it.
                    if (path == "/updater.js")
                    {
                        using (var script = Assembly.GetExecutingAssembly().GetManifestResourceStream("ShinyDex.Updater.js"))
                        using (var output = new MemoryStream()) { script.CopyTo(output); Reply(stream, 200, "application/javascript; charset=utf-8", output.ToArray(), head); }
                        return;
                    }
                    if (path == "/__shinydex_launcher") { Reply(stream, 200, "text/plain", Encoding.UTF8.GetBytes(Identity), head); return; }
                    if (path == "/") path = "/index.html";
                    // Only runtime assets and attribution are served; developer files and local backups are inaccessible.
                    bool allowed = path == "/index.html" || path == "/main.js" || path == "/style.css" || path == "/data.json" || path == "/hunts.json" || path == "/ATTRIBUTIONS.txt" || path == "/THIRD_PARTY_NOTICES.md" || path.StartsWith("/assets/pokemon/", StringComparison.Ordinal);
                    if (!allowed || path.Contains("..") || path.Contains("\\") || path.Contains(":")) { Reply(stream, 403, "text/plain", new byte[0], head); return; }
                    string file = Path.GetFullPath(Path.Combine(root, path.TrimStart('/').Replace('/', Path.DirectorySeparatorChar)));
                    if (!file.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) { Reply(stream, 403, "text/plain", new byte[0], head); return; }
                    if (!File.Exists(file)) { Reply(stream, 404, "text/plain", new byte[0], head); return; }
                    string extension = Path.GetExtension(file);
                    string mime = extension == ".html" ? "text/html; charset=utf-8" : extension == ".js" ? "application/javascript; charset=utf-8" : extension == ".css" ? "text/css; charset=utf-8" : extension == ".json" ? "application/json; charset=utf-8" : extension == ".png" ? "image/png" : "text/plain; charset=utf-8";
                    byte[] contents = File.ReadAllBytes(file);
                    if (path == "/index.html")
                    {
                        string page = Encoding.UTF8.GetString(contents);
                        if (!page.Contains("src=\"/updater.js\"")) page = page.Replace("</body>", "<script src=\"/updater.js\" defer></script></body>");
                        contents = Encoding.UTF8.GetBytes(page);
                    }
                    Reply(stream, 200, mime, contents, head);
                }
            }
            catch (IOException) { } // Browser disconnected or timed out.
            catch (ArgumentException) { }
        }
    }

    private static string Header(string headers, string name)
    {
        foreach (string line in headers.Split(new[] { "\r\n" }, StringSplitOptions.None))
            if (line.StartsWith(name + ":", StringComparison.OrdinalIgnoreCase)) return line.Substring(name.Length + 1).Trim();
        return null;
    }

    private static void Reply(Stream stream, int status, string mime, byte[] body, bool head)
    {
        string reason = status == 200 ? "OK" : status == 202 ? "Accepted" : status == 400 ? "Bad Request" : status == 403 ? "Forbidden" : status == 404 ? "Not Found" : status == 405 ? "Method Not Allowed" : status == 409 ? "Conflict" : "Request Header Fields Too Large";
        byte[] headers = Encoding.ASCII.GetBytes("HTTP/1.1 " + status + " " + reason + "\r\nContent-Type: " + mime + "\r\nContent-Length: " + body.Length + "\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n");
        stream.Write(headers, 0, headers.Length);
        if (!head) stream.Write(body, 0, body.Length);
    }
}
