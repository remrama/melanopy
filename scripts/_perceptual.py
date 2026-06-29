"""Perceptual-uniformity and CVD-recoverability checks — the §3 criteria, factored out.

These are the *exact* properties asserted for the Circadia family in
``tests/test_perceptual.py``, lifted into reusable callables so the melanopic leaderboard
(``scripts/build_figures.py``) can apply the **same** checks to every colormap without
re-deriving them. The check runs in CAM02-UCS with the Machado (2009) CVD model via
``colorspacious`` (the ``dev`` extra) — an independent perceptual space, not the OKLab
construction the generator uses, so it is not circular.

* :func:`is_pu` — perceptual uniformity: CAM02-UCS lightness ``J'`` strictly increasing and
  step-size coefficient of variation below :data:`PU_COV_THRESHOLD`.
* :func:`is_cvd_recoverable` — order recoverable under colour-vision deficiency: ``J'`` stays
  strictly increasing under full-severity deuteranomaly / protanomaly / tritanomaly.

Both also return the underlying metric (the CoV; the smallest perceived-lightness step) so a
caller can flag marginal cases. ``tests/test_perceptual.py`` imports these so the table and the
test cannot drift; the package itself never depends on them (colorspacious is dev-only).
"""

import colorspacious as cs
import numpy as np

PU_COV_THRESHOLD = 0.30
CVD_TYPES = ("deuteranomaly", "protanomaly", "tritanomaly")


def _ucs(rgb):
    """sRGB ramp -> CAM02-UCS ``(N, 3)`` array (lightness ``J'``, ``a'``, ``b'``)."""
    return cs.cspace_convert(np.clip(np.asarray(rgb, float), 0.0, 1.0), "sRGB1", "CAM02-UCS")


def _strictly_monotone(x):
    """True if ``x`` is strictly increasing **or** strictly decreasing.

    The §3 test asserts strictly *increasing* ``J'`` because every Circadia map is dark->light
    by construction; a general leaderboard ramp may run light->dark (e.g. ``Blues``), so the
    order-recoverable property is monotonicity in either direction — the same criterion without
    the sign convention.
    """
    d = np.diff(x)
    return bool(np.all(d > 0) or np.all(d < 0))


def is_pu(rgb):
    """Perceptual uniformity: strictly monotone ``J'`` and step-size CoV ``< 0.30``.

    Returns ``(ok, cov)`` — the pass/fail bool and the step-size coefficient of variation, so a
    caller can flag maps near the threshold.
    """
    u = _ucs(rgb)
    steps = np.linalg.norm(np.diff(u, axis=0), axis=1)
    cov = float(steps.std() / steps.mean())
    return (_strictly_monotone(u[:, 0]) and cov < PU_COV_THRESHOLD), cov


def is_cvd_recoverable(rgb):
    """Order recoverable under CVD: ``J'`` strictly monotone under all three simulations.

    Returns ``(ok, min_step)`` — the pass/fail bool and the smallest perceived-lightness step
    magnitude seen across deuteranomaly / protanomaly / tritanomaly (a value near zero is nearly
    non-monotone, i.e. marginal).
    """
    rgb = np.clip(np.asarray(rgb, float), 0.0, 1.0)
    ok = True
    min_step = np.inf
    for kind in CVD_TYPES:
        space = {"name": "sRGB1+CVD", "cvd_type": kind, "severity": 100}
        sim = cs.cspace_convert(rgb, space, "sRGB1")
        d = np.diff(_ucs(sim)[:, 0])
        ok = ok and _strictly_monotone(_ucs(sim)[:, 0])
        min_step = min(min_step, float(np.abs(d).min()))
    return ok, min_step
