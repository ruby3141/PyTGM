import collections
import itertools
import random

def TiRandomizer(seed): #Powered by DrPete from TetrisConcept.net
	bag = ['j', 'i', 'z', 'l', 'o', 't', 's'] * 5
	history = collections.deque(['s', 'z', 's', 'z'])
	drought_order = ['j', 'i', 'z', 'l', 'o', 't', 's']
	count = { 'j' : 0, 'i' : 0, 'z' : 0, 'l' : 0, 'o' : 0, 't' : 0, 's' : 0 }
	rng = random.Random()
	rng.seed(seed)

	# first piece is special
	first = rng.choice(['j','i','l','t'])
	history.popleft()
	history.append(first)
	yield first

	while True:
		for roll in range(6):
			i = rng.randint(0, 34)
			piece = bag[i]
			if piece not in history:
				break
			if roll < 5:
				bag[i] = drought_order[0]
		count[piece] += 1
		emulate_bug = all ([piece == drought_order[0], roll > 0, 0 not in count.values()])
		if not emulate_bug:
			bag[i] = drought_order[0]
		drought_order.remove(piece)
		drought_order.append(piece)
		history.popleft()
		history.append(piece)
		yield piece

class PosList(list): #disable negative index of array to handle sth with exception
	def __getitem__(self, ind):
		if type(ind) == int and ind < 0:
			raise TypeError("poslist index must be positive integer, not nevative.")
		return super(PosList, self).__getitem__(ind)

