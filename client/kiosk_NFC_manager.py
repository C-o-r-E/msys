#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QThread, pyqtSignal

import client_MFRC522

class nfcThread(QThread):

	sig_got_ID = pyqtSignal(str)
	polling_delay = 1

	def __init__(self, delay: int) -> None:
		QThread.__init__(self)
		self.polling_delay = delay

	def __del__(self) -> None:
		self.wait()

	def handle_ID(self, uid: str) -> None:
		print("nfcThread handle ID: [{}]".format(uid))
		self.sig_got_ID.emit(uid)

	def run(self) -> None:
		client_MFRC522.handle_MFRC522_blocking(self.handle_ID, self.polling_delay)

