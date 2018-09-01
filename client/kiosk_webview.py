#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtCore import QUrl, pyqtSlot

class MainWindow(QMainWindow):

    baseUrl = "https://msys.heliosmakerspace.ca/members"

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebView()
        self.browser.setUrl(QUrl(self.baseUrl))

        self.setCentralWidget(self.browser)

        #self.setWindowState(Qt.WindowMaximized)
        self.show()

    def set_base_url(newUrl: str) -> None:
        self.baseUrl = newUrl

    @pyqtSlot(str)
    def navigate_to_url(self, url): #todo: fix naming (url is an id right now) ... after the demo
        final_url = "{}/cards/checkin/{}/".format(self.baseUrl, url)
        print("navigate_to_url: [{}]".format(final_url))
        q = QUrl(final_url)
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)