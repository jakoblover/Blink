import os


class Media:
    def __init__(
        self,
        id,
        file_format,
        file_path,
        width=None,
        height=None,
        source=None,
        url=None,
        title=None,
        top_comment=None,
    ):
        self.id = id
        self.file_format = file_format
        self.file_path = file_path
        self.width = width
        self.height = height
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url

    def remove(self):
        if os.path.isfile(self.file_path):
            os.unlink(self.file_path)
