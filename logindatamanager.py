
import json

def get_login_data(fromFile, siteName):

	data = {}
	with open(fromFile) as json_file:
		data = json.load(json_file)

	sited = data.get(siteName)

	#y = json.dumps(sited, indent=4)
	#print(siteName, y)

	return sited


