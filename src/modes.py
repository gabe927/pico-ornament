import secrets
import requests
import time
from networking import Networking

class BaseMode:
    name = "base"

    # called during startup
    def __init__(self, context) -> None:
        self.context = context

    # called at startup and when the mode is set to the active mode
    def reset(self) -> None:
        pass
    
    # one tick worth of computation for the main running loop while the mode is active
    def run_tick(self) -> None:
        pass


class LinkedIn(BaseMode):
    name = "linkedin"
    filename = 'linkedin.txt'

    def __init__(self, context):
        super().__init__(context)
        self.text = None
        # Using this to only update once per boot
        self.is_updated = False

    # runs API calls to update text
    # returns True if successful, False if not
    def _update(self, force=False) -> bool:
        if self.is_updated and not force:
            print("LinkedIn update attempted, but is already updated")
            return False
        
        if not self.context.net.is_connected:
            print("LinkedIn update attempted, but not connected to internet")
            return False
        
        print("Attempting to create LinkedIn request")
        response = requests.get(f"https://www.googleapis.com/customsearch/v1?key={secrets.GOOGLE_KEY}&cx={secrets.GOOGLE_CX}&q={secrets.GOOGLE_QUERY}", timeout=10)
        if response.status_code != 200:
            print(f"Error - Request returned {response.status_code} code")
            return False
        print("Request successful")
        self.is_updated = True
        self.set_text(response.json()["items"][0]["pagemap"]["metatags"][0]["og:title"].replace(' | LinkedIn', ''))
        return True
    
    # gets the text from the stored file (useful for when offline)
    # returns True if successful, False if not
    def _read_file(self) -> bool:
        # NOTE this sets self.text directly instead of set_text so we're not writing to file
        try:
            print("Reading LinkedIn txt file...")
            with open(self.filename, 'r') as f:
                self.text = f.read()
            return True
        except:
            # file does not exist
            print("LinkedIn txt file does not exist!")
            self.text = 'No data'
            return False

    def reset(self) -> None:
        # checks if updated already, will only update once per boot/class init to save on API limits
        if not self.is_updated:
            # if update fails or not connected to the internet, then read from file
            if not self._update():
                self._read_file()

        self._t = self.context.scroll.get_width()
        self.context.graphics.set_font("bitmap8")
        self._wrap = -self.context.graphics.measure_text(self.text, scale=0)

    # sets and stores the text
    def set_text(self, text:str) -> None:
        print(f"Setting LinkedIn text to '{text}'")
        self.text = text.upper()
        with open(self.filename, 'w') as f:
            f.write(self.text)
        self.reset()

    def run_tick(self):
        self.context.graphics.set_pen(0)
        self.context.graphics.clear()
        self.context.graphics.set_pen(self.context.brightness.value)
        self.context.graphics.text(self.text, self._t, 0, scale=1, spacing=1)
        self.context.scroll.update(self.context.graphics)
        self._t -= 1
        time.sleep(0.1)
        if self._t <= self._wrap:
            self._t = self.context.scroll.get_width()


class MerryChristmas(BaseMode):
    name = 'merrychristmas'

    def __init__(self, context) -> None:
        super().__init__(context)
        self.text = "MERRY CHRISTMAS!!!"
    
    def reset(self) -> None:
        self._t = self.context.scroll.get_width()
        self.context.graphics.set_font("bitmap8")
        self._wrap = -self.context.graphics.measure_text(self.text, scale=0)

    def run_tick(self):
        self.context.graphics.set_pen(0)
        self.context.graphics.clear()
        self.context.graphics.set_pen(self.context.brightness.value)
        self.context.graphics.text(self.text, self._t, 0, scale=1, spacing=1)
        self.context.scroll.update(self.context.graphics)
        self._t -= 1
        time.sleep(0.1)
        if self._t <= self._wrap:
            self._t = self.context.scroll.get_width()


class Modes:
    filename = 'mode.txt'
    mode_classes = [LinkedIn, MerryChristmas]

    def __init__(self, context) -> None:
        self.context = context

        # Initiate modes
        self.modes = {}
        for c in self.mode_classes:
            self.modes.update({c.name : c(context)})
        
        # load active mode from file and set it
        # NOTE: this does cause the mode to be read then immediately written, but solve the issue of having no file at startup
        self.set_mode(self._load_mode() or list(self.modes.keys())[0])

    # Loads the mode stored in the modes file, returns None if file does not exist
    def _load_mode(self) -> str|None:
        try:
            with open(self.filename, 'r') as f:
                mode = f.read().strip()
                if mode in self.modes:
                    return mode
                else:
                    return None
        except:
            return None
        
    # saves the mode to the modes file
    def _save_mode(self) -> None:
        with open(self.filename, 'w') as f:
            f.write(self.active_mode)

    # sets the active mode to the next mode in the mode_classes list
    def next_mode(self) -> None:
        mode_keys = list(self.modes.keys())
        i = mode_keys.index(self.active_mode)
        # use the modulo to wrap the index to the beginning
        self.set_mode(mode_keys[(i + 1) % len(mode_keys)])

    # sets the active mode, stores it to file, and calls the mode's reset
    def set_mode(self, mode:str) -> None:
        if mode in self.modes:
            print(f"Setting mode to '{mode}'")
            self.active_mode = mode
            self._save_mode()
            self.modes[mode].reset()

    # runs one tick worth of computation in the active mode
    def run_tick(self) -> None:
        if self.active_mode in self.modes:
            self.modes[self.active_mode].run_tick()