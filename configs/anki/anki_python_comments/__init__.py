from anki.importing.csvfile import TextImporter


def openFileLiteralComments(self):

    self.dialect = None
    self.fileobj = open(self.file, "r", encoding='utf-8-sig')
    self.data = self.fileobj.read()

    self.data = [x+"\n" for x in self.data.split("\n")]
    if self.data:
        if self.data[0].startswith("tags:"):
            tags = str(self.data[0][5:]).strip()
            self.tagsToAdd = tags.split(" ")
            del self.data[0]
        self.updateDelimiter()
    if not self.dialect and not self.delimiter:
        raise Exception("unknownFormat")


TextImporter.openFile = openFileLiteralComments
