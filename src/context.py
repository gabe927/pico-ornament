from networking import Networking
from picographics import PicoGraphics, DISPLAY_SCROLL_PACK, PEN_P8
from picoscroll import PicoScroll

class AppContext:
    def __init__(self, scroll=PicoScroll(), networking=Networking(), brightness=10):
        self.scroll = scroll
        self.net = networking
        self.brightness = brightness
        self.graphics = PicoGraphics(DISPLAY_SCROLL_PACK,pen_type=PEN_P8)

    def set_brightness(self, value):
        self.brightness = max(0, min(255, value))

    def set_rel_brightness(self, value):
        self.set_brightness(self.brightness + value)
