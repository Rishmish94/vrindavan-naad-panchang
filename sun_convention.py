"""Sunrise / sunset convention of the Rashtriya Panchang (Indian national calendar).

Sunrise and sunset are the appearance / disappearance of the Sun's UPPER LIMB
on the horizon, with standard atmospheric refraction. The Rashtriya Panchang
states: refraction 31' + semi-diameter 16' = the Sun's centre 47' below the
true (geometric) horizon.

drik-panchanga's default is the classical Hindu rising (centre of the disc on
the horizon, no refraction), which comes about 4 minutes later in the morning
and earlier in the evening at Delhi.

`apply()` replaces `panchanga.sunrise` and `panchanga.sunset`. Every
drik-panchanga function that needs sunrise or sunset (tithi / nakshatra / yoga /
karana "at sunrise", masa, Rahu Kaal and the other kalams, day and night length,
festival rules) looks these two names up at call time, so the convention then
applies everywhere. Moonrise and moonset are not affected.
"""

from functools import lru_cache

import swisseph as swe
import panchanga

REFRACTION_ARCMIN = 31
SEMI_DIAMETER_ARCMIN = 16
CENTRE_DEPRESSION_DEG = -(REFRACTION_ARCMIN + SEMI_DIAMETER_ARCMIN) / 60  # -47'

# Event when the Sun's centre reaches CENTRE_DEPRESSION_DEG of true altitude:
# refraction and disc size are already inside that fixed angle.
_FLAGS = swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION


def _event(start_jd_ut, place, rsmi):
    lat, lon, _tz = place
    res, tret = swe.rise_trans_true_hor(
        start_jd_ut, swe.SUN, rsmi | _FLAGS, (lon, lat, 0.0),
        0.0, 0.0, CENTRE_DEPRESSION_DEG)
    if res != 0:
        raise ValueError(f"No sun {'rise' if rsmi & swe.CALC_RISE else 'set'} found "
                         f"for {place} after JD {start_jd_ut} (polar day/night?)")
    return tret[0]


@lru_cache(maxsize=4096)
def sunrise(jd, place):
    """Rashtriya Panchang sunrise for civil day `jd` (drik-panchanga's civil-day
    key), as a UT Julian day: the first rise after that day's solar midnight."""
    return _event(panchanga._solar_midnight(jd, place), place, swe.CALC_RISE)


@lru_cache(maxsize=4096)
def sunset(jd, place):
    """Rashtriya Panchang sunset: the first set after the day's sunrise (UT JD)."""
    return _event(sunrise(jd, place), place, swe.CALC_SET)


def apply():
    """Make drik-panchanga use this convention everywhere."""
    panchanga.sunrise = sunrise
    panchanga.sunset = sunset
