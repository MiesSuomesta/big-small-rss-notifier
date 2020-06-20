# big-small-rss-notifier
Python sources for small rss feed notifier

copy and modify identifications.json as ~/.rss-notifier-login-datas.json

JSON Example:

{
       "Eduskunta": {
				"public": true,
				"username": "",
				"password": "",
				"feeds": [
					"https://www.eduskunta.fi/_layouts/15/feed.aspx?xsl=1&web=%2FFI%2Frss%2Dfeeds&page=f9da32bd-3b14-433b-8205-71a52f570b09&wp=fdd65402-3b0a-4310-a0ba-ba310c157922&pageurl=%2FFI%2Frss%2Dfeeds%2FSivut%2Fdefault%2Easpx"
				]
		},
       "Puolustusministeriö": {
				"public": true,
				"username": "",
				"password": "",
				"feeds": [
					"https://www.defmin.fi/rss/puolustusministerio_uutiset_ja_tiedotteet"
				]
		},
       "Arvopaperi": {
				"public": false,
				"username": "login",
				"password": "password",
				"feeds": [
					"https://www.arvopaperi.fi/api/feed/v2/rss/ap"
				]
		},
       "Kauppalehti": {
				"public": false,
				"username": "login",
				"password": "password",
				"feeds": [
					"https://feeds.kauppalehti.fi/rss/main",
					"https://feeds.kauppalehti.fi/rss/klnyt"
				]
		}
}



