# Hotstar.com plugin written by Zoobi.
import os
import re
import urllib, urllib2
import xbmcplugin
import xbmcgui
import xbmcaddon
import operator
from datetime import date

import codecs
import json
import requests

ADDON = xbmcaddon.Addon(id='plugin.video.mihotstar')
fullurl = 'http://account.hotstar.com/AVS/besc?action={1}&{2}={0}&channel=PCTV'
cdnurl = 'http://getcdn.hotstar.com/AVS/besc?action=GetCDN&asJson=Y&channel=PCTV&id={0}&type=VOD'
ipaddress='0.0.0.0'

s=requests.Session()

##
# Prints the main categories. Called when id is 0.
##
def list_channels(name, url, language, mode, category):
    cwd = ADDON.getAddonInfo('path')
    url = fullurl.format(category, 'GetCatalogueTree', 'categoryId')
    postData = url
    print ('list_channels url=' + postData)
    data = make_request(postData)
    result = json.loads(data)
    
    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                if 'categoryList' in result['resultObj']:
                    if len(result['resultObj']['categoryList']) > 0:
                        if 'categoryList' in result['resultObj']['categoryList'][0]:
                            dcList = result['resultObj']['categoryList'][0]['categoryList']
                            for catl in dcList:
                                fin_ep_images = 'http://media0-starag.startv.in/r1/thumbs/PCTV/'+str(catl['urlPictures'])[-2:]+'/'+str(catl['urlPictures'])+'/PCTV-'+str(catl['urlPictures'])+'-hs.jpg'
                                addDir(catl['contentTitle'], '&categoryId=' + str(catl['categoryId']), 1, fin_ep_images, language, catl['categoryId'])
                            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            print ('Unknown error')
            xbmcgui.Dialog().ok("11111", 'Unknown error')

def list_channels_content(name, url, language, mode, category):
    cwd = ADDON.getAddonInfo('path')
    url = fullurl.format(category, 'GetArrayContentList', 'categoryId')
    postData = url
    print ('list_channels_content url=' + postData)
    data = make_request(postData)
    result = json.loads(data)

    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                if 'contentList' in result['resultObj']:
                    dcList = result['resultObj']['contentList']
                    for catl in dcList:
                        show_link = 'http://account.hotstar.com/AVS/besc?action=GetAggregatedContentDetails&channel=PCTV&contentId='+str(catl['contentId'])
                        show_img = 'http://media0-starag.startv.in/r1/thumbs/PCTV/'+str(catl['urlPictures'])[-2:]+'/'+str(catl['urlPictures'])+'/PCTV-'+str(catl['urlPictures'])+'-vl.jpg'
                        addDir(catl['contentTitle'], '&categoryId=' + str(catl['contentId']), 2, show_img, language, catl['contentId'])
                        
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            print ('Unknown error')
            xbmcgui.Dialog().ok("11111", 'Unknown error')

def list_shows_agg_content(category):
    cwd = ADDON.getAddonInfo('path')
    url = fullurl.format(category, 'GetAggregatedContentDetails', 'contentId')
    postData = url
    print ('list_shows_agg_content url=' + postData)
    data = make_request(postData)
    result = json.loads(data)

    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                if 'contentInfo' in result['resultObj']:
                    dcList = result['resultObj']['contentInfo'][0]
                    return dcList['categoryId']
        else:
            print ('Unknown error')
            return 0
            
def list_show_chapters(name, url, language, mode, category):
    cwd = ADDON.getAddonInfo('path')
    
    aggCategoryId = list_shows_agg_content(category)
    url = fullurl.format(aggCategoryId, 'GetCatalogueTree', 'categoryId')
    postData = url
    print ('list_show_chapters url=' + postData)
    data = make_request(postData)
    result = json.loads(data)

    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                if 'categoryList' in result['resultObj']:
                    if len(result['resultObj']['categoryList']) > 0:
                        if 'categoryList' in result['resultObj']['categoryList'][0]:
                            dcList = result['resultObj']['categoryList'][0]['categoryList']
                            for catl in dcList:
                                addDir(catl['contentTitle'], '&categoryId=' + str(catl['categoryId']), 3, postData, language, catl['categoryId'])
                            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            print ('Unknown error')
            xbmcgui.Dialog().ok("11111", 'Unknown error')
            
