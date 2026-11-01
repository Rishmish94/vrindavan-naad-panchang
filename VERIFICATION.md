# Verification — Phase 1

Manual check of the generator output (`data/panchang-2026.json`,
`data/panchang-2027.json`) against the **Rashtriya Panchang 2026–27**,
Positional Astronomy Centre, India Meteorological Department (1948 Saka Era
edition).

**Result: all checked values agree within 1 minute** (tolerance ≤ 2 minutes).

## Method

| What | How it was compared |
|---|---|
| Tithi, nakshatra, yoga and karana end times | Compared directly with the book. They are geocentric moments, so the IST times are the same for any place in India and need no conversion for New Delhi. |
| Sunrise and sunset, New Delhi | Compared with the book's four-metro sunrise/sunset table (New Delhi column). Our convention is the book's: upper limb, refraction 31' + semi-diameter 16' = centre 47' below the horizon (`sun_convention.py`). |
| Rahu Kaal | Not in the book; checked against the rule: daytime (sunrise → sunset) in 8 equal parts; Mon 2, Sat 3, Fri 4, Wed 5, Thu 6, Tue 7, Sun 8. (`generate.py` also asserts this for every generated day.) |

**Tolerance:** ≤ 2 minutes. Our times are rounded to the nearest minute.

## Verified dates

10 check points (12 calendar days — two consecutive-day pairs):
2026-11-01, 2026-11-05, 2026-11-08, 2026-11-09, 2026-11-24, 2026-12-01,
2026-12-16, 2027-01-22/23, 2027-02-08, 2027-03-03/04.

Generator values on those days (New Delhi, IST). End times on the date
itself, then the next one, with the date added when it falls on another day:

| Date | Day | Sunrise / sunset | Rahu Kaal | Tithi ends | Nakshatra ends | Yoga ends | Karana ends |
|---|---|---|---|---|---|---|---|
| 2026-11-01 | Sun | 6:33 AM / 5:36 PM | 4:13 PM – 5:36 PM | Krishna Saptami 2:52 PM; Krishna Ashtami 1:11 PM (2 Nov) | Punarvasu 5:40 AM; Pushya 4:31 AM (2 Nov) | Sadhya 2:39 PM; Shubha 12:07 PM (2 Nov) | Vishti 3:52 AM; Bava 2:52 PM; Balava 1:58 AM (2 Nov) |
| 2026-11-05 | Thu | 6:36 AM / 5:33 PM | 1:27 PM – 2:49 PM | Krishna Ekadashi 10:36 AM; Krishna Dwadashi 10:31 AM (6 Nov) | Purva Phalguni 3:30 AM; Uttara Phalguni 3:56 AM (6 Nov) | Indra 6:27 AM; Vaidhriti 5:10 AM (6 Nov) | Balava 10:36 AM; Kaulava 10:31 PM; Taitila 10:31 AM (6 Nov) |
| 2026-11-08 | Sun | 6:38 AM / 5:31 PM | 4:10 PM – 5:31 PM | Krishna Chaturdashi 11:28 AM; Amavasya 12:32 PM (9 Nov) | Chitra 5:53 AM; Swati 7:24 AM (9 Nov) | Priti 3:28 AM; Ayushman 3:03 AM (9 Nov) | Shakuni 11:28 AM; Chatushpada 11:57 PM; Naga 12:32 PM (9 Nov) |
| 2026-11-09 | Mon | 6:39 AM / 5:30 PM | 8:01 AM – 9:22 AM | Amavasya 12:32 PM; Shukla Pratipada 2:01 PM (10 Nov) | Swati 7:24 AM; Vishakha 9:20 AM (10 Nov) | Ayushman 3:03 AM; Saubhagya 2:57 AM (10 Nov) | Naga 12:32 PM; Kimstughna 1:13 AM (10 Nov) |
| 2026-11-24 | Tue | 6:51 AM / 5:24 PM | 2:46 PM – 4:05 PM | Purnima 8:24 PM; Krishna Pratipada 4:51 PM (25 Nov) | Bharani 2:02 AM; Krittika 11:25 PM; Rohini 8:36 PM (25 Nov) | Parigha 4:06 PM; Shiva 12:00 PM (25 Nov) | Vishti 10:06 AM; Bava 8:24 PM; Balava 6:38 AM (25 Nov) |
| 2026-12-01 | Tue | 6:56 AM / 5:24 PM | 2:47 PM – 4:05 PM | Krishna Saptami 12:12 AM; Krishna Ashtami 11:14 PM; Krishna Navami 10:53 PM (2 Dec) | Magha 9:01 AM; Purva Phalguni 8:55 AM (2 Dec) | Vaidhriti 12:15 PM; Vishkambha 10:32 AM (2 Dec) | Bava 12:12 AM; Balava 11:39 AM; Kaulava 11:14 PM; Taitila 10:59 AM (2 Dec) |
| 2026-12-16 | Wed | 7:07 AM / 5:26 PM | 12:17 PM – 1:34 PM | Shukla Saptami 10:46 PM; Shukla Ashtami 11:26 PM (17 Dec) | Shatabhisha 2:03 PM; Purva Bhadrapada 3:31 PM (17 Dec) | Vajra 1:46 PM; Siddhi 1:22 PM (17 Dec) | Gara 10:08 AM; Vanija 10:46 PM; Vishti 11:13 AM (17 Dec) |
| 2027-01-22 | Fri | 7:14 AM / 5:52 PM | 11:13 AM – 12:33 PM | Purnima 5:47 PM; Krishna Pratipada 2:13 PM (23 Jan) | Punarvasu 10:25 AM; Pushya 7:32 AM (23 Jan) | Vishkambha 1:51 PM; Priti 9:39 AM (23 Jan) | Vishti 7:38 AM; Bava 5:47 PM; Balava 3:58 AM (23 Jan) |
| 2027-01-23 | Sat | 7:14 AM / 5:52 PM | 9:53 AM – 11:13 AM | Krishna Pratipada 2:13 PM; Krishna Dwitiya 10:58 AM (24 Jan) | Pushya 7:32 AM; Ashlesha 4:54 AM (24 Jan) | Priti 9:39 AM; Ayushman 5:40 AM (24 Jan) | Balava 3:58 AM; Kaulava 2:13 PM; Taitila 12:32 AM (24 Jan) |
| 2027-02-08 | Mon | 7:05 AM / 6:05 PM | 8:28 AM – 9:50 AM | Shukla Dwitiya 1:07 AM (9 Feb) | Shatabhisha 1:57 AM (9 Feb) | Parigha 9:52 PM; Shiva 9:43 PM (9 Feb) | Balava 12:20 PM; Kaulava 1:07 AM (9 Feb) |
| 2027-03-03 | Wed | 6:45 AM / 6:22 PM | 12:33 PM – 2:00 PM | Krishna Dashami 4:45 AM; Krishna Ekadashi 7:25 AM (4 Mar) | Purva Ashadha 10:35 PM; Uttara Ashadha 1:36 AM (5 Mar) | Siddhi 12:07 AM; Vyatipata 1:07 AM (4 Mar) | Vishti 4:45 AM; Bava 6:05 PM; Balava 7:25 AM (4 Mar) |
| 2027-03-04 | Thu | 6:44 AM / 6:22 PM | 2:00 PM – 3:28 PM | Krishna Ekadashi 7:25 AM; Krishna Dwadashi 9:54 AM (5 Mar) | Uttara Ashadha 1:36 AM (5 Mar) | Vyatipata 1:07 AM; Variyana 2:01 AM (5 Mar) | Balava 7:25 AM; Kaulava 8:42 PM; Taitila 9:54 AM (5 Mar) |

