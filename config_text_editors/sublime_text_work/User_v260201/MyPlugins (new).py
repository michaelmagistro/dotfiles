import sublime
import sublime_plugin
import re


# ++++++++++++++++++ EXPAND TO DELIMITER +++++++++++++++++++++++++

class ExpandSelectionToDelimiterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        for sel in view.sel():
            # 1. SETUP VARIABLES (MUST BE FIRST)
            line = view.line(sel)
            line_contents = view.substr(line)
            line_start = line.begin()
            rel_begin = sel.begin() - line_start
            scope = view.scope_name(sel.begin())
            matched = False

            # 2. URL DETECTION (PRIORITY #1)
            url_pattern = r'(?:(?:https?|ftp|file)://|www\.)[^\s<>"\'){}]+(?:\?[^\s<>"\'){}]*)?'
            for match in re.finditer(url_pattern, line_contents):
                if match.start() <= rel_begin <= match.end():
                    full_url = match.group(0)
                    # Clean up trailing punctuation that Markdown sometimes adds
                    while full_url and full_url[-1] in '.,;:!?)]}':
                        full_url = full_url[:-1]
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(
                        line_start + match.start(),
                        line_start + match.start() + len(full_url)
                    ))
                    matched = True
                    break
            if matched:
                continue

            # 3. CODE BLOCKS
            code_block_scopes = ["markup.raw.code-fence", "markup.raw.block.fenced", "markup.raw.code.todo"]
            if any(s in scope for s in code_block_scopes):
                if self.expand_code_fence(sel):
                    continue

            # 4. LOGIC GATE
            # Skip only if cursor is in image metadata or bracketed [Title]
            if "meta.image" in scope or "string.other.link" in scope:
                continue

            # 5. INLINE BACKTICKS
            is_inline_code = any(s in scope for s in [
                "todo.snippet",
                "markup.raw.inline",
                "markup.inline.raw",
                "markup.raw.inline.markdown"
            ])
            if is_inline_code:
                tick_pattern = r'`([^`]+)`'
                for match in re.finditer(tick_pattern, line_contents):
                    if match.start() <= rel_begin <= match.end():
                        view.sel().subtract(sel)
                        view.sel().add(sublime.Region(
                            line_start + match.start(1),
                            line_start + match.end(1)
                        ))
                        matched = True
                        break
                if matched:
                    continue

            # 6. WINDOWS & LINUX PATHS
            # Windows paths (O:\...)
            win_path_pattern = r'[a-zA-Z]:\\[^\s`\'"()\[\]{}<>]+'
            for match in re.finditer(win_path_pattern, line_contents):
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break
            if matched:
                continue

            # Linux paths (with lookbehind to avoid stealing URL slashes)
            lin_path_pattern = r'(?<!:)~?\/[^\s`\'"()\[\]{}]+'
            for match in re.finditer(lin_path_pattern, line_contents):
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break
            if matched:
                continue

            # 7. FALLBACK DELIMITERS
            for delim in ["`", '"', "'", "~", ":", "**", "*", "!", ("(", ")"), ("[", "]")]:
                is_pair = isinstance(delim, tuple)
                d_start = delim[0] if is_pair else delim
                d_end = delim[1] if is_pair else delim
                start_idx = line_contents.rfind(d_start, 0, rel_begin + 1)
                if start_idx == -1:
                    continue
                search_from = rel_begin if rel_begin > start_idx + len(d_start) else start_idx + len(d_start)
                end_idx = line_contents.find(d_end, search_from)
                if end_idx == -1:
                    continue
                if (start_idx + len(d_start)) <= rel_begin < end_idx:
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(
                        line_start + start_idx + len(d_start),
                        line_start + end_idx
                    ))
                    matched = True
                    break
            if matched:
                continue

            # 8. WORD/LINE FALLBACK
            word = view.word(sel.begin())
            if not sel.empty() and sel == word:
                view.sel().add(line)
            else:
                view.sel().add(word)

    def expand_code_fence(self, sel):
        view = self.view
        cursor_pos = sel.begin()
        cursor_line = view.rowcol(cursor_pos)[0]
        opening_line_pt = None
        for line_num in range(cursor_line, -1, -1):
            line_region = view.line(view.text_point(line_num, 0))
            if re.match(r'^```|^~~~', view.substr(line_region).strip()):
                opening_line_pt = line_region.end()
                break
        if opening_line_pt is None:
            return False

        total_lines = view.rowcol(view.size())[0]
        for line_num in range(cursor_line, total_lines + 1):
            line_region = view.line(view.text_point(line_num, 0))
            if line_region.begin() >= opening_line_pt and re.match(r'^```|^~~~', view.substr(line_region).strip()):
                closing_line_pt = line_region.begin()
                if opening_line_pt <= cursor_pos <= closing_line_pt:
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(opening_line_pt + 1, closing_line_pt - 1))
                    return True
                break
        return False


