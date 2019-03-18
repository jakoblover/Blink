from downloaders import RedditDownloader
from PyQt5 import QtCore
import time
import yaml
import utils
from praw.exceptions import ClientException
from prawcore.exceptions import OAuthException

class DownloaderThread(QtCore.QThread):
    def __init__(self, queue, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.downloaded_ids = self._read_from_log()

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

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            self.error_log('DownloaderThread',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            utils.error_log('DownloaderThread',"Error when applying configs", e)

    def _read_from_log(self):
        try:
            with open('logs/downloaded-images.log', 'r') as f:
                return f.read().split('\n')
        except EnvironmentError as e:
            utils.error_log('DownloaderThread', "Error reading log file", e)
            return []

    def _write_to_log(self,list):
        try:
            with open('logs/downloaded-images.log', 'w+') as f:
                f.truncate()
                f.write('\n'.join(list))
        except EnvironmentError as e:
            utils.error_log('DownloaderThread', "Error writing to log file", e)

    def _log(self,id):
        if len(self.downloaded_ids) >= self._max_log_size:
            self.downloaded_ids.pop(0)
        self.downloaded_ids.append(id)
        self._write_to_log(self.downloaded_ids)

    def _check_queue(self):
        '''
        Checks if buffer needs refill :GLOM:
        '''
        return not self.queue.full()

    def _download(self):
        '''
        Decide what source to download from.
        :return: media object
        TODO: Add support for more sources
        TODO: If certain errors happen, prevent from downloading from that source again. If no more sources, stop program
        '''


        try:
            return self.reddit.download(self.downloaded_ids)
        except (OAuthException, ClientException) as e:
            print("Error when calling download function")
            utils.error_log('DownloaderThread', "Credential error", e)
            return None
        except Exception as e:
            print("Error when calling downloading")
            utils.error_log('DownloaderThread', "Error calling download function from downloader", e)
            return None

    def run(self):
        self.running = True
        while self.running:
            #If buffer needs refill
            if self._check_queue():
                media = self._download()
                if media != None:
                    self.queue.put(media)
                    self._log(media.id)

            time.sleep(2)

