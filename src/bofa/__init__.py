from __future__ import annotations

import argparse
import os
import random
import shutil
import sys
from typing import Final

from terminaltexteffects.utils.graphics import Color, Gradient
from terminaltexteffects.effects.effect_colorshift import (
    ColorShift,
    ColorShiftConfig,
)
from terminaltexteffects.effects.effect_fireworks import (
    Fireworks,
    FireworksConfig,
)
from terminaltexteffects.effects.effect_highlight import (
    Highlight,
    HighlightConfig,
)
from terminaltexteffects.effects.effect_spotlights import (
    Spotlights,
    SpotlightsConfig,
)
from terminaltexteffects.effects.effect_spray import Spray, SprayConfig
from terminaltexteffects.effects.effect_vhstape import VHSTape, VHSTapeConfig
from terminaltexteffects.engine.base_effect import BaseEffect
from terminaltexteffects.engine.terminal import TerminalConfig
from terminaltexteffects.utils.argutils import CharacterGroup

BOFA = b"\x42\x6f\x66\x61\x20\x64\x65\x65\x7a\x20\x6e\x75\x74\x73"
CELEBRATE = b"\x42\x4f\x46\x41\x20\x44\x45\x45\x5a\x20\x4e\x55\x54\x53\x21\x21\x21"
PREFIX = BOFA[:4]
ASCII_CONFETTI_CHARS: Final[str] = "*+x~^@"
UNICODE_CONFETTI_CHARS: Final[str] = "✦✧❖✺✹✷✸✶✱✲✳✴✵✼✽❇❈❉❊" + ASCII_CONFETTI_CHARS
RAINBOW_STOPS: Final[tuple[Color, ...]] = (
    Color("#e81416"),
    Color("#ffa500"),
    Color("#faeb36"),
    Color("#79c314"),
    Color("#487de7"),
    Color("#4b369d"),
    Color("#70369d"),
)


def _unicode_ok() -> bool:
    encoding = sys.stdout.encoding
    if not encoding:
        return False
    try:
        "✦❖✺".encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


def _confetti_border(width: int, rng: random.Random, unicode_ok: bool) -> str:
    charset = UNICODE_CONFETTI_CHARS if unicode_ok else ASCII_CONFETTI_CHARS
    return "".join(rng.choice(charset) for _ in range(width))


def _make_intro_text(width: int, rng: random.Random, unicode_ok: bool) -> str:
    border = _confetti_border(width, rng, unicode_ok)
    prefix = PREFIX.decode("utf-8")
    question = f"HAVE YOU HEARD OF {prefix}?"
    if unicode_ok and width >= len(question) + 4:
        question = f"✦ {question} ✦"
    return "\n".join(
        [
            border,
            question.center(width),
            border,
        ],
    )


def _make_punchline_text(
    width: int,
    rng: random.Random,
    unicode_ok: bool,
) -> str:
    border = _confetti_border(width, rng, unicode_ok)
    punchline = CELEBRATE.decode("utf-8")

    if unicode_ok and width >= len(punchline) + 4:
        punchline = f"❇ {punchline} ❇"

    return "\n".join(
        [
            border,
            punchline.center(width),
            border,
        ],
    )


def _build_terminal_config() -> TerminalConfig:
    terminal_config = TerminalConfig._build_config()
    terminal_config.frame_rate = 90
    terminal_config.canvas_width = 0
    terminal_config.canvas_height = 0
    terminal_config.anchor_canvas = "c"
    terminal_config.anchor_text = "c"
    terminal_config.reuse_canvas = True
    return terminal_config


def _play(effect: BaseEffect, rng: random.Random) -> None:
    random.seed(rng.randrange(2**32))
    with effect.terminal_output() as terminal:
        for frame in effect:
            terminal.print(frame)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moon", action="store_true")
    args = parser.parse_args()

    msg = BOFA.decode("utf-8")
    if not sys.stdout.isatty() or os.environ.get("TERM", "").lower() == "dumb":
        print(msg)
        return

    if args.moon:
        from bofa.moon import play_moon
        play_moon()
        return

    rng = random.Random()
    unicode_ok = _unicode_ok()
    width = _pick_width()
    terminal_config = _build_terminal_config()

    try:
        _play_intro(
            width=width,
            rng=rng,
            terminal_config=terminal_config,
            unicode_ok=unicode_ok,
        )

        if rng.random() < 0.75:
            _play_interlude(
                width=width,
                rng=rng,
                terminal_config=terminal_config,
                unicode_ok=unicode_ok,
            )
    except KeyboardInterrupt:
        print(msg)
        return

    fireworks_config = FireworksConfig._build_config()
    fireworks_config.explode_anywhere = True
    fireworks_config.launch_delay = 12
    fireworks_config.firework_volume = 0.12
    fireworks_config.firework_colors = RAINBOW_STOPS
    fireworks_config.firework_symbol = rng.choice(
        _firework_symbols(unicode_ok),
    )
    fireworks_config.final_gradient_stops = RAINBOW_STOPS
    fireworks_config.final_gradient_direction = Gradient.Direction.HORIZONTAL
    punchline = _make_punchline_text(
        width=width,
        rng=rng,
        unicode_ok=unicode_ok,
    )
    try:
        _play(Fireworks(punchline, fireworks_config, terminal_config), rng)
        _play_spotlights_finale(
            text=punchline,
            rng=rng,
            terminal_config=terminal_config,
        )
        _play_glitter(
            text=punchline,
            rng=rng,
            terminal_config=terminal_config,
        )
    except KeyboardInterrupt:
        print(msg)
        return

