// Public GitHub releases supply version choices and SHA-256 verified executables.
// App versions and the updater launcher are tracked separately, so rolling back
// to a release without an updater still retains the version selector.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web.Script.Serialization;

internal sealed class UpdateManager
{
    internal const string BuildTag = "v1.1.0-windows-preview";
    private const string Repository = "https://api.github.com/repos/MrMints/shinydex";
    private readonly object gate = new object();
    private JavaScriptSerializer json { get { return new JavaScriptSerializer { MaxJsonLength = 4000000 }; } }
    private readonly string directory;
    private readonly string executable;
    private readonly bool verify;
    private readonly Action<string> changeRuntime;
    private readonly Action<string> restart;
    private readonly List<Release> releases = new List<Release>();
    private Dictionary<string, object> saved;
    private string currentTag;
    private string latestTag;
    private string status = "idle";
    private string error;
    private string diagnostic;
    private int progress;
    private DateTime lastCheck = DateTime.MinValue;
    internal readonly string Token = Guid.NewGuid().ToString("N");

    private sealed class Release
    {
        internal string Tag, Name, Url, Hash;
        internal long Size;
        internal Dictionary<string, object> Public() { return new Dictionary<string, object> { { "tag", Tag }, { "name", Name }, { "size", Size } }; }
    }

    internal UpdateManager(string cacheRoot, string currentExecutable, bool verification, Action<string> change, Action<string> relaunch)
    {
        directory = Path.Combine(cacheRoot, "ShinyDex");
        executable = currentExecutable;
        verify = verification;
        changeRuntime = change;
        restart = relaunch;
        currentTag = BuildTag;
        saved = LoadState(directory);
        string selected = Text(saved, "selectedTag");
        if (ValidTag(selected) && FileMatches(InstalledPath(selected), Text(saved, "selectedHash"))) currentTag = selected;
    }

    internal string SelectedExecutable { get { return currentTag == BuildTag ? executable : InstalledPath(currentTag); } }

    internal static string Redirect(string cacheRoot, string currentExecutable)
    {
        string basePath = Path.Combine(cacheRoot, "ShinyDex");
        var state = LoadState(basePath);
        string tag = Text(state, "launcherTag");
        if (!ValidTag(tag) || CompareVersions(tag, BuildTag) <= 0) return null;
        string candidate = Path.Combine(basePath, "versions", tag, "ShinyDex.exe");
        if (Path.GetFullPath(candidate).Equals(Path.GetFullPath(currentExecutable), StringComparison.OrdinalIgnoreCase)) return null;
        return FileMatches(candidate, Text(state, "launcherHash")) ? candidate : null;
    }

    private static Dictionary<string, object> LoadState(string basePath)
    {
        try { return new JavaScriptSerializer().Deserialize<Dictionary<string, object>>(File.ReadAllText(Path.Combine(basePath, "installed.json"))) ?? new Dictionary<string, object>(); }
        catch (IOException) { return new Dictionary<string, object>(); }
        catch (ArgumentException) { return new Dictionary<string, object>(); }
        catch (InvalidOperationException) { return new Dictionary<string, object>(); }
    }

