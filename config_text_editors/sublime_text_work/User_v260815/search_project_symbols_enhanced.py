import sublime
import sublime_plugin
import os
import re
import threading
import time

HEADER_RE = re.compile(r'^(#{1,6})\s+(.*)')

# Module-level cache, keyed by full file path:
#   full_path -> (mtime, rel_path, [(title_line, line_number), ...])
# rel_path is relative to the *parent* of the project folder, so it
# includes the top-level folder name itself (e.g. 'notes\Hair Protocol.md'),
# matching what the sidebar shows and what native Goto Anything matches
# against. Surviving at module level means the cache persists across
# command invocations, so repeat searches are cheap.
_cache = {}


def _scan_file(full_path):
    """Returns [(title_line, line_number), ...] for every header in the file."""
    entries = []
    try:
        with open(full_path, encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, start=1):
                m = HEADER_RE.match(line)
                if m:
                    level = len(m.group(1))
                    title = m.group(2).strip()
                    indent = '  ' * (level - 1)
                    entries.append((indent + title, lineno))
    except (OSError, IOError):
        pass
    return entries


def _is_target(fname):
    lower = fname.lower()
    return lower.endswith('.md') or lower.endswith('.md.txt')


def _relpath_including_root(full_path, folder):
    """
    Relative path that keeps the project folder's own name as the first
    segment (e.g. 'notes\\Hair Protocol.md.txt'), by computing relative
    to the folder's *parent* rather than the folder itself. This is what
    lets you type the top-level sidebar folder name ('notes') as a filter,
    same as native Goto Anything.
    """
    folder_norm = os.path.normpath(folder)
    parent = os.path.dirname(folder_norm)
    return os.path.relpath(os.path.normpath(full_path), parent)


def _project_relpath(full_path):
    """
    Same idea as _relpath_including_root, but for the on-save cache
    refresh, which only has a bare file path to work with - it searches
    all open windows' project folders to find which one contains it.
    Falls back to the bare filename if the file isn't under any open
    project folder.
    """
    full_norm = os.path.normpath(full_path)
    best = None
    for window in sublime.windows():
        for folder in window.folders():
            folder_norm = os.path.normpath(folder)
            if full_norm.startswith(folder_norm + os.sep):
                rel = _relpath_including_root(full_norm, folder_norm)
                if best is None or len(rel) < len(best):
                    best = rel
    return best or os.path.basename(full_path)


def _refresh_cache(folders):
    """
    Walk folders and only re-read files whose mtime has changed since
    last time. Unchanged files are served straight from _cache with no
    disk read at all - just a cheap getmtime() stat call.
    """
    seen = set()
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fname in files:
                if not _is_target(fname):
                    continue
                full_path = os.path.join(root, fname)
                seen.add(full_path)
                try:
                    mtime = os.path.getmtime(full_path)
                except OSError:
                    continue
                cached = _cache.get(full_path)
                if cached is None or cached[0] != mtime:
                    rel_path = _relpath_including_root(full_path, folder)
                    _cache[full_path] = (mtime, rel_path, _scan_file(full_path))

    # drop entries for files that were deleted or left the project
    for stale in set(_cache) - seen:
        del _cache[stale]


def _warm_all_open_windows():
    """
    Called once when the plugin loads (Sublime startup, or a manual
    'Reload Plugin'). Walks every open window's project folders in the
    background so the cache is already populated by the time you first
    hit the shortcut - eliminating the cold-start delay entirely rather
    than just shrinking it.
    """
    for window in sublime.windows():
        folders = window.folders()
        if folders:
            threading.Thread(target=_refresh_cache, args=(folders,)).start()


def plugin_loaded():
    # Slight delay so this doesn't compete with Sublime's own startup work.
    sublime.set_timeout_async(_warm_all_open_windows, 200)


