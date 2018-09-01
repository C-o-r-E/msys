#!/usr/bin/python3
# -*- coding: utf-8 -*-


from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtPrintSupport import *

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebView()
        self.browser.setUrl(QUrl("https://msys.heliosmakerspace.ca"))

        self.setCentralWidget(self.browser)

        #self.setWindowState(Qt.WindowMaximized)
        self.show()

    @pyqtSlot(str)
    def navigate_to_url(self, url):
        print("navigate_to_url: [{}]".format(url))
        q = QUrl(url)
        if q.scheme() == "":
            q.setScheme("http")

        self.browser.setUrl(q)