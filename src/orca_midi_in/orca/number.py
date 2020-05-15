NUMBERS = "0123456789abcdefghijklmnopqrstuvwxyz"


def midi_to_base_36(n: int, min: int = 0) -> str:
    if n == 0:
        return "0"
    n = max(int((n / 127) * 36) - 1, min)
    return NUMBERS[n]


def seconds_to_frames(seconds: float, bpm: int, frames_per_beat: int = 8) -> str:
    bps = bpm / 60
    fps = bps * frames_per_beat
    frames = min(int(seconds * fps), 35)
    return NUMBERS[frames]
