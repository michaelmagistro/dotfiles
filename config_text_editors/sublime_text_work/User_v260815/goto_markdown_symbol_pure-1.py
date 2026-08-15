# this displays the folder path and name below the header. not the most efficient use of space, but may be good if you have longer headers.. will have to test.
import sublime
import sublime_plugin
import os
import re
import threading
import time

HEADER_RE = re.compile(r'^(#{1,6})\s+(.*)')

# Module-level cache, keyed by full file path:
#   full_path -> (mtime, rel_path, [(title_line, line_number), ...])
# Separate from goto_markdown_symbol.py's cache (different module, own
# namespace) even though the shape is the same.
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
    segment (e.g. 'notes\\Hair Protocol.md.txt'), matching the sidebar.
    Used here for DISPLAY ONLY - it is never fed into the searchable
    trigger text in this version of the script.
    """
    folder_norm = os.path.normpath(folder)
    parent = os.path.dirname(folder_norm)
    return os.path.relpath(os.path.normpath(full_path), parent)


def _project_relpath(full_path):
    """Same as above, but for the on-save refresh which only has a bare path."""
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
    """Re-scan only files whose mtime changed since last time."""
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

    for stale in set(_cache) - seen:
        del _cache[stale]


def _warm_all_open_windows():
    for window in sublime.windows():
        folders = window.folders()
        if folders:
            threading.Thread(target=_refresh_cache, args=(folders,)).start()


def plugin_loaded():
    sublime.set_timeout_async(_warm_all_open_windows, 200)


class GotoMarkdownSymbolPureCommand(sublime_plugin.WindowCommand):
    """
    Symbol-only search across all markdown files - mirrors native
    Ctrl+Shift+R (Goto Symbol in Project), but for markdown headers
    instead of code symbols.

    Each row is a native two-line quick panel item:
      trigger (bold, SEARCHED):  Header Text
      detail  (dim, NOT searched):  notes\\per\\google.md.txt

    The path/filename is shown for context but deliberately excluded
    from matching, since folder and filename text mixed into symbol
    search tends to add noise. If you want path/filename to be part of
    the search too, that's what goto_markdown_symbol.py (Ctrl+Shift+H)
    is for - the two scripts are intentionally separate so you can pick
    the right tool for the moment rather than compromising on one.

    Like the other script, run() reads only from the prebuilt _cache -
    no filesystem work happens at invocation time.
    """

    def run(self):
        folders = self.window.folders()
        if not folders:
            sublime.status_message("No project folders open.")
            return

        items = []
        for full_path, (mtime, rel_path, entries) in _cache.items():
            for title_line, lineno in entries:
                items.append((title_line, rel_path, full_path, lineno))

        if not items:
            sublime.status_message("Building markdown index...")
            threading.Thread(target=self._build_and_show, args=(folders,)).start()
            return

        items.sort(key=lambda item: (item[1].lower(), item[3]))
        self._show_panel(items)

    def _build_and_show(self, folders):
        _refresh_cache(folders)
        items = []
        for full_path, (mtime, rel_path, entries) in _cache.items():
            for title_line, lineno in entries:
                items.append((title_line, rel_path, full_path, lineno))
        items.sort(key=lambda item: (item[1].lower(), item[3]))
        sublime.set_timeout(lambda: self._show_panel(items), 0)

    def _show_panel(self, items):
        if not items:
            sublime.status_message("No markdown headers found in project.")
            return
        self.items = items
        # Two-line item: [trigger, detail]. Only 'trigger' (the header
        # text) is fuzzy-matched; 'detail' (the path) is display-only.
        display_items = [[title_line, rel_path] for title_line, rel_path, _, _ in items]
        self.window.show_quick_panel(display_items, self.on_done)

    def on_done(self, index):
        if index == -1:
            return
        _, _, path, lineno = self.items[index]
        self.window.open_file(
            "{0}:{1}".format(path, lineno),
            sublime.ENCODED_POSITION
        )


class GotoMarkdownSymbolPureReindexCommand(sublime_plugin.WindowCommand):
    """Manually rebuilds the index in the background (for external file changes)."""

    def run(self):
        folders = self.window.folders()
        if not folders:
            sublime.status_message("No project folders open.")
            return
        sublime.status_message("Reindexing markdown files...")
        threading.Thread(target=_refresh_cache, args=(folders,)).start()


class GotoMarkdownSymbolPureWarmCacheListener(sublime_plugin.EventListener):
    """Keeps the cache warm on save, and opportunistically on window focus."""

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
        if now - GotoMarkdownSymbolPureWarmCacheListener._last_focus_refresh < self._FOCUS_REFRESH_COOLDOWN:
            return
        GotoMarkdownSymbolPureWarmCacheListener._last_focus_refresh = now
        threading.Thread(target=_refresh_cache, args=(folders,)).start()
