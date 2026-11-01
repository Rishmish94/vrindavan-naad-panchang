# Vrindavan Naad – Panchang page + home card: build spec (Phase 3)

Source: advisor's "Panchang complete builder direction" (sections 0, 5–8, 10, 11) + "Phase 3 – build now" brief, 1 Nov 2026.
Design mockup: https://claude.ai/artifact/1jbKzj6xAVL5kY7vkW75ox – row 2 = full page (Version 2), row 3 = home card (Version 3). Row 1 (Version 1) is retired.

## 0. Fixed rules
1. Cost ₹0. Static files only. No paid API, server or database.
2. No scraping of any website.
3. One location: New Delhi (28.6139, 77.2090), Asia/Kolkata (IST). Label: "Times for New Delhi". No city picker.
4. Purnimanta months. Lahiri ayanamsa (already in the data).
5. Accuracy first: ONLY festivals with "verified": true are ever shown. If a value is unsure/missing, show nothing rather than something wrong.
6. Language rule: interface labels English (Cinzel); panchang values (tithi, nakshatra, yoga, karana, festival, month, paksha) in Devanagari (Noto Serif Devanagari) with English line under/next to them; times like "4:12 PM"; digits always 0–9; never use toLocaleString / Intl number formatting for display.
7. No popups, ads, login, points, streaks, comments.
8. Palette/fonts only: indigo #26213A, ink #1F1B2E, gold #C9A04A, soft gold #E8C77A, deep gold #8A6420, blush #F2CDB0, ivory #FBF6EC, card ivory #FFFDF8, muted text #4A4458, muted light text #D9D2C3. Cinzel (500/600/700), Noto Serif Devanagari (400–700). Text contrast ≥ 4.5:1.
9. Every animation stops under prefers-reduced-motion: reduce. Images stay.
10. Do not change the rest of the site, the jaap page, fonts, colours or the language rule. Only additions: the panchang page, the home card, "Panchang" in the menu.

## 1. Data (Phase 3 version)
- Site repo: /panchang/data/
  - Monthly files YYYY-MM.min.json (2026-11 … 2027-12): arrays of day entries, fields exactly as generated (date, weekday, vikram_samvat, masa, paksha, sunrise, sunset, tithis[{num,dev,en,start,end}], nakshatras, yogas, karanas, rahu_kaal{start,end}, bhadra[{start,end}]). Times are ISO strings in IST.
  - festivals-YYYY.json: arrays of {date, dev, en, type, tradition_note, bhadra_note, verified, source}. Show only verified:true. A missing festival file = no verified festivals (no error).
- NO daily values in the HTML. Page shows "Loading today's panchang…" until data arrives. <noscript>: "Today's panchang needs JavaScript."
- Load the current month's file AFTER first paint; in the last 7 days of a month also load the next month (for "Next 7 days" and midnight rollover). Load festivals for the years needed.
- No data for today → "Panchang not available for this date".
- Links: the site uses relative links to explicit .html files (works from disk and on any host). Use relative paths (e.g. panchang/index.html from home, ../index.html from the panchang page) – not root-absolute "/panchang/".
- Local testing: fetch() of JSON does not work from file://. Test with a local server from the site repo root: `python -m http.server 8000` → http://localhost:8000/

## 2. Images (site repo images/panchang/)
moon-full.webp (NASA, 320×320 transparent), sun.webp (NASA SDO, 200×200), sunrise.webp, sunset.webp (stand-ins, 3:2). Footer credit on the panchang page: "Moon and sun images: NASA". No NASA logos.

