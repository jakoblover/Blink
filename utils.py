import os
import PIL.Image

def error_log(sender='etc', message='An error has occured', error=''):

    with open("logs/{0}-errors.log".format(sender), "a+") as f:
        f.write('[ERROR] {0}. {1}\n'.format(message,error))

def remove_media(path):
    if os.path.isfile(path):
        os.unlink(path)

def remove_all_media(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            error_log('utils', 'Error removing media', e)
            print(e)

def get_gif_duration(filepath):
    try:
        img = PIL.Image.open(filepath)
        img.seek(0)
        frames = duration = 0
        try:
            while True:
                frames += 1
                duration += img.info['duration']
                img.seek(img.tell() + 1)
        except EOFError:
            return frames / duration * 1000
    except Exception as e:
        error_log('utils', 'Error fetching gif duration', e)
        return None

def get_width_height(filepath):
    try:
        img = PIL.Image.open(filepath)
        width,height = img.size[0], img.size[1]
        return width,height
    except Exception as e:
        print("Big fugg when fetching height and width")
        error_log('utils', 'Width and height could not be extracted. Image was probably not an image file.', e)
        return None,None

def valid_media(media, min_aspect_ratio=0, max_aspect_ratio=0):
    try:
        img = PIL.Image.open(media.filepath)
        aspect_ratio = img.size[0] / img.size[1]

        if aspect_ratio >= min_aspect_ratio and aspect_ratio <= max_aspect_ratio:
            return True
        else:
            return False

    except Exception as e:
        error_log('utils', 'Error checking for valid media', e)
        return False

def read_from_log(downloader=''):
    try:
        with open('logs/downloaded-images-{0}.log'.format(downloader), 'r') as f:
            return f.read().split('\n')
    except EnvironmentError as e:
        error_log('DownloaderThread', "Error reading log file", e)
        return []

def write_to_log(downloader,list):
    try:
        with open('logs/downloaded-images-{0}.log'.format(downloader), 'w+') as f:
            f.truncate()
            f.write('\n'.join(list))
    except EnvironmentError as e:
        error_log('DownloaderThread', "Error writing to log file", e)

def log(downloader='',list=None,id=None,max_log_size=1000):
    while len(list) >= max_log_size:
        list.pop(0)
    list.append(id)
    write_to_log(downloader,list)

class Media():
    def __init__(self,id=None, filetype=None, filepath=None, title=None, top_comment=None, source=None, url=None, duration=None, width=None, height=None):
        self.id = id
        self.filetype = filetype
        self.filepath = filepath
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url
        self.duration = duration
        self.width = width
        self.height = height
