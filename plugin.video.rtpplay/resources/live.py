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
import xbmc,xbmcgui,xbmcplugin,xbmcaddon,sys,os,re
from webutils import *
from common_variables import *
from directory import *

def radiotv_channels(url):
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''
		msgok(translate(30001),translate(30018))
	if page_source:
		#Tv channels
		match=re.compile('<a  id=".+?" title="(.+?)" href="(.+?)"><img src="(.+?)"').findall(page_source)
		totaltv = len(match)
		for titulo,url2,img in match:
			titulo = title_clean_up(titulo)
			stream_url = grab_live_stream_url(base_url + url2)
			addLink('[B][COLOR blue]' + titulo.replace('Direto - ','') + '[/B][/COLOR]',stream_url,img,totaltv)
		#Radio channels
		match=re.compile('<a id=".+?" title="(.+?)" href="(.+?)"><img src="(.+?)"').findall(page_source)
		totalradio = len(match)
		for titulo,url2,img in match:
			titulo = title_clean_up(titulo)
			stream_url = grab_live_stream_url(base_url + url2)
			addLink('[B][COLOR blue]' + titulo.replace('Direto - ','') + '[/B][/COLOR]',stream_url,img,totalradio)
		
		xbmc.executebuiltin("Container.SetViewMode(500)") #Verificar
	else:
		sys.exit(0)


def grab_live_stream_url(url):
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''
		msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if page_source:
		if re.search('mms:', page_source):
        		match=re.compile('\"file\": \"(.+?)\",\"streamer\": \"(.+?)\"').findall(page_source)
        		try:
        			url2 = match[0][1] + match[0][0]
        			return url2
        		except: pass
    		else:	
    			#Heuristic rules to automatically find the best stream type for each platform    		
			type_stream=selfAddon.getSetting('tipostr')		
			if type_stream == '0':
				if xbmc.getCondVisibility('system.platform.OSX'): versao = 'rtmp'
				elif xbmc.getCondVisibility('system.platform.IOS'): versao = 'm3u8'
				elif xbmc.getCondVisibility('system.platform.ATV2'): versao = 'm3u8'		
				elif xbmc.getCondVisibility('system.platform.Windows'): versao = 'rtmp'
				elif xbmc.getCondVisibility('system.platform.linux'):
					if 'armv6' in os.uname()[4]: versao = 'm3u8'
					else: versao = 'm3u8'
			elif type_stream == '1': versao = 'rtmp'
			elif type_stream == '2': versao = 'm3u8'
			#Scrape the page source for each type of stream	
			if versao == 'rtmp':
				match=re.compile('\"file\": \"(.+?)\",\"application\": \"(.+?)\",\"streamer\": \"(.+?)\"').findall(page_source)
        			url2 = 'rtmp://' + match[0][2] +'/' + match[0][1] + '/' + match[0][0] + ' swfUrl=' + player + linkpart
        			return url2
        		else:
				match=re.compile('\"smil\":\"(.+?)\"').findall(page_source)
        			url2 = match[0]
        			return url2
	else:
		sys.exit(0)
