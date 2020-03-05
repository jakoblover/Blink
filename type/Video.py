from .Media import Media


class Video(Media):
    def __init__(
        self,
        id,
        file_format,
        file_path,
        duration,
        width,
        height,
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
            title=title,
            top_comment=top_comment,
            source=source,
            url=url,
            width=width,
            height=height,
        )

        self.duration = duration
