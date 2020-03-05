import time
import utils
import random
from queue import Queue
from PyQt5 import QtCore

from type.Media import Media


class Scheduler(QtCore.QThread):
    def __init__(self, config, queue, downloaders):
        QtCore.QThread.__init__(self)
        self.config = config
        self.queue = queue
        self.downloaders = downloaders

        self.buffer = Queue(maxsize=config["parameters"]["max_queue_size"])
        self.running = False

    def validate_config(self):
        # TODO: Validate the config specifically for the downloader thread
        pass

    def _choose_downloader(self):
        keys = list(self.config["weights"].keys())
        weights = list(self.config["weights"].values())

        return random.choices(population=keys, weights=weights)[0]

    def _choose_tag(self, downloader):
        # TODO: The chosen tag needs to also be based on the schedule
        # TODO: If a tag has been tried many times and still doesnt work, wait longer to retry

        return random.choice(self.config["schedule"]["defaults"][downloader])

    def _download(self):
        """
        Decide what source to download from.
        :return: media object
        TODO: If certain errors happen, prevent from downloading from that source again. If no more sources, stop program
        """
        downloader = self._choose_downloader()
        tag = self._choose_tag(downloader)
        print(f"[SCHEDULER] Trying to download from {tag} through {downloader}")
        media = self.downloaders[downloader].download(tag)
        return media

    def run(self):
        self.running = True
        while self.running:
            if not self.buffer.full():
                media = self._download()

                if media != None:
                    if utils.is_valid_media(media):
                        print("[SCHEDULER] Added media to queue")
                        self.buffer.put(media)
                    else:
                        print("[SCHEDULER] Removing invalid media")
                        media.remove()
                else:
                    print("[SCHEDULER] Downloader returned with error")

            if not self.queue.full():
                self.queue.put(self.buffer.get())

            time.sleep(1)
