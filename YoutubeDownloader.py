import sys
import threading
import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QPushButton, QTextBrowser, QVBoxLayout, QLineEdit, QTextEdit, QListWidget
from bs4 import BeautifulSoup
from pytube import YouTube

youtubeWindow = None
video = None
threadLock = threading.Lock()


class YoutubeThread(QtCore.QObject):
    threadFinishedSignal = QtCore.pyqtSignal()
    searchFinishedSignal = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self._isRunning = False
        self.searchKey = None

    @QtCore.pyqtSlot()
    def run(self):
        self._isRunning = True
        vid_list = searchYoutube(self.searchKey)
        with self._lock:
            self.searchFinishedSignal.emit(vid_list)
        self.stop()

    def stop(self):
        self._isRunning = False
        with self._lock:
            self.threadFinishedSignal.emit()

    def setSearchKey(self, key):
        self.searchKey = key


def downloader(video_link, down_dir='./', download=True):
    global video

    # initiate the class:
    try:
        # object creation using YouTube which was imported in the beginning
        yt = YouTube(video_link, on_progress_callback=progress_function)
    except:
        print("Connection Error")  # to handle exception

    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
    video_title = video.title
    textStatus.append("Downloading Video --> {this_video}".format(this_video=video_title))
    textStatus.append('FileSize : ' + str(round(video.filesize / (1024 * 1024))) + 'MB')
    QtWidgets.qApp.processEvents()

    if download:
        if down_dir is not None:
            video.download(down_dir)
        else:
            video.download()

    textStatus.append("Download complete...")
    QtWidgets.qApp.processEvents()


def searchYoutube(searchKey):
    base = "https://www.youtube.com/results?search_query="
    r = requests.get(base + searchKey)
    page = r.text
    soup = BeautifulSoup(page, 'html.parser')
    vids = soup.findAll('a', attrs={'class': 'yt-uix-tile-link'})
    vid_list = []
    for v in vids:
        video_link = 'https://www.youtube.com' + v['href']
        vid_list.append(video_link)
        # time.sleep(0.1)
    return vid_list


def progress_function(stream, chunk, file_handle, bytes_remaining):
    size = video.filesize
    progress = (float(abs(bytes_remaining - size) / size)) * float(100)
    textStatus.append(str(round(progress, 1)) + '% done...')
    QtWidgets.qApp.processEvents()


def receivedThreadFinished():
    youtubeWindow.workerThread.quit()
    youtubeWindow.workerThread.wait()
    youtubeWindow.isConnected = False


def receivedSearchFinished(vids):
    textStatus.append("Search finished...Click Link.")
    for video_link in vids:
        listWidget.addItem(video_link)


def receivedInfo(info):
    textStatus.append(info)


def btnExitClicked(self):
    sys.exit(0)


def btnSearchClicked(self):
    listWidget.clear()
    textDownload.clear()

    textStatus.append("Searching...")
    if not textSearch.text() is None:
        youtubeWindow.worker.setSearchKey(textSearch.text())
        youtubeWindow.workerThread.start()


def btnDownloadClicked(self):
    video_link = textDownload.text()
    if video_link is not None:
        downloader(video_link)


def selectionChanged():
    for item in listWidget.selectedItems():
        textDownload.setText(item.text())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, _isConnected):
        super().__init__()
        self._isConnected = _isConnected
        self.resize(480, 600)
        self.setWindowTitle("Youtube Downloader by Türkay Biliyor")

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        self.worker = YoutubeThread()
        self.workerThread = QtCore.QThread()  # Move the Worker object to the Thread object
        self.workerThread.started.connect(self.worker.run)  # Init worker run() at startup (optional)
        self.worker.searchFinishedSignal.connect(receivedSearchFinished)  # Connect your signals/slots
        self.worker.threadFinishedSignal.connect(receivedThreadFinished)  # Connect your signals/slots
        self.worker.moveToThread(self.workerThread)
        self.workerThread.setTerminationEnabled(True)


def main():
    global youtubeWindow
    global listWidget
    global textSearch
    global textDownload
    global textStatus

    app = QtWidgets.QApplication([])
    youtubeWindow = MainWindow(False)

    btnSearch = QPushButton("Search")
    btnSearch.clicked.connect(btnSearchClicked)

    btnDownload = QPushButton("Download")
    btnDownload.clicked.connect(btnDownloadClicked)

    btnExit = QPushButton("Exit")
    btnExit.clicked.connect(btnExitClicked)

    listWidget = QListWidget()
    listWidget.setStyleSheet("font: 10pt; color: #00cccc; background-color: #001a1a;")
    listWidget.itemSelectionChanged.connect(selectionChanged)

    textSearch = QLineEdit()
    textDownload = QLineEdit()
    textStatus = QTextBrowser()
    textStatus.setStyleSheet("font: 10pt; color: #00cccc; background-color: #001a1a;")

    layoutV = QVBoxLayout(youtubeWindow.centralWidget())
    layoutV.addWidget(listWidget)
    layoutV.addWidget(textStatus)
    layoutV.addWidget(textSearch)
    layoutV.addWidget(btnSearch)
    layoutV.addWidget(textDownload)
    layoutV.addWidget(btnDownload)
    layoutV.addWidget(btnExit)
    youtubeWindow.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
