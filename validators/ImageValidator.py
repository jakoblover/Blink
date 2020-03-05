import PIL.Image

from .MediaValidator import MediaValidator


class ImageValidator(MediaValidator):
    def __init__(self, media, config):
        super(ImageValidator, self).__init__(media)

        self.config = config

    def validate(self):

        width, height = self._get_width_height(self.media.file_path)
        aspect_ratio = width / height

        if (
            aspect_ratio >= self.config["min_aspect_ratio"]
            and aspect_ratio <= self.config["max_aspect_ratio"]
        ):
            return True
        else:
            return False

    def _get_width_height(self, filepath):
        img = PIL.Image.open(filepath)
        width, height = img.size[0], img.size[1]
        return width, height
