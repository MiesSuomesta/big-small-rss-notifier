#!/usr/bin/python
import sys
import gi
from rssitem import *
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init("Notifier")

def show_note(title, body):
	note = Notify.Notification.new(title, body, "dialog-information")
	note.show()



# -------------------------------------------

URLS_KL = []

URLS_KL.append("https://feeds.kauppalehti.fi/rss/main")
URLS_KL.append("https://feeds.kauppalehti.fi/rss/klnyt")

Sites = []

siteObj = RssSiteKL(URLS_KL)

Sites.append(siteObj)

shownItemsAllSites = []

while 1:
	if len(shownItemsAllSites) > 0:
		del shownItemsAllSites

	shownItemsAllSites = []

	# Get all items in one big list
	for site in Sites:
		site.update()
		itemlist = site.list_items_to_show(30*1000*1000)
		if itemlist is None:
			continue

		for (ts, itm) in itemlist:
			shownItemsAllSites.append((ts, itm))
			shownItemsAllSites= sorted(shownItemsAllSites, key=lambda x: x[0], reverse=False)

	slept = False
	# Show all in post order
	for (ts, itm) in shownItemsAllSites:
		if itm.is_shown() is False:
			itm.show_note()
			slept = True
			time.sleep(10)
	if not slept:
		time.sleep(10)

	# Cleanup
	for site in Sites:
		site.cleanup_shown()


