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

        self._max_aspect_ratio = 0
        self._min_aspect_ratio = 0
        self._max_gif_duration = 0
        self._min_gif_duration = 0

        self._load_config()

        self.reddit = RedditDownloader()

    def _load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)

                self._max_aspect_ratio = configs['params']['max_aspect_ratio']
                self._min_aspect_ratio = configs['params']['min_aspect_ratio']
                #self._max_gif_duration = configs['params']['max_gif_duration']
                #self._min_gif_duration = configs['params']['min_gif_duration']

        except EnvironmentError as e:
            print("Error when opening config. ",e)
            self.error_log('DownloaderThread',"Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ",e)
            utils.error_log('DownloaderThread',"Error when applying configs", e)

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

        return self.reddit.download()

    def run(self):
        self.running = True
        while self.running:
            if self._check_queue():
                media = self._download()
                valid_media = utils.valid_media(media,
                                                min_aspect_ratio=self._min_aspect_ratio,
                                                max_aspect_ratio=self._max_aspect_ratio
                                                )
                print("Valid media? ", valid_media)
                if type(media) is utils.Media and valid_media:
                    print("Put in queue")
                    self.queue.put(media)

            time.sleep(2)

