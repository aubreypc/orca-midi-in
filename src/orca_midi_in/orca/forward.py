import socket

from orca_midi_in.orca.glyph import GLYPHS
from orca_midi_in.orca.number import midi_to_base_36, seconds_to_frames, NUMBERS
from src.orca_midi_in.midi.midi_handler import MidiEvent


class OrcaCommandForwarder:
    def __init__(self,
                 port: int = 49160,
                 ip: str = "localhost",
                 midi_channel: int = 0,
                 bpm: int = 120,
                 midi_cc_offset: int = 0,
                 verbose: bool = False):
        self._verbose = verbose
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.midi_channel = midi_channel
        self.midi_cc_offset = self.set_midi_cc_offset(midi_cc_offset)
        self.bpm = self.set_bpm(bpm)

    def send_cmd(self, cmd: str):
        if self._verbose:
            print(cmd)
        self.sock.sendto(cmd.encode(), (self.ip, self.port))

    def find(self, string: str):
        cmd = f"find:{string}"
        return self.send_cmd(cmd)

    def select(self, x: int, y: int, width: int = 0, height: int = 0):
        cmd = f"select:{x};{y};{width};{height}"
        return self.send_cmd(cmd)

    def write(self, glyph: str, x: int = None, y: int = None):
        cmd = f"write:{glyph}" + (f";{x};{y}" if x is not None and y is not None else "")
        return self.send_cmd(cmd)

    def write_midi_note(self,
                        event: MidiEvent,
                        x: int = None,
                        y: int = None,
                        with_octave: bool = True,
                        with_velocity: bool = True,
                        with_length: bool = True,
                        with_midi_operator: bool = True,
                        ):
        glyph = GLYPHS[(event.key - 21) % 12]
        octave = -1 + (event.key - (event.key % 12)) // 12
        velocity = midi_to_base_36(event.value, min=1)
        length = seconds_to_frames(event.time_delta, self.bpm)
        if with_midi_operator:
            write_chars = [
                ":",
                str(self.midi_channel),
                str(octave) if with_octave else None,
                glyph,
                velocity if with_velocity else None,
                length if with_length else None
            ]
            # If nothing is to the right of a char, we don't need to fill with "."
            # This way, we avoid overwriting nearby cells on the grid.
            has_right_char = False
            for i, char in reversed(list(enumerate(write_chars))):
                if char is not None:
                    has_right_char = True
                if char is None:
                    write_chars[i] = "." if has_right_char else ""
        else:
            write_chars = glyph
        self.write("".join(write_chars), x, y)

    def write_midi_cc(self,
                      event: MidiEvent,
                      x: int = None,
                      y: int = None,
                      with_midi_cc_operator: bool = False):
        value = midi_to_base_36(event.value)
        knob = NUMBERS[event.key % 36]
        write_str = value
        if with_midi_cc_operator:
            write_str = f"!{self.midi_channel}{knob}{value}"
        self.write(write_str, x, y)

    def set_bpm(self, bpm: int) -> int:
        self.bpm = bpm
        self.send_cmd(f"bpm:{bpm}")
        return bpm

    def set_midi_cc_offset(self, offset: int) -> int:
        self.midi_cc_offset = offset
        self.send_cmd(f"cc:{offset}")
