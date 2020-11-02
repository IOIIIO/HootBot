import requests

def return_reddit(url):
    api_url = '{}.json'.format(url)
    r = requests.get(api_url, headers = {'User-agent': 'Starboard v1.0'}).json()
    # only galeries have media_metadata
    if 'media_metadata' in r[0]['data']['children'][0]['data']:
        # media_metadata is unordered, gallery_data has the right order
        first = r[0]['data']['children'][0]['data']['gallery_data']['items'][0]['media_id']
        # the highest quality pic always the last one
        ret = r[0]['data']['children'][0]['data']['media_metadata'][first]['s']['u'].replace('&amp;', '&')
    else:
        # covers gifs
        ret = r[0]['data']['children'][0]['data']['url_overridden_by_dest']
        # the url doesn't end with any of these then the post is a video, so fallback to the thumbnail
        if '.jpg' not in ret and '.png' not in ret and '.gif' not in ret:
            ret = r[0]['data']['children'][0]['data']['preview']['images'][0]['source']['url'].replace('&amp;', '&')
    return ret