## 5. Full page panchang/index.html (Version 2)
### 5.1 Basics
- Standard shared site header + footer. Menu (all pages): PANCHANG between JAAP and POOJA VIDHI; current page = gold #8A6420 text + 2px #C9A04A underline, aria-current="page".
- <title>: आज का पंचांग | Aaj Ka Panchang Today – Tithi, Rahu Kaal, Festivals – Vrindavan Naad
- Meta description: one Hindi + one English sentence about today's tithi, Rahu Kaal and festivals for New Delhi (static wording, no daily values). Canonical https://vrindavannaad.in/panchang/. Add to sitemap.xml if it exists.
- Background (light): ivory #FBF6EC + radial-gradient(circle at 50% 40%, rgba(242,205,176,0.45), transparent 50%).
- Column: phones full width, 14px side padding; laptop max-width 1120px centred, 32px padding.
### 5.2 Section order (phone)
1 Today's sky panel · 2 Festival card · 3 SURYA · SUN · 4 Rahu Kaal + Bhadra · 5 More: Nakshatra, Yoga, Karana (folded) · 6 Next 7 days · 7 Note "Times are for New Delhi. For vrat dates, follow your family or temple tradition." · 8 Buttons Share on WhatsApp / Watch on YouTube · 9 Footer + NASA credit.
Laptop: sky panel full width; below two columns (flex-wrap, each flex:1 1 420px, gap 24px): left = festival + SURYA·SUN; right = Rahu/Bhadra + More + Next 7 days. Note + buttons centred below.
### 5.3 Sky panel
- radius 24px (laptop 28px), overflow hidden, background linear-gradient(180deg,#0E0C1E 0%,#1B1736 55%,#2A2245 100%) (laptop 120deg), padding 24px 20px 26px (laptop 32px 40px), ivory text, centred on phone.
- 6 twinkling stars 1–3px (ivory, one soft gold), fixed positions, vnTw with delays 0, .6, 1.2, 1.6, 2, 2.6s.
- Phone content: "AAJ KA PANCHANG" Cinzel 13px 600 ls 3px #E8C77A · h1 date "Sunday, 1 November 2026" Cinzel 16px 600 · "कार्तिक · कृष्ण पक्ष · विक्रम संवत 2083" Devanagari 13px #D9D2C3 · moon block 190×190, moon 130px · caption "Waxing moon"/"Waning moon"/"Full moon · Purnima"/"New moon · Amavasya" Cinzel 12px #E8C77A · "TITHI" Cinzel 11px ls 3px 600 #E8C77A · tithi Devanagari 38px 700 (laptop 52px) · tithi English Cinzel 15px 600 #E8C77A · "until 4:12 PM, then Dwadashi" Cinzel 13px #D9D2C3 · pill "Times for New Delhi" (1px rgba(232,199,122,.4), radius 999px, Cinzel 12px #D9D2C3, inline stroke pin SVG #E8C77A, no emoji).
- Laptop: moon block left (240px area, moon 170px), text right (left-aligned): label 14px ls 4px, h1 20px, Hindi line 15px, "TITHI · Waxing moon", tithi 52px, English 18px + "· until …" 14px, pill.
### 5.4 Moon (NASA image + phase from tithi)
- Relative box; behind: glow circle radial-gradient(circle, rgba(243,231,200,.30) 30%, rgba(243,231,200,.08) 50%, transparent 70%) with vnGlow; the moon-full.webp image; on top an SVG same size (viewBox 0 0 130 130) drawing the shadow.
- Shadow: <mask> = white circle (cx65 cy65 r64.5) minus the lit path in black, lit path blurred feGaussianBlur stdDeviation 2.2; then circle r64.5 fill #07060F opacity .87 using the mask. Unique ids per instance. NO ring/border/medallion.
- Phase from current tithi num n (1–30): p=0.5 if n=15; p=0 if n=30; else p=(n−0.5)/30. c=65, r=66. p=0.5 → full circle path; p=0 → empty path; else rx=r·|cos(2πp)|, waxing=p<0.5, limb sweep = waxing?1:0, terminator sweep = waxing ? (p<0.25?0:1) : (p<0.75?0:1); path "M c (c−r) A r r 0 0 limb c (c+r) A rx r 0 0 term c (c−r) Z". Shukla lit from right growing; Krishna lit from left shrinking. alt "Moon today: Waxing moon" etc.
### 5.5 Festival card
- #FFFDF8, 1px #F2CDB0, radius 18px, padding 18px, shadow 0 10px 30px rgba(138,100,32,.08). Left 44px indigo circle with diya icon (section 7). Right: "FESTIVAL TODAY" Cinzel 11px ls 2.5px 600 #8A6420; Devanagari name 22px 600; English Cinzel 13px #8A6420; tradition note Cinzel 12px #4A4458; bhadra note Cinzel 12px #4A4458. Several verified entries → one row each.
- None today: dashed card (1px dashed #F2CDB0) "No major festival today" + "NEXT: [Devanagari] · [English] · [Thu, 5 Nov]" (next verified entry).
### 5.6 SURYA · SUN
- Heading row (centred phone, left laptop): sun.webp 26px (laptop 30px) vnBreathe + "SURYA · SUN" Cinzel 13px ls 3px #8A6420. Sun image alt="" in heading.
- Two cards grid 2 cols gap 12px (laptop 16px), #FFFDF8, 1px #F2CDB0, radius 16px, overflow hidden: photo height 96px (laptop 150px) object-fit cover, vnZoom (sunset animation-delay −5s), alt "Sunrise over the river"/"Sunset over the river"; below "SUNRISE"/"SUNSET" Cinzel 11px ls 2px 600 #8A6420; time Cinzel 18px (laptop 20px) 600.
### 5.7 Rahu Kaal + Bhadra
- Card radius 16px, two rows split by 1px #F2CDB0, padding 16px 18px.
- Row 1: "RAHU KAAL" Cinzel 12px ls 2px 600 #8A6420 + "4:13 – 5:38 PM" Cinzel 18px 600; hint "Avoid new work" Cinzel 11px #4A4458; while in progress hint → "On now" badge (#8A6420 pill, ivory Cinzel 12px 700, 8px dot).
- Row 2: "BHADRA" + range(s) with day when crossing ("till 4:12 PM", "from 9:40 PM", "9:40 PM – 6:05 AM (Mon)"); hint "Avoid shubh karya". None → "No Bhadra today" Cinzel 16px #4A4458, no hint.
### 5.8 More: Nakshatra, Yoga, Karana
- Card; full-width toggle (min-height 52px) "More: Nakshatra, Yoga, Karana" with +/− in #8A6420, aria-expanded; folded by default (use <details>/<summary> styled the same). Open: rows label left (Cinzel 12px #8A6420), value right: Devanagari 15px + "until 9:47 PM" Cinzel 12px #4A4458; list all that change during the day.
### 5.9 Next 7 days
- "NEXT 7 DAYS" Cinzel 14px ls 3px #8A6420 (centred phone, left laptop). Card list rows: date block 52px (day number Cinzel 20px 700; "THU, NOV" Cinzel 11px #8A6420) + Devanagari name 17px 600 + English Cinzel 12px #4A4458. Purnima rows: moon image 26px at right end (alt "Full moon"). Verified entries tomorrow..+7 days; none → "No festivals in the next 7 days".
### 5.10 Time behaviour (small JS, panchang page + home card only)
- "Now" in IST regardless of phone time zone: use Intl.DateTimeFormat with timeZone 'Asia/Kolkata' ONLY to read date/time parts; format display manually (h:mm AM/PM, 0–9 digits).
- Today's entry by IST date. Current tithi = start ≤ now < end; show name, moon for its num, "until [end], then [next tithi English without Shukla/Krishna]"; end on another day → "until 2:10 AM (Mon)".
- Rahu Kaal "On now" if start ≤ now < end. Re-check every 60 seconds (tithi change, Rahu start/end, midnight → next day's entry).
- Page weight (HTML+CSS+JS, excluding images/data) < 300 KB; data never blocks first paint.
### 5.11 Buttons
- "Share on WhatsApp": #8A6420 pill, ivory text, min-height 48px, https://wa.me/?text= link updated by the script: "आज का पंचांग – [tithi Devanagari] ([English]). [Festival today if any.] Rahu Kaal [time]. https://vrindavannaad.in/panchang/"
- "Watch on YouTube": outline pill (1px #8A6420, text #8A6420) → https://www.youtube.com/@VrindavanNaadPanchaang (new tab, rel="noopener"). Gap 12px, wrap.
### 5.12 Note + credit as in 5.2; footer line "Moon and sun images: NASA" Cinzel 11px #4A4458.
### 5.13 Dark mode
- Page: ink #1F1B2E → indigo #26213A gradient; sky panel unchanged. Cards rgba(251,246,236,.04), border 1px rgba(201,160,74,.35); text ivory; labels #E8C77A; muted #D9D2C3; Share button #C9A04A with ink text; "On now" badge #C9A04A with ink text.

## 6. Home card (Version 3)
- Directly below the hero (heading + View Aarti Collection button), above the ✿ divider and Aarti Collection.
- Whole card is ONE link to panchang/index.html, aria-label "Aaj Ka Panchang – open full panchang"; nothing inside is a separate link/button. Same data + time logic as 5.10. Before data loads: a calm placeholder ("Loading today's panchang…"); no JS → noscript line.
- Below card: "Times for New Delhi" Cinzel 11px #4A4458 (centred phone, right-aligned laptop).
- Look: linear-gradient(160deg,#0E0C1E 0%,#1B1736 60%,#2A2245 100%) (laptop 110deg), radius 22px (laptop 24px), shadow 0 14px 34px rgba(31,27,46,.22), overflow hidden, ivory text, 3 twinkling stars.
- Phone (14px side margin): (1) top row padding 16px 18px 0: "AAJ KA PANCHANG" Cinzel 12px 600 ls 3px #E8C77A left; "Sun, 1 Nov" Cinzel 12px #D9D2C3 right. (2) moon + tithi row padding 12px 18px 14px gap 14px: moon area 96px with vnGlow, image 70px with phase shadow (5.4); right "TITHI" Cinzel 10px ls 2.5px 600 #E8C77A, tithi Devanagari 26px 700, "[English] · till 4:12 PM" Cinzel 12px #E8C77A. (3) festival strip (margin 0 14px, padding 10px 12px, radius 14px, bg rgba(232,199,122,.12), border 1px rgba(232,199,122,.35)): diya 22px flickering, Devanagari 16px 600, English line Cinzel 11px #D9D2C3 (with tradition note). None → dashed strip "No festival today · Next: [English, Thu 5 Nov]" (next part #E8C77A). (4) 3 tiles grid gap 8px padding 12px 14px 4px, each radius 12px bg rgba(251,246,236,.06) padding 10px: RAHU KAAL (label Cinzel 10px #E8C77A) + "4:13–5:38 PM" Cinzel 13px 600 — in progress: pulsing 7px soft-gold dot (vnPulse, aria-label "On now") + "On now · till 5:38"; BHADRA + "till 4:12 PM"/range/"None today"; SUN with sun image 14px + "↑ 6:34 AM" / "↓ 5:38 PM" two lines Cinzel 12px 600. (5) bottom row padding 12px 18px 16px: "Full panchang" Cinzel 13px 600 #E8C77A left, arrow icon right.
- Laptop (one wide strip, padding 22px 28px, wrapping row, gap 22px): header row full width "AAJ KA PANCHANG" Cinzel 13px 600 ls 3px #E8C77A + "· Sunday, 1 November" #D9D2C3 500; right pill "Full panchang →" (1px rgba(232,199,122,.6), radius 999px, Cinzel 13px 600 #E8C77A). Then [moon 112px area / 84px image + TITHI + tithi 32px + English line on one line] (flex 1 1 280px) | [festival box] (flex 1 1 220px) | [3 tiles] (flex 1.3 1 340px).

## 7. Animations (exact)
@keyframes vnGlow{0%,100%{opacity:.45;transform:scale(1)}50%{opacity:.9;transform:scale(1.06)}}
@keyframes vnTw{0%,100%{opacity:.25}50%{opacity:1}}
@keyframes vnZoom{from{transform:scale(1)}to{transform:scale(1.07)}}
@keyframes vnBreathe{0%,100%{filter:drop-shadow(0 0 4px rgba(255,190,90,.55))}50%{filter:drop-shadow(0 0 12px rgba(255,190,90,.95))}}
@keyframes vnFlicker{0%,100%{transform:scale(1,1)}30%{transform:scale(1.06,.94)}60%{transform:scale(.96,1.06)}}
@keyframes vnPulse{0%,100%{opacity:1}50%{opacity:.35}}
.vn-glow{animation:vnGlow 5s ease-in-out infinite} .vn-tw{animation:vnTw 3.5s ease-in-out infinite} .vn-zoom{animation:vnZoom 10s ease-in-out infinite alternate} .vn-breathe{animation:vnBreathe 4s ease-in-out infinite} .vn-flame{transform-origin:12px 9px;animation:vnFlicker 2.4s ease-in-out infinite} .vn-pulse{animation:vnPulse 1.6s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){.vn-glow,.vn-tw,.vn-zoom,.vn-breathe,.vn-flame,.vn-pulse{animation:none}}
Diya icon (24×24 stroke SVG, stroke #E8C77A 1.7, round caps/joins): flame "M12 3c1.6 2 2.2 3.4 2.2 4.6a2.2 2.2 0 0 1-4.4 0C9.8 6.4 10.4 5 12 3z" (filled #E8C77A, class vn-flame), bowl "M4 13h16c0 3.3-3.6 6-8 6s-8-2.7-8-6z", base "M9 19.5h6".

## 8. Accessibility
Real <a>/<button>; touch targets ≥ 48px; decorative stars/glows/icons aria-hidden="true"; moon and photos alt text; heading sun image alt=""; contrast ≥ 4.5:1 light and dark; one h1 (the date), section headings h2.

## 10. Testing checklist
1 Today's tithi, end time, sunrise, sunset, Rahu Kaal, Bhadra match `generate.py --check <today>`. 2 Change phone date to tomorrow → tomorrow's data incl. moon shape. 3 Moon shapes: Shukla Chaturthi thin crescent right; Ashtami half right; Purnima full; Krishna Ashtami half left; Amavasya dark. 4 During Rahu Kaal: "On now" badge (page) / pulsing dot (card), disappears when it ends without reload. 5 Festival day and non-festival day (card + strip). 6 Bhadra day and none. 7 More opens/closes. 8 With JavaScript off: the noscript line "Today's panchang needs JavaScript." 9 WhatsApp text correct; YouTube opens VN Panchaang. 10 Reduce motion → no animation. 11 No Devanagari digits anywhere. 12 Fast on slow 4G; first view before data loads. 13 PANCHANG in menu on every page; highlighted on its page. 14 NASA credit present. 15 Canonical, title, description, sitemap entry.

## 11. Must NOT do
No scraping/copying, no paid services; no unverified festival shown; no moon ring/medallion; no cartoon icons; no popups/ads/login/points/streaks/comments; no changes to other pages beyond menu item + home card; no new fonts or colours.
