"""generate.py — Vrindavan Naad panchang data generator.

Fixed settings: New Delhi (28.6139, 77.2090, Asia/Kolkata), Lahiri ayanamsa,
Purnimanta months, Rashtriya Panchang sunrise/sunset (sun_convention.py).
Calculations: drik-panchanga on Swiss Ephemeris (pysweph).

Usage
  python generate.py                          generate data/*.json + self-test
  python generate.py --check 2026-11-01 ...   print those days as a table

Outputs (one entry per Gregorian date, IST)
  data/panchang-YYYY.json / .min.json         daily panchang
  data/festivals-draft-YYYY.json              festival draft, all "verified": false
"""

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from math import floor
from pathlib import Path

import swisseph as swe
import panchanga as dp            # drik-panchanga
import festival_rules as fr       # drik-panchanga festival rules
from datetime_helper import Date as DpDate

import sun_convention

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")   # "→", Devanagari on Windows consoles

# --- Fixed settings -----------------------------------------------------------
LAT, LON = 28.6139, 77.2090
TZ_NAME = "Asia/Kolkata"
TZ_HOURS = 5.5
IST = timezone(timedelta(hours=5, minutes=30))
PLACE = dp.Place(LAT, LON, TZ_HOURS)
GEOPOS = (LON, LAT, 0.0)

RANGES = {  # output year → (first date, last date), both included
    2026: (date(2026, 11, 1), date(2026, 12, 31)),
    2027: (date(2027, 1, 1), date(2027, 12, 31)),
}
DATA_DIR = Path(__file__).resolve().parent / "data"

dp.set_chosen_ayanamsa("lahiri")      # library default is True Chitra
dp.set_coordinate_mode("sidereal")
sun_convention.apply()                # Rashtriya Panchang sunrise/sunset everywhere

# --- Names ----------------------------------------------------------------------
WEEKDAYS = [("Sunday", "Sun"), ("Monday", "Mon"), ("Tuesday", "Tue"), ("Wednesday", "Wed"),
            ("Thursday", "Thu"), ("Friday", "Fri"), ("Saturday", "Sat")]

TITHI_EN = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
            "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi"]
TITHI_DEV = ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी",
             "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी"]

NAKSHATRAS = [
    ("अश्विनी", "Ashwini"), ("भरणी", "Bharani"), ("कृत्तिका", "Krittika"), ("रोहिणी", "Rohini"),
    ("मृगशिरा", "Mrigashira"), ("आर्द्रा", "Ardra"), ("पुनर्वसु", "Punarvasu"), ("पुष्य", "Pushya"),
    ("आश्लेषा", "Ashlesha"), ("मघा", "Magha"), ("पूर्वा फाल्गुनी", "Purva Phalguni"),
    ("उत्तरा फाल्गुनी", "Uttara Phalguni"), ("हस्त", "Hasta"), ("चित्रा", "Chitra"),
    ("स्वाती", "Swati"), ("विशाखा", "Vishakha"), ("अनुराधा", "Anuradha"), ("ज्येष्ठा", "Jyeshtha"),
    ("मूल", "Mula"), ("पूर्वाषाढ़ा", "Purva Ashadha"), ("उत्तराषाढ़ा", "Uttara Ashadha"),
    ("श्रवण", "Shravana"), ("धनिष्ठा", "Dhanishtha"), ("शतभिषा", "Shatabhisha"),
    ("पूर्वा भाद्रपद", "Purva Bhadrapada"), ("उत्तरा भाद्रपद", "Uttara Bhadrapada"), ("रेवती", "Revati"),
]
YOGAS = [
    ("विष्कुम्भ", "Vishkambha"), ("प्रीति", "Priti"), ("आयुष्मान", "Ayushman"), ("सौभाग्य", "Saubhagya"),
    ("शोभन", "Shobhana"), ("अतिगण्ड", "Atiganda"), ("सुकर्मा", "Sukarma"), ("धृति", "Dhriti"),
    ("शूल", "Shula"), ("गण्ड", "Ganda"), ("वृद्धि", "Vriddhi"), ("ध्रुव", "Dhruva"),
    ("व्याघात", "Vyaghata"), ("हर्षण", "Harshana"), ("वज्र", "Vajra"), ("सिद्धि", "Siddhi"),
    ("व्यतीपात", "Vyatipata"), ("वरीयान", "Variyana"), ("परिघ", "Parigha"), ("शिव", "Shiva"),
    ("सिद्ध", "Siddha"), ("साध्य", "Sadhya"), ("शुभ", "Shubha"), ("शुक्ल", "Shukla"),
    ("ब्रह्म", "Brahma"), ("इन्द्र", "Indra"), ("वैधृति", "Vaidhriti"),
]
KARANA_CYCLE = [("बव", "Bava"), ("बालव", "Balava"), ("कौलव", "Kaulava"), ("तैतिल", "Taitila"),
                ("गर", "Gara"), ("वणिज", "Vanija"), ("विष्टि", "Vishti")]
