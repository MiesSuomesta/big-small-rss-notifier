from PIL import Image
import glob, os
import logindatamanager as LDM
import tempfile as TF
from webpreview import web_preview
import os
import sys
import time
from base64 import b64encode
import urllib
import urllib.request


class Screenshot():

	def download_image(self, url):
		data = None
		#print("url {} reading ...".format(url))
		with urllib.request.urlopen(url) as response:
			data = response.read()
		#print("url {} read.".format(url))
		return data

	def makeThumbnail(self, url, siteName, w, h, options=None):

		datasAt = os.getenv('HOME', None)
		if datasAt is None:
			datasAt = os.getenv('APPDATA', None)
			datasAt = os.path.join(datasAt, "..")
			datasAt = os.path.join(datasAt, "..")
			datasAt = os.path.join(datasAt, "Desktop")
			datasAt = os.path.join(datasAt, "rss-notifier-login-datas.json")
		else:
			datasAt = os.path.join(datasAt, ".rss-notifier-login-datas.json")

		siteData = LDM.get_login_data(datasAt, siteName)

		if options is None:
			options = {}

		#print("siteData", siteData)

		if siteData is not None:
			try:
				for key in siteData.keys():
					options[key] = siteData.get(key)
			except KeyError:
				pass

		# Auth for urllib and webpreviewer
		auth_ok = True
		try:
			auth_handler = urllib.request.HTTPBasicAuthHandler()
			auth_handler.add_password('realm', 'host', options['username'], options['password'])

			secret = options['username']+":"+options['password']
			secret = secret.encode()
			secretEncoded = b64encode(secret).decode("ascii")


			copener = urllib.request.build_opener(auth_handler)
			urllib.request.install_opener(copener)
		except KeyError:
			auth_ok = False
			pass

		# --------------------------------------------------------------

		if auth_ok:
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
				'Authorization': 'Basic {}'.format(secretEncoded)
			}
			
			title, description, image = web_preview(url, headers=headers, parser="lxml")
			
			imageraw = self.download_image(image)

			tfileIn  = os.path.join(TF.gettempdir(), os.urandom(24).hex())
			tfileOut = os.path.join(TF.gettempdir(), os.urandom(24).hex())
			tfileOut = tfileOut + ".ico"
			# write string containing pixel data to file
			with open(tfileIn, 'wb') as outf:
			    outf.write(imageraw)

			imgGot = Image.open(tfileIn);
			#print("imgGot:", imgGot)
			imgGot.thumbnail((w,h), Image.ANTIALIAS)
			imgGot.save(tfileOut, "ICO")

			if os.path.exists(tfileIn):
				os.remove(tfileIn)

			return tfileOut
		
		return None


