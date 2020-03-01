import importlib
import random


class Scheduler:
    def __init__(self, config, downloaders):
        self.config = config
        self.downloaders = downloaders

    def fetch(self):
        _downloader = self._choose_downloader()
        media = self.downloaders[_downloader].download()

    def _choose_downloader(self):
        keys = list(self.config["weights"].keys())
        weights = list(self.config["weights"].values())

        return random.choices(population=keys, weights=weights)[0]
