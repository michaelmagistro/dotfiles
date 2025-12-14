import sublime
import sublime_plugin
import re

# +++++++++++++++++++++++++++++++++++++++++++++++++++ EXPAND SELECTION TO TICKS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class ExpandSelectionToDelimiterCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        
        for sel in view.sel():
            # Check for code fence first
            scope = view.scope_name(sel.begin())
            print(f"Scope at cursor: {scope}")  # Debug
            
            if "markup.raw.code-fence" in scope or "markup.raw.block.fenced" in scope:
                if self.expand_code_fence(sel):
                    continue
            
            # Check if we're in a regular link (but NOT an image link)
            # Images have "meta.image" in their scope, so exclude those
            is_image = "meta.image" in scope
            is_regular_link = ("meta.link" in scope or "markup.underline.link" in scope) and not is_image
            
            if is_regular_link:
                print("In regular link scope (not image), skipping")
                continue
            
            # If we're in an image scope, don't skip - let it fall through to image handling
            if is_image:
                print("In image scope, will process as image")
            
            # Try inline delimiters on current line
            line = view.line(sel)
            line_contents = view.substr(line)
            line_start = line.begin()
            rel_begin = sel.begin() - line_start
            rel_end = sel.end() - line_start
            
            # If cursor is at start or end of line (ignoring whitespace), select whole line
            stripped = line_contents.strip()
            if stripped:
                first_char_pos = line_contents.find(stripped[0])
                last_char_pos = line_contents.rfind(stripped[-1])
                
                if rel_begin <= first_char_pos or rel_begin >= last_char_pos + 1:
                    view.sel().subtract(sel)
                    view.sel().add(line)
                    continue
            
            matched = False

            # Handle image alt text ![title](url)
            print(f"Line: '{line_contents}'")
            print(f"Cursor position: {rel_begin}")
            
            # Look for complete image pattern around cursor
            img_pattern = r'!\[([^\]]*)\]\s*\([^\)]+\)'
            matches = list(re.finditer(img_pattern, line_contents))
            print(f"Found {len(matches)} image patterns")
            
            for match in matches:
                # Parse the image components: ![alt](url)
                full_match = match.group(0)
                alt_text = match.group(1)
                
                # Find where ]( appears to separate alt from url
                bracket_paren = full_match.find('](')
                
                alt_start = match.start() + 2  # After ![
                alt_end = match.start() + 2 + len(alt_text)  # Before ]
                url_start = match.start() + bracket_paren + 2  # After ](
                url_end = match.end() - 1  # Before final )
                
                print(f"Image match: start={match.start()}, end={match.end()}")
                print(f"Alt text: '{alt_text}' from {alt_start} to {alt_end}")
                print(f"URL from {url_start} to {url_end}")
                print(f"Cursor at {rel_begin}")
                
                # If cursor is anywhere in the ![...](...) construct
                if match.start() <= rel_begin <= match.end():
                    # Determine which part to select based on cursor position
                    if alt_start <= rel_begin <= alt_end:
                        # Cursor in alt text - select alt text
                        view.sel().subtract(sel)
                        view.sel().add(sublime.Region(line_start + alt_start, line_start + alt_end))
                        print(f"Cursor in alt text, selected alt text")
                    else:
                        # Cursor elsewhere (in url or brackets) - select url
                        view.sel().subtract(sel)
                        view.sel().add(sublime.Region(line_start + url_start, line_start + url_end))
                        print(f"Cursor in url area, selected url")
                    matched = True
                    break
            
            if matched:
                print("Continuing after image match")
                continue
            
            print("No image match, trying other delimiters")

            # Try delimiters in order
            for delim in ["`", "'", '"', "**", "*"]:
                delim_len = len(delim)
                start = line_contents.rfind(delim, 0, rel_begin)
                if start == -1:
                    continue
                end = line_contents.find(delim, rel_end)
                if end == -1:
                    continue
                
                content_start = start + delim_len
                if content_start <= rel_begin <= end:
                    view.sel().subtract(sel)
                    view.sel().add(sublime.Region(line_start + content_start, line_start + end))
                    matched = True
                    break
            
            if matched:
                continue
            
            # No delimiter match - check if we already have a word selected
            if not sel.empty():
                word = view.word(sel.begin())
                # If current selection equals word selection, expand to line
                if sel == word:
                    view.sel().subtract(sel)
                    view.sel().add(line)
                    continue
            
            # Nothing selected or not a word - expand to word
            word = view.word(sel.begin())
            view.sel().subtract(sel)
            view.sel().add(word)
    
    def expand_code_fence(self, sel):
        view = self.view
        cursor_line = view.rowcol(sel.begin())[0]
        
        # Find opening fence
        opening_line = None
        for line_num in range(cursor_line, -1, -1):
            line_region = view.line(view.text_point(line_num, 0))
            if re.match(r'^```|^~~~', view.substr(line_region).strip()):
                opening_line = line_num
                break
        
        if opening_line is None:
            return False
        
        # Find closing fence
        total_lines = view.rowcol(view.size())[0]
        for line_num in range(opening_line + 1, total_lines + 1):
            line_region = view.line(view.text_point(line_num, 0))
            if re.match(r'^```|^~~~', view.substr(line_region).strip()):
                # Select content between fences
                start = view.line(view.text_point(opening_line, 0)).end() + 1
                end = line_region.begin() - 1
                view.sel().subtract(sel)
                view.sel().add(sublime.Region(start, end))
                return True
        
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