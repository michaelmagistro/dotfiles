# import sublime
# import sublime_plugin

# # expand the selection to the backticks
# class ExpandSelectionToBackticksCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         for sel in self.view.sel():
#             line = self.view.line(sel)
#             line_contents = self.view.substr(line)
#             start = line_contents.rfind('`', 0, sel.begin() - line.begin())
#             end = line_contents.find('`', sel.end() - line.begin())
#             if start != -1 and end != -1:
#                 self.view.sel().subtract(sel)
#                 self.view.sel().add(sublime.Region(line.begin() + start + 1, line.begin() + end))

# # open excel file with excel
# class OpenDefaultCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         file_name = self.view.file_name()
#         if file_name.endswith(".xlsx") or file_name.endswith(".xls"):
#             self.view.run_command("open_default_for_current_view")