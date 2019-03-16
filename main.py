from downloader import DownloaderThread
from queue import Queue
import time
import yaml
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import utils
import os


class Blink(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #Config variables
        self._max_queue_size = 0
        self._time_show_media = 0
        self._time_delay_text = 0
        self._media_filepath = ''

        #Other variables
        self.title = 'Blink'

        self._load_config()

        #Start downloader
        self.media_queue = Queue(maxsize=self._max_queue_size)
        self.downloader_thread = DownloaderThread(self.media_queue)
        self.downloader_thread.start()

        #Start viewer
        self._viewer_timer = QtCore.QTimer(self)
        self._viewer_timer.timeout.connect(self.show_media)
        self._viewer_timer.setInterval(self._time_show_media*1000)
        self._viewer_timer.start()

        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self._central_widget = QtWidgets.QWidget(self)
        self._main_layout = QtWidgets.QHBoxLayout()
        self._media_label = QtWidgets.QLabel(self)

        self._main_layout.addWidget(self._media_label)
        self._central_widget.setLayout(self._main_layout)

        self.setCentralWidget(self._central_widget)
        self.show()

    def show_media(self):
        #Pop image from queue
        #Show image on screen
        print("Showing image from queue")
        media = self.media_queue.get()

        if type(media) is utils.Media:
            filepath = os.path.join(self._media_filepath,media.id)
            print(media.top_comment)
            pixmap = QtGui.QPixmap(filepath)
            self._media_label.setPixmap(pixmap)
            self._media_label.show()
        else:
            print("Queue is empty")

    def showBlink(self):
        self.showFullScreen()

    def hideBlink(self):
        self.hide()

    def _load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._max_queue_size = configs['params']['max_queue_size']
                self._time_show_media = configs['params']['time_show_media']
                self._time_delay_text = configs['params']['time_delay_text']
                self._media_filepath = configs['params']['media_filepath']

        except EnvironmentError as e:
            print("Error when opening config. ", e)
            utils.error_log('MainApplication', "Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ", e)
            utils.error_log('MainApplication', "Error when applying configs", e)






if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Blink()
    sys.exit(app.exec_())