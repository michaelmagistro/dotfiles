import sublime
import sublime_plugin
import re

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
            
            # Check if we're in a link - let default behavior handle it
            if "meta.link" in scope or "markup.underline.link" in scope:
                print("In link scope, skipping")
                continue
            
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