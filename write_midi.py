import os
import json
from midiutil.MidiFile import MIDIFile
from base64 import b64encode
import lzma


def humanbytes(B):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string"""
    B = float(B)
    KB = float(1000)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Bytes')
    elif KB <= B < MB:
        return '{0:.2f} KBytes'.format(B / KB)
    elif MB <= B < GB:
        return '{0:.2f} MBytes'.format(B / MB)
    elif GB <= B < TB:
        return '{0:.2f} GBytes'.format(B / GB)
    elif TB <= B:
        return '{0:.2f} TBytes'.format(B / TB)


class CreateMidiFile(object):
    piano_roll = None
    track = None
    time = 0
    track_name = None
    DEFAULT_TEMPO = 130
    channel = None
    volume = None
    current_pitch = None
    DEFAULT_CHANNEL = 0
    DEFAULT_VOLUME = 100
    DEFAULT_FNAME = "output.mid"
    DEFAULT_TRACKNAME = "Sample Track"
    current_file = None

    def __init__(self, tracks_num=None, start_time=None, track_name=None, tempo=None, start_track=None,
                 track_channel=None, track_volume=None):
        self.track_tempo = tempo if tempo is not None else self.DEFAULT_TEMPO
        self.track_name = track_name if track_name is not None else self.DEFAULT_TRACKNAME
        self.piano_roll = MIDIFile(tracks_num if tracks_num is not None else 1)
        self.track = start_track if start_track is not None else 0
        self.time = start_time
        self.piano_roll.addTrackName(self.track, self.time, self.track_name)
        self.piano_roll.addTempo(self.track, self.time, tempo if tempo is not None else self.DEFAULT_TEMPO)
        self.channel = track_channel if track_channel is not None else self.DEFAULT_CHANNEL
        self.volume = track_volume if track_volume is not None else self.DEFAULT_VOLUME

    def set_volume(self, value, reset=None):
        tmp_vol = self.volume
        self.volume = value
        if reset is not None and reset:
            self.volume = tmp_vol

    def add_note(self, pitch_, time_, duration_):
        """
        pitch = pitch_  # H3 (middle H)
        time = time_  # start on beat 0
        duration = duration_  # 1 beat long
        """
        self.current_pitch = pitch_
        self.piano_roll.addNote(self.track, self.channel, self.current_pitch, time_, duration_, self.volume)

    def write_file(self):
        with open(self.current_file if self.current_file is not None else self.DEFAULT_FNAME, 'wb') as outf:
            self.piano_roll.writeFile(outf)
            outf.close()

    def write_midi_to_file(self, filename=None, overwrite=None):
        self.current_file = filename
        if overwrite is not None and overwrite:
            self.write_file()
            return

        if not os.path.isfile(self.current_file):
            self.write_file()
        else:
            print("file exists")


class NoteSheet(object):
    keys_ = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "h"]
    notes = None
    octaves = []
    octaves_n = []

    def __init__(self):
        print("note-sheet v0.1")
        self.notes = {}
        self.generate_notes()

    def generate_notes(self):
        max_notes = 127
        max_note_per_octave = 12

        real_note_id_i = 0
        octave_notes = 0
        for real_note_id in range(0, max_notes):
            octave_int = int(real_note_id / max_note_per_octave)

            octave_key_ = "octave_" + str(octave_int + 1)
            if real_note_id % max_note_per_octave == 0 and real_note_id != 0:
                real_note_id_i = 0
                octave_notes = 0
                if octave_key_ not in self.notes.keys():
                    self.notes[octave_key_] = {}
                    self.octaves.append([])
                    self.octaves_n.append([])
            elif real_note_id == 0:
                self.notes["octave_" + str(real_note_id + 1)] = {}
                self.octaves.append([])
                self.octaves_n.append([])
            octave_note_key = "note_" + str(octave_notes + 1)

            self.notes[octave_key_][octave_note_key] = {
                "name": self.keys_[real_note_id_i],
                "midiName": self.keys_[real_note_id_i].upper() + str(octave_int + 1),
                "pitch": real_note_id
            }
            index_ = len(self.octaves) - 1
            self.octaves[index_].append(real_note_id)
            self.octaves_n[index_].append(self.keys_[real_note_id_i])
            octave_notes += 1
            real_note_id_i += 1


ns_ = NoteSheet()
for octave_ in ns_.notes.keys():
    octave_int = int(octave_.replace("octave_", ""))
    for note_key in ns_.notes[octave_].keys():
        note_ = ns_.notes[octave_][note_key]
        name_ = note_["name"]
octaves = {
    "pitches": ns_.octaves,
    "names": ns_.octaves_n
}

all_notes_b = json.dumps(octaves).encode("utf-8")

unit_ = "KBytes"

enc_ = lzma.compress(all_notes_b)
str_ = humanbytes(len(all_notes_b))
str_ += " => compressed => " + humanbytes(len(enc_))
all_notes = str(b64encode(all_notes_b).decode("utf-8"))

print(str_)

dec_ = lzma.decompress(enc_)

decoded_ = json.loads(dec_.decode("utf-8"))

MIDIFile_ = CreateMidiFile(1, 0, "NoneOne Test-MidiFile", 120, 0, track_volume=None)
MIDIFile_.add_note(60, 0, 1)
MIDIFile_.set_volume(80)

MIDIFile_.add_note(64, 1, 1)
MIDIFile_.set_volume(60)

MIDIFile_.add_note(60, 2, 1)
MIDIFile_.write_midi_to_file(filename="my-wonderful-midi.mid", overwrite=True)
