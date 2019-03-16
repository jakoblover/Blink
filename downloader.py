from downloaders import RedditDownloader
from PyQt5 import QtCore
import time
import yaml
import utils
import PIL.Image


class DownloaderThread(QtCore.QThread):
    def __init__(self, queue, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.downloaded_ids = self._read_from_log()

        #Config parameters
        self._aspect_ratio_min = 0
        self._aspect_ratio_max = 0
        self._max_queue_size = 0
        self._max_log_size = 0
        self._load_config()

        self.reddit = RedditDownloader()

    def _load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._max_queue_size = configs['params']['max_queue_size']
                self._max_log_size = configs['params']['max_log_size']
                self._aspect_ratio_min = configs['params']['aspect_ratio_min']
                self._aspect_ratio_max = configs['params']['aspect_ratio_max']

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            self.error_log('DownloaderThread',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            self.error_log('DownloaderThread',"Error when applying configs", e)

    def _read_from_log(self):
        try:
            with open('logs/downloaded-images.log', 'r') as f:
                return f.read().split('\n')
        except EnvironmentError:
            print("Unable to open log file. Returning empty list.")
            return []

    def _write_to_log(self,list):
        with open('logs/downloaded-images.log', 'w+') as f:
            f.truncate()
            f.write('\n'.join(list))

    def _log(self,id):
        print("Logging IDs")
        if len(self.downloaded_ids) >= self._max_log_size:
            print("Queue is full. Removing top entry")
            self.downloaded_ids.pop(0)
        self.downloaded_ids.append(id)
        print("Writing to log")
        self._write_to_log(self.downloaded_ids)


    def _check_queue(self):
        '''
        Checks if buffer needs refill :GLOM:
        '''
        return not self.queue.full()

    def _valid_media(self, media):
        img = PIL.Image.open(media.path)
        aspect_ratio = img.size[0] / img.size[1]
        if aspect_ratio >= self._aspect_ratio_min and aspect_ratio <= self._aspect_ratio_max:
            return True
        else:
            return False

    def _download(self):
        '''
        Decide what source to download from.
        :return: media object
        @TODO: Add support for more sources
        '''

        return self.reddit.download(self.downloaded_ids)

    def run(self):
        self.running = True
        while self.running:
            #If buffer needs refill
            if self._check_queue():
                media = self._download()

                if media != None:
                    if self._valid_media(media):
                        print("Adding to queue")
                        self.queue.put(media)
                    else:
                        print("Media did not meet config specs. Skipping.")
                        utils.remove_media(media.path)
                    self._log(media.id)

            time.sleep(2)

