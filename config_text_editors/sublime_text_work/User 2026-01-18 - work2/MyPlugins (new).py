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
            
            if "markup.raw.code-fence" in scope or "markup.raw.block.fenced":
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

            # Check if we're in a todo code snippet (your custom scope)
            is_inline_code = any(s in scope for s in [
                "todo.snippet",                     # your custom Tasks syntax
                "markup.raw.inline",                # most common in MarkdownEditing & many others
                "markup.inline.raw",                # some variants
                "markup.raw.inline.markdown",       # built-in & CommonMark-based syntaxes
                "inline.raw.markup.markdown"        # older bundles (rare nowadays)
            ])

            if is_inline_code:
                # Try to expand to full backtick content first
                tick_pattern = r'`([^`]+)`'
                matches = list(re.finditer(tick_pattern, line_contents))
                for match in matches:
                    if match.start() <= rel_begin <= match.end():   # inclusive on both ends
                        view.sel().subtract(sel)
                        view.sel().add(sublime.Region(
                            line_start + match.start(1),
                            line_start + match.end(1)
                        ))
                        matched = True
                        break

                if matched:
                    continue

            # === Only reach here if NOT in snippet OR backticks didn't match ===
            # 1. PATH DETECTION (now safe — won't override snippets)
            path_pattern = r'[a-zA-Z]:\\[^\s`\'"()\[\]{}]+'
            path_matches = list(re.finditer(path_pattern, line_contents))
            for match in path_matches:
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break

            if matched:
                continue

            # Only if NOT in snippet (or snippet didn't match) → try paths
            # 1. PATH DETECTION
            path_pattern = r'[a-zA-Z]:\\[^\s`\'"()\[\]{}]+'
            path_matches = list(re.finditer(path_pattern, line_contents))
            for match in path_matches:
                # Keep your original <= end to catch cursor at the very end
                if match.start() <= rel_begin <= match.end():
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + match.start(), line_start + match.end()))
                    matched = True
                    break

            if matched:
                continue

            # 3. FALLBACK DELIMITERS — backticks FIRST so they always win when present
            for delim in ["`", '"', "'", "~", ":", "**", "*", ("(", ")")]:
                is_pair = isinstance(delim, tuple)
                d_start = delim[0] if is_pair else delim
                d_end   = delim[1] if is_pair else delim
                
                delim_len_start = len(d_start)
                delim_len_end   = len(d_end)
                
                # Find nearest opening delimiter to the LEFT of cursor
                start_idx = line_contents.rfind(d_start, 0, rel_begin + 1)  # +1 to include cursor position
                if start_idx == -1:
                    continue
                
                # Find nearest closing delimiter to the RIGHT of cursor
                # Start search from cursor position onward
                search_from = rel_begin if rel_begin > start_idx + delim_len_start else start_idx + delim_len_start
                end_idx = line_contents.find(d_end, search_from)
                if end_idx == -1:
                    continue
                
                content_start = start_idx + delim_len_start
                content_end   = end_idx
                
                # Cursor must be inside the content (after open, before close)
                if content_start <= rel_begin < content_end:   # strict < at end → excludes closing delim
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(
                        line_start + content_start,
                        line_start + content_end
                    ))
                    matched = True
                    break
            
            if matched: continue
            
            # 4. WORD/LINE FALLBACK
            word = view.word(sel.begin())
            if not sel.empty() and sel == word:
                view.sel().add(line)
            else:
                view.sel().add(word)

    def expand_code_fence(self, sel):
        view = self.view
        cursor_line = view.rowcol(sel.begin())[0]
        opening_line = None
        for line_num in range(cursor_line, -1, -1):
            line_region = view.line(view.text_point(line_num, 0))
            if re.match(r'^```|^~~~', view.substr(line_region).strip()):
                opening_line = line_num
                break
        if opening_line is None: return False
        
        total_lines = view.rowcol(view.size())[0]
        for line_num in range(opening_line + 1, total_lines + 1):
            line_region = view.line(view.text_point(line_num, 0))
            if re.match(r'^```|^~~~', view.substr(line_region).strip()):
                start = view.line(view.text_point(opening_line, 0)).end() + 1
                end = line_region.begin() - 1
                view.sel().subtract(sel)
                view.sel().add(sublime.Region(start, end))
                return True
        return False

# This line passes the class to the expand to backticks command, so, you're essentially replacing the backticks command with expand to delimiter. otherwise, you'd need to create a custom command and update your keybindings file.
class ExpandSelectionToBackticksCommand(ExpandSelectionToDelimiterCommand):
    pass

# ++++++++++++++++++ EXTEND PLAINTASKS +++++++++++++++++++++++++

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

# ++++++++++++++++++ OTHER +++++++++++++++++++++++++

class OpenDefaultCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name()
        if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
            self.view.run_command("open_default_for_current_view")