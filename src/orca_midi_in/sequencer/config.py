from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Dict

from orca_midi_in.sequencer.location import Location, LocationManager


@dataclass
class SequencerConfig:
    midi_port: int
    midi_controller_port: int = None
    list_devices: bool = False
    cc: Dict[int, str] = None
    verbosity: int = 0
    with_midi_operator: bool = True
    with_midi_cc_operator: bool = False
    with_length: bool = True
    with_octave: bool = True
    with_velocity: bool = True
    locations: LocationManager = None
    next_location: int = None
    prev_location: int = None
    scroll_location: int = None
    play: int = None
    stop: int = None
    quiet: bool = False


class SequencerConfigBuilder(ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument("midi_port", type=int,
                          help="The MIDI port from which to read when sequencing")
        self.add_argument("--controller", type=int, default=None, dest="midi_controller_port",
                          help="The MIDI port to use for controller messages")
        self.add_argument("-d", action="store_true", dest="list_devices",
                          help="List available MIDI ports and exit")
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
        self.add_argument("-l", "--location", nargs="*", type=str, default=None, dest="locations",
                          help="Specifies a note sequencing location, e.g. -l 0;10;8 sets x=0 y=10 with height 8")
        self.add_argument("-ln", "--next-location", type=int, default=None, dest="next_location",
                          help="Specifies a MIDI binding for jumping to the next location")
        self.add_argument("-lp", "--prev-location", type=int, default=None, dest="prev_location",
                          help="Specifies a MIDI binding for jumping to the previous location")
        self.add_argument("-ls", "--scroll-location", type=int, default=None, dest="scroll_location",
                          help="Specifies a MIDI CC binding for scrolling through the notes in a location")
        self.add_argument("-p", "--play", type=int, default=None, dest="play",
                          help="Specifies a MIDI binding for resuming playback")
        self.add_argument("-s", "--stop", type=int, default=None, dest="stop",
                          help="Specifies a MIDI binding for stopping plaback")
        self.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                          help="Disables playback upon running the script")

    @staticmethod
    def _transform(config: SequencerConfig) -> SequencerConfig:
        config.midi_ports = [config.midi_port]
        if config.midi_controller_port is not None:
            config.midi_ports.append(config.midi_controller_port)
        # Convert --cc map strings to dict
        if config.cc:
            pairs = (pair.split(":") for pair in config.cc)
            config.cc = {int(cc_id): var for cc_id, var in pairs}
        else:
            config.cc = dict()
        # Convert location coords into LocationManager
        if config.locations:
            locations = []
            for loc_str in config.locations:
                params = loc_str.split(";")
                x, y = params[0], params[1]
                if len(params) == 3:
                    height = params[2]
                    locations.append(Location(int(x), int(y), int(height)))
                    continue
                locations.append(Location(int(x), int(y)))
            config.locations = LocationManager(locations)
        return config

    def build(self) -> SequencerConfig:
        config = self.parse_args(namespace=SequencerConfig)
        return self._transform(config)


if __name__ == "__main__":
    seq_config = SequencerConfigBuilder().build()
    print(repr(seq_config))
