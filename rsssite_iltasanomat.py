import sys
import traceback
import urllib3
import xmltodict
import json
import gi
import time
from htmltogif import *
from rssitem import *
import tempfile as TF
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("Notifier")



class RssSiteIltasanomat(RssSite):

	# description
	ch_dictObj = None
	scrshot = None
	def __init__(self, uri, shotter):
		super().__init__(uri, 'iltasanomat', shotter)
		self.scrshot = shotter
		self.update()


	# 0 no, 1 yes, 2 no item 
	def is_guid_shown(self, gGuid):
		rv = 2
		for (ts, itm) in super().getItems():
			if itm.is_guid(gGuid):
				if itm.is_shown():
					rv = 1
				else:
					rv = 0
		return rv

	def preprocessxml(xmldata):
		#print("to prepared:", xmldata)

		p = re.compile('(<!\[CDATA\[|\]\]>|\\n|\n)')

		(xml, nro) = p.subn('', xmldata)

		print("prepared:", nro, xml)
		return xml

	def update(self, xml_attribs=None, namespaces=None, force_cdata=False, preprocessrawxml=preprocessxml):
		super().update(xml_attribs=xml_attribs, namespaces=namespaces, force_cdata=force_cdata, preprocessrawxml=preprocessrawxml)
		self.ch_dictObj = super().getSourceDict().get("rss").get("channel")
		super().setSourceDict(self.ch_dictObj)
		super().debug_print()

		for i in self.ch_dictObj.get("item"):
			rv = self.is_guid_shown( i.get("guid") )
			if rv == 2:
				rssitemobj = RssItem(i, 'iltasanomat', self.scrshot, xml_attribs=xml_attribs, namespaces=namespaces, force_cdata=force_cdata)
				super().add_rss_item(rssitemobj)




