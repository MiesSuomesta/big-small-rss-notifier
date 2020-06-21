#!/usr/bin/python
import sys

from collections import OrderedDict
from rssfeeditem import *
from htmltogif import *
import traceback
from feedconfigdatamanager import *
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

Feeds = []

feedconfig = feedconfig_get_data()
if feedconfig is not None:
	print("Configuration parsed ok")
	
for fciSiteName in feedconfig.keys():
    fciSiteData = feedconfig.get(fciSiteName)
    if 'feeds' in fciSiteData:
        for fciSiteFeed in fciSiteData.get('feeds'):
            Feeds.append( RssFeed(fciSiteName, fciSiteFeed, fciSiteData) )
            print("Added {} feed {} to be monitored".format(fciSiteName,fciSiteFeed))


class Firehose:
	def __init__(self, out=sys.stdout, delay=5.0):
		self.screenshot = Screenshot()
		# file-like object to write output to
		self.out = out
		# seconds to sleep between each update loop   	
		self.delay = delay
		# list of installed source objects
		self._sources = []
		self.itemsAdded = OrderedDict()
		self.guidsDeleted = []
		self.cleaner_running = False
		self.dict_locked = False

		#watchdog reset times
		self.update_ts = time.monotonic_ns()
		self.cleanup_ts = time.monotonic_ns()
		self.cleanup_deleted_list_ts = time.monotonic_ns()
		self.watchdog_ts = time.monotonic_ns()

	def watchdog(self):

		while True:
			timeUsec = 	(self.update_ts 		/ 1000*1000) + 60
			timeCsec = 	(self.cleanup_ts 		/ 1000*1000) + 60
			timeCDLsec = 	(self.cleanup_deleted_list_ts	/ 1000*1000) + 60
			timeWDLsec = 	(self.watchdog_ts 		/ 1000*1000) + 60
			TO = 		(time.monotonic_ns()		/ 1000*1000)

			die = False
			reason="WD died"

			if (TO < timeUsec):
				reason="Updater died"
				die = True

			if (TO < timeCsec):
				reason="Cleanup died"
				die = True

			if (TO < timeCDLsec):
				reason="Cleanup guids died"
				die = True

			if (TO < timeWDLsec):
				reason="WD died"
				die = True

			if die:
				print("Dying: {}....".format(reason))
				os.exit(1)

			time.sleep(20)


		self.watchdog_ts = time.monotonic_ns()
		print("... All threads alive.")

	def setSources(self, feeds):
		self._sources = feeds

	def getSources(self, feeds):
		return self._sources

	def setItems(self, alist):
		self.itemsAdded = alist

	def getItems(self):
		return self.itemsAdded

	def dumpItems(self):
		for itm in self.getItems():
			ts = itm[0]
			upditem = itm[1]
			guid = upditem['guid']
			print("- TS {}, guid: {}".format(ts, guid))

	def sortItemsByPubDate(self):
		orgItemsDict = self.getItems().copy()
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

		self.setItems(newItemsDict)


	def update(self):
		''' Update all sources. '''

		self.update_ts = time.monotonic_ns()

		feedItems = self.getItems().copy()
		for source in self._sources:
			try:
				#print("--> items update {}".format(feedItems))
				source.update(self.guidsDeleted)
				srcDict = source.getItemDict().copy()
				feedItems.update(srcDict)
				#print("<-- items update {}".format(feedItems))
			except:
				print("alist update problem!")
				traceback.print_exc(file=sys.stdout)
				continue
		self.setItems(feedItems)

		self.sortItemsByPubDate() #Sort all together

		#self.dumpItems()

	def show_notes(self):
		''' Update all items added. '''
		while True:
			#print("show_notes: items:", alist)
			itemlist = self.getItems().copy()
			itemkeylist = itemlist.keys()

			print("Showing {} items".format(len(itemkeylist)))
			slept = False
			for dictKey in itemkeylist:
				pUpdateItem = itemlist.get(dictKey)
				#print("show_notes:: item:{} and {}".format(dictKey, pUpdateItem))

				try:
					#print("item SHOW:{} {}".format(ts, pItem))
					show_note(self.screenshot, pUpdateItem)
					pUpdateItem['shown'] = True
				except:
					print("item show problem")
					traceback.print_exc(file=sys.stdout)
					continue
				slept = True
				time.sleep(15)

			if not slept:
				time.sleep(30)

	def check_if_delete_ok(self, guid, pUpdateItem):

		try:
			if guid in self.guidsDeleted:
				#print("guid in deleted: ", guid)
				return True

			if 'shown' in pUpdateItem:
				#print("guid shown: ", pUpdateItem['shown'])
				return pUpdateItem['shown']

		except:
			print("check_if_delete_ok problem")
			traceback.print_exc(file=sys.stdout)
			pass

		return False

	def cleanup(self):
		''' Update all items added. '''
		while True:
			time.sleep(self.delay*2)
			self.cleanup_ts = time.monotonic_ns()
			print("Cleaning up............")		

			aDict = self.getItems()
			keysToDelete = []
			for feedKey in aDict.keys():
				UpdateItem = aDict.get(feedKey)
				guid = UpdateItem['guid']

				if self.check_if_delete_ok(guid, UpdateItem) is False:
					continue

				if guid not in keysToDelete:
					keysToDelete.append(guid)

			print("keysToDelete len:", len(keysToDelete))

			for feedKey in keysToDelete:
				UpdateItem = aDict.get(feedKey)


				try:
					if guid not in self.guidsDeleted:
						self.guidsDeleted.append(guid)

					filePath = UpdateItem['tmpimage']

					if filePath is not None:
						if os.path.exists(filePath):
							os.remove(filePath)

					del aDict[guid]

				except:
					print("delete key problem")
					traceback.print_exc(file=sys.stdout)
					pass

			self.setItems(aDict)
			print("{} clean up saved".format(len(aDict)))
			time.sleep(self.delay*2)

	def cleanup_deleted_list(self, maxItems):
		''' Delete old guid from track items list. '''
		while True:
			for t in range(1, 24*60):
				time.sleep(60) # 24 tunnin välein
				self.cleanup_deleted_list_ts = time.monotonic_ns()
			cnt = 0

			print("Cleaning up old list.. keeping {}, max".format(maxItems))

			aDict = self.getItems()
			for feedItem in aDict.items():
				guid, UpdateItem = feedItem

				cnt = cnt + 1

				if cnt < maxItems:
					continue


				try:
					filePath = pItem['tmpimage']

					if filePath is not None:
						if os.path.exists(filePath):
							os.remove(filePath)

					del aDict[guid]

				except:
					print("delete problem")
					traceback.print_exc(file=sys.stdout)
					pass

			print("{} GUID's saved".format(len(newlist)))
			self.setItems(aDict)

	def start(self):
		''' Start the firehose. '''
		while True:
			if not self.cleaner_running:
				print("update...")
				self.update()
			#print("update sleep...")
			time.sleep(self.delay)

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

