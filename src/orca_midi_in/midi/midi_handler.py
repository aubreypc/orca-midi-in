import time
from enum import Enum
from typing import Any, Tuple
from dataclasses import dataclass

from rtmidi import MidiIn
from rtmidi.midiutil import open_midiinput

MIDI_PORTS = MidiIn().get_ports()
MIDI_MESSAGES = {
    144: "note_on",
    128: "note_off",
    176: "cc",
}


@dataclass
class MidiEvent:
    message_id: int
    key: int
    value: int
    time_delta: float = 0.0


class MidiHandler:
    def __init__(self, port: int):
        self._port_name = MIDI_PORTS[port]
        self._midi_in = None

    def __enter__(self):
        self._midi_in = open_midiinput(self._port_name)[0]
        self._midi_in.set_callback(self._callback_wrapper)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._midi_in.cancel_callback()
        self._midi_in.close_port()

    def _callback_wrapper(self, tup: Tuple, _data: Any):
        event, time_delta = tup
        event = MidiEvent(*event, time_delta)
        return self.midi_event_callback(event)

    def midi_event_callback(self, event: MidiEvent) -> None:
        message_name = MIDI_MESSAGES[event.message_id]
        return self.__getattribute__(message_name)(event)

    def note_on(self, event: MidiEvent) -> None:
        pass

    def note_off(self, event: MidiEvent) -> None:
        pass

    def cc(self, event: MidiEvent) -> None:
        print(event)


if __name__ == "__main__":
    with MidiHandler(0):
        time.sleep(10)
