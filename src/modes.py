import secrets
import requests
import time
import ntptime
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
        if self._t <= self._wrap:
            self._t = self.context.scroll.get_width()


class Countdown(BaseMode):
    name = "countdown"

    def __init__(self, context) -> None:
        super().__init__(context)
        self.error_prefix = "SOME TIME"
        self.suffix_text = " UNTIL CHRISTMAS"
        self.text = self.error_prefix + self.suffix_text
        self.is_final_countdown = False
        self.resets_until_sync = 20
        self._resets_remaining_until_sync = 0

    def seconds_until_christmas(self, sync=False):

        if sync:
            # Sync RTC with NTP (UTC)
            try:
                ntptime.settime()
            except:
                pass

        # Get current UTC time as seconds
        now_utc = time.time()

        # Convert to Eastern Standard Time
        now_et = now_utc + (-5 * 3600)
        now = time.gmtime(now_et)

        year, month, day = now[0], now[1], now[2]

        # Check if today is Christmas Day
        is_christmas = (month == 12 and day == 25)

        # Christmas this year
        christmas = (year, 12, 25, 0, 0, 0, 0, 0)

        now_seconds = time.mktime(now)
        christmas_seconds = time.mktime(christmas)

        # If Christmas has already passed, use next year
        if now_seconds > christmas_seconds:
            christmas = (year + 1, 12, 25, 0, 0, 0, 0, 0)
            christmas_seconds = time.mktime(christmas)

        return int(christmas_seconds - now_seconds), is_christmas
    
    def reset(self, skip_sync=False) -> None:
        sync = (self._resets_remaining_until_sync == 0) and not skip_sync
        if self._resets_remaining_until_sync == 0:
            self._resets_remaining_until_sync = self.resets_until_sync
        s, is_christmas = self.seconds_until_christmas(sync)
        self.is_final_countdown = False
        if not self.context.net.is_connected:
            self.text = self.error_prefix + self.suffix_text
        elif s < 99:
            self.is_final_countdown = True
            self.text = str(s)
        elif is_christmas:
            self.text = "MERRY CHRISTMAS!!!"
        else:
            self.text = str(s) + " SECONDS" + self.suffix_text
        
        self._t = self.context.scroll.get_width()
        self.context.graphics.set_font("bitmap8")
        # add 1 to clear screen when device hangs during sync
        self._wrap = -(self.context.graphics.measure_text(self.text, scale=0) + 1)

    def run_tick(self) -> None:
        self.context.graphics.set_pen(0)
        self.context.graphics.clear()
        self.context.graphics.set_pen(self.context.brightness.value)
        # don't wrap the text during the final countdown
        if self.is_final_countdown:
            self.context.graphics.text(self.text, 0, 0, scale=1, spacing=1)
            self.context.scroll.update(self.context.graphics)
            # Skip the NTP sync during the final countdown so we're not syncing every tick
            self.reset(skip_sync=True)
        else:
            self.context.graphics.text(self.text, self._t, 0, scale=1, spacing=1)
            self.context.scroll.update(self.context.graphics)
            self._t -= 1
            if self._t <= self._wrap:
                # update time
                self.reset()


class Modes:
    filename = 'mode.txt'
    mode_classes = [LinkedIn, MerryChristmas, Countdown]

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