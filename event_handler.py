import subprocess
import re


class MetaKeyError(Exception):
    pass


class UndefinedSymbolError(Exception):
    pass


class Shortcut(str):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keys = []

    @property
    def valid(self):
        # FIXME: is dual pressed?
        if len(self.keys) == 0:
            return False
        return bool(re.match(r"^((s)|(m*[bk]?))$", "".join(i.symbol_type[0] for i in self.keys)))

    @property
    def string(self):
        return " + ".join(i.repr for i in self.keys) + ("+ " if self.all_modifiers() else "")

    def has_any_type(self, type_):
        return any((i.is_type(type_) for i in self.keys))

    def all_modifiers(self):
        return all(i.is_type("modifier") for i in self.keys) and len(self.keys) > 0

    def __iadd__(self, other):
        self.keys.insert(0, other)
        return self

    def __str__(self):
        if self.valid:
            return self.string
        else:
            return self.string + " is not a valid combo."

    def __repr__(self):
        return "+".join(i.repr for i in self.keys) + ("+" if self.all_modifiers() else "")


class Event:
    all_symbols = {
        'modifiers': {'Shift_L': 'LeftShift', 'Alt_L': 'LeftAlt', 'Super_L': 'Super_L', 'Control_L': 'LeftCtrl',
                      'Control_R': 'RightCtrl', 'Shift_R': 'RightShift', 'Alt_R': 'RightAlt', 'Super_R': 'Super_R'},
        'buttons': {'Button 1': 'Button1', 'Button 3': 'Button2', 'Button 2': 'Button3', 'Button 8': 'Button6',
                    'Button 9': 'Button7', 'Button 10': 'Button8', 'Button 11': 'Button9', 'Button 12': 'Button10',
                    'Button 13': 'Button11'},
        'specials': {'DPIUp': 'DPIUp', 'DPIDown': 'DPIDown', 'DPICycle': 'DPICycle', 'ModeSwitch': 'ModeSwitch',
                     'DPIShift': 'DPIShift', 'DPIDefault': 'DPIDefault'},
        'keys': {'Return': 'Enter', 'Escape': 'Escape', 'BackSpace': 'Backspace', 'Tab': 'Tab', 'space': 'Space',
                 'equal': '=', 'bracketleft': '[', 'bracketright': ']', 'backslash': '\\', 'semicolon': ';',
                 'minus': '-', 'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'e', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I',
                 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S',
                 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z', 'A': 'A', 'B': 'B', 'C': 'C',
                 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G', 'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M',
                 'N': 'N', 'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U', 'V': 'V', 'W': 'W',
                 'X': 'X', 'Y': 'Y', 'Z': 'Z', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
                 '7': '7', '8': '8', '9': '9', 'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5', 'F6': 'F6',
                 'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10', 'F11': 'F11', 'F12': 'F12', 'apostrophe': "'",
                 'grave': '`', 'comma': ',', 'period': '.', 'slash': '/', 'Pause': 'Pause', 'KP_Insert': 'Insert',
                 'Home': 'Home', 'Delete': 'Delete', 'Right': 'Right', 'Left': 'Left', 'Down': 'Down',
                 'Print': 'PrintScreen', 'KP_Prior': 'PageUp', 'KP_Next': 'PageDown', 'KP_Home': 'Home',
                 'KP_End': 'End', 'Up': 'Up', 'Num_Lock': 'NumLock', 'Insert': 'Insert', 'Scroll_Lock': 'ScrollLock',
                 'KP_Divide': 'Num/', 'KP_Multiply': 'Num*', 'KP_Subtract': 'Num-', 'KP_Add': 'Num+',
                 'KP_Enter': 'NumEnter', 'KP_0': 'Num0', 'KP_1': 'Num1', 'KP_2': 'Num2', 'KP_3': 'Num3', 'KP_4': 'Num4',
                 'KP_5': 'Num5', 'KP_6': 'Num6', 'KP_7': 'Num7', 'KP_8': 'Num8', 'KP_9': 'Num9', 'KP_Decimal': 'Num.',
                 'Menu': 'Menu'}}

    def __init__(self, event_type, symbol, keycode=None, keyname=None):
        self.type = event_type
        self.symbol = symbol
        self.keycode = keycode

        if keycode:
            self.keymap = self.find_keymap()
            try:
                self.names = self.keymap[0]  # TODO: if user is not using english keyboard layout, warn him/her
                if keyname and keyname in self.keymap:
                    self.names = keyname

            except TypeError:
                self.names = None
                raise Exception(f"this exception should not be occur at all\n"
                                f"event type: {event_type} symbol: {symbol} keycode: {keycode} keyname: {keyname}")
        else:
            self.names = "Button " + symbol

        for type_ in ["modifier", "button", "special", "key"]:
            if self.is_type(type_):
                self.symbol_type = type_
                self.repr = self.all_symbols[type_ + "s"][self.names]
                break
        else:
            raise UndefinedSymbolError(f"symbol not defined, '{self.names}'")

        if self.is_type("modifier"):
            self.dual = self.repr.replace("Left", "Right").replace("_L", "_R")
            if self.dual == self.repr:
                self.dual = self.repr.replace("Right", "Left").replace("_R", "_L")
        else:
            self.dual = None

    def is_type(self, type_):
        return self.names in self.all_symbols[type_ + "s"]

    def find_keymap(self):
        return list(filter(lambda x: "NoSymbol" not in x,
                           subprocess.run(["./find_keymap.sh", str(self.keycode)], capture_output=True).stdout.decode(
                               "utf-8").strip().split()))

    def set_new_name(self, new_name):
        self.names = new_name

    def set_new_repr(self, new_repr):
        self.repr = new_repr

    def __repr__(self):
        return f"{self.type} {self.repr} {self.symbol_type}"

    def __str__(self):
        return self.__repr__()


