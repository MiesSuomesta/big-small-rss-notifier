#!/usr/bin/python
import sys

from rssfeeditem import *
from htmltogif import *

import traceback
from bs4 import BeautifulSoup
import feedparser
import time
import re
import time
import tempfile as TF
from tinyurl import *

if sys.platform == "win32":
	from windows_balloon_note import *
	import webbrowser
else:
	import gi
	gi.require_version('Notify', '0.7')
	from gi.repository import Notify, GdkPixbuf
	Notify.init("Notifier")

# -------------------------------------------

USE_PLYER = False

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

# Kyberturvallisuuskeskus
Feeds.append( RssFeed('kyberturvallisuuskeskus', "https://www.kyberturvallisuuskeskus.fi/feed/rss/fi") )

# verohallinto
Feeds.append( RssFeed('verohallinto', "https://www.vero.fi/api/rss/news/fi") )

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
		self.cleaner_running = False

	def setSources(self, feeds):
		self._sources = feeds

	def getSources(self, feeds):
		return self._sources

	def setItems(self, alist):
		from operator import itemgetter
		self.itemsAdded = sorted(alist, key=itemgetter(0), reverse=True)

	def getItems(self):
		from operator import itemgetter
		self.itemsAdded = sorted(self.itemsAdded, key=itemgetter(0), reverse=True)
		return self.itemsAdded

	def dumpItems(self):
		for itm in self.getItems():
			ts = itm[0]
			upditem = itm[1]
			guid = upditem['guid']
			print("- TS {}, guid: {}".format(ts, guid))

	def update(self):
		''' Update all sources. '''
		alist = []
		for source in self._sources:
			try:
				#print("--> items update {}".format(source))
				source.update(self.guidsDeleted)
				#print("items updated:", source.getItemlist())
				alist.extend(source.getItemlist())
				#print("alist items updated: {}".format(alist))
			except:
				print("alist update problem: {}".format(e))
				traceback.print_exc(file=sys.stdout)
				continue
		self.setItems(alist)
		#self.dumpItems()
		

	def show_notes(self):
		''' Update all items added. '''
		while True:
			#print("show_notes: items:", alist)

			for (ts,pItem) in self.getItems():
				time.sleep(self.delay/3)
				#print("show_notes:: item:{} and {}".format( type(ts), type(pItem)))
				try:
					print("item SHOW:{} {}".format(ts, pItem))
					show_note(self.screenshot, pItem)
					pItem['shown'] = True;
				except:
					print("item show problem: {}".format(e))
					traceback.print_exc(file=sys.stdout)
					continue
			time.sleep(15)

	def cleanup(self):
		''' Update all items added. '''
		while True:
			time.sleep(self.delay*2)
			print("Cleaning up............")		
			while self.cleaner_running:
				time.sleep(10)
			self.cleaner_running = True
			alist = self.getItems()
			for upditem in alist:
				try:
					(ts,pItem) = upditem
					if 'shown' in pItem:
						if pItem['shown']:
							#print("Cleaning up: {}".format(pItem['guid']))

							self.guidsDeleted.append(pItem['guid'])
							filePath = pItem['tmpimage']

							if filePath is not None:
								if os.path.exists(filePath):
									os.remove(filePath)

							alist.remove( upditem )
							self.setItems(alist)
							alist = self.getItems()
							del pItem;
				except:
					print("item cleanup problem: {}".format(e))
					traceback.print_exc(file=sys.stdout)
			self.cleaner_running = False
			time.sleep(self.delay*2)

	def cleanup_deleted_list(self):
		''' Delete old guid from track items list. '''
		while True:
			time.sleep(24*60*60) # 24 tunnin välein
			while self.cleaner_running:
				time.sleep(10)
			self.cleaner_running = True
			print("Cleaning up old list.. keeping 100, max")
			alist = self.guidsDeleted
			newlist = []
			for upditem in range(0, 100):
				if len(alist) > 0:
					guid = alist.pop()
					if guid is not None:
						newlist.append(guid)
					else:
						break
				else:
					break
			del alist
			del self.guidsDeleted
			self.guidsDeleted = newlist
			print("{} GUID's saved".format(len(newlist)))
			self.cleaner_running = False

	def start(self):
		''' Start the firehose. '''
		while True:
			if not self.cleaner_running:
				print("update...")
				self.update()
			#print("update sleep...")
			time.sleep(self.delay/8)

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
#toaster = ToastNotifier()

def show_note(screenshot, updateItem):

	def show_note_item_clicked(obj):
		if sys.platform == "win32":
			print("Open browset to {}".format(obj))
			webbrowser.open(obj)

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

	category="News from " + siteName
	if tags is not None:
		if tags[0] is not None:
			if 'term' in tags[0]:
				category = tags[0]['term']

	link = TinyUrl.mkShortUrl(link)

	thumbnailFP = screenshot.makeThumbnail(link, siteName, 150, 100)

	categories = category

	if isinstance(category, list):
		categories = ""
		for cat in category:

			comma=", "
			if categories == "":
				comma = ""

			categories = categories + comma + cat

	if sys.platform == "win32":
		msgTitle = '''// {} //\n{}\n{}'''.format(siteName, categories, title)

		if (len(siteName) + len(categories)) < 40:
			msgTitle = '''// {} // {}\n{}'''.format(siteName, categories, title)

		msgTitle = '''// {} // {}\n{}'''.format(siteName, categories, title)
		msgBody = str(description) + str(published)

		wbn = WindowsBalloonNote()
		#print("show_note:: windows")
		wbn.show_toast(msgTitle,
					msgBody,
					threaded=True,
					icon_path=thumbnailFP,
					cbFunc = show_note_item_clicked,
				        cbArgs = link
				)

	else: # not windows
		if len(categories) > 0:
			categories = categories + ":"

		if description is None:
			description = ""
		else:
			description = description + "\n"

		msgTitle = '''// {} // {}\n{}'''.format(siteName, categories, title)
		msgBody = str(description) + str(published) +" <a href='"+ link +"'>Link to news</a>"
		
		encodeto='UTF-8'
		msgTitle.encode(encodeto)
		msgBody.encode(encodeto)

		note = Notify.Notification.new(msgTitle, msgBody, "dialog-information")

		image = None
		updateItem['tmpimage'] = None
		if thumbnailFP is not None:
			try:
				image = GdkPixbuf.Pixbuf.new_from_file(thumbnailFP)
				updateItem['tmpimage'] = thumbnailFP
			except:
				pass

			finally:
				if image is not None:
					note.set_image_from_pixbuf(image)

		#print("show_note:: linux: ")
		note.show()





import _thread


def start_cleanup_deleted_list(tn, MO):
	MO.cleanup_deleted_list()

def start_notes_show(tn, MO):
	MO.show_notes()

def start_notes_build(tn, MO):
	MO.start()

def start_notes_cleaner(tn, MO):
	MO.cleaner()


MainObj = Firehose(delay=30);

MainObj.setSources(Feeds)

_thread.start_new_thread(start_notes_show, 		('Note show',MainObj,))
_thread.start_new_thread(start_notes_build, 		('Note build',MainObj,))
_thread.start_new_thread(start_notes_cleaner, 		('Note cleaner',MainObj,))
_thread.start_new_thread(start_cleanup_deleted_list, 	('Guid list cleaner',MainObj,))


while True:
	#print("Sleep .........")
	time.sleep(1000);



