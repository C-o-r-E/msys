#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from PyQt5.QtWidgets import QApplication
from  PyQt5.QtCore import QThread

from kiosk_webview import MainWindow
from kiosk_NFC_manager import nfcThread

CONFIG_BASE_URL = 'https://msys.heliosmakerspace.ca/members/'
CONFIG_FULLSCREEN = True
CONFIG_POLL_DELAY = 1

#attempt opening config file
base = os.path.dirname(os.path.abspath(__file__))
cfg_path = "{}/config_msys_kiosk.json".format(base)

try:
    f = open(cfg_path)
    data = json.load(f)
    f.close()
    if 'base_url' in data:
        CONFIG_BASE_URL = data['base_url']
    if 'fullscreen' in data:
        CONFIG_FULLSCREEN = data['fullscreen']
    if 'poll_delay' in data:
        CONFIG_POLL_DELAY = data['poll_delay']
except FileNotFoundError as e:
    print("error opening file: [{}]".format(e))
    print("using default settings")

app = QApplication(sys.argv)
app.setApplicationName("Helios Kiosk")
app.setOrganizationName("Helios Makerspace")
app.setOrganizationDomain("heliosmakerspace.ca")

window = MainWindow(screen_mode=CONFIG_FULLSCREEN)
t = nfcThread(CONFIG_POLL_DELAY)
t.sig_got_ID.connect(window.navigate_to_url)



t.start()
app.exec_()