    private string InstalledPath(string tag) { return Path.Combine(directory, "versions", tag, "ShinyDex.exe"); }
    private static bool ValidTag(string tag) { return tag != null && Regex.IsMatch(tag, @"^v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?$") && tag.Length < 100 && !tag.Contains(".."); }
    private static string Text(Dictionary<string, object> record, string name) { object value; return record.TryGetValue(name, out value) ? value as string : null; }
    private static Version Number(string tag) { return new Version(Regex.Match(tag ?? "", @"\d+\.\d+\.\d+").Value); }
    private static int CompareVersions(string a, string b) { try { return Number(a).CompareTo(Number(b)); } catch (ArgumentException) { return 0; } catch (FormatException) { return 0; } }
    private static string Hash(string path) { using (var file = File.OpenRead(path)) using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(file)).Replace("-", "").ToLowerInvariant(); }
    private static bool FileMatches(string path, string hash) { try { return Regex.IsMatch(hash ?? "", "^[a-f0-9]{64}$") && File.Exists(path) && Hash(path) == hash; } catch (IOException) { return false; } }

    internal string Snapshot()
    {
        lock (gate)
        {
            var choices = new List<Dictionary<string, object>>();
            foreach (Release release in releases) choices.Add(release.Public());
            return json.Serialize(new { currentVersion = currentTag, launcherVersion = BuildTag, latestVersion = latestTag, updateAvailable = latestTag != null && CompareVersions(latestTag, currentTag) > 0, releases = choices, status = status, progress = progress, error = error, token = Token, processId = verify ? Process.GetCurrentProcess().Id : 0, diagnostic = verify ? diagnostic : null });
        }
    }

    internal void Check()
    {
        lock (gate)
        {
            if (status == "checking" || status == "downloading" || status == "restarting") return;
            if (DateTime.UtcNow - lastCheck < TimeSpan.FromSeconds(30)) return;
            status = "checking"; error = null;
        }
        Task.Run((Action)FetchReleases);
    }

    private void FetchReleases()
    {
        try
        {
            string fixture = verify ? Environment.GetEnvironmentVariable("SHINYDEX_RELEASE_FIXTURE") : null;
            var parsed = new List<Release>();
            string newest = null;
            if (!string.IsNullOrEmpty(fixture))
            {
                var sample = json.Deserialize<Dictionary<string, object>>(File.ReadAllText(fixture));
                parsed.AddRange(ParseReleases((IEnumerable)sample["releases"], true));
                newest = Text(sample, "latestTag");
            }
            else
            {
                // Latest is explicit; published-at order is not a semantic version order.
                var latest = json.Deserialize<Dictionary<string, object>>(DownloadText(Repository + "/releases/latest"));
                newest = Text(latest, "tag_name");
                for (int page = 1; page <= 10; page++)
                {
                    var items = json.DeserializeObject(DownloadText(Repository + "/releases?per_page=100&page=" + page)) as object[];
                    if (items == null) throw new InvalidDataException("Invalid release list.");
                    parsed.AddRange(ParseReleases(items, false));
                    if (items.Length < 100) break;
                }
            }
            if (!parsed.Exists(item => item.Tag == newest)) newest = null;
            parsed.Sort((a, b) => CompareVersions(b.Tag, a.Tag));
            lock (gate) { releases.Clear(); releases.AddRange(parsed); latestTag = newest; status = "ready"; error = null; lastCheck = DateTime.UtcNow; }
        }
        catch (Exception failure)
        {
            // Offline, rate-limited, and unavailable release services do not interrupt the app.
            lock (gate) { status = "error"; error = "Could not check for updates. Your installed app still works; try again later."; diagnostic = failure.ToString(); lastCheck = DateTime.UtcNow; }
        }
    }

    private IEnumerable<Release> ParseReleases(IEnumerable rows, bool fixture)
    {
        var result = new List<Release>();
        foreach (object row in rows)
        {
            var item = row as Dictionary<string, object>;
            if (item == null || (item.ContainsKey("draft") && Convert.ToBoolean(item["draft"]))) continue;
            string tag = Text(item, "tag_name");
            if (!ValidTag(tag)) continue;
            IEnumerable assets = item.ContainsKey("assets") ? item["assets"] as IEnumerable : null;
            if (assets == null) continue;
            foreach (object value in assets)
            {
                var asset = value as Dictionary<string, object>;
                if (asset == null || Text(asset, "name") != "ShinyDex.exe") continue;
                string url = Text(asset, "browser_download_url");
                string digest = Text(asset, "digest");
                string expected = "https://github.com/MrMints/shinydex/releases/download/" + tag + "/ShinyDex.exe";
                if ((!fixture && url != expected) || !Regex.IsMatch(digest ?? "", "^sha256:[a-f0-9]{64}$")) continue;
                long size = Convert.ToInt64(asset["size"]);
                if (size < 1024 || size > 200000000) continue;
                result.Add(new Release { Tag = tag, Name = Text(item, "name") ?? tag, Url = url, Hash = digest.Substring(7), Size = size });
                break;
            }
        }
        return result;
    }

    private static HttpWebRequest Request(string url)
    {
        var request = (HttpWebRequest)WebRequest.Create(url);
        request.UserAgent = "ShinyDex-Windows-Updater";
        request.Accept = "application/vnd.github+json";
        request.Timeout = 30000;
        request.ReadWriteTimeout = 30000;
        return request;
    }

    private static string DownloadText(string url)
    {
        using (var response = Request(url).GetResponse())
        using (var input = response.GetResponseStream())
        using (var reader = new StreamReader(input)) return reader.ReadToEnd();
    }

    internal bool Install(string body)
    {
        Dictionary<string, object> request;
        try { request = json.Deserialize<Dictionary<string, object>>(body); } catch (ArgumentException) { return false; } catch (InvalidOperationException) { return false; }
        if (request == null) return false;
        string tag = Text(request, "tag");
        string collection = Text(request, "collection");
        // Only JSON records are accepted as local backups; no client paths or URLs are accepted.
        if (collection != null)
        {
            if (collection.Length > 200000) return false;
            try
            {
                var record = json.Deserialize<Dictionary<string, object>>(collection);
                if (record == null || !(record["captured"] is IEnumerable) || !(record["shinies"] is IEnumerable)) return false;
            }
            catch (Exception) { return false; }
        }
        Release selected;
        lock (gate)
        {
            if (status == "checking" || status == "downloading" || status == "restarting") return false;
            selected = releases.Find(item => item.Tag == tag);
            if (selected == null || selected.Tag == currentTag) return false;
            status = "downloading"; progress = 0; error = null;
        }
        Task.Run(() => Apply(selected, collection));
        return true;
    }

    private void Apply(Release release, string collection)
    {
        var before = new Dictionary<string, object>(saved);
        string previousTag = currentTag;
        bool committed = false;
        try
        {
            if (collection != null)
            {
                string backups = Path.Combine(directory, "collections", "backups");
                Directory.CreateDirectory(backups);
                File.WriteAllText(Path.Combine(backups, DateTime.UtcNow.ToString("yyyyMMddTHHmmssfff") + "-" + Guid.NewGuid().ToString("N") + ".json"), collection, Encoding.UTF8);
            }
            string file = InstalledPath(release.Tag);
            Directory.CreateDirectory(Path.GetDirectoryName(file));
            if (!FileMatches(file, release.Hash))
            {
                string partial = file + ".download";
                try
                {
                    if (verify && new Uri(release.Url).IsFile)
                    {
                        File.Copy(new Uri(release.Url).LocalPath, partial, true);
                        lock (gate) progress = 100;
                    }
                    else
                    {
                        using (var response = Request(release.Url).GetResponse())
                        using (var input = response.GetResponseStream())
                        using (var output = File.Create(partial))
                        {
                            byte[] buffer = new byte[65536]; int count; long total = 0;
                            while ((count = input.Read(buffer, 0, buffer.Length)) > 0)
                            {
                                total += count;
                                if (total > release.Size) throw new InvalidDataException("Download size mismatch.");
                                output.Write(buffer, 0, count);
                                lock (gate) progress = (int)(total * 100 / release.Size);
                            }
                        }
                    }
                    if (new FileInfo(partial).Length != release.Size || !FileMatches(partial, release.Hash)) throw new InvalidDataException("Download verification failed.");
                    if (File.Exists(file)) File.Delete(file);
                    File.Move(partial, file);
                }
                finally { if (File.Exists(partial)) File.Delete(partial); }
            }
            // Validate and unpack first; failed downloads/extraction never change the active version.
            string newRoot = Launcher.UnpackFile(file, directory);
            var next = new Dictionary<string, object>(saved);
            next["selectedTag"] = release.Tag; next["selectedHash"] = release.Hash;
            bool newLauncher = CompareVersions(release.Tag, BuildTag) > 0;
            if (newLauncher) { next["launcherTag"] = release.Tag; next["launcherHash"] = release.Hash; }
            SaveState(next);
            committed = true;
            lock (gate) { saved = next; currentTag = release.Tag; status = newLauncher ? "restarting" : "installed"; progress = 100; }
            if (newLauncher) restart(file); else changeRuntime(newRoot);
        }
        catch (Exception failure)
        {
            if (committed) { try { SaveState(before); } catch (IOException) { } }
            lock (gate) { saved = before; currentTag = previousTag; status = "error"; error = "The update could not be installed or verified. Your current version and saved collection are unchanged. Retry when ready."; diagnostic = failure.ToString(); progress = 0; }
        }
    }

    private void SaveState(Dictionary<string, object> state)
    {
        Directory.CreateDirectory(directory);
        string file = Path.Combine(directory, "installed.json");
        string temp = file + ".new";
        File.WriteAllText(temp, json.Serialize(state), Encoding.UTF8);
        if (File.Exists(file)) File.Replace(temp, file, file + ".previous", true); else File.Move(temp, file);
    }
}
