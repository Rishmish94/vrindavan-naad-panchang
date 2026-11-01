# vrindavan-naad-panchang
Panchang data generator for Vrindavan Naad (New Delhi, Lahiri, Purnimanta)

**Verification:** Phase 1 output was checked against the Rashtriya Panchang
2026–27 (IMD) — all values within 1 minute. Details and open items:
[VERIFICATION.md](VERIFICATION.md).

## Running the generator

Setup once (see [Setup](#setup)), then from this folder:

```
.venv\Scripts\python generate.py          # Windows
.venv/bin/python generate.py              # Linux / macOS
```

This writes the files below and runs a self-test (about 10 seconds). It exits
with code 1 if any self-test fails.

| File | Contents |
|---|---|
| `data/panchang-2026.json` | 1 Nov – 31 Dec 2026, pretty-printed |
| `data/panchang-2026.min.json` | same, no spaces (for the website) |
| `data/panchang-2027.json` / `.min.json` | all of 2027 |
| `data/festivals-draft-2026.json`, `-2027.json` | festival draft for manual verification — **never shown on the site** |

The date ranges are set in `RANGES` at the top of `generate.py`.

### Check mode

```
.venv\Scripts\python generate.py --check 2026-11-01 2026-11-05
```

Prints those days as a readable table (no files written): sunrise, sunset,
Rahu Kaal, every tithi / nakshatra / yoga / karana with its end time, and
Bhadra. Times look like `2:52 PM`, with the date added when it falls on
another day, e.g. `1:11 PM (2 Nov)`.

### Self-test (runs after every generation)

- one entry per date, in order; sunrise before sunset, both on that date
- tithis / nakshatras / yogas / karanas cover the whole day (00:00–24:00 IST)
  with no gaps or overlaps, continuous from the previous day, and tithi
  numbers in sequence
- Rahu Kaal equals the 8-part rule (asserted for every day while generating)
  and lies within daytime
- Vikram Samvat cross-checked against drik-panchanga's own formula
- only digits 0–9 in every file; `.min.json` equals `.json`; every festival
  entry `"verified": false`
- file sizes are printed

### Panchang format

A JSON array, one object per Gregorian date (IST). Times are ISO 8601 strings
in IST rounded to the minute, e.g. `"2026-11-01T14:52:00+05:30"`.

```json
{
  "date": "2026-11-01",
  "weekday": {"en": "Sunday", "short": "Sun"},
  "vikram_samvat": 2083,
  "masa": {"dev": "कार्तिक", "en": "Kartik", "system": "purnimanta"},
  "paksha": {"dev": "कृष्ण पक्ष", "en": "Krishna Paksha"},
  "sunrise": "2026-11-01T06:33:00+05:30",
  "sunset": "2026-11-01T17:36:00+05:30",
  "tithis": [
    {"num": 22, "dev": "कृष्ण सप्तमी", "en": "Krishna Saptami",
     "start": "2026-10-31T16:58:00+05:30", "end": "2026-11-01T14:52:00+05:30"},
    {"num": 23, "dev": "कृष्ण अष्टमी", "en": "Krishna Ashtami",
     "start": "2026-11-01T14:52:00+05:30", "end": "2026-11-02T13:11:00+05:30"}
  ],
  "nakshatras": [{"dev": "पुनर्वसु", "en": "Punarvasu", "start": "…", "end": "…"}, …],
  "yogas": [{"dev": "साध्य", "en": "Sadhya", "start": "…", "end": "…"}, …],
  "karanas": [{"dev": "विष्टि", "en": "Vishti", "start": "…", "end": "…"}, …],
  "rahu_kaal": {"start": "2026-11-01T16:13:00+05:30", "end": "2026-11-01T17:36:00+05:30"},
  "bhadra": [{"start": "2026-10-31T16:58:00+05:30", "end": "2026-11-01T03:52:00+05:30"}]
}
```

- **tithis / nakshatras / yogas / karanas**: every one in force at any moment
  of the date (00:00–24:00 IST), in order, with true start and end (start may
  be on the previous day, end on the next).
- **tithi `num`**: 1–15 = Shukla Pratipada … Purnima; 16–30 = Krishna
  Pratipada … Amavasya.
- **masa, paksha**: as at sunrise. An adhika month is prefixed
  `"अधिक "` / `"Adhik "`.
- **vikram_samvat**: changes at Chaitra Shukla Pratipada (7 April 2027 → 2084).
- **rahu_kaal**: daytime (sunrise → sunset) in 8 equal parts; Mon 2, Sat 3,
  Fri 4, Wed 5, Thu 6, Tue 7, Sun 8.
- **bhadra**: every Vishti karana overlapping the date — listed on both days if
  it crosses midnight; `[]` = none.

### Festival draft format

A JSON array sorted by date:
`{"date", "dev", "en", "type": "festival" | "vrat", "verified": false}`.
Ekadashi entries also have `"smarta_date"` and `"vaishnava_date"` (always
both; `"date"` = Smarta date).

- Festivals come from drik-panchanga's rule catalogue, fed with our sunrise.
  The catalogue leans South Indian (Ugadi, Onam, Upakarma) and mostly uses
  the **tithi-at-sunrise** rule, so festivals that follow another time of
  day need manual checking — e.g. **Deepavali 2026 comes out as 9 Nov
  (Amavasya at sunrise); North Indian Lakshmi Puja follows pradosh-kaal
  Amavasya (8 Nov)**. Same caution for Naraka Chaturdashi, Holika Dahan,
  Janmashtami (midnight), Maha Shivaratri (nishita), Karwa Chauth (moonrise).
- Ekadashi **Smarta**: the first day Ekadashi prevails at sunrise; if it
  prevails at no sunrise (kshaya), the next day (same as drik-panchanga,
  asserted). **Vaishnava**: Ekadashi must already prevail at arunodaya
  (96 minutes before sunrise) — otherwise it is Dashami-viddha and moves to
  the next day — and if it prevails at two sunrises, the second day.
  Names follow the Purnimanta month (Parama / Padmini in an adhika month).

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