KARANA_FIXED = {1: ("किंस्तुघ्न", "Kimstughna"), 58: ("शकुनि", "Shakuni"),
                59: ("चतुष्पद", "Chatushpada"), 60: ("नाग", "Naga")}
VISHTI = "Vishti"

# 1 = Chaitra … 12 = Phalguna (North Indian names)
MASAS = [("चैत्र", "Chaitra"), ("वैशाख", "Vaishakh"), ("ज्येष्ठ", "Jyeshtha"), ("आषाढ़", "Ashadha"),
         ("श्रावण", "Shravan"), ("भाद्रपद", "Bhadrapad"), ("आश्विन", "Ashwin"), ("कार्तिक", "Kartik"),
         ("मार्गशीर्ष", "Margashirsha"), ("पौष", "Paush"), ("माघ", "Magh"), ("फाल्गुन", "Phalgun")]
PAKSHA = {"S": ("शुक्ल पक्ष", "Shukla Paksha"), "K": ("कृष्ण पक्ष", "Krishna Paksha")}

# Rahu Kaal: which eighth of the daytime (1-based); 0 = Sunday
RAHU_PART = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}

# Ekadashi names by Purnimanta month: (Krishna, Shukla); adhika month separate
EKADASHI_NAMES = {
    1: (("पापमोचिनी", "Papmochani"), ("कामदा", "Kamada")),
    2: (("वरूथिनी", "Varuthini"), ("मोहिनी", "Mohini")),
    3: (("अपरा", "Apara"), ("निर्जला", "Nirjala")),
    4: (("योगिनी", "Yogini"), ("देवशयनी", "Devshayani")),
    5: (("कामिका", "Kamika"), ("श्रावण पुत्रदा", "Shravana Putrada")),
    6: (("अजा", "Aja"), ("परिवर्तिनी", "Parivartini")),
    7: (("इन्दिरा", "Indira"), ("पापांकुशा", "Papankusha")),
    8: (("रमा", "Rama"), ("देवउठनी", "Devutthana")),
    9: (("उत्पन्ना", "Utpanna"), ("मोक्षदा", "Mokshada")),
    10: (("सफला", "Saphala"), ("पौष पुत्रदा", "Pausha Putrada")),
    11: (("षटतिला", "Shattila"), ("जया", "Jaya")),
    12: (("विजया", "Vijaya"), ("आमलकी", "Amalaki")),
}
EKADASHI_ADHIKA = (("परमा", "Parama"), ("पद्मिनी", "Padmini"))

