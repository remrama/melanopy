"""Lock the baked representative coefficients to the primary SPD model.

The numbers in ``coeffs.PANELS["representative"]`` are not free parameters: they are the
output of ``coefficients_from_primaries(representative_primaries())`` rounded to 4 dp. This
asserts they still are, so the hand-baked constants and the model can't silently diverge.

Skipped when the vendored CIE ``data/`` tables are absent (``melanopy.spectra`` reads them
at import); see ``src/melanopy/data/NOTICE.md``.
"""

import pytest

from melanopy.coeffs import PANELS

try:
    from melanopy import spectra
except (FileNotFoundError, ImportError):  # vendored CIE data/ not present
    spectra = None


@pytest.mark.skipif(spectra is None, reason="vendored CIE data/ not present")
def test_representative_coeffs_match_primary_model():
    derived = spectra.coefficients_from_primaries(spectra.representative_primaries())
    assert {k: round(v, 4) for k, v in derived.items()} == PANELS["representative"]
