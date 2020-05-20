import sys

import mido
from mido.backends.rtmidi import Input

from orca_midi_in.midi.midi_handler import MidiHandler, MIDI_PORTS
from orca_midi_in.orca.forward import OrcaCommandForwarder
from orca_midi_in.orca.number import midi_to_base_36
from orca_midi_in.sequencer.config import SequencerConfig, SequencerConfigBuilder


class OrcaMidiInputSequencer(MidiHandler):
    def __init__(self, config: SequencerConfig):
        self._config = config
        self.forwarder = OrcaCommandForwarder(verbose=config.verbosity >= 1, quiet=config.quiet)
        super().__init__(config.midi_ports, verbose=config.verbosity >= 2)

    def _route_msg_to_method(self, midi_in: Input, msg: mido.Message):
        prefix = "seq" if midi_in.port_id == self._config.midi_port else "controller"
        attr = f"{prefix}_{msg.type}"
        if hasattr(self, attr):
            return getattr(self, attr)(msg)

    def controller_note_on(self, msg: mido.Message):
        # TODO: allow buttons to be mapped to inject commands
        if msg.velocity == 0:
            return
        if self._config.locations and msg.note == self._config.next_location:
            self._config.locations.next()
            self.forwarder.select(*self._config.locations.current.position)
        elif msg.note == self._config.play:
            self.forwarder.send_cmd("play")
        elif msg.note == self._config.stop:
            self.forwarder.send_cmd("stop")

    def seq_note_on(self, msg: mido.Message) -> None:
        print(msg)

    def seq_note_off(self, msg: mido.Message) -> None:
        """
        Sequence a MIDI operator at the next position in the current location, or the current cursor position.
        """
        x, y = None, None
        if self._config.locations:
            x, y = self._config.locations.current.position
        self.forwarder.write_midi_note(
            msg,
            x,
            y,
            with_midi_operator=self._config.with_midi_operator,
            with_length=self._config.with_length,
            with_octave=self._config.with_octave,
            with_velocity=self._config.with_velocity,
        )
        if self._config.locations:
            new_x, new_y = self._config.locations.current.scroll()
            self.forwarder.select(new_x, new_y)

    def seq_control_change(self, msg: mido.Message):
        """
        If the event's CC number is mapped to a variable, update the variable declaration.
        Otherwise, insert a MIDI CC operator at the current cursor position.
        """
        if self._config.cc and msg.control in self._config.cc:
            variable = self._config.cc[msg.control]
            value = midi_to_base_36(msg.value)
            self.forwarder.find(f"{variable}V")
            self.forwarder.write(f"{variable}V{value}")
        else:
            self.forwarder.write_midi_cc(
                msg,
                with_midi_cc_operator=self._config.with_midi_operator
            )

    def controller_control_change(self, msg: mido.Message):
        if self._config.locations and msg.control == self._config.scroll_location:
            new_x, new_y = self._config.locations.current.scroll(cc=msg.value)
            self.forwarder.select(new_x, new_y)


if __name__ == "__main__":
    cfg = SequencerConfigBuilder().build()
    if cfg.list_devices:
        print("\n".join(MIDI_PORTS))
        sys.exit(0)
    OrcaMidiInputSequencer(cfg).run()
