from __future__ import annotations


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def interpolate_color(start: str, end: str, factor: float) -> str:
    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)
    channels = [round(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * factor) for i in range(3)]
    return "#" + "".join(f"{channel:02x}" for channel in channels)
