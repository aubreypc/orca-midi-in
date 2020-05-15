from orca_midi_in.midi.midi_handler import MidiHandler, MidiEvent
from orca_midi_in.orca.forward import OrcaCommandForwarder
from orca_midi_in.orca.number import midi_to_base_36
from orca_midi_in.sequencer.config import SequencerConfig, SequencerConfigBuilder


class OrcaMidiInputSequencer(MidiHandler):
    def __init__(self, config: SequencerConfig):
        self._config = config
        self.forwarder = OrcaCommandForwarder(verbose=config.verbosity >= 1)
        super().__init__(config.midi_port, verbose=config.verbosity >= 2)

    def note_on(self, event: MidiEvent) -> None:
        # TODO: allow play/stop buttons to send play/stop commands. On my controller, these are ch 1 A#5 / A5.
        # TODO: allow buttons to be mapped to inject commands
        pass

    def note_off(self, event: MidiEvent) -> None:
        """
        Sequence a MIDI operator at the current cursor position.
        """
        self.forwarder.write_midi_note(
            event,
            with_midi_operator=self._config.with_midi_operator,
            with_length=self._config.with_length,
            with_octave=self._config.with_octave,
            with_velocity=self._config.with_velocity,
        )

    def cc(self, event: MidiEvent):
        """
        If the event's CC number is mapped to a variable, update the variable declaration.
        Otherwise, insert a MIDI CC operator at the current cursor position.
        """
        # TODO: updating CC on *every* event is quite laggy -- is there a better way?
        if self._config.cc and event.key in self._config.cc:
            variable = self._config.cc[event.key]
            value = midi_to_base_36(event.value)
            self.forwarder.find(f"{variable}V")
            self.forwarder.write(f"{variable}V{value}")
        else:
            self.forwarder.write_midi_cc(
                event,
                with_midi_cc_operator=self._config.with_midi_operator
            )


if __name__ == "__main__":
    config = SequencerConfigBuilder().build()
    with OrcaMidiInputSequencer(config) as seq:
        while True:
            pass
