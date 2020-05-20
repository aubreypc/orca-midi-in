from typing import List

import mido
from mido.backends.rtmidi import Input

MIDI_PORTS = mido.get_input_names()


class MidiHandler:
    def __init__(self, port_ids: List[int], verbose: bool = False):
        self._port_ids = port_ids
        self._midi_ins = []
        self._verbose = verbose
        self.running = False

    def run(self):
        self.running = True
        self._midi_ins = self._open_ports()
        while self.running:
            for midi_in in self._midi_ins:
                self._handle_midi_in(midi_in)

    def _open_ports(self) -> List[Input]:
        midi_ins = []
        for port_id in self._port_ids:
            midi_in = mido.open_input(MIDI_PORTS[port_id])
            midi_in.port_id = port_id
            midi_ins.append(midi_in)
        return midi_ins

    def _handle_midi_in(self, midi_in: Input):
        """
        Polls for a message and passes it to the method with the same name as its .type attr
        """
        msg = midi_in.poll()
        if msg is not None:
            if self._verbose:
                print(midi_in.port_id, MIDI_PORTS[midi_in.port_id], msg)
            self._route_msg_to_method(midi_in, msg)

    def _route_msg_to_method(self, midi_in: Input, msg: mido.Message):
        return getattr(self, msg.type)(midi_in, msg)

    def stop(self):
        self.running = False
        for midi_in in self._midi_ins:
            midi_in.close()

    def note_on(self, midi_in: Input, msg: mido.Message) -> None:
        pass

    def note_off(self, midi_in: Input, msg: mido.Message) -> None:
        pass

    def control_change(self, midi_in: Input, msg: mido.Message) -> None:
        pass


if __name__ == "__main__":
    MidiHandler([0, 2]).run()
