import subprocess
import re


class MetaKeyError(Exception):
    pass


class UndefinedSymbolError(Exception):
    pass


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

    # 'Control_R': 'RightCtrl', 'Shift_R': 'RightShift', 'Alt_R': 'RightAlt',
    # 'Super_R': 'Super_R', 'Shift_L': 'LeftShift', 'Alt_L': 'LeftAlt', 'Super_L': 'Super_L',
    # 'Control_L': 'LeftCtrl'

    def __init__(self, event_type, symbol, keycode=None, keyname=None):
        self.type = event_type
        self.symbol = symbol
        self.keycode = keycode

        if keycode:
            self.keymap = self.find_keymap()
            try:
                self.name = self.keymap[0]  # TODO: if user is not using english kayboard layout, warn him/her
                if keyname and keyname in self.keymap:
                    self.name = keyname
            except TypeError:
                self.name = None
                raise Exception(f"this exception should not be occur at all\n"
                                f"event type: {event_type} symbol: {symbol} keycode: {keycode} keyname: {keyname}")
        else:
            self.name = "Button " + symbol

        for type_ in ["modifier", "button", "special", "key"]:
            if self.is_type(type_):
                self.symbol_type = type_
                self.repr = self.all_symbols[type_ + "s"][self.name]
                break
        else:
            raise UndefinedSymbolError(f"symbol not defined, '{self.name}'")

        if self.is_type("modifier"):
            self.dual = self.repr.replace("Left", "Right").replace("_L", "_R")
            if self.dual == self.repr:
                self.dual = self.repr.replace("Right", "Left").replace("_R", "_L")
        else:
            self.dual = None

    def is_type(self, type_):
        return self.name in self.all_symbols[type_ + "s"]

    def find_keymap(self):
        return subprocess.run(["./find_keymap.sh", str(self.keycode)], capture_output=True).stdout.decode(
            "utf-8").strip().split()

    def set_new_name(self, new_name):
        self.name = new_name

    def set_new_repr(self, new_repr):
        self.repr = new_repr

    def __repr__(self):
        return f"{self.type} {self.repr} {self.symbol_type}"

    def __str__(self):
        return self.__repr__()


class ShortcutString:
    def __init__(self):
        self.keys = []

    @property
    def valid(self):
        # FIXME: is dual pressed?
        return re.match(r"^((s)|(m*[bk]?))$", "".join(i.symbol_type[0] for i in self.keys))

    @property
    def repr(self):
        return self.__str__()

    def has_any_type(self, type_):
        return any((i.is_type(type_) for i in self.keys))

    # def dual_pressed(self, k):
    #     try:
    #         return any(i.dual == k.repr for i in self.keys)
    #     except AttributeError:
    #         self.valid = False
    #         return True

    def all_modifiers(self):
        return all(i.is_type("modifier") for i in self.keys)

    def __iadd__(self, other):
        # print(other.repr, other.type)
        self.keys.insert(0, other)
        return self

    def __str__(self):
        r = " + ".join(i.repr for i in self.keys) + ("+ " if self.all_modifiers() else "")
        if self.valid:
            return r
        else:
            return r + " is not a valid combo."

    def __repr__(self):
        return "+".join(i.repr for i in self.keys) + ("+" if self.all_modifiers() else "")


class EventList(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def append(self, event):
        if not self.__contains__(event):
            super(EventList, self).append(event)

    def get_events(self):
        process = subprocess.run("./xev_parser.sh", capture_output=True)
        event_table = map(str.split, (process.stdout.decode("utf-8").splitlines()))
        for row in event_table:
            self.append(Event(*row))

    def mouse_presses(self, type_="all"):
        if type_ == "all":
            event_types = ("ActualButtonPress", "ModifiedButtonPress")
        elif type_ == "actual":
            event_types = ("ActualButtonPress",)
        elif type_ == "modified":
            event_types = ("ModifiedButtonPress",)

        return EventList(filter(lambda x: x.type in event_types, self))

    def keyboard_presses(self, dummy_var):
        return EventList(filter(lambda x: x.type == "KeyPress", self))

    def non_modifier_button(self, input_device, type_=None):
        n = []
        for event in getattr(self, input_device + "_presses")(type_):
            if event.symbol_type in ("key", "button"):
                n.append(event)
        return n

    def __contains__(self, item):
        return item in [i.repr for i in self]

    def remove(self, shortcut_list):
        self[:] = [event for event in self if event.repr not in shortcut_list]

    def get_shortcut_string(self):
        shortcut_string = ShortcutString()
        import ratslap
        mode = ratslap.Ratslap("/home/sahin/Desktop/ratslap/ratslap").parse_mode("4")
        xev_transitions_for_buttons = {'left': '1', 'right': '3', 'middle': '2', 'g4': '8', 'g5': '9', 'g6': '10',
                                       'g7': '11', 'g8': '12', 'g9': '13'}
        mode = {i: list(map(str.strip, filter(None, j.split(" +")))) for i, j in mode.items()}
        print(mode)

        while True:
            try:
                event = self[-1]  # type: Event
            except IndexError:
                break
            else:
                if event.type in ("ActualButtonPress", "ModifiedButtonPress"):
                    best_button = self.get_best_button(mode, event)
                    e = Event("ActualButtonPress", xev_transitions_for_buttons[best_button['name']])
                    self.remove(best_button["shortcut"])
                    shortcut_string += e
                else:
                    self.remove([event.repr])
                    shortcut_string += event
        return shortcut_string

    def get_best_button(self, mode, event):
        possible_buttons = {k: v for k, v in mode.items() if event.repr in v}
        r = {'name': '', 'shortcut': []}
        for button_name, shortcut in possible_buttons.items():
            if all(keyname in self for keyname in shortcut) and len(shortcut) > len(r['shortcut']):
                r['name'], r['shortcut'] = button_name, shortcut

        return r


if __name__ == '__main__':
    e = EventList()
    e.get_events()
    print(e.get_shortcut_string())
