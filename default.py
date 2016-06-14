# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,string,random,cookielib,xbmcvfs

import time
import json
import libMediathek
import resources.lib._utils as _utils
from operator import itemgetter

icon = 'http://multicam.sportschau.de/img/player_default.jpg'
fanart = 'http://multicam.sportschau.de/img/bgr.jpg'

channels = 'http://clipsapi.sportschau.de/ARDX/36640243euro2016/3.0/channels.json'
test = 'http://multicam.sportschau.de/match/2017884'
feed = 'http://livestreamapi.sportschau.de/feed/ard/cup=3/livestreaming.json'
idk = 'http://clipsapi.sportschau.de/ARDX/36640243euro2016/3.0/channels/2017884/publications.json'
idk2 = 'http://clipsapi.sportschau.de/ARDX/36640243euro2016/3.0/channels/2017884.json'

pluginhandle = int(sys.argv[1])

perspAlias = {
	'lsf':'Standardperspektive',
	'playa':'Spielerkamera A',
	'playb':'Spielerkamera B',
	'mc1':'Hauptkamera A',
	'mc2':'Hauptkamera B',
	'cablecam':'Cablecam',
	'tactical':'Dachkamera',
	'tactical ':'Dachkamera',
	'revmid':'Gegenseite',
	'16ml':'16m-Raum links',
	'16mr':'16m-Raum rechts',
	'6ml':'6m-Raum links',
	'6mr':'6m-Raum rechts',
	'steadyl':'Steady Cam links',
	'steadyr':'Steady Cam rechts',
	'pitchl':'Feldkamera links',
	'pitchr':'Feldkamera rechts',
	'cranel':'Torkran links',
	'craner':'Torkran rechts',
	'boxl':'Tor links',
	'boxr':'Tor rechts',
	'teama':'Team A',
	'teamb':'Team B',
	'pitchhw':'Feldkamera Mittellinie',
	'revpitchhw':'Feldkamera Mittellinie gegenüber',
	#'pitchhw':'',
	
	'heli':'Helikopter'
	}

def main():
	a = {}
	list = []
	response = _utils.getUrl(channels)
	j = json.loads(response)
	for item in j:
		if 'description' in item['metadata']:
			dict = {}
			dict['name'] = item['metadata']['description']
			dict['shortCode'] = item['shortCode']
			dict['thumb'] = icon
			dict['fanart'] = fanart
			dict['mode'] = 'listVideos'
			dict['type'] = 'dir'
			a[dict['shortCode']] = item['metadata']['description']
			list.append(dict)
	list = sorted(list, key=itemgetter('name')) 
	
	a['name']   = 'Ganze Spiele Live/Aufzeichnung'
	a['mode']   = 'listFull'
	a['type']   = 'dir'
	a['url']    = feed
	a['fanart'] = fanart
	a['thumb']  = icon
	libMediathek.addEntry(a)

	libMediathek.addEntries(list)
	
def listFull():
	list = []
	response = _utils.getUrl(feed)
	j = json.loads(response)
	for match in j:
		dict = {}
		dict['name'] = params.get(str(match['matchID']),str(match['matchID']))

		if match['VideoStreaming'][0]['Status'] == 'Live':
			dict['name'] = 'Live: ' + dict['name']
		dict['matchID'] = match['matchID']
		dict['thumb'] = icon
		dict['fanart'] = fanart
		dict['mode'] = 'listFullPersp'
		dict['type'] = 'dir'
		list.append(dict)
	libMediathek.addEntries(list)
		
	
def listFullPersp():
	list = []
	response = _utils.getUrl(feed)
	j = json.loads(response)
	for match in j:
		if str(match['matchID']) == params['matchID']:
			j2 = match
	for persp in j2['VideoStreaming']:
		if persp['Description'] == 'lsf':
			dict = {}
			dict['name'] = 'Hauptperspektive - englischer Kommentator'
			dict['url'] = persp['Url']
			dict['thumb'] = icon
			dict['fanart'] = fanart
			dict['mode'] = 'play'
			dict['type'] = 'video'
			list.append(dict)
			dict = {}
			if persp['Url'].endswith('filter=english)'):
				dict['name'] = 'Hauptperspektive - ohne Kommentator'
				dict['url'] = persp['Url'].replace(',filter=english','').replace('format=m3u8-aapl-v3','format=m3u8-aapl')
				dict['thumb'] = icon
				dict['fanart'] = fanart
				dict['mode'] = 'play'
				dict['type'] = 'video'
				list.append(dict)
		else:
			dict = {}
			dict['name'] = perspAlias.get(persp['Description'],persp['Description'])
			dict['url'] = persp['Url']
			dict['thumb'] = icon
			dict['fanart'] = fanart
			dict['mode'] = 'play'
			dict['type'] = 'video'
			list.append(dict)
	list = sorted(list, key=itemgetter('name')) 
	libMediathek.addEntries(list)
	
