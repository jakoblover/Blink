from .MediaValidator import MediaValidator


class WEBMValidator(MediaValidator):
    def __init__(self, media):
        super(WEBMValidator, self).__init__(media)

    def validate(self):
        pass