def list_show_chapter_episodes(name, url, language, mode, category):
    cwd = ADDON.getAddonInfo('path')
    url = fullurl.format(category, 'GetArrayContentList', 'categoryId')
    postData = url
    print ('list_show_chapter_episodes url=' + postData)
    data = make_request(postData)
    result = json.loads(data)

    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                if 'contentList' in result['resultObj']:
                    dcList = result['resultObj']['contentList']
                    dcListSorted = sorted(dcList, key=operator.itemgetter("episodeNumber"), reverse=True)
                    for catl in dcListSorted:
                        fin_ep_images = 'http://media0-starag.startv.in/r1/thumbs/PCTV/'+str(catl['urlPictures'])[-2:]+'/'+str(catl['urlPictures'])+'/PCTV-'+str(catl['urlPictures'])+'-vl.jpg'
                        addDir(str(catl['episodeNumber']) + '-' + catl['episodeTitle'], '&categoryId=' + str(catl['contentId']), 4, fin_ep_images, language, catl['contentId'], catl['duration'], True, catl['episodeNumber'])
                    xbmcplugin.endOfDirectory(int(sys.argv[1]))
        else:
            print ('Unknown error')
            xbmcgui.Dialog().ok("11111", 'Unknown error')

def get_cdn(name, url, language, mode, category):
    cwd = ADDON.getAddonInfo('path')
    url = cdnurl.format(category)
    postData = url
    print ('get_cdn url=' + postData)
    data = make_request(postData)
    result = json.loads(data)

    if "resultCode" in result:
        if 'OK' == result['resultCode']:
            if "resultObj" in result:
                return result['resultObj']['src']
        else:
            print ('Unknown error')
            xbmcgui.Dialog().ok("11111", 'Unknown error')


##
# Plays the video. Called when the id is 2.
##
def play_video(name, url, language, mode, category):

    location = xbmc.getIPAddress()

    cdn_response = get_cdn(name, url, language, mode, category)
    #print ('play_video: ' + cdn_response)
    movie_link = ""
    movie_link = cdn_response

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()

    listitem = xbmcgui.ListItem(name)
    playlist.add(urllib.unquote(movie_link), listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)

def make_request(url):
    try:
        headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding':'gzip, deflate, sdch', 'Connection':'keep-alive', 'User-Agent':'AppleCoreMedia/1.0.0.12B411 (iPhone; U; CPU OS 8_1 like Mac OS X; en_gb)', 'X-Forwarded-For': ipaddress}
        response = s.get(url, headers=headers, cookies=s.cookies)
        data = response.text
        return data
    except urllib2.URLError, e:    # This is the correct syntax
        print e

def get_video_url(name, url, language, mode, category):
    videos = []
    params = []
    manifest1 = cdn_response = get_cdn(name, url, language, mode, category)
    manifest1 = manifest1.replace('http://','https://')
    manifest1 = manifest1.replace('/z/','/i/')
    manifest1 = manifest1.replace('manifest.f4m', 'master.m3u8')
    
    if manifest1:
        manifest_url = make_request(manifest1)
        if manifest_url:

            matchlist2 = re.compile("BANDWIDTH=(\d+).*x720[^\n]*\n([^n].*)").findall(str(manifest_url))
            if matchlist2:
                for (size, video) in matchlist2:
                    if size:
                        size = int(size)
                    else:
                        size = 0
                    videos.append( [size, video] )
        else:
            videos.append( [-2, match] )
    
    videos.sort(key=lambda L : L and L[0], reverse=True)
    cookieString = ""
    c = s.cookies
    i = c.items()
    for name2, value in i:
        cookieString+= name2 + "=" + value + ";"
    print 'MIH-cookieString is', cookieString
    
    raw3_start = videos[0][1]
    high_video = raw3_start+"|Cookie="+cookieString+"&X-Forwarded-For="+ipaddress
    print ('MIH-get_video_url >' + 'high_video is: ' + high_video)
    print ('MIH-get_video_url >' + 'high_video name: ' + name)
    
    listitem =xbmcgui.ListItem(name)
    listitem.setProperty('mimetype', 'video/x-msvideo')
    listitem.setPath(high_video)
    
    # xbmc.executebuiltin("PlayMedia(%s)"%high_video)
    ##xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
    # xbmc.Player().play(high_video, listitem)
    # sys.exit()
    
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()

    playlist.add(urllib.unquote(high_video), listitem)
    xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(playlist)
    
