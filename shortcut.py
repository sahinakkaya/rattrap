import subprocess


class MetaKeyError(Exception):
    pass


class UndefinedKeyError(Exception):
    pass


class Key:
    all_keys = {'MODIFIERS': {'Shift_L': 'LeftShift', 'Alt_L': 'LeftAlt', 'Super_L': 'Super_L', 'Control_L': 'LeftCtrl',
                              'Control_R': 'RightCtrl', 'Shift_R': 'RightShift', 'Alt_R': 'RightAlt',
                              'Super_R': 'Super_R'},
                'BUTTONS': {'Button 1': 'Button1', 'Button 3': 'Button2', 'Button 2': 'Button3', 'Button 8': 'Button6',
                            'Button 9': 'Button7', 'Button 10': 'Button8', 'Button 11': 'Button9',
                            'Button 12': 'Button10', 'Button 13': 'Button11'},
                'SPECIALS': {'DPIUp': 'DPIUp', 'DPIDown': 'DPIDown', 'DPICycle': 'DPICycle', 'ModeSwitch': 'ModeSwitch',
                             'DPIShift': 'DPIShift', 'DPIDefault': 'DPIDefault'},
                'KEYS': {'Return': 'Enter', 'Escape': 'Escape', 'BackSpace': 'Backspace', 'Tab': 'Tab',
                         'space': 'Space', 'equal': '=', 'bracketleft': '[', 'bracketright': ']', 'backslash': '\\',
                         'semicolon': ';', 'minus': '-', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f',
                         'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o',
                         'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x',
                         'y': 'y', 'z': 'z', 'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'E': 'e', 'F': 'f', 'G': 'g',
                         'H': 'h', 'I': 'i', 'J': 'j', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'O': 'o', 'P': 'p',
                         'Q': 'q', 'R': 'r', 'S': 's', 'T': 't', 'U': 'u', 'V': 'v', 'W': 'w', 'X': 'x', 'Y': 'y',
                         'Z': 'z', '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
                         '8': '8', '9': '9', 'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5', 'F6': 'F6',
                         'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
                         'apostrophe': "'", 'grave': '`', 'comma': ',', 'period': '.', 'slash': '/', 'Pause': 'Pause',
                         'KP_Insert': 'Insert', 'Home': 'Home', 'Delete': 'Delete', 'Right': 'Right', 'Left': 'Left',
                         'Down': 'Down', 'Print': 'PrintScreen', 'KP_Prior': 'PageUp', 'KP_Next': 'PageDown',
                         'KP_Home': 'Home', 'KP_End': 'End', 'Up': 'Up', 'Num_Lock': 'NumLock', 'KP_Divide': 'Num/',
                         'KP_Multiply': 'Num*', 'KP_Subtract': 'Num-', 'KP_Add': 'Num+', 'KP_Enter': 'NumEnter',
                         'KP_0': 'Num0', 'KP_1': 'Num1', 'KP_2': 'Num2', 'KP_3': 'Num3', 'KP_4': 'Num4', 'KP_5': 'Num5',
                         'KP_6': 'Num6', 'KP_7': 'Num7', 'KP_8': 'Num8', 'KP_9': 'Num9', 'KP_Decimal': 'Num.',
                         'Menu': 'Menu', 'Control_R': 'RightCtrl', 'Shift_R': 'RightShift', 'Alt_R': 'RightAlt',
                         'Super_R': 'Super_R', 'Shift_L': 'LeftShift', 'Alt_L': 'LeftAlt', 'Super_L': 'Super_L',
                         'Control_L': 'LeftCtrl'}}

    def __init__(self, key):
        self.name = key
        for type_ in ["modifier", "button", "special", "key"]:
            if self.is_type(type_):
                self.type = type_
                break
        else:
            if key in ("Meta_L", "Meta_R"):
                raise MetaKeyError(key)
            raise UndefinedKeyError(f"key not defined, '{key}'")
        self.repr = self.all_keys[self.type.upper() + "S"][self.name]
        if self.is_type("modifier"):
            self.dual = self.repr.replace("Left", "Right").replace("_L", "_R")
            if self.dual == self.repr:
                self.dual = self.repr.replace("Right", "Left").replace("_R", "_L")

    def is_type(self, key_type):
        return self.name in self.all_keys[key_type.upper() + "S"]

    def __repr__(self):
        return self.repr

    def __str__(self):
        return self.name


class KeyCombo:
    def __init__(self):
        self.keys = []
        self.valid = True

    def any_button_pressed(self):
        return any((i.is_type("button") for i in self.keys))

    def any_key_pressed(self):
        return any((i.is_type("key") and not i.is_type("modifier") for i in self.keys))

    def any_special_pressed(self):
        return any((i.is_type("special") for i in self.keys))

    def dual_pressed(self, k: Key):
        try:
            return any(i.dual == k.repr for i in self.keys)
        except AttributeError:
            self.valid = False
            return True

    def all_modifiers(self):
        return all(i.is_type("modifier") for i in self.keys)

    def __add__(self, other: Key):
        if other.type in ("key", 'button', "special"):
            if self.any_button_pressed() or self.any_key_pressed() or self.any_special_pressed():
                self.valid = False
        else:
            if self.any_button_pressed() or self.any_key_pressed() or self.any_special_pressed():
                self.valid = False
            if self.dual_pressed(other):
                self.valid = False
        self.keys.append(other)

    def __str__(self):
        r = " + ".join(i.repr for i in self.keys) + (" +" if self.all_modifiers() else "")
        if self.valid:
            return r
        else:
            return r + " is not a valid combo."

    def sort(self):
        if self.valid:
            insert_position = 0
            sorted_keys = []
            for key in self.keys:
                if "Ctrl" in key.repr:
                    sorted_keys.insert(0, key)
                    insert_position += 1
                elif "Shift" in key.repr:
                    sorted_keys.insert(insert_position, key)
                    insert_position += 1
                elif "Alt" in key.repr:
                    sorted_keys.insert(insert_position, key)
                else:
                    sorted_keys.append(key)
        else:
            sorted_keys = self.keys

        return " + ".join(i.repr[:1].upper() + i.repr[1:] for i in sorted_keys) + (" +" if self.all_modifiers() else "")


def get_events():
    p1 = subprocess.Popen(["xev"], stdout=subprocess.PIPE)

    p2 = subprocess.Popen(['grep', '-A' '2', '-e', '^KeyPress', '-e', 'ButtonPress'], stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p1.stdout.close()
    output, err = p2.communicate()
    output = iter(output.decode("utf-8").splitlines())

    all_events = []
    while True:
        try:
            line = next(output)
            event_type = line.split()[0]
            next(output)
            line = next(output)
            if event_type == "ButtonPress":
                button_number = line.split("button")[1].split(",")[0]
                event = event_type, f"Button{button_number}"
                if event not in all_events:
                    all_events.append((event_type, f"Button{button_number}"))
            else:
                key_name = line.split("keysym", 1)[1].split("), same_screen")[0].split(",", 1)[1].strip()
                event = event_type, key_name
                if event not in all_events:
                    all_events.append((event_type, key_name))
            next(output)
        except StopIteration:
            break

    return all_events


def get_key_combo():
    key_combo = KeyCombo()
    events = get_events()
    message = None
    for event in events:
        try:
            k = Key(event[1])

        except MetaKeyError as e:
            key = Key("Alt_" + e.args[0][-1])
            message = f"Please press {key.repr} first then Shift."
            key_combo.valid = False
        else:
            key_combo + k

    return key_combo.sort(), key_combo.valid, message


if __name__ == '__main__':
    print(get_key_combo())
