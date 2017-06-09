import sdl2
import sdl2.sdlimage as sdlimage
import sdl2.sdlttf as sdlttf
import sdl2.ext

class View:
	windowsize = (1024, 768)
	origin = (120,120)
	tsize = 24
	ssize = 12

	def __init__(self, model):
		self.model = model
		sdlttf.TTF_Init()
		self.window = sdl2.ext.Window("PyTGM Alpha", size=self.windowsize)
		self.renderer = sdl2.ext.SoftwareSpriteRenderSystem(self.window)
		self.sfactory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
		self.tspr = self.sfactory.from_color(0x00000000, size=(350, 650),
			masks=(0xff000000,0x00ff0000,0x0000ff00,0x000000ff))
		self.trds = sdl2.ext.Renderer(self.tspr)
		self.trds.blendmode = sdl2.SDL_BLENDMODE_BLEND
		self.tfactory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer = self.trds)
		self.trds.color = sdl2.ext.Color(255,255,255,0)
		self.trds.clear()
		self.loadtexture()
		self.window.show()
		self.render = self.draw()

	def loadtexture(self):
		self.blocktex = self.tfactory.from_image("./res/block.png")
		self.sblocktex = self.tfactory.from_image("./res/sblock.png")
		self.border = self.sfactory.from_image("./res/border.png")
		self.border.x, self.border.y = self.origin[0]-self.tsize, self.origin[1]
		self.mainfont = sdlttf.TTF_OpenFont(b"./res/mainfont.ttf",32)
		self.largefont = sdlttf.TTF_OpenFont(b"./res/mainfont.ttf",48)
		self.timertex = None
		self.leveltex = None

	def drawblock(self, pos, ptype):
		if ptype == 0:
			return
		else:
			ptype -= 1
			src = (ptype%4*self.tsize, ptype//4*self.tsize, self.tsize, self.tsize)
			dst = (pos[0], pos[1], self.tsize, self.tsize)
			self.trds.copy(self.blocktex, srcrect=src, dstrect=dst)

	def drawsblock(self, pos, ptype):
		if ptype == 0:
			return
		else:
			ptype -= 1
			src = (ptype%4*self.ssize, ptype//4*self.ssize, self.ssize, self.ssize)
			dst = (pos[0], pos[1], self.ssize, self.ssize)
			self.trds.copy(self.sblocktex, srcrect=src, dstrect=dst)

	def drawstack(self):
		for c, col in enumerate(reversed(self.model.stack)):
			for r, block in enumerate(col):
				self.drawblock((r*self.tsize, c*self.tsize), block)

	def drawpiece(self, ptype, piecepos, pos):
		for c, col in enumerate(self.model.piecedict[ptype][piecepos[2]]):
			for r, block in enumerate(col):
				self.drawblock((r*self.tsize + pos[0], c*self.tsize + pos[1]), block)

	def drawspiece(self, ptype, piecepos, pos):
		for c, col in enumerate(self.model.piecedict[ptype][piecepos[2]]):
			for r, block in enumerate(col):
				self.drawsblock((r*self.ssize + pos[0], c*self.ssize + pos[1]), block)

	def drawcpiece(self):
		self.drawpiece(self.model.next[0], self.model.piecepos, (240,0))

	def drawnext(self):
		self.drawspiece(self.model.hold, (0,0,0), (0, 528))
		self.drawpiece(self.model.next[1], (0,0,0), (72, 504))
		self.drawspiece(self.model.next[2], (0,0,0), (168, 540))
		self.drawspiece(self.model.next[3], (0,0,0), (228, 540))

	def drawtime(self, tick):
		tick_ms = (50 * tick) // 3
		tickstr = "{2:02d}:{1:02d}:{0:02d}"\
			.format(tick_ms//10%100, tick_ms//1000%60, tick_ms//60000%100)
		self.timertex = self.sfactory.from_surface( sdlttf.TTF_RenderText_Solid(self.largefont,
			bytes(tickstr,"utf-8"),sdl2.SDL_Color(255,255,255,255)).contents, True)
		self.timertex.x, self.timertex.y = 410,575

	def drawlevel(self):
		levelstr = str(self.model.level)
		self.leveltex = self.sfactory.from_surface(sdlttf.TTF_RenderText_Solid(self.mainfont,
			bytes(str(levelstr),"utf-8"),sdl2.SDL_Color(255,255,255,255)).contents,True)
		self.leveltex.x, self.leveltex.y = 410, 530

	def draw(self):
		stacksprite = self.tspr.subsprite((0, 0, 240, 504))
		stacksprite.x, stacksprite.y = self.origin
		cpiecesprite = self.tspr.subsprite((240, 0, 96, 96))
		nextsprite = self.tspr.subsprite((0,504,288,96))
		nextsprite.x, nextsprite.y = 120,36
		tick = 0
		cp = ['',-1]
		while True:
			yield
			tick += 1
			if cp[0] != [self.model.next[0], self.model.piecepos[2]]:
				self.trds.clear()
				self.drawstack()
				self.drawnext()
				self.drawcpiece()
				self.drawlevel()
				cp = [self.model.next[0], self.model.piecepos[2]]
			cpiecesprite.y, cpiecesprite.x = \
				(20-self.model.piecepos[0])*self.tsize+self.origin[1], \
				self.model.piecepos[1]*self.tsize+self.origin[0]
			self.drawtime(tick)
			sdl2.ext.fill(self.renderer.surface, sdl2.ext.Color(0,0,0))
			self.renderer.render([stacksprite, nextsprite, self.border, self.timertex, 
				self.leveltex, cpiecesprite])
			self.window.refresh()
