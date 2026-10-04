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

internal static class Launcher
{
    private const string Identity = "ShinyDex Windows launcher v1";
    private static TcpListener listener;
    private static string root;
    private static string address;

    [STAThread]
    private static int Main(string[] args)
    {
        bool verify = args.Length == 2 && args[0] == "--verify";
        int port = 5173;
        if (verify && (!int.TryParse(args[1], out port) || port < 1024 || port > 65535)) return 2;
        address = "http://localhost:" + port + "/";
        bool first;
        using (var mutex = new Mutex(true, "Local\\ShinyDexLauncher-" + port, out first))
        {
            if (!first) { if (!verify) OpenBrowser(); return 0; }
            try
            {
                root = Unpack(verify);
                listener = new TcpListener(IPAddress.Loopback, port);
                listener.Start();
                Task.Run((Action)AcceptClients);
                if (verify) { Thread.Sleep(120000); return 0; }
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
                if (!verify) MessageBox.Show("Port " + port + " is already in use. Close the previous ShinyDex server (or the app using that port), then open ShinyDex.exe again.", "ShinyDex", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return 1;
            }
            catch (Exception error)
            {
                if (verify) Console.Error.WriteLine(error.ToString());
                if (!verify) MessageBox.Show("ShinyDex could not start.\n\n" + error.Message, "ShinyDex", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return 1;
            }
            finally { if (listener != null) listener.Stop(); }
        }
    }

    private static void OpenBrowser() { Process.Start(new ProcessStartInfo(address) { UseShellExecute = true }); }

    private static string Unpack(bool verify)
    {
        using (Stream bundled = Assembly.GetExecutingAssembly().GetManifestResourceStream("ShinyDex.Web.zip"))
        using (var bytes = new MemoryStream())
        {
            bundled.CopyTo(bytes);
            byte[] payload = bytes.ToArray();
            string hash;
            using (var sha = SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(payload)).Replace("-", "").ToLowerInvariant();
            string cacheRoot = verify ? Environment.GetEnvironmentVariable("LOCALAPPDATA") : Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            string directory = Path.Combine(cacheRoot, "ShinyDex", "app", hash);
            // A completion marker is written only after successful extraction. Each build has its own cache.
            if (!File.Exists(Path.Combine(directory, ".complete")))
            {
                Directory.CreateDirectory(directory);
                using (var archive = new ZipArchive(new MemoryStream(payload), ZipArchiveMode.Read))
                foreach (var entry in archive.Entries)
                {
                    string file = Path.GetFullPath(Path.Combine(directory, entry.FullName));
                    if (!file.StartsWith(directory + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("Invalid bundled path.");
                    Directory.CreateDirectory(Path.GetDirectoryName(file));
                    using (var source = entry.Open())
                    using (var target = File.Create(file)) source.CopyTo(target);
                }
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
                    if (request[0] != "GET" && !head) { Reply(stream, 405, "text/plain", new byte[0], false); return; }
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
                    Reply(stream, 200, mime, File.ReadAllBytes(file), head);
                }
            }
            catch (IOException) { } // Browser disconnected or timed out.
            catch (ArgumentException) { }
        }
    }

    private static void Reply(Stream stream, int status, string mime, byte[] body, bool head)
    {
        string reason = status == 200 ? "OK" : status == 400 ? "Bad Request" : status == 403 ? "Forbidden" : status == 404 ? "Not Found" : status == 405 ? "Method Not Allowed" : "Request Header Fields Too Large";
        byte[] headers = Encoding.ASCII.GetBytes("HTTP/1.1 " + status + " " + reason + "\r\nContent-Type: " + mime + "\r\nContent-Length: " + body.Length + "\r\nX-Content-Type-Options: nosniff\r\nConnection: close\r\n\r\n");
        stream.Write(headers, 0, headers.Length);
        if (!head) stream.Write(body, 0, body.Length);
    }
}
