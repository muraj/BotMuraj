"""On the keyword 'pic' followed by a url of an image, this will display the ascii equivalent of the image."""
#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
from PIL import Image, ImageOps
from math import sqrt
import re
import sys
RULE=r'(?i)^pic\shttp\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?$'
PRIORITY=-20
COMMAND='PRIVMSG'
#GRADIENT='@8OCoc:. '
GRADIENT='.:coCO8@'
DIRECTED=True
# Via http://irssi.org/documentation/formats
colors=[	(255, 255, 255),	#White
		(0, 0, 0),		#Black (white is the new black)
		(0, 0, 255),		#Blue
		(0, 255, 0),		#Green
		(255, 128, 128),	#Light Red
		(255, 0, 0),		#Red
		(180, 0, 180),		#Purple
		(255, 180, 0),		#Orange
		(255, 255, 0),		#Yellow
		(128, 255, 128),	#LimeGreen
		(0, 200, 200),		#Cyan
		(0, 255, 255),		#LightCyan
		(128, 128, 255),	#LightBlue
		(255, 0, 255),		#LightMagenta
		(128, 128, 128),	#Grey
		(169, 169, 169)]	#LightGrey
def PROCESS(bot, args, text):
	global GRADIENT
	groups=re.search(r'(http\://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)+)( invert)?',text)
	if not groups:
		bot.log('Regex failed to return the url %s' % (text), 'error')
		return True
	else: url=groups.group(0)
	try:
		f=urllib.urlretrieve(url)
		im=Image.open(f[0])
		im.verify()
		im=Image.open(f[0])
	except:
		bot.mesg('Error retrieving & opening image, this may not be a supported format for PIL', args[1])
		return False
	im=im.resize((im.size[0],im.size[1]/2),Image.ANTIALIAS)	#For maintaining aspect ratio in ascii
	im.thumbnail((80,30), Image.ANTIALIAS)
	#-----
	origcolordata=list(im.getdata())
	colordata=[]
	if im.mode != 'L':
		for color in origcolordata:
			besti=0	#Default to white
			best_dist=0xFFFFFF
			for i,colorcheck in enumerate(colors):
				test=sqrt((color[0]-colorcheck[0])**2+(color[1]-colorcheck[1])**2+(color[2]-colorcheck[2])**2)
				if best_dist >= test:
					besti=i
					best_dist=test
			colordata.append(besti)
	else: colordata = [ 0 ] * len(origcolordata)
	#----
	im=ImageOps.grayscale(im)
	if im.mode != 'L':
		bot.mesg('Error converting image to grayscale...', args[1])
		return False
	data=list(im.getdata())
	out=''
	for i,p in enumerate(data):
		if i%im.size[0]==0:
			bot.mesg(out,args[1])
			out=''
		ch=GRADIENT[int((len(GRADIENT)-1)*p/255.0)]
		out=out+("%c%02d%c" % (chr(3), colordata[i], ch))
	return False
