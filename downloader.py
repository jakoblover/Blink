import importlib

from downloaders import RedditDownloader
from PyQt5 import QtCore
import time
import utils
from config import Config
from scheduler import Scheduler


class DownloaderThread(QtCore.QThread):
    def __init__(self, queue, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.queue = queue
        self.downloaders = dict()

        self.config = Config("config.yaml")
        self.scheduler = Scheduler(self.config.get_scheduler_config())

        for _downloader_name, _downloader_config in self.config.get_downloaders().items():
            _module = importlib.import_module("downloaders")
            _class = getattr(_module, _downloader_config["class"])
            instance = _class(self.config.get_downloader_config(_downloader_name))

            self.downloaders[_downloader_name] = instance

    def validate_config(self):
        pass

    def _check_queue(self):
        """
        Checks if buffer needs refill :GLOM:
        """
        return not self.queue.full()

    def _download(self):
        """
        Decide what source to download from.
        :return: media object
        TODO: Add support for more sources
        TODO: If certain errors happen, prevent from downloading from that source again. If no more sources, stop program
        """

        return self.reddit.download()

    def run(self):
        self.running = True
        while self.running:
            if self._check_queue():
                media = self._download()
                valid_media = utils.valid_media(
                    media,
                    min_aspect_ratio=self._min_aspect_ratio,
                    max_aspect_ratio=self._max_aspect_ratio,
                )
                if type(media) is utils.Media and valid_media:
                    print("Put in queue")
                    self.queue.put(media)
                elif type(media) is utils.Media and not valid_media:
                    print("Not valid media, deleting ", media.filepath)
                    utils.remove_media(media.filepath)
                else:
                    print("Returned image was not of media type")

            time.sleep(2)
