from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Dict


@dataclass
class SequencerConfig:
    midi_port: int
    cc: Dict[int, str] = None
    verbosity: int = 0
    with_midi_operator: bool = True
    with_midi_cc_operator: bool = False
    with_length: bool = True
    with_octave: bool = True
    with_velocity: bool = True


class SequencerConfigBuilder(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("midi_port", type=int,
                          help="The MIDI port from which to read")
        self.add_argument("-v", action="count", default=0, dest="verbosity",
                          help="Increments verbosity level. Level 1 logs Orca commands; level 2 also logs MIDI events")
        self.add_argument("--cc", nargs="*", type=str, default=None,
                          help="Maps MIDI CC values to Orca variables, e.g. --cc 14:a")
        self.add_argument("--bpm", type=int, default=120,
                          help="The beats per minute of the track")
        self.add_argument("-nm", "--pitch-only", action="store_false", dest="with_midi_operator",
                          help="Disables sequencing of MIDI operators. When present, only sequences the note value.")
        self.add_argument("-nc", "--val-only", action="store_false", dest="with_midi_operator",
                          help="Disables sequencing of MIDI operators. When present, only sequences the CC value.")
        self.add_argument("-nl", "--no_length", action="store_false", dest="with_length",
                          help="Disables sequencing of note length in MIDI operators")
        self.add_argument("-no", "--no_octave", action="store_false", dest="with_octave",
                          help="Disables sequencing of note octave in MIDI operators")
        self.add_argument("-nv", "--no_velocity", action="store_false", dest="with_velocity",
                          help="Disables sequencing of note velocity in MIDI operators")


    @staticmethod
    def _transform(config: SequencerConfig) -> SequencerConfig:
        # Convert --cc map strings to dict
        if config.cc:
            pairs = (pair.split(":") for pair in config.cc)
            config.cc = {int(cc_id): var for cc_id, var in pairs}
        else:
            config.cc = dict()
        return config

    def build(self) -> SequencerConfig:
        config = self.parse_args(namespace=SequencerConfig)
        return self._transform(config)


if __name__ == "__main__":
    seq_config = SequencerConfigBuilder().build()
    print(repr(seq_config))
