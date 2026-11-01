"""scratch_check.py — proof that drik-panchanga works for our fixed settings.

Not the final generator. Prints, for New Delhi on 2026-11-01 and 2026-11-05:
sunrise, sunset, every tithi / nakshatra / yoga / karana in force during the
Hindu day (sunrise to next sunrise) with start and end times in IST, Rahu Kaal
(checked against the 8-part rule), and the Purnimanta month and paksha.

Sunrise / sunset follow the Rashtriya Panchang (upper limb, refraction 31' +
semi-diameter 16' = centre 47' below the horizon): see sun_convention.py.

Run:  .venv\\Scripts\\python scratch_check.py      (Windows)
      .venv/bin/python scratch_check.py            (Linux / macOS)
"""

import sys
from datetime import datetime, timedelta, timezone
from math import floor

import swisseph as swe
import panchanga as dp  # drik-panchanga
import sun_convention

# Windows consoles may default to a legacy code page; "→" needs UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- Fixed settings -------------------------------------------------------
LAT, LON = 28.6139, 77.2090          # New Delhi
IST = timezone(timedelta(hours=5, minutes=30), "IST")
TZ_HOURS = 5.5
DATES = [(2026, 11, 1), (2026, 11, 5)]

dp.set_chosen_ayanamsa("lahiri")     # library default is True Chitra: override
dp.set_coordinate_mode("sidereal")
sun_convention.apply()               # Rashtriya Panchang sunrise/sunset everywhere
PLACE = dp.Place(LAT, LON, TZ_HOURS)

# --- Names (English transliteration) --------------------------------------
TITHI = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
         "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
         "Trayodashi", "Chaturdashi"]
NAKSHATRA = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
             "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
             "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
             "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
             "Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
             "Revati"]
YOGA = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
        "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
        "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
KARANA_CYCLE = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
MASA = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
        "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
WEEKDAY = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
# Rahu Kaal = which 1/8 part of the daytime (1-based), Sunday first
RAHU_PART = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}


def tithi_name(n):          # n = 1..30
    if n == 15:
        return "Shukla Purnima"
    if n == 30:
        return "Krishna Amavasya"
    return ("Shukla " if n < 15 else "Krishna ") + TITHI[(n - 1) % 15]


def karana_name(n):         # n = 1..60
    if n == 1:
        return "Kimstughna"
    if n >= 58:
        return ["Shakuni", "Chatushpada", "Naga"][n - 58]
    return KARANA_CYCLE[(n - 2) % 7]


# --- Angles from drik-panchanga (Lahiri sidereal) --------------------------
def elongation(jd):
    return dp.lunar_phase(jd)                                    # Moon - Sun, 0..360


def moon(jd):
    return dp.lunar_longitude(jd)


def sun_plus_moon(jd):
    return (dp.lunar_longitude(jd) + dp.solar_longitude(jd)) % 360


ELEMENTS = [  # (label, angle function, degrees per segment, namer)
    ("Tithi", elongation, 12.0, tithi_name),
    ("Nakshatra", moon, 360 / 27, lambda n: NAKSHATRA[n - 1]),
    ("Yoga", sun_plus_moon, 360 / 27, lambda n: YOGA[n - 1]),
    ("Karana", elongation, 6.0, karana_name),
]

HOUR = 1 / 24
SECOND = 1 / 86400


def index_at(fn, size, jd):
    return int(floor(fn(jd) / size)) + 1


def crossing(fn, size, a, b):
    """Bisect the instant in (a, b] where the segment index changes (to ~1 s)."""
    ia = index_at(fn, size, a)
    while b - a > SECOND:
        mid = (a + b) / 2
        if index_at(fn, size, mid) == ia:
            a = mid
        else:
            b = mid
    return b


def segments(fn, size, start, end):
    """Every segment in force between start and end (UT JDs) with its own
    start and end. Hourly steps are safe: the shortest element (karana) lasts
    well over 9 hours."""
    # Start of the segment in force at `start`: step back until it changes
    first = index_at(fn, size, start)
    t = start
    while index_at(fn, size, t - HOUR) == first:
        t -= HOUR
    seg_start = crossing(fn, size, t - HOUR, t)

    out, cur, t = [], first, start
    while True:
        nxt = t + HOUR
        if index_at(fn, size, nxt) != cur:
            change = crossing(fn, size, t, nxt)
            out.append((cur, seg_start, change))
            if change >= end:
                return out
            cur, seg_start = index_at(fn, size, change), change
        t = nxt


# --- Formatting: "4:12 PM", ASCII digits only -------------------------------
def to_ist(jd_ut):
    y, m, d, h = swe.revjul(jd_ut)
    return (datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)).astimezone(IST)


def clock(jd_ut, civil_day=None):
    t = to_ist(jd_ut + 30 * SECOND)            # round to the nearest minute
    text = f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"
    if civil_day is not None and t.date() != civil_day:
        text += f" ({t.day} {t.strftime('%b')})"
    return text


# --- Report -------------------------------------------------------------------
def report(y, m, d):
    jd = swe.julday(y, m, d, 0.0)              # drik-panchanga's civil-day key
    day = datetime(y, m, d).date()
    rise, sset = dp.sunrise(jd, PLACE), dp.sunset(jd, PLACE)
    next_rise = dp.sunrise(jd + 1, PLACE)
    weekday = dp.vaara(jd)

    print(f"New Delhi — {WEEKDAY[weekday]} {d} {day.strftime('%B')} {y}")
    print(f"  Sunrise   {clock(rise)}")
    print(f"  Sunset    {clock(sset)}")

    for label, fn, size, namer in ELEMENTS:
        for n, s, e in segments(fn, size, rise, next_rise):
            print(f"  {label:<9} {namer(n):<22} {clock(s, day)} → {clock(e, day)}")

    # Rahu Kaal from the library, checked against the 8-part rule
    r_start, r_end = dp.rahu_kalam(jd, PLACE)
    part = RAHU_PART[weekday]
    eighth = (sset - rise) / 8
    rule_start, rule_end = rise + (part - 1) * eighth, rise + part * eighth
    ok = abs(r_start - rule_start) < SECOND and abs(r_end - rule_end) < SECOND
    print(f"  Rahu Kaal {clock(r_start)} → {clock(r_end)}   "
          f"(rule: part {part} of 8 → {clock(rule_start)} → {clock(rule_end)}: {'OK' if ok else 'MISMATCH'})")

    # Purnimanta month and paksha at sunrise
    t_now = dp.tithi(jd, PLACE)[0]
    masa_num, adhika = dp.masa(jd, PLACE, amanta=False)
    amanta_num, _ = dp.masa(jd, PLACE, amanta=True)
    paksha = "Shukla" if t_now <= 15 else "Krishna"
    vikram = dp.elapsed_year(jd, amanta_num)[2]
    print(f"  Month     {'Adhika ' if adhika else ''}{MASA[masa_num - 1]} (Purnimanta), {paksha} paksha"
          f"   [Amanta: {MASA[amanta_num - 1]}; Vikram Samvat {vikram}]")
    print()
    return ok


if __name__ == "__main__":
    print(f"drik-panchanga · Swiss Ephemeris {swe.version} · ayanamsa Lahiri · "
          f"{LAT}, {LON} · IST (UTC+5:30)")
    print("Sunrise/sunset: Rashtriya Panchang — upper limb, centre "
          f"{-sun_convention.CENTRE_DEPRESSION_DEG * 60:.0f}' below the horizon\n")
    results = [report(*date) for date in DATES]
    print("Rahu Kaal rule check:", "all OK" if all(results) else "MISMATCH")