class SearchProjectSymbolsEnhancedCommand(sublime_plugin.WindowCommand):
    """
    Merges 'goto filename', 'goto symbol in project', and folder-path
    filtering for markdown files - the same three things native Goto
    Anything blends for regular files.

    Each row is a single line: 'notes\\per\\google.md.txt  >  Header Text'.
    Sublime's quick panel only fuzzy-matches this trigger text (a second
    'detail' line is a display-only feature, not searched - confirmed by
    testing), so everything worth typing lives in this one line: folder
    path, filename, and header, all fuzzy-matchable in any order, e.g.
    'secure acct google per notes'.

    run() does NOT touch the filesystem - it only reads the already-built
    _cache, same as native Ctrl+Shift+R reads its own prebuilt index. The
    cache is kept current by plugin_loaded() (startup), on_post_save_async
    (your own edits), and SearchProjectSymbolsEnhancedReindexCommand (manual, for
    files added/removed/edited outside Sublime).
    """

    def run(self):
        folders = self.window.folders()
        if not folders:
            sublime.status_message("No project folders open.")
            return

        items = []
        for full_path, (mtime, rel_path, entries) in _cache.items():
            for title_line, lineno in entries:
                trigger = "{0}  \u203a  {1}".format(rel_path, title_line)
                items.append((trigger, full_path, lineno))

        if not items:
            # Cache genuinely empty (e.g. plugin just installed, or this
            # project folder was added mid-session and never warmed) -
            # fall back to a one-time synchronous-feeling background build.
            sublime.status_message("Building markdown index...")
            threading.Thread(target=self._build_and_show, args=(folders,)).start()
            return

        items.sort(key=lambda item: (item[1].lower(), item[2]))
        self._show_panel(items)

    def _build_and_show(self, folders):
        _refresh_cache(folders)
        items = []
        for full_path, (mtime, rel_path, entries) in _cache.items():
            for title_line, lineno in entries:
                trigger = "{0}  \u203a  {1}".format(rel_path, title_line)
                items.append((trigger, full_path, lineno))
        items.sort(key=lambda item: (item[1].lower(), item[2]))
        sublime.set_timeout(lambda: self._show_panel(items), 0)

    def _show_panel(self, items):
        if not items:
            sublime.status_message("No markdown headers found in project.")
            return
        self.items = items
        display_items = [trigger for trigger, _, _ in items]
        self.window.show_quick_panel(display_items, self.on_done)

    def on_done(self, index):
        if index == -1:
            return
        _, path, lineno = self.items[index]
        self.window.open_file(
            "{0}:{1}".format(path, lineno),
            sublime.ENCODED_POSITION
        )


class SearchProjectSymbolsEnhancedReindexCommand(sublime_plugin.WindowCommand):
    """
    Manually rebuilds the index in the background. Needed when files
    change outside Sublime's awareness - added, deleted, or edited by
    something other than this editor (git pull, external rename, etc.) -
    since on_post_save_async only catches saves made from inside Sublime.
    """

    def run(self):
        folders = self.window.folders()
        if not folders:
            sublime.status_message("No project folders open.")
            return
        sublime.status_message("Reindexing markdown files...")
        threading.Thread(target=_refresh_cache, args=(folders,)).start()


class SearchProjectSymbolsEnhancedWarmCacheListener(sublime_plugin.EventListener):
    """
    Keeps the cache warm two ways:
    1. The moment you save a markdown file from inside Sublime, its
       entry is refreshed immediately (on_post_save_async).
    2. When a window regains focus, a background refresh is kicked off
       (throttled to once per 5s) to opportunistically pick up changes
       made outside Sublime - e.g. switching back after a git pull -
       without you needing to remember the manual reindex command.
       This never blocks the UI and never runs on every single
       tab-switch, only on actual window activation.
    """

    _last_focus_refresh = 0.0
    _FOCUS_REFRESH_COOLDOWN = 5.0

    def on_post_save_async(self, view):
        fname = view.file_name()
        if not fname or not _is_target(os.path.basename(fname)):
            return
        try:
            mtime = os.path.getmtime(fname)
        except OSError:
            return
        rel_path = _project_relpath(fname)
        _cache[fname] = (mtime, rel_path, _scan_file(fname))

    def on_activated_async(self, view):
        window = view.window()
        if not window:
            return
        folders = window.folders()
        if not folders:
            return
        now = time.monotonic()
        if now - SearchProjectSymbolsEnhancedWarmCacheListener._last_focus_refresh < self._FOCUS_REFRESH_COOLDOWN:
            return
        SearchProjectSymbolsEnhancedWarmCacheListener._last_focus_refresh = now
        threading.Thread(target=_refresh_cache, args=(folders,)).start()