# drik-panchanga festival catalog → (Devanagari, type)
FESTIVAL_NAMES = {
    "Ugadi": ("उगादि", "festival"),
    "Rama Navami": ("राम नवमी", "festival"),
    "Hanuman Jayanti": ("हनुमान जयंती", "festival"),
    "Mesha Sankranti": ("मेष संक्रांति", "festival"),
    "Akshaya Tritiya": ("अक्षय तृतीया", "festival"),
    "Vasavi Jayanti": ("वासवी जयंती", "festival"),
    "Narasimha Jayanti": ("नृसिंह जयंती", "festival"),
    "Vata Savitri Purnima": ("वट सावित्री पूर्णिमा", "vrat"),
    "Dakshinayana": ("दक्षिणायन", "festival"),
    "Guru Purnima": ("गुरु पूर्णिमा", "festival"),
    "Naga Panchami": ("नाग पंचमी", "festival"),
    "Varamahalakshmi Vrata": ("वरमहालक्ष्मी व्रत", "vrat"),
    "Rig Upakarma": ("ऋग् उपाकर्म", "festival"),
    "Yajur Upakarma": ("यजुर् उपाकर्म", "festival"),
    "Raksha Bandhan": ("रक्षा बंधन", "festival"),
    "Sama Upakarma": ("साम उपाकर्म", "festival"),
    "Onam": ("ओणम", "festival"),
    "Janmashtami": ("जन्माष्टमी", "festival"),
    "Swarna Gowri Vrata": ("स्वर्ण गौरी व्रत", "vrat"),
    "Ganesha Chaturthi": ("गणेश चतुर्थी", "festival"),
    "Rishi Panchami": ("ऋषि पंचमी", "vrat"),
    "Ananta Chaturdashi": ("अनंत चतुर्दशी", "festival"),
    "Mahalaya Amavasya": ("महालया अमावस्या", "festival"),
    "Durga Ashtami": ("दुर्गा अष्टमी", "festival"),
    "Ayudha Puja": ("आयुध पूजा", "festival"),
    "Vijayadashami": ("विजयादशमी", "festival"),
    "Karwa Chauth": ("करवा चौथ", "vrat"),
    "Dhana Trayodashi": ("धनतेरस", "festival"),
    "Naraka Chaturdashi": ("नरक चतुर्दशी", "festival"),
    "Deepavali": ("दीपावली", "festival"),
    "Bali Padyami": ("बलि प्रतिपदा", "festival"),
    "Surya Shashthi / Chhath": ("छठ पूजा", "festival"),
    "Gita Jayanti": ("गीता जयंती", "festival"),
    "Uttarayana": ("उत्तरायण", "festival"),
    "Vaikuntha Ekadashi": ("वैकुण्ठ एकादशी", "vrat"),
    "Makara Sankranti": ("मकर संक्रांति", "festival"),
    "Vasavi Atmarpana": ("वासवी आत्मार्पण", "festival"),
    "Vasanta Panchami": ("वसंत पंचमी", "festival"),
    "Ratha Saptami": ("रथ सप्तमी", "festival"),
    "VSN Jayanti": ("विष्णु सहस्रनाम जयंती", "festival"),
    "Maha Shivaratri": ("महाशिवरात्रि", "festival"),
    "Kama Dahana (Holi)": ("होलिका दहन", "festival"),
}


def tithi_names(num):
    """(Devanagari, English) for tithi 1..30."""
    if num == 15:
        return "पूर्णिमा", "Purnima"
    if num == 30:
        return "अमावस्या", "Amavasya"
    i = (num - 1) % 15
    if num < 15:
        return "शुक्ल " + TITHI_DEV[i], "Shukla " + TITHI_EN[i]
    return "कृष्ण " + TITHI_DEV[i], "Krishna " + TITHI_EN[i]


def karana_names(num):
    """(Devanagari, English) for karana 1..60."""
    return KARANA_FIXED.get(num) or KARANA_CYCLE[(num - 2) % 7]


# --- Time helpers -----------------------------------------------------------------
SECOND = 1 / 86400
HOUR = 1 / 24


def civil_jd(d):
    """drik-panchanga's key for civil day d (00:00 UT)."""
    return swe.julday(d.year, d.month, d.day, 0.0)


def ist_midnight_jd(d):
    """UT Julian day of 00:00 IST on date d."""
    return civil_jd(d) - TZ_HOURS / 24


def to_ist(jd_ut):
    """IST datetime rounded to the nearest minute."""
    y, m, d, h = swe.revjul(jd_ut + 30 * SECOND)
    t = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=h)
    return t.astimezone(IST).replace(second=0, microsecond=0)


def iso(jd_ut):
    return to_ist(jd_ut).isoformat()


def clock(jd_ut, on_day=None):
    """"2:52 PM", plus " (2 Nov)" when not on on_day. ASCII digits only."""
    t = to_ist(jd_ut)
    text = f"{t.hour % 12 or 12}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"
    if on_day is not None and t.date() != on_day:
        text += f" ({t.day} {t.strftime('%b')})"
    return text


