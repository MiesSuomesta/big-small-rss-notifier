import traceback
import json, os, sys

def get_login_data_file_path():

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
	print("login datas at: {}".format(datasAt))

	return datasAt

def get_login_data(fromFile, siteName):

	data = {}
	with open(fromFile) as json_file:
		data = json.load(json_file)

	sited = data.get(siteName)

	#y = json.dumps(sited, indent=4)
	#print(siteName, y)

	return sited


