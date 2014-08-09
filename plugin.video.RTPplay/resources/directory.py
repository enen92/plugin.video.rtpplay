#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
 Author: enen92 

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
"""
import xbmc,xbmcplugin,xbmcaddon,xbmcgui,sys,os,urllib
from utilities import *
from common_variables import *


#Function to add a Show directory
def addprograma(name,url,mode,iconimage,number_of_items,information):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
	try: u +="&plot="+urllib.quote_plus(information["plot"])
	except: pass
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', os.path.join(artfolder,'fanart.png'))
	liz.setInfo( type="Video", infoLabels=information)
	contextMenuItems = []
	savepath = programafav
	name2 = name.replace('[B]','')
	name2 = name2.replace('[/B]','')
	name2 = name2.replace('[COLOR blue]','')
	name2 = name2.replace('[/COLOR]','')
	NewFavFile=os.path.join(savepath,removeNonAscii(name2.lower())+'.txt')
	if os.path.exists(NewFavFile):
		contextMenuItems.append(('Remover programa dos favoritos', 'XBMC.RunPlugin(%s?mode=26&name=%s&url=%s&iconimage=%s&checker=%s)' % (sys.argv[0], name2.lower(), url, iconimage, 'programa')))
	else:
		contextMenuItems.append(('Adicionar programa aos favoritos', 'XBMC.RunPlugin(%s?mode=24&name=%s&url=%s&iconimage=%s&checker=%s)' % (sys.argv[0], name, url, iconimage, 'programa')))
	liz.addContextMenuItems(contextMenuItems, replaceItems=True)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=number_of_items)
	return ok
	
#Function to add a Episode
def addepisode(name,url,mode,iconimage,number_of_items,information):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', os.path.join(artfolder,'fanart.png'))
	liz.setInfo( type="Video", infoLabels=information)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False,totalItems=number_of_items)
	return ok
	
#Function to add a video/audio Link
def addLink(name,url,iconimage,number_of_items):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', addonfolder + artfolder + 'fanart.png')
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False,totalItems=number_of_items)
	return ok

#Function to add a regular directory
def addDir(name,url,mode,iconimage,number_of_items,pasta=True):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', os.path.join(artfolder,'fanart.png'))
	liz.setInfo( type="Video", infoLabels={ "Title": name })
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=number_of_items)
	return ok
