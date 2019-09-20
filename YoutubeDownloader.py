import sys
import threading
from concurrent.futures import thread

import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QTextCursor, QTextBlockFormat
from PyQt5.QtWidgets import QWidget, QPushButton, QTextBrowser, QVBoxLayout, QLineEdit, QTextEdit, QListWidget
from bs4 import BeautifulSoup
from pytube import YouTube
from textract.colors import red

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


class DownloadThread(QtCore.QObject):
    downloadFinishedSignal = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()
        self.videoLink = None
        self._isRunning = False

    @QtCore.pyqtSlot()
    def run(self):
        self._isRunning = True
        downloader(self.videoLink)
        self.stop()

    def stop(self):
        self._isRunning = False
        with self._lock:
            self.downloadFinishedSignal.emit()

    def setVideoLink(self, link):
        self.videoLink = link


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
    print("Downloading Video --> {this_video}".format(this_video=video_title))
    print('FileSize : ' + str(round(video.filesize / (1024 * 1024))) + 'MB')

    if download:
        if down_dir is not None:
            video.download(down_dir)
        else:
            video.download()

    print("Download complete...")


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
    print(round(progress, 1), '% done...')


def receivedThreadFinished():
    youtubeWindow.workerThread.quit()
    youtubeWindow.workerThread.wait()
    youtubeWindow.isConnected = False


def receivedSearchFinished(vids):
    textStatus.append("Search finished...")
    for video_link in vids:
        listWidget.addItem(video_link)


def receivedDownloadFinished():
    textStatus.append("Download Finished...")
    youtubeWindow.dworkerThread.quit()
    youtubeWindow.dworkerThread.wait()


def btnExitClicked(self):
    sys.exit(0)


def btnSearchClicked(self):
    listWidget.clear()
    textDownload.clear()

    textStatus.append("Searching...")
    youtubeWindow.worker.setSearchKey("paragliding+crash")
    youtubeWindow.workerThread.start()


def btnDownloadClicked(self):
    video_link = textDownload.text()
    if video_link is not None:
        youtubeWindow.dworker.setVideoLink(video_link)
        youtubeWindow.dworkerThread.start()


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

        self.dworker = DownloadThread()
        self.dworkerThread = QtCore.QThread()  # Move the Worker object to the Thread object
        self.dworkerThread.started.connect(self.dworker.run)  # Init worker run() at startup (optional)
        self.dworker.downloadFinishedSignal.connect(receivedDownloadFinished)  # Connect your signals/slots
        self.dworkerThread.moveToThread(self.dworkerThread)
        self.dworkerThread.setTerminationEnabled(True)


def main():
    global youtubeWindow
    global listWidget
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

    textDownload = QLineEdit()
    textStatus = QTextBrowser()
    textStatus.setStyleSheet("font: 10pt; color: #00cccc; background-color: #001a1a;")

    layoutV = QVBoxLayout(youtubeWindow.centralWidget())
    layoutV.addWidget(listWidget)
    layoutV.addWidget(textStatus)
    layoutV.addWidget(btnSearch)
    layoutV.addWidget(textDownload)
    layoutV.addWidget(btnDownload)
    layoutV.addWidget(btnExit)
    youtubeWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
