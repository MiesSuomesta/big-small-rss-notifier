import sys
import traceback
import urllib3
import xmltodict
import json
import gi
import time
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("Notifier")


class RssItem:
	itemValues = None
	timestamp = None
	shown = False
	def __init__(self, values):
		self.itemValues = values;
		self.timestamp = time.monotonic_ns()

	def show_note(self):

		category = self.getKeyValue("category")
		pubdate = self.getKeyValue("pubDate")
		title = self.getKeyValue("title")
		link = self.getKeyValue("link")
		description = self.getKeyValue("description")

		msgTitle = '''{} | {}'''.format(category, title)
		msgBody = '{}\n{} <a href="{}">Link</a>'.format(description, pubdate, link)

		note = Notify.Notification.new(msgTitle, msgBody, "dialog-information")
		note.show()
		self.shown = True
		

	def getKeyValue(self, val):
		rv = None
		if self.itemValues is not None:
			rv = self.itemValues.get(val)
		return rv

	def is_guid(self, gGuid):
		val = self.getKeyValue("guid")
		return val is gGuid;

	def is_shown(self):
		return self.shown;

	def debug_print(self):
		y = json.dumps(self.itemValues, indent=4)
		print(y)


class RssSite:
	items = []
	siteURI = []
	siteSourceDictObj = None
	siteSourceDictObjTS = None

	MAX_TS_DIFF_SECS = 30
	MAX_TS_DIFF_NS = MAX_TS_DIFF_SECS * 1000 * 1000
	

	def __init__(self, uri):
		self.siteURI = uri
		self.update()

	def getSourceDict(self):
		return self.siteSourceDictObj

	def setSourceDict(self, obj):
		now = time.monotonic_ns()
		if self.siteSourceDictObj is not None:
			del self.siteSourceDictObj
		self.siteSourceDictObj = obj
		self.siteSourceDictObjTS = now

	def getItems(self):
		return self.items

	def setItems(self, itms):
		if self.items is not None:
			del self.items
		self.items = itms

	def getSourceDictTS(self):
		return self.siteSourceDictObjTS

	def setSourceDictTS(self, ts):
		self.siteSourceDictObjTS = ts

	def update(self):
		self.siteSourceDictObjUpdate()

	def debug_print(self):
		y = json.dumps(self.siteSourceDictObj, indent=4)
		#print(y)
		

	def siteSourceDictObjUpdate(self):

		def dictMerge(dict1, dict2):
			dict2.update(dict1)
			return dict2

		sourceDictObj = {}
		for uri in self.siteURI:

			http = urllib3.PoolManager()
			response = http.request('GET', uri)
			try:
				uriDictObj = xmltodict.parse(response.data)
				sourceDictObj = dictMerge(uriDictObj, sourceDictObj)
			except:
		#		print("Failed to parse xml from response (%s)" % traceback.format_exc())
				return None
		#print("Setting dict: {}".format(sourceDictObj))
		self.setSourceDict(sourceDictObj)

		now = time.monotonic_ns()
		self.setSourceDictTS(now)
		return True

	def add_rss_item(self, rssitem):
		self.items.append((rssitem.timestamp, rssitem));
		self.items = sorted(self.items, key=lambda x: x[0], reverse=False)

	def cleanup_shown(self):
		nlist = []
		sItems = self.getItems()
		for (ts, itm) in sItems:
			if itm.is_shown():
				del itm
				del ts
			else:
				nlist.append((ts, itm));
		del sItems
		self.setItems(nlist)

	def list_items_to_show(self, maxDiff):
		nlist = []
		nowTS = time.monotonic_ns()
		sourceTS = self.getSourceDictTS()
		sourceOldest = nowTS - maxDiff

		sItems = self.getItems()
		for (ts, itm) in sItems:
			if not itm.is_shown() and nowTS > sourceOldest:
				nlist.append((ts, itm));

		return nlist

class RssSiteKL(RssSite):

	# description
	ch_dictObj = None

	def __init__(self, uri):
		super().__init__(uri)
		self.update()

	def is_guid_listed(self, gGuid):
		sItems = super().getItems()
		for (ts, itm) in sItems:
			if itm.is_guid(gGuid):
				return True
		return False		

	def update(self):
		super().update()
		self.ch_dictObj = super().getSourceDict().get("rss").get("channel")
		super().setSourceDict(self.ch_dictObj)
		super().debug_print()

		self.ch_description = self.ch_dictObj.get("description")

		for i in self.ch_dictObj.get("item"):
			if not self.is_guid_listed( i.get("guid") ):
				rssitemobj = RssItem(i)
		#		print("Inserting:\n")
		#		rssitemobj.debug_print()
				super().add_rss_item(rssitemobj)




