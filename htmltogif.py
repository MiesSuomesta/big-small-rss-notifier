from PIL import Image
import glob, os
import logindatamanager as LDM
import tempfile as TF
from webpreview import web_preview
import traceback
import os
import sys
import time
from base64 import b64encode
import urllib
import urllib.request


class Screenshot():

	def download_image(self, url):
		data = None
		if url is not None:
			try:
				#print("url {} reading ...".format(url))
				with urllib.request.urlopen(url) as response:
					data = response.read()
				#print("url {} read.".format(url))
				return data
			except:
				print("Download image: url {} reading error".format(url))
				traceback.print_exc()
				pass

		print("None as url?")
		return data

	def makeThumbnail(self, url, siteName, w, h, options=None):

		datasAt = LDM.get_login_data_file_path()
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
			
			imageraw = None;
			if image is not None:
				imageraw = self.download_image(image)


			tfileOut = None

			if imageraw is not None:
				prefix="rss-feed-img-"
				tfileIn  = os.path.join(TF.gettempdir(), prefix + os.urandom(24).hex())
				tfileOut = os.path.join(TF.gettempdir(), prefix + os.urandom(24).hex())

				if sys.platform == "win32":
					tfileOut = tfileOut + ".ico"
				else:
					tfileOut = ".png"

				# write string containing pixel data to file
				with open(tfileIn, 'wb') as outf:
				    outf.write(imageraw)

				imgGot = Image.open(tfileIn);
				#print("imgGot:", imgGot)
				imgGot.thumbnail((w,h), Image.ANTIALIAS)

				if sys.platform == "win32":
					imgGot.save(tfileOut, "ICO")
				else:
					imgGot.save(tfileOut, "PNG")

				if os.path.exists(tfileIn):
					os.remove(tfileIn)

			return tfileOut
		



