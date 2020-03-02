import PIL.Image

from .MediaValidator import MediaValidator


class ImageValidator(MediaValidator):
    def __init__(self, media):
        super(ImageValidator, self).__init__(media)

    def validate(self):
        img = PIL.Image.open(self.media.filepath)
        aspect_ratio = img.size[0] / img.size[1]

        if aspect_ratio >= min_aspect_ratio and aspect_ratio <= max_aspect_ratio:
            return True
        else:
            return False