def show_note(screenshot, updateItem):

	def show_note_item_clicked(obj):
		if sys.platform == "win32":
			print("Open browset to {}".format(obj))
			webbrowser.open(obj)

	#print("show_note:: RAW: {}".format(updateItem))

	rawEntry = getKeyVal(updateItem, 'rawEntry', None)
	siteData = getKeyVal(updateItem, 'siteData', None)

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
	description = getKeyVal(rawEntry, 'description', None)
	siteName 	= getKeyVal(updateItem, 'siteName', None)

	category="News from " + siteName
	if tags is not None:
		if tags[0] is not None:
			if 'term' in tags[0]:
				category = tags[0]['term']

	link = TinyUrl.mkShortUrl(link)

	thumbnailFP = screenshot.makeThumbnail(link, siteName, siteData, 150, 100)
	
	categories = category

	if isinstance(category, list):
		categories = ""
		for cat in category:

			comma=", "
			if categories == "":
				comma = ""

			categories = categories + comma + cat

	thumbnailFP = None

	if sys.platform == "win32":
		msgTitle = '''// {} //\n{}\n{}'''.format(siteName, categories, title)

		if (len(siteName) + len(categories)) < 40:
			msgTitle = '''// {} // {}\n{}'''.format(siteName, categories, title)

		msgTitle = '''// {} // {}\n{}'''.format(siteName, categories, title)
		msgBody = str(description) + str(published)
		
		
		
		try:
			wbn = WindowsBalloonNote()
			#print("show_note:: windows")
			wbn.show_toast(msgTitle,
					msgBody,
					threaded=True,
					icon_path=thumbnailFP,
					cbFunc = show_note_item_clicked,
				        cbArgs = link
				)
		except:
			pass

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

		try:
			note = Notify.Notification.new(msgTitle, msgBody, "dialog-information")
			image = None
			if thumbnailFP is not None:
				try:
					image = GdkPixbuf.Pixbuf.new_from_file(thumbnailFP)
					updateItem['tmpimage'] = thumbnailFP
				except:
					pass

				finally:
					if image is not None:
						note.set_image_from_pixbuf(image)

			note.show()
		except:
			pass

	updateItem['tmpimage'] = thumbnailFP


# ------------ MAIN THREADS ------------------------------------------
import _thread

def start_cleanup_deleted_list(tn, MO):
	MO.cleanup_deleted_list(100)

def start_notes_show(tn, MO):
	MO.show_notes()

def start_notes_build(tn, MO):
	MO.start()

def start_notes_cleaner(tn, MO):
	MO.cleaner()

def start_wd(tn, MO):
	MO.watchdog()


MainObj = Firehose(delay=5*60);

MainObj.setSources(Feeds)

_thread.start_new_thread(start_notes_show, 		('Note show',MainObj,))
_thread.start_new_thread(start_notes_build, 		('Note build',MainObj,))
_thread.start_new_thread(start_notes_cleaner, 		('Note cleaner',MainObj,))
_thread.start_new_thread(start_cleanup_deleted_list, 	('Guid list cleaner',MainObj,))
_thread.start_new_thread(start_wd, 			('Watchdog',MainObj,))


while True:
	#print("Sleep .........")
	time.sleep(1000);



