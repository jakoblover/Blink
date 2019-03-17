import os
import PIL.Image

def error_log(sender='etc', message='An error has occured', error=''):
    with open("logs/{0}-errors.log".format(sender), "a+") as f:
        f.write('[ERROR] {0}. {1}\n'.format(message,error))

def remove_media(path):
    os.remove(path)

def valid_media(media, min_aspect_ratio, max_aspect_ratio):
    img = PIL.Image.open(media.filepath)
    aspect_ratio = img.size[0] / img.size[1]
    if aspect_ratio >= min_aspect_ratio and aspect_ratio <= max_aspect_ratio:
        return True
    else:
        return False

class Media():
    def __init__(self,id=None, filetype=None, filepath=None, title=None, top_comment=None, source=None, url=None):
        self.id = id
        self.filetype = filetype
        self.filepath = filepath
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url
