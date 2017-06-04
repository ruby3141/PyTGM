import module.model as model
import module.view as view
import time
import sdl2
import sdl2.ext

class Ctrl:
	def __init__(self):
		self.viewer = view.View()
		self.model = model.Model('', time.time())
		self.framerate = 60;

	def run(self):
		sdl2.ext.init()
		window = sdl2.ext.Window("PyTGM Alpha", size=(1280, 720))
		window.show()
		next(self.model.tick)
		self.keydict = { #key mapped here
			sdl2.SDLK_a:[False,False, 0, -1], #left
			sdl2.SDLK_d:[False,False, 0, 1], #right
			sdl2.SDLK_w:[False,False, 1, -1], #up
			sdl2.SDLK_s:[False,False, 1, 1], #down
			sdl2.SDLK_l:[False,False, 2, 1], #A
			sdl2.SDLK_j:[False,False, 2, -1], #B
			sdl2.SDLK_i:[False,False, 3, 1]} #Hold
		self.intup = [0,0,0,0] #(left/right), (up/down), (b/a), (hold)
		running = True
		d = sdl2.timer.SDL_GetTicks()
		t = d
		tick = 0
		while running:
			tick += 1
			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT:
					running=False
					break
				if event.type == sdl2.SDL_KEYDOWN:
					if event.key.keysym.sym in self.keydict.keys():
						self.keydict[event.key.keysym.sym][0] = True
				if event.type == sdl2.SDL_KEYUP:
					if event.key.keysym.sym in self.keydict.keys():
						self.keydict[event.key.keysym.sym][0] = False
			for i, d in enumerate(self.intup):
				if d != 0:
					self.intup[i] += ( 1 if d > 0 else -1 )
			for key in self.keydict.keys():
				if self.keydict[key][0] != self.keydict[key][1]:
					if self.keydict[key][0]:
						self.intup[self.keydict[key][2]] = self.keydict[key][3]
					elif self.intup[self.keydict[key][2]] * self.keydict[key][3] > 0:
						self.intup[self.keydict[key][2]] = 0
					self.keydict[key][1] = self.keydict[key][0]
			self.model.tick.send(self.intup)
			#screen render will perform here
			window.refresh()
			d = sdl2.timer.SDL_GetTicks()
			sdl2.timer.SDL_Delay(max((tick*1000)//self.framerate-d+t, 0))
		return