##
# Displays the setting view. Called when mode is 12
##
def display_setting(name, url, language, mode):
    ADDON.openSettings()

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

#########################################################
# Function  : GUIEditExportName                         #
#########################################################
# Parameter :                                           #
#                                                       #
# name        sugested name for export                  #
#                                                       # 
# Returns   :                                           #
#                                                       #
# name        name of export excluding any extension    #
#                                                       #
#########################################################
def GUIEditExportName(name):
    exit = True 
    while (exit):
          kb = xbmc.Keyboard('default', 'heading', True)
          kb.setDefault(name)
          kb.setHeading("Enter the search term")
          kb.setHiddenInput(False)
          kb.doModal()
          if (kb.isConfirmed()):
              name = kb.getText()
              exit = False
          else:
              GUIInfo(2,__language__(33225)) 
    return(name)

def addLink(name,url,iconimage):
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, lang='', catgory=564, duration=0, isPlayable=False, episode=0):
    try:
        name = unicode(name).decode("utf-8")
        print ('addDir-mode=' + str(mode) + ',url=' + url + ',catgory=' + str(catgory))
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&lang="+urllib.quote_plus(lang)+"&category="+str(catgory)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Duration": duration, "episode": episode } )
        if 'vl.jpg' in iconimage:
            image2 = iconimage.replace('vl.jpg', 'hl.jpg')
            liz.setArt({'fanart': image2})
        else:
            liz.setArt({'fanart': iconimage})
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=not isPlayable)
        return ok
    except:
        pass

params=get_params()
url=''
name=''
mode=0
language=''
category = 564

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass

try:
    name=urllib.unquote_plus(params["name"])
except:
    pass

try:
    mode=int(params["mode"])
except:
    pass

try:
    category=int(params["category"])
except:
    pass

try:
    language=urllib.unquote_plus(params["lang"])
except:
    pass

print ('Parsed category=' + str(category))

# Modes
# 0: The main Categories Menu. Selection of language
# 1: For scraping the movies from a list of movies in the website
# 2: For playing a video
# 3: The Recent Section
# 4: The top viewed list. like above
# 5: The top rated list. Like above
# 6: Search options
# 7: Sub menu
# 8: A-Z view.
# 9: Yearly view
# 10: Actor view
# 11: Director view
# 12: Show Addon Settings

function_map = {}
function_map[0] = list_channels #main_categories 
function_map[1] = list_channels_content #get_movies_and_music_videos
function_map[2] = list_show_chapters #play_video
function_map[3] = list_show_chapter_episodes #content #show_recent_sections
function_map[4] = get_video_url #play_video #show_featured_movies
function_map[5] = '' #show_top_rated_options
function_map[6] = '' #show_search_box
function_map[7] = '' #inner_categories
function_map[8] = '' #show_A_Z
function_map[9] = '' #show_list
function_map[10] = '' #show_list
function_map[11] = '' #show_list
function_map[12] = '' #display_setting
function_map[13] = '' #display_BluRay_listings
function_map[14] = '' #list_music_videos
function_map[15] = '' #list_movies_from_JSON_API
function_map[16] = '' #mp3_menu

function_map[mode](name, url, language, mode, category)
s.close()
