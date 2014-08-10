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

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,xbmcvfs
import os,sys
from resources.common_variables import *
from resources.utilities import *
from resources.directory import *
from resources.webutils import *
from resources.ondemand import *
from resources.live import *
from resources.arquivo import *
from resources.resolver import *
from resources.favourites import *

def main_menu():
	addDir('[COLOR blue][B]Em directo[/B][/COLOR]','Volta menu','', 'rtp',1)
	addDir('[B]- Canais Tv/Rádio[/B]','http://www.rtp.pt/play/direto',1,os.path.join(artfolder,'tvradio_icon.png'),1)
	addDir('[COLOR blue][B]Emissões[/B][/COLOR]','Volta menu','', 'rtp',1)
	addDir('[B]- Mais recentes[/B]','http://www.rtp.pt/play/ondemand',2, os.path.join(artfolder,'maisrecentes.png'),1)
	addDir('[B]- Mais populares[/B]','http://www.rtp.pt/play/sideWidget.php?type=popular&place=HP',3,os.path.join(artfolder,'maispopulares.png'),11)
	addDir('[B]- Listar[/B]','http://www.rtp.pt/play/ondemand',4,os.path.join(artfolder,'lista.png'),1)
	addDir('[B]- Pesquisar[/B]','http://www.rtp.pt/play/ondemand',5,os.path.join(artfolder,'pesquisa.png'),1)
	addDir('[COLOR blue][B]Programas[/B][/COLOR]','Volta menu','', 'rtp',1)
	addDir('[B]- Favoritos[/B]','http://www.rtp.pt/play/ondemand',6,os.path.join(artfolder,'programasaz.png'),1)
	addDir('[B]- De A-Z[/B]','http://www.rtp.pt/play/ondemand',7,os.path.join(artfolder,'programasaz.png'),1)
	addDir('[B]- Pesquisar[/B]','http://www.rtp.pt/play/ondemand',8,os.path.join(artfolder,'pesquisa.png'),1)
	addDir('[COLOR blue][B]Arquivo RTP[/B][/COLOR]','Volta menu','', 'rtp',1)
	addDir('[B]- Colecções[/B]','http://www.rtp.pt/arquivo/colecoes',9,os.path.join(artfolder,'arquivo.png'),1)
	xbmc.executebuiltin("Container.SetViewMode(501)")

def radio_tv_menu(name):
	if 'recentes' in name:
		mode = 3
	elif 'A-Z' in name:
		mode = 13
	addDir('[B]- Emissões da TV[/B]','http://www.rtp.pt/play/recent.php?type=TV',mode, addonfolder + artfolder + 'tv.png',2)
	addDir('[B]- Emissões da rádio[/B]','http://www.rtp.pt/play/recent.php?type=RADIO',mode, addonfolder + artfolder + 'radio.png',2)
	
def az_menu(name):
	alphabet = ['0-9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	if 'TV' in name:
		tipo = 'tv'
	elif 'rádio' in name:
		tipo = 'radio'
	else: sys.exit(0)
	for letter in alphabet:
		addDir('[B]'+ letter +'[/B]','http://www.rtp.pt/play/az.php?letter='+letter+'&channelType='+tipo,15, addonfolder + artfolder + 'programasaz.png',len(alphabet))
	

def menu_emissao():
	addDir('[B]- Por canal[/B]','http://www.rtp.pt/play/ondemand',12, addonfolder + artfolder + 'por_canal.png',2)
	addDir('[B]- Por tema[/B]','http://www.rtp.pt/play/ondemand',12, addonfolder + artfolder + 'por_tema.png',2)
	
def emissao_lista(name,url):
	try:
		page_source = abrir_url(url)
	except:
		page_source = ''
		msgok('RTP Play','Não conseguiu abrir o site / Check your internet connection')
	if page_source:
		if 'canal' in name:
			regex = '<a href="/play/procura\?p_c=(.+?)" title=".+?">(.+?)</a>'
			link_part = '/play/procura?p_c='
		elif 'tema' in name:
			regex = '<a href="/play/procura\?p_t=(.+?)" title=".+?">(.+?)</a>'
			link_part = '/play/procura?p_t='
		match=re.compile(regex).findall(page_source)
		for canal,titulo in match:
			titulo = title_clean_up(titulo)
			addDir('[B]' + titulo + '[/B]',base_url + link_part + canal,14, addonfolder + artfolder + 'tree.png',len(match))
	else:
		sys.exit(0)
		

"""

Addon navigation is below
 
"""	
			
            
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


params=get_params()
url=None
name=None
mode=None
iconimage=None
plot=None

try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try: plot=urllib.unquote_plus(params["plot"])
except: pass

print ("Mode: "+str(mode))
print ("URL: "+str(url))
print ("Name: "+str(name))
print ("iconimage: "+str(iconimage))


if mode==None or url==None or len(url)<1: main_menu()
elif mode==1: radiotv_channels(url)
elif mode==2: radio_tv_menu(name)
elif mode==3: list_episodes(url,plot)
elif mode==4: menu_emissao()
elif mode==5: pesquisa_emissoes()
elif mode==6: list_favourites()
elif mode==7: radio_tv_menu(name)
elif mode==8: pesquisa_programas()
elif mode==9: arquivo_coleccoes(url)
elif mode==10: listar_programas_arquivo(url)
elif mode==11: listar_episodios_arquivo(url)
elif mode==12: emissao_lista(name,url)
elif mode==13: az_menu(name)
elif mode==14: list_emissoes(url)
elif mode==15: list_tv_shows(name,url)
elif mode==16: list_episodes(url,plot)
elif mode==17: get_show_episode_parts(name,url,iconimage)

elif mode==19: add_favourite(name,url,iconimage,plot)
elif mode==20: remove_favourite(name)
elif mode==21: mark_as_watched(url)
elif mode==22: remove_watched_mark(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
