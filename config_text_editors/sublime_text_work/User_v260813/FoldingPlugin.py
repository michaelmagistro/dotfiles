import sublime
import sublime_plugin


class FoldAllExceptTopLevelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        # Guard against empty selection or empty file
        if not view.sel() or view.size() == 0:
            return

        sel = view.sel()[0]
        cursor_line = view.rowcol(sel.begin())[0]
        max_line = view.rowcol(view.size())[0]

        def is_blank(line_num):
            return view.substr(view.line(view.text_point(line_num, 0))).strip() == ""

        def indent(line_num):
            return view.indentation_level(view.text_point(line_num, 0))

        def line_end(line_num):
            return view.line(view.text_point(line_num, 0)).end()

        def line_begin(line_num):
            return view.line(view.text_point(line_num, 0)).begin()

        # Collect all top-level (indent 0) block starting lines
        top_level_starts = []
        for line_num in range(0, max_line + 1):
            if not is_blank(line_num) and indent(line_num) == 0:
                top_level_starts.append(line_num)

        def block_content_end(block_start, next_block_start):
            """Last line index of a block's content, given the next top-level start (or EOF)."""
            if next_block_start is not None:
                return next_block_start - 1
            return max_line

        def fold_block_to_level1(block_start, next_block_start):
            """Fold everything inside this block — ellipsis on the heading line."""
            content_end = block_content_end(block_start, next_block_start)
            if content_end < block_start + 1:
                return
            view.fold(sublime.Region(line_end(block_start), line_end(content_end)))

        def fold_block_to_level2(block_start, next_block_start):
            """Keep level-1 children visible; fold each of their contents individually."""
            content_end = block_content_end(block_start, next_block_start)

            # Collect level-1 children (indent == 1) within this block
            children = []
            for line_num in range(block_start + 1, content_end + 1):
                if not is_blank(line_num) and indent(line_num) == 1:
                    children.append(line_num)

            for j, child in enumerate(children):
                # Child content ends just before next child, or at block_content_end
                if j + 1 < len(children):
                    child_content_end = children[j + 1] - 1
                else:
                    child_content_end = content_end

                if child_content_end < child + 1:
                    continue  # no content to fold

                view.fold(sublime.Region(line_end(child), line_end(child_content_end)))

        # Determine cursor context
        cursor_on_top_level = not is_blank(cursor_line) and indent(cursor_line) == 0
        cursor_at_line_end = sel.begin() == line_end(cursor_line)

        # Find which top-level block the cursor belongs to
        target_top = cursor_line
        if not cursor_on_top_level:
            while target_top > 0:
                if not is_blank(target_top) and indent(target_top) == 0:
                    break
                target_top -= 1

        # --- Three modes ---
        #
        # Mode A: cursor is mid-line on a project heading
        #   → fold ALL projects to level 1, including the one the cursor is on
        #
        # Mode B: cursor is at end-of-line on a project heading
        #   → fold all OTHER projects to level 1
        #   → fold THIS project to level 2 (subtask names stay visible)
        #
        # Mode C: cursor is inside a project (not on the heading)
        #   → fold all OTHER projects to level 1
        #   → leave THIS project fully visible

        for i, block_start in enumerate(top_level_starts):
            next_start = top_level_starts[i + 1] if i + 1 < len(top_level_starts) else None

            if cursor_on_top_level and not cursor_at_line_end:
                # Mode A — fold every block including the cursor's
                fold_block_to_level1(block_start, next_start)

            elif cursor_on_top_level and cursor_at_line_end:
                # Mode B — fold others to L1, cursor block to L2
                if block_start == target_top:
                    fold_block_to_level2(block_start, next_start)
                else:
                    fold_block_to_level1(block_start, next_start)

            else:
                # Mode C — fold all other blocks to L1, leave cursor block open
                if block_start != target_top:
                    fold_block_to_level1(block_start, next_start)

        view.show_at_center(sel)