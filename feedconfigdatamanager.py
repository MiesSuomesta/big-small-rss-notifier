import traceback
import json, os, sys
FILEPATH_SHOWN = False

def feedconfig_get_feed_config_file_path():

	datasAt=""
	if sys.platform == "win32":
		HOME = os.getenv('APPDATA', None)
		datasAt=HOME
		datasAt = os.path.join(datasAt, "..")
		datasAt = os.path.join(datasAt, "..")
		datasAt = os.path.join(datasAt, "Desktop")
		datasAt = os.path.join(datasAt, "rss-notifier-login-datas.json")
	else:
		HOME = os.getenv('HOME', None)
		datasAt=HOME
		datasAt = os.path.join(datasAt, ".rss-notifier-login-datas.json")

	global FILEPATH_SHOWN
	if not FILEPATH_SHOWN:
		print("login datas at: {}".format(datasAt))
		FILEPATH_SHOWN=True

	return datasAt

def feedconfig_get_data():

	filenameFrom = feedconfig_get_feed_config_file_path();

	data = {}
	with open(filenameFrom) as json_file:
		data = json.load(json_file)

	#y = json.dumps(sited, indent=4)
	#print(siteName, y)

	return data

def feedconfig_get_site_data(siteName):

	filenameFrom = get_feed_config_file_path();

	data = feedconfig_get_data()
	sited = data.get(siteName)

	#y = json.dumps(sited, indent=4)
	#print(siteName, y)

	return sited


