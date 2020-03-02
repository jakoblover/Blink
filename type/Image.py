from .Media import Media
from validators.ImageValidator import ImageValidator


class Image(Media):
    def __init__(
        self,
        id=None,
        file_format=None,
        file_path=None,
        title=None,
        top_comment=None,
        source=None,
        url=None,
        duration=None,
        width=None,
        height=None,
    ):
        super(Media, self).__init__(
            id=id,
            file_format=file_format,
            file_path=file_path,
            title=title,
            top_comment=top_comment,
            source=source,
            url=url,
            width=width,
            height=height,
        )
        self.id = id
        self.file_format = file_format
        self.file_path = file_path
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url
        self.width = width
        self.height = height

        self.validator = ImageValidator(self)
