class Brightness:
    filename = 'brightness.txt'

    def __init__(self, value=None) -> None:
        if value:
            self.set_value(value)
        else:
            value_from_file = self._read_file()
            if value_from_file:
                self.set_value(value_from_file, skip_save=True)
            else:
                self.set_value(255)

    def _read_file(self) -> int|None:
        try:
            with open(self.filename, 'r') as f:
                return int(f.read())
        except:
            return None
    
    def _save_file(self) -> None:
        with open(self.filename, 'w') as f:
            f.write(str(self.value))

    def set_value(self, value, skip_save=False) -> None:
        self.value = max(0, min(255, value))
        if not skip_save:
            self._save_file()

    def set_rel_value(self, value) -> None:
        self.set_value(self.value + value)