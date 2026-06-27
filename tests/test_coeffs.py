"""Lock every baked panel coefficient set to its primary SPD model.

The numbers in ``coeffs.PANELS`` are not free parameters: each is the output of
``coefficients_from_primaries(panel_primaries(kind))`` rounded to 4 dp. This asserts they
still are, so the hand-baked constants and the panel models can't silently diverge.

Skipped when the vendored CIE ``data/`` tables are absent (``melanopy.spectra`` reads them at
import); see ``src/melanopy/data/NOTICE.md``.
"""

import pytest

from melanopy.coeffs import PANELS

try:
    from melanopy import spectra
except (FileNotFoundError, ImportError):  # vendored CIE data/ not present
    spectra = None

PANEL_KINDS = getattr(spectra, "PANEL_KINDS", ("representative",))


@pytest.mark.skipif(spectra is None, reason="vendored CIE data/ not present")
@pytest.mark.parametrize("kind", PANEL_KINDS)
def test_panel_coeffs_match_primary_model(kind):
    derived = spectra.coefficients_from_primaries(spectra.panel_primaries(kind))
    assert {k: round(v, 4) for k, v in derived.items()} == PANELS[kind]