# --- Element timelines ---------------------------------------------------------------
def elongation(jd):
    return dp.lunar_phase(jd)                                         # Moon − Sun


def moon_longitude(jd):
    return dp.lunar_longitude(jd)


def sun_plus_moon(jd):
    return (dp.lunar_longitude(jd) + dp.solar_longitude(jd)) % 360


ELEMENTS = {  # name: (angle function, degrees per segment, number of segments)
    "tithi": (elongation, 12.0, 30),
    "nakshatra": (moon_longitude, 360 / 27, 27),
    "yoga": (sun_plus_moon, 360 / 27, 27),
    "karana": (elongation, 6.0, 60),
}


def index_at(element, jd):
    fn, size, count = ELEMENTS[element]
    return min(int(floor(fn(jd) / size)), count - 1) + 1


def crossing(element, a, b):
    """Instant in (a, b] where the index changes, to ~1 second (bisection)."""
    ia = index_at(element, a)
    while b - a > SECOND:
        mid = (a + b) / 2
        if index_at(element, mid) == ia:
            a = mid
        else:
            b = mid
    return b


def timeline(element, start, end):
    """All segments (num, start_jd, end_jd) covering [start, end], in order.

    Hourly steps cannot miss a change: the shortest element (karana) lasts
    well over 9 hours."""
    first = index_at(element, start)
    t = start
    while index_at(element, t - HOUR) == first:
        t -= HOUR
    seg_start = crossing(element, t - HOUR, t)
    out, cur, t = [], first, start
    while True:
        nxt = t + HOUR
        if index_at(element, nxt) != cur:
            change = crossing(element, t, nxt)
            out.append((cur, seg_start, change))
            if change >= end:
                return out
            cur, seg_start = index_at(element, change), change
        t = nxt


class Timelines:
    def __init__(self, first, last):
        start = ist_midnight_jd(first) - 2
        end = ist_midnight_jd(last) + 3
        self.lines = {name: timeline(name, start, end) for name in ELEMENTS}

    def overlapping(self, element, a, b):
        """Segments with start < b and end > a."""
        return [s for s in self.lines[element] if s[1] < b and s[2] > a]

    def at(self, element, jd):
        for num, s, e in self.lines[element]:
            if s <= jd < e:
                return num
        raise ValueError(f"{element} timeline does not cover JD {jd}")


# --- One day ---------------------------------------------------------------------------
def vikram_samvat(d, amanta_masa):
    """VS year: Gregorian + 57 from Chaitra Shukla Pratipada, + 56 before it.
    From January to May, amanta Margashirsha–Phalguna (9–12) are still the old
    year (early January can still be amanta Margashirsha)."""
    if d.month <= 5 and amanta_masa >= 9:
        return d.year + 56
    return d.year + 57


