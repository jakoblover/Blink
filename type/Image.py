from .Media import Media


class Image(Media):
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
        Media.__init__(
            self,
            id=id,
            file_format=file_format,
            file_path=file_path,
            width=width,
            height=height,
            source=source,
            url=url,
            title=title,
            top_comment=top_comment,
        )
