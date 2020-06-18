import sys
import traceback
import urllib3
import xmltodict
import json
import re
import time
import tempfile as TF
from bs4 import BeautifulSoup
import feedparser
import time
from base64 import b64encode
import urllib
import urllib.request

class RssFeed():


	def __init__(self, pSiteName, pUrl):
	
		self.SOURCE = pSiteName+':'+ pUrl
		self.timestamp = time.monotonic_ns()
		self.shown = False
		self.info = {}
		self.info['url'] = pUrl;
		self.info['siteName'] = pSiteName
		self.info['siteIcon'] = None;
		self.Itemlist = []

	def getInfo(self):
		return self.info

	def setInfo(self, pInfo):
		self.info = pInfo

	def getItemlist(self):
		return self.Itemlist

	def setItemlist(self, pItemlist):
		self.Itemlist = pItemlist
	
	def update(self, deletedGuids):


		feed = feedparser.parse(self.info['url'])
		#print("feed: {}".format(feed))
		self.timestamp = time.monotonic_ns()


		entries = feed['entries']
		#print("feed entries: {}".format(entries))
		for entry in reversed(entries):

			Items = self.getItemlist()
			#print("--------------------\nfeed entry: {}".format(entry))
			entryGuid = entry['guid']

			if entryGuid in Items:
				#print("guid exists..")
				continue
			#else:
                        #        print("guid {}".format(entryGuid))
				

			if entryGuid in deletedGuids:
				#print("guid already shown: {}".format(entryGuid))
				continue
			#else:
                        #        print("guid {}".format(entryGuid))


			if not self.filter(entry):
				continue


			update = {}
			update['guid'] = entryGuid
			update['siteName'] = self.info['siteName']
			update['siteIcon'] = self.info['siteIcon']
			update['siteUrl'] = self.info['url']
			update['rawEntry'] = entry
			update['cleantitle'] = clean_html(entry['title'])
			update['cleanbody'] = self.clean_body(_extract_body(entry))

			thumb = _extract_thumb(entry)
			if thumb:
				update['thumb'] = thumb
			
			raw_date = entry['published_parsed']
			update['date'] = time.strftime('%Y-%m-%d %H:%M:%S', raw_date)
			update['timeNS'] = time.monotonic_ns()
			update['source'] = self.SOURCE
			update['shown'] = False
			
			Items.append( (update['date'], update) )

			self.setItemlist(Items)

	def clean_body(self, text):
		return clean_html(text)

	def filter(self, entry):
		return True


def clean_html(raw):
	return BeautifulSoup(raw, 'html.parser').get_text().strip()

def _extract_body(entry):
	texts = []

	if 'summary' in entry:
		texts.append(entry['summary'])

	# some publications put the whole article so we search for the true summary
	# by looking for the shortest text/html content if multiple exist.
	if 'content' in entry:
		for content in entry['content']:
			if content['type'] == 'text/html':
				texts.append(content['value'])
		texts.sort(key=lambda x: len(x))

	retval = ''

	if len(texts) > 0:
		retval = texts[0]

	return retval

def _extract_thumb(entry):
	if 'media_thumbnail' in entry and len(entry['media_thumbnail']) > 0:
		return entry['media_thumbnail'][0]['url']

	if 'media_content' in entry and len(entry['media_content']) > 0:
		return entry['media_content'][0]['url']

	if 'links' in entry and len(entry['links']) > 0:
		imgs = [x for x in entry['links'] if 'image' in x['type']]

	if len(imgs) > 0:
		return imgs[0]['href']

	retval = None
	if 'summary' in entry:
		soup = BeautifulSoup(entry['summary'], 'html.parser')
		img = soup.find('img')
		if img:
			retval = img['src']
	return retval


