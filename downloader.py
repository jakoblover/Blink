from downloaders import RedditDownloader

class Downloader(QtCore.QThread):
    def __init__(self, queue, parent=None):
        self.queue = queue
        self.id_list = self.read_from_log()
        self.reddit = RedditDownloader()

    def _write_to_log(self, all_ids):
        with open('logs/downloaded-images.log', 'w+') as f:
            f.truncate()
            f.write('\n'.join(all_ids))

    def _read_from_log(self):
        try:
            with open('logs/downloaded-images.log', 'r') as f:
                return f.read().split('\n')
        except EnvironmentError:
            print("Unable to open log file. Returning empty list.")
            return []