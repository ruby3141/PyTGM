import sdl2
import sdl2.sdlmixer as sdlmixer
import sdl2.audio as sdlaudio

class Audio:
	def __init__(self, model):
		sdlmixer.Mix_Init(0)
		sdlmixer.Mix_OpenAudio(22050, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
		self.model = model
		self.loadaudiofx()
		self.player = self.play()

	def loadaudiofx(self):
		self.blockfx = {
			'j': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/j.wav"),
			'i': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/i.wav"),
			'z': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/z.wav"),
			'l': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/l.wav"),
			'o': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/o.wav"),
			't': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/t.wav"),
			's': sdlmixer.Mix_LoadWAV(b"./res/audio/fx/s.wav")
		}
		self.lockfx = sdlmixer.Mix_LoadWAV(b"./res/audio/fx/lock.wav")
		self.dropfx = sdlmixer.Mix_LoadWAV(b"./res/audio/fx/drop.wav")
		self.erasefx = sdlmixer.Mix_LoadWAV(b"./res/audio/fx/erase.wav")

	def play(self):
		while(True):
			yield
			if self.model.state[0] == 'lineclear':
				sdlmixer.Mix_PlayChannel(-1, self.erasefx, 0)
				while(self.model.state[0] != 'are'):
					yield
				sdlmixer.Mix_PlayChannel(-1, self.dropfx, 0)
				while(self.model.state[0] == 'are'):
					yield
			if self.model.state[0] == 'are':
				sdlmixer.Mix_PlayChannel(-1, self.lockfx, 0)
				while(self.model.state[0] == 'are'):
					yield
			if self.model.state[0] == 'spawn':
				sdlmixer.Mix_PlayChannel(-1, self.blockfx[self.model.next[1]], 0)
				continue
