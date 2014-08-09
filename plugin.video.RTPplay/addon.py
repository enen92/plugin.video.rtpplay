#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author enen92 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,xbmcvfs
import os,sys
from resources.common_variables import *
from resources.utilities import *
from resources.directory import *
from resources.webutils import *
from resources.ondemand import *
from resources.live import *
from resources.arquivo import *



def main_menu():
	addDir('[COLOR blue][B]EM DIRECTO[/B][/COLOR]','Volta menu',5, 'rtp',11)
	addDir('[B]- Canais Tv/Rádio[/B]','http://www.rtp.pt/play/direto',4,os.path.join(artfolder,'tvradio_icon.png'),11)
	addDir('[COLOR blue][B]EMISSÕES[/B][/COLOR]','Volta menu',5, 'rtp',11)
	addDir('[B]- Mais recentes[/B]','http://www.rtp.pt/play/ondemand',8, os.path.join(artfolder,'maisrecentes.png'),11)
	addDir('[B]- Mais populares[/B]','http://www.rtp.pt/play/sideWidget.php?type=popular&place=HP',10,os.path.join(artfolder,'maispopulares.png'),11)
	addDir('[B]- Listar[/B]','http://www.rtp.pt/play/ondemand',16,os.path.join(artfolder,'lista.png'),11)
	addDir('[B]- Pesquisar[/B]','http://www.rtp.pt/play/ondemand',21,os.path.join(artfolder,'pesquisa.png'),11)
	addDir('[COLOR blue][B]PROGRAMAS[/B][/COLOR]','Volta menu',5, 'rtp',11)
	addDir('[B]- Favoritos[/B]','http://www.rtp.pt/play/ondemand',25,os.path.join(artfolder,'programasaz.png'),11)
	addDir('[B]- De A-Z[/B]','http://www.rtp.pt/play/ondemand',8,os.path.join(artfolder,'programasaz.png'),11)
	addDir('[B]- Pesquisar[/B]','http://www.rtp.pt/play/ondemand',22,os.path.join(artfolder,'pesquisa.png'),11)
	addDir('[COLOR blue][B]ARQUIVO RTP[/B][/COLOR]','Volta menu',5, 'rtp',11)
	addDir('[B]- Coleccoes[/B]','http://www.rtp.pt/arquivo/colecoes',27,os.path.join(artfolder,'arquivo.png'),11)
	xbmc.executebuiltin("Container.SetViewMode(501)")

def radio_tv_menu(name):
	if 'recentes' in name:
		mode = 10
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
	addDir('[B]- Por canal[/B]','http://www.rtp.pt/play/ondemand',17, addonfolder + artfolder + 'por_canal.png',2)
	addDir('[B]- Por tema[/B]','http://www.rtp.pt/play/ondemand',17, addonfolder + artfolder + 'por_tema.png',2)

		
		
#####################################################
#               Site parsing functions              #
#####################################################

# Live Content


		
#On Demand Content
		
#This function parses the broadcast pages and show the results for channels and genre		
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
			addDir('[B]' + titulo + '[/B]',base_url + link_part + canal,19, addonfolder + artfolder + 'tree.png',len(match))
	else:
		sys.exit(0)		
			
		


                



#programa_programas(urltmp)



