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

        for _downloader_name, _downloader_config in self.config.get_downloaders().items():
            _module = importlib.import_module("downloaders")
            _class = getattr(_module, _downloader_config["class"])
            instance = _class(self.config.get_downloader_config(_downloader_name))

            self.downloaders[_downloader_name] = instance

        self.scheduler = Scheduler(self.config.get_scheduler_config(), self.downloaders)

    def validate_config(self):
        # TODO: Validate the config specifically for the downloader thread
        pass

    def _is_queue_full(self):
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

        return self.scheduler.fetch()

    def run(self):
        self.running = True
        while self.running:
            if self._check_queue():
                media = self._download()
                if utils.is_valid_media(media):
                    self.queue.put(media)
                else:
                    utils.remove_media(media.filepath)

            time.sleep(2)
