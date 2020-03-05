from .MediaValidator import MediaValidator


class VideoValidator(MediaValidator):
    def __init__(self, media):
        super(VideoValidator, self).__init__(media)

    def validate(self):
        pass
