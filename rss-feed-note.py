#!/usr/bin/python
import sys
from rssitem import *

# Sites
from rsssite_kauppalehti import *
from rsssite_yle import *

# -------------------------------------------

URLS_KL = []

URLS_KL.append("https://feeds.kauppalehti.fi/rss/main")
URLS_KL.append("https://feeds.kauppalehti.fi/rss/klnyt")

URLS_YLE = []

URLS_YLE.append("https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET")
URLS_YLE.append("https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss")


shotter = Screenshot()

Sites = []

siteObjKL = RssSiteKL(URLS_KL, shotter)
siteObjYLE = RssSiteYle(URLS_YLE, shotter)

Sites.append(siteObjKL)
Sites.append(siteObjYLE)

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