class Model:
	piecedict = {
		'':((),(),(),()),
		'j':(((0,0,0),(1,1,1),(0,0,1)),((0,1,1),(0,1,0),(0,1,0)), \
			((0,0,0),(1,0,0),(1,1,1)),((0,1,0),(0,1,0),(1,1,0))),
		'i':(((0,0,0,0),(2,2,2,2),(0,0,0,0),(0,0,0,0)), \
			((0,0,2,0),(0,0,2,0),(0,0,2,0),(0,0,2,0))),
		'z':(((0,0,0),(3,3,0),(0,3,3)),((0,0,3),(0,3,3),(0,3,0))),
		'l':(((0,0,0),(4,4,4),(4,0,0)),((0,4,0),(0,4,0),(0,4,4)), \
			((0,0,0),(0,0,4),(4,4,4)),((4,4,0),(0,4,0),(0,4,0))),
		'o':(((0,0,0),(0,5,5),(0,5,5)),),
		't':(((0,0,0),(6,6,6),(0,6,0)),((0,6,0),(0,6,6),(0,6,0)), \
			((0,0,0),(0,6,0),(6,6,6)),((0,6,0),(6,6,0),(0,6,0))),
		's':(((0,0,0),(0,7,7),(7,7,0)),((7,0,0),(7,7,0),(0,7,0)))}
	speedunit = 65536
	speedtuples = \
		[(0, 1024), (30, 1536), (35, 2048), (40, 2560), (50, 3072), (60, 4096), (70, 8192),\
		(80, 12288), (90, 16384), (100, 20480), (120, 24576), (140, 28672), (160, 32768),\
		(170, 36864), (200, 1024), (220, 8192), (230, 16384), (233, 24576), (236, 32768),\
		(239, 40960), (243, 49152), (247, 57344), (251, 65536), (300, 131072), (330, 196608),\
		(360, 262144), (400, 3270680), (420, 262144), (450, 196608), (500, 1310720)]
	#ARE, Line Clear ARE, DAS, Lock Delay, Line Clear Delay
	vartuples = \
		[(0,25,25,14,30,40),(500,25,25,8,30,25),(600,25,16,8,30,16),\
		(700,16,12,8,30,12),(800,12,6,8,30,6),(900,12,6,6,17,6),\
		(1000,6,6,6,17,6),(1100,5,5,6,15,6),(1200,4,4,6,15,6)]

	def __init__(self, playerid, seed):
		self.randomizer = TiRandomizer(seed)
		self.stack = PosList()
		for _ in range(21):
			self.stack.append(PosList([0]*10))
		self.next = collections.deque([]) #next[0] is current piece
		self.hold = '';
		for _ in range(4):
			self.next.append(next(self.randomizer))
		self.piecepos = [20,3,0] #col, row, rotation. this is initial spawn value.
		self.dropcounter = 0 #drop one line per gravunit. -1 if piece is on ground state
		self.speedvar = [1024, 25, 25, 14, 30, 40]
		self.vg = self.setvar()
		self.sg = self.setspeed()
		#same order with speedtuples. first value is current speed.
		self.level = 1
		self.indicatedlevel = 1
		self.state = ["init"]
		self.tick = self.processor()

	def checkpoint(self, point):
		try:
			if self.stack[point[0]][point[1]] != 0:
				return False
			else:
				return True
		except:
			return False

	def colcheck(self, piece, piecepos):
		arrsize = len(self.piecedict[piece][piecepos[2]])
		return all([self.checkpoint((piecepos[0] - c, piecepos[1] + l)) \
			for c, l in itertools.product(range(arrsize), range(arrsize)) \
			if self.piecedict[piece][piecepos[2]][c][l] != 0])

	def isdropable(self, piece, piecepos):
		temppos = piecepos[:]; temppos[0] -= 1
		return self.colcheck(piece, temppos)

	def rotate(self, direction):
		temppos = self.piecepos[:]
		#exceptional rule for l, j, t prevent from rotating
		if self.next[0] in ('l', 'j', 't') and \
			temppos[2] in (0, 2) and self.checkpoint([temppos[0], temppos[1] + 1]) == False:
			return False
		elif (self.next[0] in ('l', 'j') and \
			((temppos[2] == 0 and self.checkpoint([temppos[0]- 2,temppos[1] + 1]) == False) or \
			(temppos[2] == 2 and self.checkpoint([temppos[0] - 1, temppos[1] + 1]) == False))):
			if (self.next[0] == 'j' and self.checkpoint([temppos[0], temppos[1] + 2]) == True) \
			or (self.next[0] == 'l' and self.checkpoint([temppos[0], temppos[1]]) == True):
				return False
		temppos[2] += direction; temppos[2] %= len(self.piecedict[self.next[0]])
		if self.colcheck(self.next[0], temppos):
			self.piecepos = temppos; return True
		#Wallkick
		temppos[1] = self.piecepos[1] + 1
		if self.colcheck(self.next[0], temppos):
			self.piecepos = temppos; return True
		temppos[1] = self.piecepos[1] - 1
		if self.colcheck(self.next[0], temppos):
			self.piecepos = temppos; return True
		#Additional Wallkick and Floorkick for I piece
		if self.next[0] == 'i':
			temppos[1] = self.piecepos[1] + 2
			if self.colcheck(self.next[0], temppos):
				self.piecepos = temppos; return True
			if self.isdropable(self.next[0], self.piecepos):
				#Floorkick of I set its lock delay to 0
				temppos[1] = self.piecepos[1]; temppos[0] = self.piecepos[0] + 1
				if self.colcheck(self.next[0], temppos):
					self.piecepos = temppos; self.speedvar[4] = 0; return True
				temppos[0] = self.piecepos[0] + 2
				if self.colcheck(self.next[0], temppos):
					self.piecepos = temppos; self.speedvar[4] = 0; return True
		#Floorkick for T piece
		if self.next[0] == 't':
			temppos[1] = self.piecepos[1]; temppos[0] = self.piecepos[0] + 1
			if self.colcheck(self.next[0], temppos):
				self.piecepos = temppos; return True
		return False

	def setvar(self):
		curvar = self.vartuples[0]
		for vartuple in self.vartuples:
			while vartuple[0] > self.level:
				self.speedvar = self.speedvar[0:1]+list(curvar[1:])
				yield
			curvar = vartuple
		while True:
			self.speedvar = self.speedvar[0:1]+list(curvar[1:])
			yield

	def setspeed(self):
		curspeed = self.speedtuples[0]
		for speedtuple in self.speedtuples:
			while speedtuple[0] > self.level:
				self.speedvar = list(curspeed[1:]) + self.speedvar[1:]
				yield
			curspeed = speedtuple
		while True:
			self.speedvar = list(curspeed[1:]) + self.speedvar[1:]
			yield

	def setspeedvar(self):
		next(self.vg)
		next(self.sg)

	def holdpiece(self):
		try:
			if self.holdtimer == self.level:
				return False
		except:
			pass
		self.holdtimer = self.level
		if self.hold == '':
			self.state.append('hold')
			self.hold = self.next[0]
			self.next.popleft()
			self.next.append(next(self.randomizer))
		else:
			self.hold, self.next[0] = self.next[0], self.hold
		self.piecepos = [20,3,0]

	def setpiece(self):
		for c, col in enumerate(self.piecedict[self.next[0]][self.piecepos[2]]):
			for r, row in enumerate(col):
				if row != 0:
					self.stack[self.piecepos[0]-c][self.piecepos[1]+r] = row
		self.next[0] = ''

	def stackcheck(self):
		cline = []
		for i, row in enumerate(self.stack):
			if all(block > 0 for block in row):
				self.stack[i] = (0,0,0,0,0,0,0,0,0,0)
				cline.append(i)
		return cline

	def processor(self):
		self.tickcount = 0
		delaycounter = 0
		yield #for start
		while(True):
			#Spawn phase
			linermd = False
			self.setspeedvar()
			self.piecepos = [20, 3, 0]
			if not self.colcheck(self.next[0], self.piecepos):
				break
			#Initial process phase
			self.state = ['spawn']
			intup = yield #intup is tuple of four value, (left/right),(up/down),(b/a),(hold)
			self.tickcount += 1
			if intup[3] > 0:
				self.holdpiece()
			if intup[2] != 0:
				self.rotate(1 if intup[2] > 0 else -1)
			if intup[1] < 0:
				self.dropcounter += self.speedunit * 20
			if self.isdropable(self.next[0], self.piecepos):
				self.dropcounter += self.speedvar[0]
			while self.dropcounter >= self.speedunit and \
				self.isdropable(self.next[0], self.piecepos):
				self.dropcounter -= self.speedunit
				self.piecepos[0] -= 1
			if not self.isdropable(self.next[0], self.piecepos):
				self.dropcounter = 0
				delaycounter += 1
			#Process phase
			while(True):
				self.state = ['process']
				intup = yield
				self.tickcount += 1
				if intup[3] == 1:
					self.holdpiece()
				if abs(intup[2]) == 1:
					self.rotate(intup[2])
				if abs(intup[0]) == 1 or abs(intup[0]) >= self.speedvar[3]:
					temppos = self.piecepos[:]; temppos[1] += intup[0] // abs(intup[0])
					if self.colcheck(self.next[0], temppos):
						self.piecepos = temppos
				if intup[1] < 0:
					self.dropcounter += self.speedunit * 20
				if self.isdropable(self.next[0], self.piecepos):
					self.dropcounter += self.speedvar[0]
				while self.dropcounter >= self.speedunit and \
					self.isdropable(self.next[0], self.piecepos):
					self.dropcounter -= self.speedunit
					self.piecepos[0] -= 1
					delaycounter = 0
				if not self.isdropable(self.next[0], self.piecepos):
					self.state.append('lockdelay')
					self.dropcounter = 0
					delaycounter += 1
				if (not self.isdropable(self.next[0], self.piecepos) and intup[1] > 0) \
					or delaycounter >= self.speedvar[4]:
					break
			self.setpiece()
			delaycounter = 0
			cline = self.stackcheck()
			#Line Clear Delay + Line Clear ARE
			if cline != []:
				self.state = ['lineclear'] + cline
				while delaycounter <= self.speedvar[5]:
					yield
					self.tickcount += 1
					delaycounter += 1
				try:
					while True:
						self.stack.remove((0,0,0,0,0,0,0,0,0,0))
						self.stack.append(PosList([0]*10))
						self.level += 1
						self.linermd = True
				except:
					pass
				delaycounter = 0
				self.state = ['are','lineclear']
				while delaycounter <= self.speedvar[2]:
					yield
					self.tickcount += 1
					delaycounter += 1
			#ARE without Line Clear
			else:
				self.state = ['are']
				while delaycounter <= self.speedvar[1]:
					yield
					self.tickcount += 1
					delaycounter += 1
			if self.level % 100 != 99 and not linermd:
				self.level += 1
			self.next.popleft()
			self.next.append(next(self.randomizer))
			print("level: {}".format(self.level))
		return "Game Over"
