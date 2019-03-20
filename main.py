from downloader import DownloaderThread
from queue import Queue
import time
import yaml
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import utils
import math



class Blink(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        #Config variables
        self._max_queue_size = 0
        self._image_duration = 0
        self._time_delay_text = 0
        self._media_filepath = ''
        self._title_font_size = 0
        self._min_gif_duration = 0
        self._max_gif_duration = 0
        self._gif_iterations = 0

        #Other variables
        self.title = 'Blink'
        self._current_media = None

        self._load_config()

        #Start downloader
        self.media_queue = Queue(maxsize=self._max_queue_size)
        self.downloader_thread = DownloaderThread(self.media_queue)
        self.downloader_thread.start()

        #Start viewer

        self._viewer_timer = QtCore.QTimer()
        self._viewer_timer.setSingleShot(True)
        self._viewer_timer.timeout.connect(self.show_media)

        #Clear the image buffer
        utils.remove_all_media(self._media_filepath)

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
        self._title_label.setFont(QtGui.QFont("Sans Serif", self._title_font_size, QtGui.QFont.Bold))
        drop_shadow = QtWidgets.QGraphicsDropShadowEffect()
        drop_shadow.setBlurRadius(5)
        drop_shadow.setColor(QtGui.QColor("#000000"))
        drop_shadow.setOffset(0,0)
        self._title_label.setGraphicsEffect(drop_shadow)

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
        print(self._media_label.size())

        if type(self._current_media) is utils.Media:
            utils.remove_media(self._current_media.filepath)

        self._current_media = self.media_queue.get()

        duration = self._image_duration

        if type(self._current_media) is utils.Media:
            if self._current_media.filetype == 'gif':
                gif = QtGui.QMovie(self._current_media.filepath)

                # Scaling magic to resize gif
                media_label_width = self._media_label.size().width()
                media_label_height = self._media_label.size().height()
                width_scale_factor = media_label_width/self._current_media.width
                height_scale_factor = media_label_height/self._current_media.height
                scale_factor = min(width_scale_factor,height_scale_factor)
                gif_resized_size = QtCore.QSize(self._current_media.width*scale_factor,self._current_media.height*scale_factor)
                gif.setScaledSize(gif_resized_size)

                #Calculate amount of time needed to loop the gif right amount of times
                if type(self._current_media.duration) is not None:

                    duration = self._gif_iterations*self._current_media.duration
                    if not self._current_media.duration > self._max_gif_duration:
                        while(duration < self._min_gif_duration):
                            duration += self._current_media.duration
                        while(duration > self._max_gif_duration):
                            duration -= self._current_media.duration
                    else:
                        duration = self._max_gif_duration

                    print("Gif duration: ", self._current_media.duration)
                    print("Min gif duration: ", self._min_gif_duration)
                    print("Max gif duration: ", self._max_gif_duration)
                    print("New gif duration: ", duration)

                    # if duration < self._min_gif_duration:
                    #     duration = self._current_media.duration*math.ceil(self._min_gif_duration/self._current_media.duration)

                #Actually start gif
                self._media_label.setMovie(gif)
                self._title_label.setText(self._current_media.title)
                gif.start()
            else:
                self._title_label.setText(self._current_media.title)
                pixmap = QtGui.QPixmap(self._current_media.filepath)
                self._media_label.setPixmap(pixmap.scaled(self._media_label.size(),QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
                self._viewer_timer.startTimer(self._image_duration)
        else:
            print("Queue is empty")

        print(duration)
        timer = QtCore.QTimer.singleShot(duration*1000, self.show_media)



    def showBlink(self):
        self.showFullScreen()

    def hideBlink(self):
        self.hide()

    def _load_config(self):
        try:
            with open("config.yaml") as f:
                configs = yaml.safe_load(f)
                self._max_queue_size = configs['params']['max_queue_size']
                self._image_duration = configs['params']['image_duration']
                self._time_delay_text = configs['params']['time_delay_text']
                self._media_filepath = configs['params']['media_filepath']
                self._title_font_size = configs['params']['title_font_size']
                self._min_gif_duration = configs['params']['min_gif_duration']
                self._max_gif_duration = configs['params']['max_gif_duration']
                self._gif_iterations = configs['params']['gif_iterations']

        except EnvironmentError as e:
            print("Error when opening config. ", e)
            utils.error_log('MainApplication', "Error when opening config", e)
        except KeyError as e:
            print("Error when applying config. ", e)
            utils.error_log('MainApplication', "Error when applying configs", e)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Blink()
    ex.show_media()
    sys.exit(app.exec_())