To reproduce any row:

```
.venv\Scripts\python generate.py --check 2026-11-01
```

## Result

All tithi, nakshatra, yoga and karana end times and all New Delhi sunrise /
sunset times on the dates above agree with the Rashtriya Panchang 2026–27
**within 1 minute**. Rahu Kaal matches the 8-part rule on every date.

## Open items for Phase 2

These are festival-date rules, not astronomy: the underlying tithi times agree
with the book. The festival file (`data/festivals-draft-*.json`) stays a draft,
`"verified": false`, never shown on the site.

1. **Deepavali / Lakshmi Puja 2026 — library 9 Nov, book 8 Nov (North India).**
   Amavasya runs from 11:28 AM on 8 Nov to 12:32 PM on 9 Nov. drik-panchanga
   picks the day with Amavasya at sunrise (9 Nov); North Indian Lakshmi Puja
   follows Amavasya in pradosh kaal (after sunset), which only 8 Nov has.
   Phase 2: a pradosh-kaal rule for Deepavali, and a review of other festivals
   that depend on a time of day other than sunrise (Naraka Chaturdashi,
   Holika Dahan, Janmashtami, Maha Shivaratri, Karwa Chauth).

2. **Vijaya Ekadashi 2027 — draft Smarta 3 Mar / Vaishnava 4 Mar, book lists 4 Mar.**
   Ekadashi begins at 4:45 AM on 3 Mar — before sunrise (6:45 AM) but after
   arunodaya (5:09 AM, 96 minutes earlier), so it is Dashami-viddha — and
   lasts past sunrise on 4 Mar (ends 7:25 AM). The book's 4 Mar matches our
   Vaishnava rule. Phase 2: decide which date the site shows for Ekadashi
   (Smarta, Vaishnava, or both) and align the Smarta rule for this case.
