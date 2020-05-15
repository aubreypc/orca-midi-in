from orca_midi_in.midi.midi_handler import MidiHandler, MidiEvent
from orca_midi_in.orca.forward import OrcaCommandForwarder


class OrcaMidiInputSequencer(MidiHandler):
    def __init__(self, port: int):
        self.forwarder = OrcaCommandForwarder()
        super().__init__(port)

    def note_off(self, event: MidiEvent) -> None:
        self.forwarder.write_midi_note(event, with_midi_operator=True)

    def cc(self, event: MidiEvent):
        self.forwarder.write_midi_cc(event, with_midi_cc_operator=True)


if __name__ == "__main__":
    with OrcaMidiInputSequencer(0) as seq:
        while True:
            pass