def play_lista(url,name):
	dp = xbmcgui.DialogProgress()
	dp.create("RTP Play",'Modo playlist')
	dp.update(0)
	playlist = xbmc.PlayList(1)
	playlist.clear()
	link2 = abrir_url(url)
	if re.search('mms:', link2):
		match=re.compile('\"file\": \"(.+?)\",\"streamer\": \"(.+?)\"').findall(link2)
		url2 = match[0][1] + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 1[/B]',url2,'')
	elif re.search('.flv', link2):
        	match=re.compile('"file": "(.+?)","image": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][3] +'/' + match[0][2] + ' playpath=flv:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 1[/B]',url2,'')
	elif re.search('.*mp4', link2):
		match=re.compile('"file": "(.+?)","image": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][3] +'/' + match[0][2] + ' playpath=mp4:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 1[/B]',url2,'')
	elif re.search('mp3'):
		match=re.compile('"file": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][2] +'/' + match[0][1] + ' playpath=mp3:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 1[/B]',url2,'')
	match = re.compile('.*href=\'(.+?)\'><b>Parte</b>2').findall(link2)
	link2 = abrir_url(base_url + match[0])
	if re.search('mms:', link2):
		match=re.compile('\"file\": \"(.+?)\",\"streamer\": \"(.+?)\"').findall(link2)
		url2 = match[0][1] + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 2[/B]',url2,'')
	elif re.search('.flv', link2):
        	match=re.compile('"file": "(.+?)","image": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][3] +'/' + match[0][2] + ' playpath=flv:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 2[/B]',url2,'')
	elif re.search('.*mp4', link2):
		match=re.compile('"file": "(.+?)","image": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][3] +'/' + match[0][2] + ' playpath=mp4:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 2[/B]',url2,'')
	elif re.search('mp3'):
		match=re.compile('"file": "(.+?)","application": "(.+?)","streamer": "(.+?)"').findall(link2)
		url2 = 'rtmp://' + match[0][2] +'/' + match[0][1] + ' playpath=mp3:' + match[0][0]
		liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage='')
	        liz.setInfo('Video', {})
	        liz.setProperty('mimetype', 'video')                
		playlist.add(url2, liz)
		addLink(name + '[B] - Parte 2[/B]',url2,'')
	dp.update(1, 'A adicionar à playlist.')
	if dp.iscanceled(): return
        dp.close()
        xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        xbmcPlayer.play(playlist)

def FAVORITOS_PROGRAMAS():
	favpath=os.path.join(datapath,'Favourites')
	programafav=os.path.join(favpath,'Programa')
	print programafav
	try:
		programasdircontents=os.listdir(programafav)
	except:
		programasdircontents=None
 
	if programasdircontents == None:
		xbmc.executebuiltin("XBMC.Notification("+"RTP Play"+","+"Nao tem programas favoritos"+","+"6000"+","")")
	else:
		print programasdircontents
		i=0
		while i < len(programasdircontents):
			try:
				print programafav + programasdircontents[i]
				f = open(programafav + '/'+ programasdircontents[i], "r")
				string = f.read() 
				print string
				match = re.compile('(.+?)\|(.+?)\|(.+?)\|').findall(string)
				print match
				for name, url, img in match:
					addDir_programa('[B][COLOR blue]' + name + '[/B][/COLOR]',url,10,img,'programa')	
				f.close()
				i += 1
			except:
				i += 1
				pass
			

def REMOVER_PROGRAMAS_FAVORITO(name):
	print name
	savepath = programafav
	NewFavFile=os.path.join(savepath,name.lower()+'.txt')
	print NewFavFile
	os.remove(NewFavFile)
	xbmc.executebuiltin("XBMC.Notification("+"RTP Play"+","+"Programa removido dos favoritos"+","+"6000"+","")")
	xbmc.executebuiltin("XBMC.Container.Refresh")

############################################################################################################################



def ADD_TO_FAVOURITES(name,url,iconimage,checker):
	print 'Adicionando aos favoritos: name: %s, tipo: %s, url: %s' % (name, checker, url)
	favpath=os.path.join(datapath,'Favourites')
	emissaofav=os.path.join(favpath,'Emissao')
	programafav=os.path.join(favpath,'Programa')

	try:
		os.makedirs(emissaofav)
	except:
		pass
	try:
		os.makedirs(programafav)
	except:
		pass
	if checker == 'emissao':
		savepath = emissaofav
	elif checker == 'programa':
		savepath = programafav
	
	name = name.replace('[b]','')
	name = name.replace('[/b]','')
	name = name.replace('[color blue]','')
	name = name.replace('[/color]','')
	print 'o nome e',name
	NewFavFile=os.path.join(savepath,name+'.txt')
	if not os.path.exists(NewFavFile):
		favcontents=name+'|'+url+'|'+iconimage+'|'
		save(NewFavFile,favcontents)
		xbmc.executebuiltin("XBMC.Notification("+name+","+"adicionado aos favoritos"+","+"6000"+","")")
		xbmc.executebuiltin("XBMC.Container.Refresh")
	else:
		print 'Aviso - favorito ja existe'
		xbmc.executebuiltin("XBMC.Notification("+name+","+"ja esta nos favoritos"+","+"6000"+","")")


             
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


def save(filename,contents):  
     fh = open(filename, 'w')
     fh.write(contents)  
     fh.close()


params=get_params()
url=None
name=None
mode=None
checker=None
iconimage=None
plot=None

try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: checker=urllib.unquote_plus(params["checker"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try: plot=urllib.unquote_plus(params["plot"])
except: pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Checker: "+str(checker)
print "iconimage: "+str(iconimage)
print "plot: "+str(plot) #a remover daqui

if mode==None or url==None or len(url)<1: main_menu()
       
elif mode==1:
        print ""+url
        INDEX(url)
        
elif mode==2:
        print ""+url
        VIDEOLINKS(url,name)

elif mode==3:
        LIVEMENU()

elif mode==4: radiotv_channels(url)

elif mode==5:
        print ""
        ONDEMANDMENU()

elif mode==6:
        print ""
        RECOMENDADOS(url)

elif mode==7:
        print ""
        POPULARES(url)

elif mode==8: radio_tv_menu(name)

elif mode==9:
        print ""
        RECENTES(url)

elif mode==10: list_episodes(url,plot)



elif mode==12:
        print ""
        AZMENU()

elif mode==13: az_menu(name)

elif mode==14:
        print ""
        RADIOAZMENU()

elif mode==15:
        print ""
        list_tv_shows(name,url)

elif mode==16: menu_emissao()

elif mode==17: emissao_lista(name,url)

elif mode==18:
        print ""
        EMISSAOLISTARMENU_TEMA(url)

elif mode==19:	list_emissoes(url)

elif mode==20:
        print ""
	page_logical='1'
        programa_emissoes(url,page_logical)

elif mode==21:
        print ""
        pesquisa_emissoes()

elif mode==22:
        print ""
        pesquisa_programas()

elif mode==23:
        print ""
        play_lista(url,name)

elif mode==24:
        print ""
        ADD_TO_FAVOURITES(name,url,iconimage,checker)

elif mode==25:
	print ""
	FAVORITOS_PROGRAMAS()

elif mode==26:
	print ""
	REMOVER_PROGRAMAS_FAVORITO(name)

elif mode==27: arquivo_coleccoes(url)
elif mode==28: listar_programas_arquivo(url)
elif mode==29: listar_episodios_arquivo(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