class EventList(list):
    def __init__(self, mouse_profile, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mouse_profile = {i: list(map(str.strip, filter(None, j.split(" +")))) for i, j in mouse_profile.items()}

    def append(self, event):
        if not self.__contains__(event):
            super(EventList, self).append(event)

    def get_events(self):
        process = subprocess.run("./xev_parser.sh", capture_output=True)
        event_table = map(str.split, (process.stdout.decode("utf-8").splitlines()))
        for row in event_table:
            self.append(Event(*row))

    def __contains__(self, item):
        return item in [i.repr for i in self]

    def remove(self, shortcut_list):
        self[:] = [event for event in self if event.repr not in shortcut_list]

    def create_shortcut_from_events(self):
        shortcut = Shortcut()

        xev_transitions_for_buttons = {'left': '1', 'right': '3', 'middle': '2', 'g4': '8', 'g5': '9', 'g6': '10',
                                       'g7': '11', 'g8': '12', 'g9': '13'}

        while True:
            try:
                event = self[-1]  # type: Event
            except IndexError:
                break
            else:
                print(event)
                if event.type == "ButtonPress":
                    best_button = self.get_best_button(self.mouse_profile, event)
                    e = Event("ButtonPress", xev_transitions_for_buttons[best_button['name']])
                    self.remove(best_button["shortcut"])
                    shortcut += e
                else:
                    self.remove([event.repr])
                    shortcut += event
        return shortcut

    def get_best_button(self, mode, event):
        possible_buttons = {k: v for k, v in mode.items() if event.repr in v}
        r = {'name': '', 'shortcut': []}
        for button_name, shortcut in possible_buttons.items():
            if all(keyname in self for keyname in shortcut) and len(shortcut) > len(r['shortcut']):
                r['name'], r['shortcut'] = button_name, shortcut
        return r


if __name__ == '__main__':
    import ratslap
    from db_helper import DBHelper

    with DBHelper("settings.db") as conn:
        path = conn.select("file_paths", ("path",), program_name="ratslap").fetchone()[0]

    event_list = EventList(ratslap.Ratslap(path).parse_mode(3))
    event_list.get_events()
    print(event_list.create_shortcut_from_events())
