import os
import PIL.Image

def error_log(sender='etc', message='An error has occured', error=''):
    with open("logs/{0}-errors.log".format(sender), "a+") as f:
        f.write('[ERROR] {0}. {1}\n'.format(message,error))

def remove_media(path):
    os.remove(path)

def valid_media(media, min_aspect_ratio, max_aspect_ratio):
    try:
        img = PIL.Image.open(media.filepath)
        aspect_ratio = img.size[0] / img.size[1]
        if aspect_ratio >= min_aspect_ratio and aspect_ratio <= max_aspect_ratio:
            return True
        else:
            return False

    except Exception as e:
        print("Something wrong happened when checking if media was valid. ",e)

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
    if len(list) >= max_log_size:
        list.pop(0)
    list.append(id)
    write_to_log(downloader,list)

class Media():
    def __init__(self,id=None, filetype=None, filepath=None, title=None, top_comment=None, source=None, url=None):
        self.id = id
        self.filetype = filetype
        self.filepath = filepath
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url
