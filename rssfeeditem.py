import sys, os
import traceback
import urllib3
import xmltodict
import json
import re
import time
import tempfile as TF
from bs4 import BeautifulSoup
import feedparser
from base64 import b64encode
import urllib
import urllib.request
import hashlib
from collections import OrderedDict


class RssFeed():

	



	def __init__(self, pSiteName, pUrl, siteData):
		self.SOURCE = pSiteName+':'+ pUrl
		self.timestamp = time.monotonic_ns()
		self.shown = False
		self.m_guidItems = OrderedDict()
		self.info = {}
		self.info['url'] = pUrl;
		self.info['siteName'] = pSiteName
		self.info['siteIcon'] = None;
		self.info['siteData'] = siteData;

	def sortItemsByPubDate(self):
		return # sorting done in main class

		orgItemsDict = self.getItemDict()
		newItemsDict = OrderedDict()


		alist = []
		last_ts = None
		first_item = True

		if orgItemsDict is None:
			return

		for dictKey in orgItemsDict.keys():
			updItem = orgItemsDict.get(dictKey)
			ts = updItem['raw_published_date']

			if updItem['shown']:
				continue

			if first_item:
				last_ts = ts
				alist.append(updItem)
				first_item = False
				continue

			if ts < last_ts:
				alist.append(updItem)
			else:
				alist.insert(0, updItem)

		for feedItem in alist:
			iKey = feedItem['guid']
			newItemsDict[iKey] = feedItem

		self.setItemDict(newItemsDict)


	def getInfo(self):
		return self.info

	def setInfo(self, pInfo):
		self.info = pInfo

	def getItemDict(self): # Mapping: guid -> updateitem
		return self.m_guidItems

	def setItemDict(self, pItemDict): # Mapping: guid -> updateitem
		del self.m_guidItems
		self.m_guidItems = pItemDict

	def get_md5(self, data):
		return hashlib.md5(data.encode()).hexdigest()

	def update(self, deletedGuids):


		feed = feedparser.parse(self.info['url'])
		#print("feed: {}".format(feed))

		entries = feed['entries']
		#print("feed entries: {}".format(entries))
		Items = self.getItemDict()

		for feedEntry in reversed(entries):

			if 'guid' not in feedEntry:
				feedEntry['guid'] = self.get_md5(self.info['siteName'] + self.info['url'])

			entryGuid = feedEntry['guid']
			alreadyHadObj = Items.get(entryGuid, None)	
			if alreadyHadObj is not None:
				if 'shown' in alreadyHadObj:
					if alreadyHadObj['shown']:
						#print("guid already listed: {}".format(entryGuid))
						continue

			if entryGuid in deletedGuids:
				#print("guid already shown: {}".format(entryGuid))
				continue


			if not self.filter(feedEntry):
				continue


			update = {}
			update['guid'] = entryGuid
			update['siteName'] = self.info['siteName']
			update['siteIcon'] = self.info['siteIcon']
			update['siteData'] = self.info['siteData']
			update['siteUrl'] = self.info['url']
			update['rawEntry'] = feedEntry
			update['cleantitle'] = clean_html(feedEntry['title'])
			update['cleanbody'] = self.clean_body(_extract_body(feedEntry))

			thumb = _extract_thumb(feedEntry)
			if thumb:
				feedEntry['thumb'] = thumb
			
			raw_date = feedEntry['published_parsed']
			#print("raw_date", raw_date)
			update['date'] = time.strftime('%Y-%m-%d %H:%M:%S', raw_date)
			update['timeNS'] = time.monotonic_ns()
			update['source'] = self.SOURCE
			update['shown'] = False
			update['raw_published_date'] = time.strftime('%s', raw_date)
			#print("raw_date -> sec", update['raw_date'])

			## New key
			Items[entryGuid] = update

		self.setItemDict(Items)
		self.sortItemsByPubDate()


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


