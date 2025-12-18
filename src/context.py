from networking import Networking
from brightness import Brightness
from picographics import PicoGraphics, DISPLAY_SCROLL_PACK, PEN_P8
from picoscroll import PicoScroll

class AppContext:
    def __init__(self, scroll=PicoScroll(), networking=Networking(), brightness=Brightness()):
        self.scroll = scroll
        self.net = networking
        self.brightness = brightness
        self.graphics = PicoGraphics(DISPLAY_SCROLL_PACK,pen_type=PEN_P8)
