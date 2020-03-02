import time
import utils

from downloaders import RedditDownloader
from random import random
from PyQt5 import QtCore


class Scheduler(QtCore.QThread):
    def __init__(self, config, queue, downloaders):
        QtCore.QThread.__init__(self)
        self.config = config
        self.queue = queue
        self.downloaders = downloaders

    def validate_config(self):
        # TODO: Validate the config specifically for the downloader thread
        pass

    def _choose_downloader(self):
        keys = list(self.config["weights"].keys())
        weights = list(self.config["weights"].values())

        return random.choices(population=keys, weights=weights)[0]

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
        _downloader = self._choose_downloader()
        media = self.downloaders[_downloader].download()
        return media

    def run(self):
        self.running = True
        while self.running:
            if self._is_queue_full():
                media = self._download()
                if utils.is_valid_media(media):
                    self.queue.put(media)
                else:
                    utils.remove_media(media.filepath)

            time.sleep(2)
