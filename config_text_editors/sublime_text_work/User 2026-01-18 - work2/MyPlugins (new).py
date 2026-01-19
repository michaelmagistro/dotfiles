import sublime
import sublime_plugin
import re

# ++++++++++++++++++ EXPAND TO DELIMITER +++++++++++++++++++++++++

class ExpandSelectionToDelimiterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        
        for sel in view.sel():
            scope = view.scope_name(sel.begin())
            is_todo_snippet = "todo.snippet" in scope
            
            # --- CODE BLOCK LOGIC ---
            code_block_scopes = [
                "markup.raw.code-fence", 
                "markup.raw.block.fenced", 
                "markup.raw.code.todo" 
            ]
            
            if any(s in scope for s in code_block_scopes):
                if self.expand_code_fence(sel):
                    continue
            
            is_image = "meta.image" in scope
            is_regular_link = ("meta.link" in scope or "markup.underline.link" in scope) and not is_image and not is_todo_snippet
            
            if is_regular_link:
                continue
            
            line = view.line(sel)
            line_contents = view.substr(line)
            line_start = line.begin()
            rel_begin = sel.begin() - line_start
            
            matched = False

            # Check for inline backtick snippets
            is_inline_code = any(s in scope for s in ["todo.snippet", "markup.raw.inline", "markup.inline.raw", "markup.raw.inline.markdown"])
            if is_inline_code:
                tick_pattern = r'`([^`]+)`'
                matches = list(re.finditer(tick_pattern, line_contents))
                for match in matches:
                    if match.start() <= rel_begin <= match.end():
                        view.sel().subtract(sel)
                        view.sel().add(sublime.Region(line_start + match.start(1), line_start + match.end(1)))
                        matched = True
                        break
                if matched: continue

            # --- PATH DETECTION (SEPARATE STEPS FOR STABILITY) ---

            # --- URL DETECTION ---
            # This captures common protocols and handles the full URL
            url_pattern = r'\b(?:https?|ftp|file)://[^\s`\'"()\[\]{}]+'
            url_matches = list(re.finditer(url_pattern, line_contents))
            for match in url_matches:
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break
            if matched: continue

            # 1. WINDOWS PATHS (Starts with Drive Letter)
            win_path_pattern = r'[a-zA-Z]:\\[^\s`\'"()\[\]{}]+'
            win_matches = list(re.finditer(win_path_pattern, line_contents))
            for match in win_matches:
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break
            if matched: continue

            # 2. LINUX PATHS (Starts with / or ~/)
            lin_path_pattern = r'~?\/[^\s`\'"()\[\]{}]+'
            lin_matches = list(re.finditer(lin_path_pattern, line_contents))
            for match in lin_matches:
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break
            if matched: continue

            # --- FALLBACK DELIMITERS ---
            for delim in ["`", '"', "'", "~", ":", "**", "*", ("(", ")")]:
                is_pair = isinstance(delim, tuple)
                d_start = delim[0] if is_pair else delim
                d_end   = delim[1] if is_pair else delim
                
                delim_len_start = len(d_start)
                start_idx = line_contents.rfind(d_start, 0, rel_begin + 1)
                if start_idx == -1: continue
                
                search_from = rel_begin if rel_begin > start_idx + delim_len_start else start_idx + delim_len_start
                end_idx = line_contents.find(d_end, search_from)
                if end_idx == -1: continue
                
                if (start_idx + delim_len_start) <= rel_begin < end_idx:
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + start_idx + delim_len_start, line_start + end_idx))
                    matched = True
                    break
            
            if matched: continue
            
            # --- FINAL FALLBACK ---
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
            line_str = view.substr(line_region).strip()
            if re.match(r'^```|^~~~', line_str):
                opening_line_pt = line_region.end()
                break
        
        if opening_line_pt is None: return False
        
        total_lines = view.rowcol(view.size())[0]
        for line_num in range(cursor_line, total_lines + 1):
            line_region = view.line(view.text_point(line_num, 0))
            line_str = view.substr(line_region).strip()
            if line_region.begin() >= opening_line_pt and re.match(r'^```|^~~~', line_str):
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
        # Append current past_due regions to existing bookmarks
        existing_bookmarks = view.get_regions("bookmarks")
        past_due_regions = view.get_regions("past_due")
        existing_bookmarks.extend(past_due_regions)
        flags = (sublime.HIDDEN | sublime.PERSISTENT) if ST3 else 0
        view.add_regions('bookmarks', existing_bookmarks, 'bookmarks', 'bookmark', flags)