# vrindavan-naad-panchang
Panchang data generator for Vrindavan Naad (New Delhi, Lahiri, Purnimanta)

## Library choice

### Fixed settings

| Setting | Value |
|---|---|
| Location | New Delhi — latitude 28.6139, longitude 77.2090 |
| Time zone | Asia/Kolkata (IST, UTC+5:30) |
| Ayanamsa | Lahiri (Chitrapaksha) |
| Month system | Purnimanta (North Indian month names) |
| Sunrise / sunset | Rashtriya Panchang convention (below) |
| Cost | ₹0 — free, open-source libraries only, no paid APIs |

### Sunrise / sunset convention

Sunrise and sunset follow the **Rashtriya Panchang** (Indian national
calendar): the appearance / disappearance of the Sun's **upper limb** on the
horizon, with standard atmospheric refraction — refraction 31' + semi-diameter
16' = the Sun's **centre 47' below the true horizon**.

This replaces drik-panchanga's default (classical Hindu rising: disc centre on
the horizon, no refraction, about 4 minutes later at sunrise and earlier at
sunset in Delhi). `sun_convention.py` installs it with `sun_convention.apply()`,
so it is used everywhere sunrise or sunset matters: day boundaries
(sunrise to next sunrise), tithi / nakshatra / yoga / karana at sunrise, masa,
Rahu Kaal and the other kalams, and festival rules. Moonrise/moonset are not
affected. Tithi / nakshatra / yoga / karana end times do not depend on it.

Reference check, New Delhi, against the Rashtriya Panchang 2026-27:

| Date | Rashtriya Panchang sunrise / sunset | This generator |
|---|---|---|
| 1 Nov 2026 | 6:33 AM / 5:36 PM | 6:33 AM / 5:36 PM |
| 5 Nov 2026 | 6:36 AM / 5:33 PM | 6:36 AM / 5:33 PM |

Rahu Kaal is rechecked against the 8-part rule with these times in
`scratch_check.py` (1 Nov, Sunday, part 8: 4:13 PM → 5:36 PM; 5 Nov, Thursday,
part 6: 1:27 PM → 2:49 PM).

### Comparison (checked 1 November 2026)

| | **drik-panchanga** 2.0.0 | **kaalavidya** 0.3.2 | **Kalagana** 0.1.3 |
|---|---|---|---|
| Published | PyPI + GitHub (`bdsatish/drik-panchanga`) | PyPI only — listed GitHub repo returns 404 | PyPI + GitHub (`mitjangid/Kalagana`) |
| Licence | AGPL-3.0-or-later ✅ same as ours | MIT ✅ (but uses AGPL Swiss Ephemeris) | MIT ✅ |
| Maintained | ✅ release Oct 2026, commits Oct 2026 | ⚠️ last release Feb 2026, source not public | ⚠️ new (Oct 2026), single author, 1 star |
| Engine | Swiss Ephemeris | Swiss Ephemeris | Own Meeus code, no Swiss Ephemeris |
| Tithi / nakshatra / yoga / karana with times | ✅ value at sunrise + end time; we add a small transition finder for all starts/ends | ✅ all transitions with end times | ⚠️ start + end given, but **missed transitions** (Pushya → Ashlesha 2 Nov 4:30 AM; Vaidhriti → Vishkambha 6 Nov 5:09 AM) |
| Sunrise / sunset | ✅ (default classical Hindu: disc centre, no refraction; we switch it to the Rashtriya Panchang convention) | ✅ (classical and apparent) | ✅ (apparent) |
| Rahu Kaal | ✅ matches the 8-part rule | ✅ | ✅ |
| Purnimanta month names | ✅ `masa(amanta=False)` | ✅ | ✅ |
| Vikram Samvat | ✅ from Kali-day count | ⚠️ fixed year offset | ✅ |
| Festival rules | ✅ most complete: Ekadashi upavasa + parana (kshaya/vriddhi), many festivals (South-Indian leaning); no explicit Smarta/Vaishnava switch | ❌ none | ⚠️ rule table, Ekadashi on one arunodaya rule; no Smarta/Vaishnava switch |
| Lahiri + custom location/time zone | ✅ (default is True Chitra — must set `lahiri`) | ✅ (Lahiri fixed) | ✅ |
| Ease of use | ⚠️ function-level API, installs generic top-level modules (`panchanga`, `config`, `data`) | ✅ one `Panchanga(...).compute()` call | ✅ one `daily_panchang()` call |

Cross-check: for 1 and 5 November 2026 the two Swiss Ephemeris libraries agree
to within 1 minute on every tithi, nakshatra and yoga end time; Kalagana's
independent maths agrees to within about 2 minutes where it finds a transition.

### Choice: drik-panchanga (with pysweph)

- **Licence fits exactly**: AGPL-3.0, same as this repository and Swiss Ephemeris.
- **Actively maintained**, source and issue tracker public.
- **Most complete** for what the website needs next: Purnimanta months, Vikram
  Samvat, Rahu Kaal and the richest festival / Ekadashi rules.
- **Accurate**: Swiss Ephemeris, confirmed against kaalavidya.
- Gaps we cover with our own small code: listing every tithi / nakshatra /
  yoga / karana in a day with start and end (see `scratch_check.py`), and
  Smarta/Vaishnava Ekadashi selection (to be added in the generator).
- Swiss Ephemeris comes from **pysweph**, the maintained fork of pyswisseph
  (same `import swisseph`), because pyswisseph has no wheels for Python 3.12+.

Swiss Ephemeris is AGPL-licensed; this generator is public to comply. Not legal advice.

### Setup

```
python -m venv .venv
.venv\Scripts\python -m pip install --no-deps -r requirements.txt     # Windows
.venv/bin/python -m pip install --no-deps -r requirements.txt         # Linux / macOS
```

`--no-deps` is required: see the note at the top of `requirements.txt`.

### Proof script

```
.venv\Scripts\python scratch_check.py      # Windows
.venv/bin/python scratch_check.py          # Linux / macOS
```

Prints sunrise, sunset (Rashtriya Panchang convention), every tithi /
nakshatra / yoga / karana with start and end times (IST), Rahu Kaal checked
against the 8-part rule, and the Purnimanta month and paksha for New Delhi on
1 and 5 November 2026.
