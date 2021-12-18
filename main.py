import threading
import pygame as pg
import pygame.midi
from pynput import keyboard
import time
from datetime import datetime
import json


class MidiListener(threading.Thread):
    def _print_device_info(self):
        for i in range(pygame.midi.get_count()):
            r = pygame.midi.get_device_info(i)
            (interf, name, input, output, opened) = r

            in_out = ""
            if input:
                in_out = "(input)"
            if output:
                in_out = "(output)"

            print(
                "%2i: interface :%s:, name :%s:, opened :%s:  %s"
                % (i, interf, name, opened, in_out)
            )

    def input_main(self, device_id=None):
        pg.init()
        pg.fastevent.init()
        event_get = pg.fastevent.get
        event_post = pg.fastevent.post

        pygame.midi.init()

        self, self._print_device_info()

        if device_id is None:
            input_id = pygame.midi.get_default_input_id()
        else:
            input_id = device_id

        print("using input_id :%s:" % input_id)
        i = pygame.midi.Input(input_id)

        pg.display.set_mode((1, 1))

        going = True
        while going:
            events = event_get()
            for e in events:
                if e.type in [pg.QUIT]:
                    going = False
                if e.type in [pg.KEYDOWN]:
                    going = False
                if e.type in [pygame.midi.MIDIIN]:
                    print(e)

            if i.poll():
                midi_events = i.read(10)
                midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

                for m_e in midi_evs:
                    event_post(m_e)

        del i
        pygame.midi.quit()

    running = True
    started = False
    device_id = None
    listener_thread = None

    def __init__(self, device_id):
        self.device_id = device_id
        super(MidiListener, self).__init__()

    def run(self) -> None:
        if not self.started:
            print("done")
            self.listener_thread = threading.Thread(target=input_main(self.device_id))
            self.started = True


class MidiNote(object):
    key = None
    start_t = None
    end_t = None
    data = None

    def __init__(self, key):
        self.key = key
        self.start_t = time.time()

    def set_end_t(self):
        self.end_t = time.time()
        self.data = {
            "note_key": self.key,
            "time_start": self.start_t,
            "time_end": self.end_t,
            "duration": float(self.end_t-self.start_t),
            "duration_s": float(self.end_t - self.start_t)
        }
        return self.data


def get_note_from_mapping(key=None):
    global current_note
    if current_note is not None:
        note_key = key if key is not None else current_note.key
        for k in mappin_a["keys"].keys():
            current_line = mappin_a["keys"][str(k)]
            if str(note_key) in current_line.keys():
                return current_line[current_note.key]
                break
        return False

if __name__ == '__main__':
    current_note = None
    current_key = None
    pressed = False

    def on_press(key):
        global current_key
        global current_note
        global pressed
        try:
            k = key.char  # single-char keys
        except:
            k = key.name  # other keys
        current_key = k

        if not pressed:
            current_note = MidiNote(key=k)
            print(str(get_note_from_mapping(current_key)),end="")
            pressed = True


    def on_release(key):
        global pressed
        if pressed:
            pressed = False
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        else:
            print(get_note_from_mapping())

    mappin_a = {
        "keys": {},
        "octave_num_start": 1
    }

    mapping_keys_n = ["2", "3",      "5", "6", "7",      "9", "0",      "´"]
    mapping_keys_a = ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"]

    mapping_keys_o = ["s", "d", "g", "h", "j", "k", "l", "ö"]
    mapping_keys_b = ["y", "x", "c", "v", "b", "n", "m", ",", ".", "-"]

    a_p = ["cis", "dis",    "fis","gis", "b", "cis", "dis", "fis", "gis", "b"]
    a_notes_keys_a = ["c", "d", "e", "f", "g", "a", "h", "c", "d", "e", "f", "g", "a", "h"]

    c_current = False
    c_again = False
    keys_i = 0

    current_octave = 2
    for i_a in range(0, len(mapping_keys_n)):
        if str(keys_i) not in mappin_a["keys"].keys():
            mappin_a["keys"][str(keys_i)] = {}
        key_a = mapping_keys_n[i_a]

        if a_notes_keys_a[i_a] == "c":
            if not c_current:
                c_current = True
            else:
                if c_current:
                    current_octave += 1
                    c_current = False
                    c_again = False

        mappin_a["keys"][str(keys_i)][key_a] = a_p[i_a].upper() + str(current_octave)
        if i_a == len(mapping_keys_n) - 1:
            keys_i += 1

    current_octave = 2
    for i_a in range(0, len(mapping_keys_a)):
        if str(keys_i) not in mappin_a["keys"].keys():
            mappin_a["keys"][str(keys_i)] = {}
        key_a = mapping_keys_a[i_a]

        if a_notes_keys_a[i_a] == "c":
            if not c_current:
                c_current = True
            else:
                if c_current:
                    current_octave += 1
                    c_current = False
                    c_again = False

        mappin_a["keys"][str(keys_i)][key_a] = a_notes_keys_a[i_a].upper()+str(current_octave)
        if i_a == len(mapping_keys_a) - 1:
            keys_i += 1

    current_octave = 1
    for i_a in range(0, len(mapping_keys_o)):
        if str(keys_i) not in mappin_a["keys"].keys():
            mappin_a["keys"][str(keys_i)] = {}
        key_a = mapping_keys_o[i_a]

        if a_notes_keys_a[i_a] == "c":
            if not c_current:
                c_current = True
            else:
                if c_current:
                    current_octave += 1
                    c_current = False
                    c_again = False

        mappin_a["keys"][str(keys_i)][key_a] = a_p[i_a].upper() + str(current_octave)
        if i_a == len(mapping_keys_o) - 1:
            keys_i += 1
    current_octave = 1
    for i_a in range(0, len(mapping_keys_b)):
        if str(keys_i) not in mappin_a["keys"].keys():
            mappin_a["keys"][str(keys_i)] = {}
        key_a = mapping_keys_b[i_a]

        if a_notes_keys_a[i_a] == "c":
            if not c_current:
                c_current = True
            else:
                if c_current:
                    current_octave += 1
                    c_current = False
                    c_again = False

        mappin_a["keys"][str(keys_i)][key_a] = a_notes_keys_a[i_a].upper() + str(current_octave)
        if i_a == len(mapping_keys_b) - 1:
            keys_i += 1

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()  # start to listen on a separate thread
    listener.join()  # remove if main thread is polling self.keys

