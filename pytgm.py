#!/usr/bin/python3
if __name__ == "__main__":
	import module.ctrl as ctrl
	ctr = ctrl.controller()
	ctr.run()
else:
	import sdl2
	import sdl2.ext
	import random
	sdl2.ext.init()
	window = sdl2.ext.Window("Triggered", size=(320, 371))
	window.show()
	RESOURCES = sdl2.ext.Resources(__file__, "./res")
	factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
	sprite = factory.from_image(RESOURCES.get_path("triggered.png"))
	spriterenderer = factory.create_sprite_render_system(window)
	running = True
	while running:
		events=sdl2.ext.get_events()
		for event in events:
			if event.type == sdl2.SDL_QUIT:
				running=False
				break;
		sprite.position = random.randrange(-5,6), random.randrange(-5,6)
		spriterenderer.render(sprite)
		sdl2.SDL_Delay(16)
	window.hide()
