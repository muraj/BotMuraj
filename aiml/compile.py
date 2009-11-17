if __name__ == '__main__':
	from Kernel import Kernel
	brain = Kernel()
	brain.learnFiles('standard/*.aiml')
	brain.saveBrain('IRCBot.brn')