def compute_day(d, tl):
    jd = civil_jd(d)
    day_start = ist_midnight_jd(d)
    day_end = day_start + 1
    rise, sset = dp.sunrise(jd, PLACE), dp.sunset(jd, PLACE)

    # Rahu Kaal from the library, asserted against the 8-part rule
    weekday = (d.weekday() + 1) % 7                       # 0 = Sunday
    assert dp.vaara(jd) == weekday, f"{d}: weekday mismatch"
    r_start, r_end = dp.rahu_kalam(jd, PLACE)
    part, eighth = RAHU_PART[weekday], (sset - rise) / 8
    assert abs(r_start - (rise + (part - 1) * eighth)) < SECOND and \
        abs(r_end - (rise + part * eighth)) < SECOND, f"{d}: Rahu Kaal rule failed"

    # Masa and paksha as at sunrise
    t_rise = tl.at("tithi", rise)
    masa_p, adhika = dp.masa(jd, PLACE, amanta=False, tithi_number=t_rise)
    masa_a, _ = dp.masa(jd, PLACE, amanta=True, tithi_number=t_rise)
    m_dev, m_en = MASAS[masa_p - 1]
    if adhika:
        m_dev, m_en = "अधिक " + m_dev, "Adhik " + m_en
    p_dev, p_en = PAKSHA["S" if t_rise <= 15 else "K"]

    def entries(element, namer, with_num=False):
        out = []
        for num, s, e in tl.overlapping(element, day_start, day_end):
            dev, en = namer(num)
            item = {"num": num} if with_num else {}
            item.update({"dev": dev, "en": en, "start": iso(s), "end": iso(e)})
            out.append(item)
        return out

    bhadra = [{"start": iso(s), "end": iso(e)}
              for num, s, e in tl.overlapping("karana", day_start, day_end)
              if karana_names(num)[1] == VISHTI]

    entry = {
        "date": d.isoformat(),
        "weekday": {"en": WEEKDAYS[weekday][0], "short": WEEKDAYS[weekday][1]},
        "vikram_samvat": vikram_samvat(d, masa_a),
        "masa": {"dev": m_dev, "en": m_en, "system": "purnimanta"},
        "paksha": {"dev": p_dev, "en": p_en},
        "sunrise": iso(rise),
        "sunset": iso(sset),
        "tithis": entries("tithi", tithi_names, with_num=True),
        "nakshatras": entries("nakshatra", lambda n: NAKSHATRAS[n - 1]),
        "yogas": entries("yoga", lambda n: YOGAS[n - 1]),
        "karanas": entries("karana", karana_names),
        "rahu_kaal": {"start": iso(r_start), "end": iso(r_end)},
        "bhadra": bhadra,
    }
    extra = {"jd": jd, "rise": rise, "sset": sset, "t_rise": t_rise, "masa_a": masa_a,
             "masa_p": masa_p, "adhika": adhika, "weekday": weekday}
    return entry, extra


def date_range(first, last):
    d = first
    while d <= last:
        yield d
        d += timedelta(days=1)


# --- Festivals draft -----------------------------------------------------------------------
def day_records(first, last, tl):
    """drik-panchanga DayRecords (amanta masa codes), built on our sunrise."""
    records = []
    for d in date_range(first, last):
        jd = civil_jd(d)
        rise = dp.sunrise(jd, PLACE)
        t = tl.at("tithi", rise)
        masa_a, adhika = dp.masa(jd, PLACE, amanta=True, tithi_number=t)
        code = f"S{t}" if t <= 15 else f"K{t - 15}"
        records.append(fr.DayRecord(DpDate(d.year, d.month, d.day), code, tl.at("nakshatra", rise),
                                    tl.at("yoga", rise), f"A{masa_a}" if adhika else str(masa_a),
                                    adhika, rise))
    return records


def to_date(dp_date):
    return date(dp_date.year, dp_date.month, dp_date.day)


def ekadashis(first, last, tl, records):
    """Smarta and Vaishnava dates for every Ekadashi.

    Smarta (as drik-panchanga): the first day Ekadashi prevails at sunrise;
    if it prevails at no sunrise (kshaya), the following day.
    Vaishnava: Ekadashi must already prevail at arunodaya (96 min before
    sunrise) — otherwise it is Dashami-viddha and moves to the next day — and
    when Ekadashi prevails at two sunrises the second day is taken."""
    library_smarta = {to_date(x) for x in fr.ekadashi_dates_from_records(records)}
    rises = {d: dp.sunrise(civil_jd(d), PLACE) for d in date_range(first - timedelta(days=3),
                                                                   last + timedelta(days=3))}
    lo, hi = ist_midnight_jd(first) - 2, ist_midnight_jd(last) + 2
    out = []
    for num, s, e in tl.lines["tithi"]:
        if num not in (11, 26) or not lo <= s <= hi:
            continue
        at_rise = [d for d, r in sorted(rises.items()) if s <= r < e]
        if at_rise:
            d1 = at_rise[0]
            smarta = d1
            arunodaya = rises[d1] - 96 / 1440
            vaishnava = d1 + timedelta(days=1) if (s > arunodaya or len(at_rise) > 1) else d1
        else:
            d0 = max(d for d, r in rises.items() if r <= s)
            smarta = vaishnava = d0 + timedelta(days=1)
        if not first <= smarta <= last:
            continue
        assert smarta in library_smarta, f"Ekadashi {smarta}: differs from drik-panchanga rule"
        masa_p, adhika = dp.masa(civil_jd(smarta), PLACE, amanta=False, tithi_number=num)
        pair = EKADASHI_ADHIKA if adhika else EKADASHI_NAMES[masa_p]
        dev, en = pair[0] if num == 26 else pair[1]
        out.append({"date": smarta.isoformat(), "dev": dev + " एकादशी", "en": en + " Ekadashi",
                    "type": "vrat", "smarta_date": smarta.isoformat(),
                    "vaishnava_date": vaishnava.isoformat(), "verified": False})
    return out


