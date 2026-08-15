import sublime
import sublime_plugin
import os
import re
import threading

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


class GotoMarkdownSymbolCommand(sublime_plugin.WindowCommand):
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
    """

    def run(self):
        folders = self.window.folders()
        if not folders:
            sublime.status_message("No project folders open.")
            return

        # Do the filesystem walk / re-scan on a background thread so the
        # UI never blocks. On a warm cache this is just stat() calls.
        threading.Thread(target=self._build_and_show, args=(folders,)).start()

    def _build_and_show(self, folders):
        _refresh_cache(folders)
        items = []
        for full_path, (mtime, rel_path, entries) in _cache.items():
            for title_line, lineno in entries:
                # Single line, fully searchable (Sublime's quick panel only
                # fuzzy-matches the trigger line - a separate detail line
                # is display-only and never searched, so there's no value
                # in splitting this across two lines). Path first, since
                # that's what groups/sorts naturally; header after the
                # arrow as the "what's actually in this file" payload.
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


class GotoMarkdownSymbolWarmCacheListener(sublime_plugin.EventListener):
    """
    Keeps the cache warm: the moment you save a markdown file, its entry
    is refreshed immediately rather than waiting for the next panel
    invocation to notice the mtime changed.
    """

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