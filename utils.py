import os

def error_log(sender='etc', message='An error has occured', error=''):
    with open("logs/{0}-errors.log".format(sender), "a+") as f:
        f.write('[ERROR] {0}. {1}\n'.format(message,error))

def remove_media(path):
    os.remove(path)

class Media():
    def __init__(self,id=None, filetype=None, filepath=None, title=None, top_comment=None, source=None, url=None):
        self.id = id
        self.filetype = filetype
        self.filepath = filepath
        self.title = title
        self.top_comment = top_comment
        self.source = source
        self.url = url
