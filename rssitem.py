import sys
import traceback
import urllib3
import xmltodict
import json
import gi
import re
import time
from htmltogif import *
import tempfile as TF

gi.require_version('Notify', '0.7')
from gi.repository import Notify, GdkPixbuf

Notify.init("Notifier")


class RssItem:

	itemValues = None
	timestamp = None
	shown = False
	scrshot = None
	siteName = None
	thumbnailFP = None

	def __init__(self, values, siteName, shotter, xml_attribs=None, namespaces=None, force_cdata=False, preprocessrawxml=None):
		#print("RSSITEM", shotter, siteName)
		self.scrshot = shotter
		self.itemValues = values;
		self.siteName = siteName
		self.timestamp = time.monotonic_ns()
		self.update(xml_attribs=xml_attribs, namespaces=namespaces, force_cdata=force_cdata, preprocessrawxml=preprocessrawxml)

	def show_note(self):

		if self.shown:
			return None

		category = self.getKeyValue("category", "")
		pubdate = self.getKeyValue("pubDate", "")
		title = self.getKeyValue("title", "")
		link = self.getKeyValue("link", "")
		description = self.getKeyValue("description", "")

		thumbnailFP = self.scrshot.makeThumbnail(link, self.siteName, 150, 100)

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

		msgTitle = '''// {} // {}\n{}'''.format(self.siteName, categories, title)
		msgBody = str(description) + str(pubdate) +" <a href='"+ str(link) +"'>Link to news</a>"

		note = Notify.Notification.new(msgTitle, msgBody, "dialog-information")

		image = None
		if thumbnailFP is not None:
			try:
				image = GdkPixbuf.Pixbuf.new_from_file(thumbnailFP)
			except:
				pass

			finally:
				if image is not None:
					note.set_image_from_pixbuf(image)

		note.show()

		self.shown = True
		

	def getKeyValue(self, val, default=None):
		rv = default
		if self.itemValues is not None:
			rv = self.itemValues.get(val, default)
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

	MAX_TS_DIFF_SECS = 30
	MAX_TS_DIFF_NS = MAX_TS_DIFF_SECS * 1000 * 1000
	

	def __init__(self, uri, siteName, shotter, 
			pxml_attribs=None,
			pnamespaces=None, 
			pforce_cdata=False, 
			ppreprocessrawxml=None):
		#print("RSSSITE", shotter)
		self.items = []
		self.siteSourceDictObj = None
		self.siteSourceDictObjTS = None
		self.scrshot = shotter
		self.siteURI = uri
		self.siteName = siteName
		self.update(xml_attribs=pxml_attribs, namespaces=pnamespaces, force_cdata=pforce_cdata, preprocessrawxml=ppreprocessrawxml)

	def getSourceDict(self):
		return self.siteSourceDictObj

	def setSourceDict(self, obj):
		now = time.monotonic_ns()
		self.siteSourceDictObj = obj
		self.siteSourceDictObjTS = now

	def getItems(self):
		return self.items

	def setItems(self, itms):
		self.items = itms

	def getSourceDictTS(self):
		return self.siteSourceDictObjTS

	def setSourceDictTS(self, ts):
		self.siteSourceDictObjTS = ts

	def update(self, pxml_attribs=None, pnamespaces=None, pforce_cdata=False, ppreprocessrawxml=None):
		self.siteSourceDictObjUpdate(xml_attribs=pxml_attribs, namespaces=pnamespaces, force_cdata=pforce_cdata, preprocessrawxml=ppreprocessrawxml)

	def debug_print(self):
		y = json.dumps(self.siteSourceDictObj, indent=4)
		print(y)
		


	def siteSourceDictObjUpdate(self, xml_attribs=None, namespaces=None, force_cdata=False, preprocessrawxml=None):
		def dictMerge(dict1, dict2):
			dict2.update(dict1)
			return dict2

		sourceDictObj = {}
		for uri in self.siteURI:

			http = urllib3.PoolManager()
			response = http.request('GET', uri)
			xmldata = response.data

			if preprocessrawxml is not None:
				print("pre processing.....")
				xmldata = preprocessrawxml(xmldata)
				print("pre processed.")


			try:
				uriDictObj = xmltodict.parse(xmldata,
							xml_attribs=xml_attribs,
							namespaces=namespaces,
							force_cdata=force_cdata)

				sourceDictObj = dictMerge(uriDictObj, sourceDictObj)
			except:
				print("Failed to parse xml from response (%s)" % traceback.format_exc())
				return None


		print("Setting dict: {}".format(sourceDictObj))
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

