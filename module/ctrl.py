import module.model as model
import module.view as view
import sdl2
import sdl2.ext

class controller:
	def __init__(self):
		self.viewer = view.View()
		self.model = model.Model()

	def run(self):
		pass