def festivals_draft(first, last, tl):
    pad_first, pad_last = first - timedelta(days=40), last + timedelta(days=40)
    records = day_records(pad_first, pad_last, tl)
    out = []
    for rule in fr.FESTIVAL_RULES:
        if rule.name not in FESTIVAL_NAMES:
            raise KeyError(f"No Devanagari name for festival {rule.name!r}: add it to FESTIVAL_NAMES")
        dev, kind = FESTIVAL_NAMES[rule.name]
        for x in fr.select_dates_for_rule(rule, records, GEOPOS, TZ_NAME):
            d = to_date(x)
            if first <= d <= last:
                out.append({"date": d.isoformat(), "dev": dev, "en": rule.name, "type": kind,
                            "verified": False})
    out += ekadashis(first, last, tl, records)
    return sorted(out, key=lambda f: (f["date"], f["en"]))


# --- Self-test --------------------------------------------------------------------------------
CYCLE = {"tithis": 30, "nakshatras": 27, "yogas": 27, "karanas": 60}
NAMERS = {"nakshatras": NAKSHATRAS, "yogas": YOGAS}


def self_test(year, days, extras, festivals, paths):
    problems = []
    first, last = RANGES[year]
    expected = [d.isoformat() for d in date_range(first, last)]
    if [e["date"] for e in days] != expected:
        problems.append("dates are not one per day, in order")

    prev_last = {}
    vs_diff = []
    for entry, x in zip(days, extras):
        d = entry["date"]
        day_start = f"{d}T00:00:00+05:30"
        next_day = (date.fromisoformat(d) + timedelta(days=1)).isoformat() + "T00:00:00+05:30"
        if not entry["sunrise"] < entry["sunset"]:
            problems.append(f"{d}: sunrise not before sunset")
        if not (entry["sunrise"].startswith(d) and entry["sunset"].startswith(d)):
            problems.append(f"{d}: sunrise/sunset not on this date")
        for key, cycle in CYCLE.items():
            items = entry[key]
            if not items or items[0]["start"] > day_start or items[-1]["end"] < next_day:
                problems.append(f"{d}: {key} do not cover the whole day")
            for a, b in zip(items, items[1:]):
                if a["end"] != b["start"]:
                    problems.append(f"{d}: gap/overlap between {key} {a['en']} and {b['en']}")
            if key == "tithis":
                for a, b in zip(items, items[1:]):
                    if (b["num"] - a["num"]) % 30 != 1:
                        problems.append(f"{d}: tithi {a['num']} followed by {b['num']}")
            # continuity with the previous day's last item
            if key in prev_last and items[0] != prev_last[key] and items[0]["start"] != prev_last[key]["end"]:
                problems.append(f"{d}: {key} not continuous from previous day")
            prev_last[key] = items[-1]
        rk = entry["rahu_kaal"]
        if not entry["sunrise"] <= rk["start"] < rk["end"] <= entry["sunset"]:
            problems.append(f"{d}: Rahu Kaal outside daytime")
        lib_vs = dp.elapsed_year(x["jd"], x["masa_a"])[2]
        if lib_vs != entry["vikram_samvat"]:
            vs_diff.append(f"{d} (ours {entry['vikram_samvat']}, library {lib_vs})")

    for path in paths:
        text = path.read_text(encoding="utf-8")
        if re.search("[०-९]", text):
            problems.append(f"{path.name}: contains Devanagari digits")
    pretty, mini = paths[0], paths[1]
    if json.loads(pretty.read_text(encoding="utf-8")) != json.loads(mini.read_text(encoding="utf-8")):
        problems.append("pretty and min JSON differ")
    if any(f["verified"] is not False for f in festivals):
        problems.append("a festival entry is not verified: false")

    print(f"  Self-test {year}: {len(days)} days — "
          f"sunrise<sunset, tithi continuity (no gaps/overlaps), Rahu Kaal rule (asserted per day), "
          f"full-day coverage, digits 0–9, pretty==min: {'OK' if not problems else 'FAILED'}")
    for p in problems[:20]:
        print("    ✗", p)
    if vs_diff:
        print(f"    note: Vikram Samvat differs from drik-panchanga's elapsed_year on {len(vs_diff)} day(s): "
              + ", ".join(vs_diff[:5]) + (" …" if len(vs_diff) > 5 else ""))
    for path in paths:
        print(f"    {path.relative_to(DATA_DIR.parent)}  {path.stat().st_size / 1024:,.1f} KB")
    return not problems


