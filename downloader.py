from downloaders import RedditDownloader
from PyQt5 import QtCore
import time
import yaml
from utils import error_log,Media

class DownloaderThread(QtCore.QThread):
    def __init__(self, queue, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.downloaded_ids = self._read_from_log()

        self._max_buffer_size = 0
        self._max_log_size = 0
        self._load_config()

        self.reddit = RedditDownloader()

    def _load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._max_buffer_size = configs['params']['max_buffer_size']
                self._max_log_size = configs['params']['max_log_size']

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            error_log('DownloaderThread',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            error_log('DownloaderThread',"Error when applying configs", e)

    def _write_to_log(self):
        with open('logs/downloaded-images.log', 'w+') as f:
            f.truncate()
            f.write('\n'.join(self.downloaded_ids))

    def _read_from_log(self):
        try:
            with open('logs/downloaded-images.log', 'r') as f:
                return f.read().split('\n')
        except EnvironmentError:
            print("Unable to open log file. Returning empty list.")
            return []

    def _log(self,id):
        print("Logging IDs")
        if len(self.downloaded_ids) >= self._max_log_size:
            print("Buffer is full")
            self.downloaded_ids.pop(0)
        self.downloaded_ids.append(id)
        print("Writing to log")
        self._write_to_log()


    def _check_buffer(self):
        '''
        Checks if buffer needs refill :GLOM:
        '''
        return not self.queue.full()

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
            if self._check_buffer():
                media = self._download()
                if media != None:
                    self.queue.put(media)
                    self._log(media.id)
            time.sleep(2)
            #return