class ExpandSelectionToBackticksCommand(ExpandSelectionToDelimiterCommand):
    pass

class OpenDefaultCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            self.view.run_command("open_default_for_current_view")

# +++++++++++++++++++++++++++++++++++++++++++++++++++ EXTEND PLAINTASKS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ST3 = int(sublime.version()) >= 3000

class PlainTasksDueBookmarks(sublime_plugin.EventListener):
    # ========== BOOKMARK TOGGLES ==========
    # Set to True to enable bookmarks for each category
    BOOKMARK_PAST_DUE = True # Items past their due date
    BOOKMARK_CRITICAL = True # Items tagged with @critical
    BOOKMARK_BLOCKER = True  # Items tagged with @blocker
    BOOKMARK_DUE_SOON = True # Items due soon
    BOOKMARK_HIGH = True # Items tagged with @critical
    BOOKMARK_TODAY = True # Items tagged with @today
    # ======================================
    
    def on_activated(self, view):
        self.update_bookmarks(view)

    def on_post_save(self, view):
        self.update_bookmarks(view)

    def on_load(self, view):
        self.update_bookmarks(view)

    def update_bookmarks(self, view):
        if view.score_selector(0, "text.todo") <= 0:
            return
        
        # Run vanilla toggle to ensure past_due regions are up-to-date
        view.run_command('plain_tasks_toggle_highlight_past_due')
        
        # Start with existing bookmarks
        all_regions = list(view.get_regions("bookmarks"))
        
        # Add past due items
        if self.BOOKMARK_PAST_DUE:
            past_due_regions = view.get_regions("past_due")
            all_regions.extend(past_due_regions)
        
        # Add due soon items - try both possible region names
        if self.BOOKMARK_DUE_SOON:
            due_soon_regions = view.get_regions("due_soon")
            if not due_soon_regions:
                # If no region exists, find by scope instead
                due_soon_regions = view.find_by_selector("text.todo meta.item.todo.pending string.other.tag.todo.high")
            all_regions.extend(due_soon_regions)
        
        # Add critical tagged items
        if self.BOOKMARK_CRITICAL:
            critical_regions = view.find_by_selector("text.todo meta.item.todo.pending string.other.tag.todo.critical")
            all_regions.extend(critical_regions)

        # Add critical tagged items
        if self.BOOKMARK_HIGH:
            high_regions = view.find_by_selector("text.todo meta.item.todo.pending string.other.tag.todo.high")
            all_regions.extend(high_regions)
        
        # Add blocker tagged items
        if self.BOOKMARK_BLOCKER:
            blocker_regions = view.find_by_selector("text.todo meta.item.todo.pending string.other.tag.todo.blocker")
            all_regions.extend(blocker_regions)
        
        # Add today tagged items
        if self.BOOKMARK_TODAY:
            today_regions = view.find_by_selector("text.todo meta.item.todo.pending string.other.tag.todo.today")
            all_regions.extend(today_regions)
        
        # Remove duplicates
        unique_regions = []
        seen = set()
        for region in all_regions:
            key = (region.begin(), region.end())
            if key not in seen:
                seen.add(key)
                unique_regions.append(region)
        
        flags = (sublime.HIDDEN | sublime.PERSISTENT) if ST3 else 0
        view.add_regions('bookmarks', unique_regions, 'bookmarks', 'bookmark', flags)