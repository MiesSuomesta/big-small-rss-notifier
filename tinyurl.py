from base64 import b64encode
import urllib
import urllib.request
import requests

APIURL = "http://tinyurl.com/api-create.php"

class TinyUrl():
	def mkShortUrl(pUrl):
		global APIURL
		pUrlEncoded = urllib.parse.urlencode({"url": pUrl})
		url = APIURL + "?" + pUrlEncoded
		response = requests.get(url)
		return response.text
