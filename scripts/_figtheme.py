"""Shared figure palettes for the ``build_*.py`` figure scripts.

Two themes carry the *same* semantic roles, so the figure code never branches on theme —
it just reads the module globals the scripts bind via :func:`apply`:

* ``dark`` — the original dark-console look (good in dark mode / when these maps are viewed
  in the dim settings they target);
* ``light`` — a white-page print look for the manuscript PDF and the docs site's default
  (light) theme.

Roles: ``BG`` figure canvas, ``PANEL`` axes background, ``INK`` strong text/marks,
``INK2`` secondary text/ticks, ``HAIR`` spines/hairlines, ``AMBER``/``TEAL``/``BLUE`` the
protective/spread/alerting accents, ``GREY`` the neutral mid-line, ``RGB`` the per-primary
R/G/B curve colours. The colormap swatches themselves are data and never come from here.

Select with ``--theme`` on either script, or the ``MELANOPY_FIG_THEME`` env var. Light is
the default (the canonical, paper-facing look); ``--theme dark`` regenerates the dark set.
"""

import os

DARK = {
    "BG": "#181410",
    "PANEL": "#221C16",
    "INK": "#ECE3D4",
    "INK2": "#A99D89",
    "HAIR": "#3A332B",
    "AMBER": "#F2A93E",
    "TEAL": "#34C2A4",
    "BLUE": "#4A9BE8",
    "GREY": "#A99D89",
    "RGB": ("#E0573B", "#79CC70", "#4987D9"),
}

# Light mirror: accents deepened so they clear ~3:1 contrast on white; greys flipped from
# warm-cream (on dark) to warm near-black / mid-grey (on white).
LIGHT = {
    "BG": "#FFFFFF",
    "PANEL": "#F5F3EF",
    "INK": "#1B1712",
    "INK2": "#6E6353",
    "HAIR": "#CFC7B8",
    "AMBER": "#B5790E",
    "TEAL": "#1B8E78",
    "BLUE": "#2E6FB5",
    "GREY": "#7E7568",
    "RGB": ("#CF4A2C", "#2F8F43", "#3B7AC9"),
}

THEMES = {"dark": DARK, "light": LIGHT}
DEFAULT = "light"

_KEYS = ("BG", "PANEL", "INK", "INK2", "HAIR", "AMBER", "TEAL", "BLUE", "GREY")


def resolve(name=None):
    """Return ``(name, palette)`` for ``name`` (env ``MELANOPY_FIG_THEME``, then light)."""
    name = name or os.environ.get("MELANOPY_FIG_THEME") or DEFAULT
    if name not in THEMES:
        raise SystemExit(f"unknown theme {name!r}; choose from {', '.join(THEMES)}")
    return name, THEMES[name]


def apply_theme(ns, name=None):
    """Bind the palette globals (``BG``, ``INK``, ``RGB_COLS`` …) into namespace ``ns``.

    ``ns`` is a script's ``globals()``; the figure functions read these names directly, so
    rebinding here is all it takes to reskin every figure. Returns the resolved theme name.
    """
    name, t = resolve(name)
    for k in _KEYS:
        ns[k] = t[k]
    ns["RGB_COLS"] = list(t["RGB"])
    return name
