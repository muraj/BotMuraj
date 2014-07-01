#!/bin/python
import sys
from re import sub as rsub
import WordSub, DefaultSubs
"""TODO: Bug with multi-sentence pattern/that/template(s)"""
if __name__ == "__main__":
	xml=['<?xml version=\'1.0\' encoding=\'ISO-8859-1\'?>','<aiml>']
	that=rsub(r'<[a-zA-Z\/][^>]*>','',sys.argv[1].upper())
	pattern=rsub(r'<[a-zA-Z\/][^>]*>','',sys.argv[2].upper())
	template=rsub(r'<[a-zA-Z\/][^>]*>','',sys.argv[3])

	subbers={}	#Do aiml default substitutions for best match.
	subbers['gender']=WordSub.WordSub(DefaultSubs.defaultGender)
	subbers['person']=WordSub.WordSub(DefaultSubs.defaultPerson)
	subbers['person2']=WordSub.WordSub(DefaultSubs.defaultPerson2)
	subbers['normal']=WordSub.WordSub(DefaultSubs.defaultNormal)
	for sub in subbers:
		that=subbers[sub].sub(that)
		pattern=subbers[sub].sub(pattern)

	xml.append('<category>')
	xml.append("<pattern>%s</pattern>" % pattern)
	if not that=='':
		xml.append("<that>%s</that>" % that)
	xml.append("<template>%s</template>" % template)
	xml.append('</category>')
	
	xml.append('</aiml>')
	f=open('learning.aiml','w')
	f.write('\n'.join(xml))
	f.flush()
	f.close()