# --- Main --------------------------------------------------------------------------------------
def write_json(path, data, pretty):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        else:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def generate():
    DATA_DIR.mkdir(exist_ok=True)
    all_first = min(r[0] for r in RANGES.values())
    all_last = max(r[1] for r in RANGES.values())
    print(f"Computing timelines {all_first} → {all_last} …")
    tl = Timelines(all_first - timedelta(days=45), all_last + timedelta(days=45))
    ok = True
    for year, (first, last) in RANGES.items():
        days, extras = [], []
        for d in date_range(first, last):
            entry, extra = compute_day(d, tl)
            days.append(entry)
            extras.append(extra)
        festivals = festivals_draft(first, last, tl)
        paths = [DATA_DIR / f"panchang-{year}.json", DATA_DIR / f"panchang-{year}.min.json",
                 DATA_DIR / f"festivals-draft-{year}.json"]
        write_json(paths[0], days, pretty=True)
        write_json(paths[1], days, pretty=False)
        write_json(paths[2], festivals, pretty=True)
        print(f"{year}: {first} → {last}, {len(days)} days, {len(festivals)} festival draft entries")
        ok &= self_test(year, days, extras, festivals, paths)
    print("All self-tests passed." if ok else "SELF-TEST FAILED.")
    return ok


def check(dates):
    tl = Timelines(min(dates), max(dates))
    for d in dates:
        e, x = compute_day(d, tl)
        day_start = ist_midnight_jd(d)
        print(f"{e['weekday']['en']} {d.day} {d.strftime('%b')} {d.year}  ·  "
              f"{e['masa']['en']} {e['paksha']['en']} (Purnimanta)  ·  Vikram Samvat {e['vikram_samvat']}")
        print(f"  {'Sunrise':<11}{clock(x['rise'])}")
        print(f"  {'Sunset':<11}{clock(x['sset'])}")
        r = dp.rahu_kalam(x["jd"], PLACE)
        print(f"  {'Rahu Kaal':<11}{clock(r[0])} – {clock(r[1])}")
        for label, element, namer in (("Tithi", "tithi", lambda n: tithi_names(n)[1]),
                                      ("Nakshatra", "nakshatra", lambda n: NAKSHATRAS[n - 1][1]),
                                      ("Yoga", "yoga", lambda n: YOGAS[n - 1][1]),
                                      ("Karana", "karana", lambda n: karana_names(n)[1])):
            for i, (num, s, end) in enumerate(tl.overlapping(element, day_start, day_start + 1)):
                print(f"  {label if i == 0 else '':<11}{namer(num):<20} ends {clock(end, d)}")
        bhadra = [(s, end) for num, s, end in tl.overlapping("karana", day_start, day_start + 1)
                  if karana_names(num)[1] == VISHTI]
        print(f"  {'Bhadra':<11}" + ("; ".join(f"{clock(s, d)} – {clock(end, d)}" for s, end in bhadra)
                                      if bhadra else "none"))
        print()


def main():
    parser = argparse.ArgumentParser(description="Vrindavan Naad panchang generator")
    parser.add_argument("--check", nargs="+", metavar="YYYY-MM-DD",
                        help="print these days as a table instead of generating files")
    args = parser.parse_args()
    if args.check:
        check([date.fromisoformat(s) for s in args.check])
        return 0
    return 0 if generate() else 1


if __name__ == "__main__":
    sys.exit(main())
