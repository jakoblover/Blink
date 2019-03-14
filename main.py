from downloader import DownloaderThread
from queue import Queue
import time

media_queue = Queue(maxsize=10)
downloader_thread = DownloaderThread(media_queue)
downloader_thread.start()

while True:
    time.sleep(1)