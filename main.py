import importlib
import sys
import time

import utils
from config import Config
from PyQt5 import QtCore, QtGui, QtWidgets
from downloader import Scheduler
from queue import Queue


class Blink(QtWidgets.QMainWindow):
    def __init__(self, config, media_queue):
        super(Blink, self).__init__()

        # Config variables
        self._media_duration = config["media_duration"]
        self._min_video_duration = config["min_video_duration"]
        self._max_video_duration = config["max_video_duration"]
        self._video_iterations = config["video_iterations"]
        self._time_delay_text = config["time_delay_text"]
        self._media_path = config["media_path"]
        self._log_path = config["log_path"]
        self._min_aspect_ratio = config["min_aspect_ratio"]
        self._max_aspect_ratio = config["max_aspect_ratio"]
        self._title_font_size = config["title_font_size"]

        # Other variables
        self.title = "Blink"
        self.media_queue = media_queue
        self._current_media = None

        # Start viewer
        self._viewer_timer = QtCore.QTimer()
        self._viewer_timer.setSingleShot(True)
        self._viewer_timer.timeout.connect(self.show_media)

        # Clear the image buffer
        utils.remove_all_media(self._media_path)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        screenShape = QtWidgets.QDesktopWidget().screenGeometry()
        self.resize(screenShape.width(), screenShape.height())

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)

        self._title_label = QtWidgets.QLabel(self)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet("QLabel { color : white;}")
        self._title_label.setFont(
            QtGui.QFont("Sans Serif", self._title_font_size, QtGui.QFont.Bold)
        )

        self._media_label = QtWidgets.QLabel(widget)
        self._media_label.setAlignment(QtCore.Qt.AlignCenter)
        self._media_label.resize(screenShape.width(), screenShape.height())
        self._media_label.setStyleSheet("background-color:black;")

        main_layout = QtWidgets.QHBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._title_label)
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        self._media_label.showFullScreen()
        self.showFullScreen()

    def show_media(self):

        # Delete the previously shown media
        if self._current_media != None:
            self._current_media.remove()

        # Fetch new image from queue
        self._current_media = self.media_queue.get()

        # Show new image from queue
        if self._current_media != None:
            self._title_label.setText(self._current_media.title)
            pixmap = QtGui.QPixmap(self._current_media.file_path)
            if pixmap.isNull():
                duration = 0.1
            else:
                self._media_label.setPixmap(
                    pixmap.scaled(
                        self._media_label.size(),
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation,
                    )
                )

        else:
            print("Queue is empty")

        timer = QtCore.QTimer.singleShot(self._media_duration * 1000, self.show_media)

    def showBlink(self):
        self.showFullScreen()

    def hideBlink(self):
        self.hide()


if __name__ == "__main__":
    print("[MAIN] Instantiating application")
    app = QtWidgets.QApplication(sys.argv)

    print("[MAIN] Importing config")
    config = Config("config.yaml")
    downloaders = dict()
    media_queue = Queue(maxsize=config.get_queue_size())

    print("[MAIN] Creating media and log paths")
    utils.prepare_folders(config.get_media_path(), config.get_log_path())

    print("[MAIN] Instantiating downloaders")
    for _downloader_name, _downloader_config in config.get_downloaders().items():
        _module = importlib.import_module("downloaders")
        _class = getattr(_module, _downloader_config["class"])
        instance = _class(
            config.get_downloader_config(_downloader_name),
            config.get_media_path(),
            config.get_log_path(),
        )

        print(f"[MAIN] Instantiated downloader {_class}")
        downloaders[_downloader_name] = instance

    print("[MAIN] Starting Scheduler")
    scheduler = Scheduler(config.get_scheduler_config(), media_queue, downloaders)
    scheduler.start()
    print("[MAIN] Starting application")
    ex = Blink(config.get_gui_config(), media_queue)
    print("[MAIN] Showing media")
    scheduler.running = True
    ex.show_media()

    sys.exit(app.exec_())
