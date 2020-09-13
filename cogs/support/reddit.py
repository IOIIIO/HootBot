import requests

def return_reddit(url):
	api_url = '{}.json'.format(url)
	r = requests.get(api_url, headers = {'User-agent': 'Starboard v1.0'}).json()
	try:
		url = r[0]["data"]["children"][0]["data"]["media_metadata"]["u6yr7w5mstb51"]["s"]["u"].replace("&amp;", "&")
	except:
		url = r[0]["data"]["children"][0]["data"]["preview"]["images"][0]["source"]["url"].replace("&amp;", "&")
	#else:
	#	url = ""
	if ".jpg" in url:
		return url
	else:
		return ''