def _play_intro(
    *,
    width: int,
    rng: random.Random,
    terminal_config: TerminalConfig,
    unicode_ok: bool,
) -> None:
    intro = _make_intro_text(width=width, rng=rng, unicode_ok=unicode_ok)

    roll = rng.random()
    if roll < 0.34:
        intro_config = ColorShiftConfig._build_config()
        intro_config.cycles = 2
        intro_config.gradient_frames = 1
        intro_config.gradient_stops = RAINBOW_STOPS
        intro_config.travel_direction = Gradient.Direction.HORIZONTAL
        intro_config.final_gradient_stops = RAINBOW_STOPS
        intro_config.final_gradient_direction = Gradient.Direction.HORIZONTAL
        _play(ColorShift(intro, intro_config, terminal_config), rng)
        return

    if roll < 0.67:
        spotlight_config = SpotlightsConfig._build_config()
        spotlight_config.search_duration = 160
        spotlight_config.spotlight_count = 4
        spotlight_config.final_gradient_stops = RAINBOW_STOPS
        spotlight_config.final_gradient_direction = Gradient.Direction.RADIAL
        _play(Spotlights(intro, spotlight_config, terminal_config), rng)
        return

    spray_config = SprayConfig._build_config()
    spray_config.spray_position = rng.choice(
        ("n", "ne", "e", "se", "s", "sw", "w", "nw", "center"),
    )
    spray_config.spray_volume = 0.08
    spray_config.movement_speed_range = (0.8, 2.2)
    spray_config.final_gradient_stops = RAINBOW_STOPS
    spray_config.final_gradient_direction = Gradient.Direction.HORIZONTAL
    _play(Spray(intro, spray_config, terminal_config), rng)


def _play_interlude(
    *,
    width: int,
    rng: random.Random,
    terminal_config: TerminalConfig,
    unicode_ok: bool,
) -> None:
    border = _confetti_border(width, rng, unicode_ok)
    prefix = PREFIX.decode("utf-8")
    line_1 = f"...{prefix} {prefix} {prefix}..."
    if unicode_ok and width >= len(line_1) + 4:
        line_1 = f"✧ {line_1} ✧"
    interlude = "\n".join(
        [
            border,
            line_1.center(width),
            border,
        ],
    )

    glitch_config = VHSTapeConfig._build_config()
    glitch_config.total_glitch_time = 140
    glitch_config.glitch_line_chance = 0.22
    glitch_config.noise_chance = 0.03
    glitch_config.glitch_line_colors = (
        Color("#ffffff"),
        *RAINBOW_STOPS,
        Color("#ffffff"),
    )
    glitch_config.glitch_wave_colors = glitch_config.glitch_line_colors
    glitch_config.final_gradient_stops = RAINBOW_STOPS
    glitch_config.final_gradient_direction = Gradient.Direction.HORIZONTAL
    _play(VHSTape(interlude, glitch_config, terminal_config), rng)


def _play_glitter(
    *,
    text: str,
    rng: random.Random,
    terminal_config: TerminalConfig,
) -> None:
    glitter_config = HighlightConfig._build_config()
    glitter_config.highlight_brightness = 2.6
    glitter_config.highlight_width = 14
    glitter_config.highlight_direction = rng.choice(
        (
            CharacterGroup.DIAGONAL_BOTTOM_LEFT_TO_TOP_RIGHT,
            CharacterGroup.DIAGONAL_BOTTOM_RIGHT_TO_TOP_LEFT,
            CharacterGroup.DIAGONAL_TOP_LEFT_TO_BOTTOM_RIGHT,
            CharacterGroup.DIAGONAL_TOP_RIGHT_TO_BOTTOM_LEFT,
        ),
    )
    glitter_config.final_gradient_stops = RAINBOW_STOPS
    glitter_config.final_gradient_direction = Gradient.Direction.HORIZONTAL
    _play(Highlight(text, glitter_config, terminal_config), rng)


def _play_spotlights_finale(
    *,
    text: str,
    rng: random.Random,
    terminal_config: TerminalConfig,
) -> None:
    spotlight_config = SpotlightsConfig._build_config()
    spotlight_config.search_duration = 120
    spotlight_config.search_speed_range = (0.7, 1.4)
    spotlight_config.spotlight_count = 5
    spotlight_config.beam_width_ratio = 1.25
    spotlight_config.beam_falloff = 0.25
    spotlight_config.final_gradient_stops = RAINBOW_STOPS
    spotlight_config.final_gradient_direction = Gradient.Direction.RADIAL
    _play(Spotlights(text, spotlight_config, terminal_config), rng)


def _firework_symbols(unicode_ok: bool) -> tuple[str, ...]:
    if unicode_ok:
        return ("✦", "✧", "❇", "❈", "✺", "*", "+", "x")
    return ("o", "*", "+", "x")


def _pick_width() -> int:
    columns = shutil.get_terminal_size(fallback=(80, 24)).columns
    target = columns - 2
    if target <= 0:
        target = columns
    return max(34, min(target, 120))
