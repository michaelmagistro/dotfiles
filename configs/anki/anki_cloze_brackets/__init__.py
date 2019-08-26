from anki.template.template import Template
import re


def clozeTextPatch(self, txt, ord, type):
    clozeReg = r"(?si)\{\{(c)%s::(.*?)(::(.*?))?\}\}"
    reg = clozeReg
    if not re.search(reg%ord, txt):
        return ""
    txt = self._removeFormattingFromMathjax(txt, ord)
    def repl(m):
        # replace chosen cloze with type
        if type == "q":
            if m.group(4):
                buf = "%s" % m.group(4)
            else:
                buf = "..."
        else:
            buf = m.group(2)
        # uppercase = no formatting
        if m.group(1) == "c":
            buf = "<span class=cloze>%s</span>" % buf
        return buf
    txt = re.sub(reg%ord, repl, txt)
    # and display other clozes normally
    return re.sub(reg%r"\d+", "\\2", txt)

Template.clozeText = clozeTextPatch