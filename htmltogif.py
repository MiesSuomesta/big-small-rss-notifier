from PIL import Image
import glob, os
import logindatamanager as LDM
import tempfile as TF
import os
import sys
import time
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import *


class Screenshot(QWebEngineView):
	def __init__(self):
		self.app = QApplication(sys.argv)
		QWebEngineView.__init__(self)
		self._loaded = False
		self.setAttribute(Qt.WA_DontShowOnScreen)
		self.page().settings().setAttribute(
			QWebEngineSettings.ShowScrollBars, False)
		self.loadFinished.connect(self._loadFinished)
		self.show()

	def wait_load(self, delay=0):
		while not self._loaded:
			self.app.processEvents()
			time.sleep(delay)

		self._loaded = False

	def _loadFinished(self, result):
		print("Loading done: ", result)
		self.setVisible(True)
		size = self.page().contentsSize().toSize()
		self.resize(size)
		time.sleep(2)
		self._loaded = True

	def get_image(self, url):

		self.load(url)

		self.wait_load()

		grabbed = self.grab()

		print("grab: ", grabbed)
		print("grab: ", grabbed.size())
		grabbed.save("/tmp/foo.png", 'PNG')
		return grabbed

	def makeThumbnail(self, url, siteName, w, h, options=None):

		HOME = os.getenv('HOME', None)
		if HOME is not None:
			HOME = HOME + "/"

		siteData = LDM.get_login_data(HOME + '.rss-notifier-login-datas.json', siteName)

		if options is None:
			options = {}

		print("siteData", siteData)

		if siteData is not None:
			try:
				for key in siteData.keys():
					options[key] = siteData.get(key)
			except KeyError:
				pass

		options['custom-header'] : [
			('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0')
		]


		print("options", options)

		pUrl = QUrl(url)
		pUrl.setUserName(options['username'])
		pUrl.setPassword(options['password'])

		tfile = TF.NamedTemporaryFile(prefix="tmp-thumbnail-rss-notifier", suffix=".png", delete=False)

		imgGot = self.get_image(pUrl)
		print("imgGot:", imgGot)
		scaledImg = imgGot.scaledToHeight(h)
		scaledImg.save(tfile.name)


		return tfile.name



