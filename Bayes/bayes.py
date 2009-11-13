import re, heapq, shelve
class Tokenizer:
	WORDREG = re.compile(r'(\w+)', re.UNICODE)
	#This is by no means a comprehensive list, but can help in reducing
	#the bucket sizes by a lot.
	COMMON = ['the', 'of', 'a', 'I', 'and', 'to', 'an', 'in', 'is', 'it', 
		'you', 'he', 'she', 'that', 'was', 'for', 'on', 'are', 'with', 'as',
		'his', 'her', 'they', 'be', 'at', 'have', 'this', 'from', 'or', 'had',
		'by', 'but', 'some', 'what', 'there', 'we', 'can', 'out', 'other',
		'all', 'were', 'your', 'when', 'up', 'use', 'how', 'each', 'which']
	COMMON_REGEX = [re.compile(r'(?i)\b'+c+r'\b',re.UNICODE) for c in COMMON]
	def tokenize(self, input):
		"""Returns a generator of words"""
		if type(input) != unicode: input=unicode(input, 'utf-8')
		input=input.lower()
		for r in self.COMMON_REGEX:
			input = r.sub('',input)
		else: input = re.sub(r'\b\d+\b','',input,re.UNICODE)
		return self.WORDREG.findall(input)
class Bayes:
	MEST = 1	# Rare word handling
	PEST = 0.1	# <- tune ?
	def __init__(self, tokenizer=Tokenizer):
		self.tokenizer = tokenizer()
		self.buckets = {}
		self.tokens = 0
	def train(self, topic, input):
		"""Train on the input"""
		if type(topic) == unicode: topic = topic.encode('utf-8')
		topic = topic.upper()
		for w in set(self.tokenizer.tokenize(input)):
			if not topic in self.buckets: self.buckets[topic]={}
			x=self.buckets[topic]
			x[w] = x.get(w,0) + 1
			self.buckets[topic] = x	#Due to how shelve works...
			self.tokens+=1
		if hasattr(self.buckets,'sync'): self.buckets.sync()
	def guess(self, input):
		"""Given the input as a string, return the best guess at the topic."""
		denom = 0.0
		Parg = {}
		words = set(self.tokenizer.tokenize(input))	#unique set of words
		for topic in self.buckets.iterkeys():	#TODO: Add m-estimate
			Pa = 1.0*len(self.buckets[topic]) / self.tokens
			Fw = [self.buckets[topic][w] for w in words if w in self.buckets[topic]]
			Pwa = 1.0*reduce(lambda x,y: x+y, Fw, self.MEST*self.PEST) / (len(self.buckets[topic]) + self.MEST)
			Parg[topic] = Pwa*Pa
			denom+=Parg[topic]
		ret=max(Parg, key=lambda x: Parg[x]/denom)
		return (ret, Parg[ret]/denom)
	def forget(self,input,topic):
		"""Forget input words for a given topic"""
		topic = topic.upper()
		input = input.lower()
		for w in self.tokenizer.tokenize(input):
			if w in self.buckets[topic]:
				del self.buckets[topic][w]
	def save(self, filename):
		"""Save the brain to a file, or if already loaded, sync it to same file"""
		if hasattr(self.buckets, 'sync'):
			self.buckets.sync()
			return
		sh=shelve.open(filename)
		for k,b in self.buckets.iteritems(): sh[k]=b
		sh.sync()
		sh.close()
	def load(self, filename):
		"""Load the brain"""
		if hasattr(self.buckets,'close'): self.buckets.close()
		self.buckets=shelve.open(filename)
		self.tokens=reduce(lambda x,y: x+len(self.buckets[y]), self.buckets, 0)
if __name__ == '__main__':	#Unit tests
	import glob, os
	training = glob.glob('*.txt')
	brain = Bayes()
	for fn in training:
		print 'Training on',os.path.basename(fn)[:-4]
		f = open(fn, 'r')
		for l in f:
			brain.train(os.path.basename(fn)[:-4],l)
		f.close()
	if os.path.exists('bayes.bay'): os.unlink('bayes.bay')
	brain.save('bayes.bay')