def listVideos():
	list = []
	response = _utils.getUrl('http://clipsapi.sportschau.de/ARDX/36640243euro2016/3.0/channels/' + params['shortCode'] + '/publications.json')
	j = json.loads(response)
	for item in j:
		dict = {}
		dict['id'] = item['id']
		dict['url'] = 'http://clipsapi.sportschau.de/ARDX/36640243euro2016/3.0/channels/' + params['shortCode'] + '/publications/' + item['id'] + '.json'
		if item['hidden']:
			
			print 'TODO'
		else:
			try:
				if 'title_translation_de' in item['metadata']:
					dict['name'] = item['metadata']['title_translation_de']
				else:
					dict['name'] = item['metadata']['title']
				dict['name'] += ' (' + str(item['videoAssetsCount']) + ')'
				dict['thumb'] = _fetchthumb(item)
				dict['fanart'] = fanart
				if item['videoAssetsCount'] == 1:
					dict['mode'] = 'playSingle'
					dict['type'] = 'video'
				else:
					dict['mode'] = 'listPersp'
					dict['type'] = 'dir'
				list.append(dict)
			except:
				xbmc.log(str(item))
	libMediathek.addEntries(list)
	
def listPersp():
	list = []
	response = _utils.getUrl(params['url'])
	j = json.loads(response)
	for asset in j['videoAssets']:
		dict = {}
		dict['name'] = perspAlias.get(asset['recorderShortCode'],asset['recorderShortCode'])
		dict['duration'] = asset['duration']
		#dict['url'] = 'http://clipassets-i.sportschau.de/' + asset['renditions']['multibitrate'] + '.m3u8'#http://clipassets-p.sportschau.de/59D085D7C0F398439DA19A77FE4DA512/59D085D7C0F398439DA19A77FE4DA512.m3u8
		dict['url'] = 'http://clipassets-p.sportschau.de/' + asset['renditions']['digital'] + '.mp4'#http://clipassets-p.sportschau.de/59D085D7C0F398439DA19A77FE4DA512/59D085D7C0F398439DA19A77FE4DA512.m3u8
		dict['thumb'] = params['thumb']
		dict['fanart'] = fanart
		dict['mode'] = 'play'
		dict['type'] = 'video'
		#todo thumb
		list.append(dict)
	libMediathek.addEntries(list)	

	
def play():
	listitem = xbmcgui.ListItem(path=params['url'])
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	
def playSingle():
	response = _utils.getUrl(params['url'])
	j = json.loads(response)
	url = 'http://clipassets-p.sportschau.de/' + j['videoAssets'][0]['renditions']['digital'] + '.mp4'#http://clipassets-p.sportschau.de/59D085D7C0F398439DA19A77FE4DA512/59D085D7C0F398439DA19A77FE4DA512.m3u8
	listitem = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	
def _fetchthumb(j):
	for asset in j['thumbAssets']:
		if "Default" in asset['tags']:
			#return 'http://clipassets-i.sportschau.de/' + asset['renditions']['thumbs-l'] + '.jpg'
			return 'http://clipassets-i.sportschau.de/' + asset['renditions']['thumbs-m'] + '.jpg'
params=libMediathek.get_params()
if not params.has_key('mode'):
	main()
elif params['mode'] == 'listFull':
	listFull()
elif params['mode'] == 'listFullPersp':
	listFullPersp()
elif params['mode'] == 'listVideos':
	listVideos()
elif params['mode'] == 'listPersp':
	listPersp()
elif params['mode'] == 'play':
	play()
elif params['mode'] == 'playSingle':
	playSingle()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
