# Vendored spectral data — provenance & licensing

The files in this directory are **CIE reference data tables**, licensed by CIE under
**CC BY-SA 4.0** (see *Licensing* below). They are bundled with — but **not** covered by —
Melanopy's MIT license, which applies to the code only.

## Files

### `cie_s026_actionspectra.csv`
CIE S 026:2018 *α-opic action spectra* (columns: `nm, sc, mc, lc, rh, mel`). The **`mel`**
column — the melanopic action spectrum — is the one consumed by the rater; the others are
included as-published. Each spectrum is normalised to a peak of 1.0 (melanopic peaks at
490 nm), with `NaN` outside each photoreceptor's defined range.

- **Primary source:** CIE S 026/E:2018, *CIE System for Metrology of Optical Radiation for
  ipRGC-Influenced Responses to Light*, Table 2.
- **Data table:** CIE 2018, *CIE α-opic action spectra*, International Commission on
  Illumination (CIE), Vienna, AT. DOI: [10.25039/CIE.DS.vqqhzp5a](https://doi.org/10.25039/CIE.DS.vqqhzp5a)
- **Source file:** <https://files.cie.co.at/CIE_a-opic_action_spectra.csv> (380–780 nm).
- **Changes:** values verbatim (verified identical to the CIE source); reformatted only by
  adding the header row and padding the grid to 360–830 nm with `NaN`.

### `ciexyz_1931_2.dat`
CIE 1931 2° standard colorimetric observer colour-matching functions (columns:
`nm, x̄, ȳ, z̄`); **ȳ = V(λ)**, the photopic luminous efficiency function (ȳ(555 nm) = 1.0
by definition). 360–830 nm at 1 nm.

- **Primary source:** CIE 1931 2° standard colorimetric observer (ISO/CIE 11664-1).
- **Data table:** CIE 2019, *Colour-matching functions of CIE 1931 standard colorimetric
  observer*, International Commission on Illumination (CIE), Vienna, AT. DOI:
  [10.25039/CIE.DS.xvudnb9b](https://doi.org/10.25039/CIE.DS.xvudnb9b)
- **Source file:** <https://files.cie.co.at/CIE_xyz_1931_2deg.csv> (values verbatim; stored
  with a `.dat` extension, no header).

## Licensing

Both tables are © CIE and published under the **Creative Commons Attribution-ShareAlike 4.0
International (CC BY-SA 4.0)** license — <https://creativecommons.org/licenses/by-sa/4.0/> —
per each dataset's metadata at files.cie.co.at. CC BY-SA 4.0 **permits redistribution**
(including bundling here) provided the work is attributed, the license is named/linked, and
changes are indicated — all done above.

- **Code vs. data.** Melanopy's MIT license covers its source. These data files keep their
  CC BY-SA 4.0 license. Bundling a CC-licensed file alongside separately-licensed code is a
  *collection* under CC BY-SA 4.0 §1(b)/§4 — it does **not** place the code under CC BY-SA.
- **ShareAlike.** Only *adaptations* of the data must themselves be CC BY-SA. The bundled
  files are unmodified (value-verbatim). The three per-primary coefficients baked into
  `melanopy.coeffs` are factual scalars derived jointly from these spectra and Melanopy's own
  primary model (`melanopy.spectra.representative_primaries`); they are treated as
  non-copyrightable measurements, not a creative adaptation.

This is the project's good-faith provenance record, not formal legal advice.

> Note: runtime fetching (e.g. via `pooch`) would only avoid shipping these ~25 KB files —
> which CC BY-SA 4.0 already permits — while adding a network/offline dependency and not
> changing the coefficient-derivation question above. Melanopy's rater/generator never read
> these files; only `melanopy.spectra` does, to derive the coefficients in `melanopy.coeffs`.
