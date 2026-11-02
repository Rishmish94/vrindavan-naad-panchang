# Vrindavan Naad – Panchang Calendar (Version 4): build spec

Mockup: https://claude.ai/artifact/1jbKzj6xAVL5kY7vkW75ox – row 4 "Version 4 · month calendar" (phone + laptop). Sample tithis/times in the mockup are layout only; real values come from the data.
Also follow panchang-site-spec.md (rules section 0, dark mode 5.13, moon formula 5.4, animations 7, accessibility 8).

## What it is
A Calendar view of the panchang: any day's tithi for the coming months, tap a day for its details, upcoming Ekadashis at a glance.

## C1 – Tabs and URLs
- A "Today | Calendar" pill switch at the top of panchang/index.html and every calendar page. Active tab: deep gold #8A6420 with ivory text; other: ivory with blush border. Each tab is a real link, ≥44px tall.
- panchang/calendar/index.html sends the visitor to the current month in IST (small script; noscript: a plain list of month links).
- One static page per month: panchang/calendar/2026-11/index.html … panchang/calendar/2027-12/index.html.
- Each month page: own title, e.g. "पंचांग नवंबर 2026 | Panchang Calendar November 2026 – Tithi, Ekadashi, Festivals – Vrindavan Naad"; meta description; canonical https://vrindavannaad.in/panchang/calendar/2026-11/; sitemap entry.
- Links use relative paths like the rest of the site.

## C2 – Month page generator (build time, not in the browser)
- A small script in the site repo (e.g. scripts/build_calendar.py, standard library only) builds every month page from panchang/data/YYYY-MM.min.json + festivals-YYYY.json. Re-run whenever data or verified festivals change.
- Day box tithi = tithi at sunrise (udaya tithi). A kshaya tithi (starts and ends between two sunrises) appears only in the day card's "till … then …" line. A tithi in force at two sunrises shows on both days – normal.
- Festivals: only "verified": true. Months with no verified list yet (Apr 2027 onward): show above the festival list "Festival dates for this month will be added after checking against the Government of India panchang."
- The page must be complete without JavaScript (List view, all days).
- Month page HTML ≤ 80 KB (excluding fonts/images).

## C3 – Layout
Phone, top to bottom:
1. Tabs.
2. Month bar: round 48px ‹ button · month name (h1, Cinzel 20px 700) with "कार्तिक – मार्गशीर्ष · विक्रम संवत 2083" under it (14px, muted) · › button. Arrows go no earlier than Nov 2026 and no later than the last data month (hidden/disabled at the ends).
3. Month chips: current month + next two (counted from today in IST). Active chip indigo #26213A with ivory text; others ivory with blush border.
4. Grid | List toggle.
5. Grid: SUN…SAT row (Cinzel 10px deep gold), 7 columns, 5px gap. Cell: radius 10px, ivory #FFFDF8, 1px blush border, min-height 66px; date (Cinzel 16px 700), moon icon 13px for the phase at sunrise (formula 5.4), marker: diya 13px = festival, "एका." = Ekadashi. Ekadashi cells tinted #F6E9C9. Today: date in an indigo circle with ivory text. Selected: 2px deep gold ring. Each cell is a button with full aria-label, e.g. "Thursday 5 November, Krishna Ekadashi, Rama Ekadashi".
6. Legend: Ekadashi, Festival, Purnima, Today.
7. Selected-day card (C4).
8. "EKADASHI · NEXT 3 MONTHS" card (C4).
9. "VRAT & FESTIVALS · [MONTH]" list (verified only).
10. Note: "Tithi shown is the tithi at sunrise (udaya tithi). Times for New Delhi. For vrat dates, follow your family or temple tradition."
List view (phone; also the no-JS default): one row per day – date + weekday, moon 18px, tithi Devanagari 16px + English, festival in deep gold; Ekadashi rows tinted. Show 10 days then a "Show all 30 days" button; without JS all days show.
Laptop: tabs, month bar (h1 24px) and chips centred. Two columns: left (flex 1 1 680px) grid with cells ≥108px tall showing date, moon 16px top right, tithi name Devanagari 15px without paksha, "Shukla"/"Krishna" Cinzel 10px, festival name 12px deep gold one line with ellipsis; right (380px) selected-day card + Ekadashi card. Festival list full width below, then the note.
Dark mode (5.13): translucent cards, soft gold labels; Ekadashi tint rgba(232,199,122,0.14); today circle gold #C9A04A with ink text.

## C4 – Small script (reuse panchang-core.js; no new libraries)
- Marks today (IST) and selects it by default if today is in the month shown; otherwise selects the 1st.
- Tapping a day updates the selected-day card without reload: weekday + date; "TITHI AT SUNRISE"; tithi Devanagari 26px 700; English + "till [time], then [next]"; festival box (diya + names) or "No major festival"; 2×2 grid Sunrise / Sunset / Rahu Kaal / Bhadra.
- Grid | List choice remembered in localStorage (try/catch).
- Ekadashi card always counts from today (not the month shown): next Ekadashis within 3 months, verified only; a Smarta/Vaishnava pair shares one row: "Smarta · Vaishnava: Sat 21 Nov".
- Digits 0–9; times formatted by hand "4:12 PM". Support the ?date=&time= test override.

## C5 – Links and testing
- Add "Full month calendar →" under "Next 7 days" on panchang/index.html.
- Tests (phone light/dark + laptop): today circled and selected; tap 3 days → correct values (compare one with generate.py --check); Ekadashi tint + card match verified list; chips/arrows span Nov 2026 – Dec 2027 and stop; List view works, JS off shows full list; an April 2027 month shows the "will be added" line and no festivals; no Devanagari digits; each month page < 80 KB; titles, canonicals, sitemap entries present.

## Must NOT change
Today view, home card, menu, fonts, colours, language rule. Never show an unverified festival. No new libraries.
