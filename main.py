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
        self._current_media = None

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
        self._main_layout = QtWidgets.QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._media_label = QtWidgets.QLabel(self)
        self._media_label.setAlignment(QtCore.Qt.AlignCenter)

        self._main_layout.addWidget(self._media_label)
        self._central_widget.setLayout(self._main_layout)
        self._central_widget.setStyleSheet("QWidget { background-color: black; }")
        self.setCentralWidget(self._central_widget)

        self._media_label.showFullScreen()
        self.showFullScreen()

    def show_media(self):
        print("Showing image from queue")

        self._current_media = self.media_queue.get()


        if type(self._current_media) is utils.Media:
            if self._current_media.filetype == 'gif':
                gif = QtGui.QMovie(self._current_media.filepath)
                self._media_label.setMovie(gif)
                gif.start()
            else:
                pixmap = QtGui.QPixmap(self._current_media.filepath)
                self._media_label.setPixmap(pixmap.scaled(self._media_label.size(),QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
                #utils.remove_media(self._current_media.filepath)


        else:
            print("Queue is empty")

    def showBlink(self):
        self._viewer_timer.start()
        self.showFullScreen()

    def hideBlink(self):
        self._viewer_timer.stop()
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