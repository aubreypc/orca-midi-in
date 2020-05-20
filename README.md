This tool allows you to sequence notes in [ORCA](https://github.com/hundredrabbits/Orca) via a MIDI controller.


## Example usage


Dump available MIDI input ports:
```
./src/orca_midi_in/sequencer/sequencer.py 0 -d
```

Bind MIDI CC inputs to ORCA variables:
```
./src/orca_midi_in/sequencer/sequencer.py 0 --controller 2 --cc 14:a 15:b 16:c
```
