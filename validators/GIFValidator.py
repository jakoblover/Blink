from .MediaValidator import MediaValidator


class GIFValidator(MediaValidator):
    def __init__(self, media):
        super(GIFValidator, self).__init__(media)

    def validate(self):
        pass
