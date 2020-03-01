class BaseDownloader:
    def __init__(self, config):
        self.config = config

    def download(self):
        raise NotImplementedError()
