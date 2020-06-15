#!/usr/bin/python
import sys

from rssfeeditem import *
from htmltogif import *

from bs4 import BeautifulSoup
import feedparser
import time
from win10toast import ToastNotifier


# -------------------------------------------

Feeds = []

# Kauppalehti
Feeds.append( RssFeed('kauppalehti', "https://feeds.kauppalehti.fi/rss/main") )
Feeds.append( RssFeed('kauppalehti', "https://feeds.kauppalehti.fi/rss/klnyt") )

# Yle
Feeds.append( RssFeed('yle', "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET") )
Feeds.append( RssFeed('yle', "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss") )

# Kaleva
Feeds.append( RssFeed('kaleva', "https://www.kaleva.fi/feedit/rss/managed-listing/rss-uusimmat/") )
Feeds.append( RssFeed('kaleva', "https://www.kaleva.fi/feedit/rss/managed-listing/kotimaa/") )
Feeds.append( RssFeed('kaleva', "https://www.kaleva.fi/feedit/rss/managed-listing/ulkomaat/") )

# Iltasanomat
Feeds.append( RssFeed('iltasanomat', "https://www.is.fi/rss/tuoreimmat.xml") )
Feeds.append( RssFeed('iltasanomat', "https://www.is.fi/rss/viihde.xml") )
Feeds.append( RssFeed('iltasanomat', "https://www.is.fi/rss/elokuvat.xml") )



class Firehose:
	def __init__(self, out=sys.stdout, delay=5.0):
		self.screenshot = Screenshot()
		# file-like object to write output to
		self.out = out
		# seconds to sleep between each update loop   	
		self.delay = delay
		# list of installed source objects
		self._sources = []
		self.itemsAdded = []
		self.guidsDeleted = []

	def setSources(self, feeds):
		self._sources = feeds

	def getSources(self, feeds):
		return self._sources

	def setItems(self, alist):
		self.itemsAdded = alist
		self.itemsAdded = sorted(alist, key=lambda x: x[0], reverse=False)

	def getItems(self):
		self.itemsAdded = sorted(self.itemsAdded, key=lambda x: x[0], reverse=False)
		return self.itemsAdded

	def update(self):
		''' Update all sources. '''
		alist = self.getItems()
		for source in self._sources:
			try:
				#print("--> items update {}".format(source))
				source.update(self.guidsDeleted)
				#print("items updated:", source.getItemlist())
				alist.extend(source.getItemlist())
				#print("alist items updated: {}".format(alist))
			except Exception as e:
				print("alist update problem: {}".format(e))
				continue

		self.setItems(alist)
		#self.itemsAdded = sorted(self.itemsAdded, key=lambda x: x[0], reverse=False)


	def show_notes(self):
		''' Update all items added. '''
		while True:
			#print("show_notes: items:", alist)

			for (ts,pItem) in self.getItems():
				time.sleep(self.delay)
				#print("show_notes:: item:{} and {}".format( type(ts), type(pItem)))
				#try:
					#print("item SHOW:{} {}".format(ts, pItem))
				show_note(self.screenshot, pItem)
				pItem['shown'] = True;
				#except Exception as e:
				#	print("item show problem: {}".format(e))
				#	continue
			time.sleep(5)

	def cleanup(self):
		''' Update all items added. '''
		while True:
			time.sleep(self.delay*2)
			print("Cleaning up............")		
			alist = self.getItems()
			for upditem in alist:
#				#try:
				(ts,pItem) = upditem
				if 'shown' in pItem:
					if pItem['shown']:
						print("Cleaning up: {}".format(pItem['guid']))

						self.guidsDeleted.append(pItem['guid'])
						filePath = updateItem['tmpimage']

						if os.path.exists(filePath):
							os.remove(filePath)

						alist.remove( upditem )
						self.setItems(alist)
						alist = self.getItems()
						del pItem;
#				except Exception as e:
#					print("item cleanup problem: {}".format(e))
#					continue
			time.sleep(self.delay*2)

	def start(self):
		''' Start the firehose. '''
		while True:
			print("update...")
			self.update()
			#print("update sleep...")
			time.sleep(self.delay/4)

	def cleaner(self):
		''' Start the firehose. '''
		while True:
			self.cleanup()

def getKeyVal(ofrom, key, default):
	rv = default
	if isinstance(ofrom, dict):
		if key in ofrom:
			rv = ofrom.get(key)
	#print("{} {} -> {}".format(type(ofrom), key, rv))
	return rv

# One-time initialization
toaster = ToastNotifier()

def show_note(screenshot, updateItem, toaster=toaster):

	#print("show_note:: RAW: {}".format(updateItem))

	rawEntry 	= getKeyVal(updateItem, 'rawEntry', None)

	#y = json.dumps(rawEntry, indent=4)
	#print(y)


	if rawEntry is None:
		return

	tags 		= getKeyVal(rawEntry, 'tags', None)
	title 		= getKeyVal(rawEntry, 'title', None)
	url 		= getKeyVal(rawEntry, 'url', None)
	link 		= getKeyVal(rawEntry, 'link', None)
	thumb 		= getKeyVal(rawEntry, 'thumb', None)
	published 	= getKeyVal(rawEntry, 'published', None)
	description 	= getKeyVal(rawEntry, 'description', None)
	siteName 	= getKeyVal(updateItem, 'siteName', None)


	category = tags[0]['term']

	thumbnailFP = screenshot.makeThumbnail(link, siteName, 150, 100)

	updateItem['tmpimage'] = thumbnailFP

	categories = category

	if isinstance(category, list):
		categories = ""
		for cat in category:

			comma=", "
			if categories == "":
				comma = ""

			categories = categories + comma + cat

	if len(categories) > 0:
		categories = categories + ":"

	if description is None:
		description = ""
	else:
		description = description + "\n"

	msgTitle = '''// {} //\n{}\n{}'''.format(siteName, categories, title)
	msgBody = str(description) + str(published) +" <a href='"+ str(link) +"'>Link to news</a>"

        # Show notification whenever needed
	toaster.show_toast(msgTitle, msgBody, threaded=True, icon_path=thumbnailFP, duration=20)  # 3 seconds





import _thread

def start_notes_show(tn, MO):
	MO.show_notes()

def start_notes_build(tn, MO):
	MO.start()

def start_notes_cleaner(tn, MO):
	MO.cleaner()


MainObj = Firehose(delay=10);

MainObj.setSources(Feeds)

_thread.start_new_thread(start_notes_show, 	('Note show',MainObj,))
_thread.start_new_thread(start_notes_build, 	('Note build',MainObj,))
_thread.start_new_thread(start_notes_cleaner, 	('Note cleaner',MainObj,))

while True:
	#print("Sleep .........")
	time.sleep(10);


