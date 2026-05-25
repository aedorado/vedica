# Vedica Astrology Webapp - Feature Roadmap

**Current State:** D1 (Rashi) chart ✅  
**Next:** Migrate to PyJHora for full astrology capabilities

---

## Quick Summary

| Phase | Feature | Timeline | Priority | Value |
|-------|---------|----------|----------|-------|
| **1** | **Migration to PyJHora** | 2-3h | ⭐⭐⭐ CRITICAL | Unlocks all features |
| **2** | D9 Navamsha + D10/D12 | 1-2w | ⭐⭐⭐ | Essential |
| **3** | Planetary Strength (Bala) | 1w | ⭐⭐⭐ | Important |
| **4** | Yoga Detection (284 yogas) | 2-3w | ⭐⭐⭐ | Revenue |
| **5** | Dasha-Bhukti Timing | 2w | ⭐⭐⭐ | Prediction engine |
| **6** | Dosha Detection | 1-2w | ⭐⭐ | Marriage/relationships |
| **7** | Transits & Forecasts | 2-3w | ⭐⭐ | Forecasting |
| **8** | Marriage Compatibility | 1-2w | ⭐⭐⭐ | 💰 Revenue |
| **9** | Panchanga (Calendar) | 1w | ⭐ | Nice-to-have |
| **10** | Advanced Analytics | 3+w | ⭐ | Enthusiasts |

---

## Phase 1: Migration to PyJHora (2-3 hours)

### Current State
- Using `swisseph` for planet calculations
- Manual chart rendering
- D1 only

### Target State
- Use PyJHora as calculation engine
- Keep existing UI (North/South Indian charts)
- Access to 284+ yogas, all divisional charts, Bala, Dasha, etc.

### Steps
1. Replace `core/ephemeris.py` to use PyJHora API
2. Update chart data structure
3. Verify D1 output matches current
4. Update database schema if needed

### PyJHora Modules We Need
```
from pyjhora.horoscope.chartdata import ChartData
from pyjhora.horoscope import Horoscope
from pyjhora.horoscope.chart.charts import DivisionalChart
from pyjhora.horoscope.chart.strength import Strength
from pyjhora.horoscope.chart.yoga import Yoga
from pyjhora.horoscope.dhasa import *
```

---

## Phase 2: Divisional Charts (D2-D60)

### MVP (Minimum Viable Product)
- **D9 Navamsha** ⭐ Most important (spouse, hidden nature)
- **D10 Dasamsha** (career)
- **D12 Dwadasamsha** (parents)

### Later
- D2, D3, D4, D7, D20, D24, D60, etc.

### UI Changes
```
Chart Type Selector:
  [ D1 ] [ D9 ] [ D10 ] [ D12 ] [ All ]

Each chart:
  - Same North/South Indian visualization
  - Planet positions in that varga
  - Color-coded importance
```

### Time Estimate
- D9: 2-3 hours (design + implement)
- D10, D12: 1 hour each

---

## Phase 3: Planetary Strength (Bala)

### What It Shows
- How strong each planet is at the time of birth
- Affects planet's ability to give results
- Critical for accurate prediction

### Components
1. **Dig Bala** - Directional strength (which houses benefit which planets)
2. **Kaala Bala** - Temporal strength (time of day/month/year effects)
3. **Chesta Bala** - Motional strength (speed, retrograde)
4. **Sthana Bala** - Positional strength (sign, nakshatra, aspects)
5. **Shad Bala** - Combined 6-fold strength
6. **Dwadasavarga Bala** - 12-fold varga strength

### UI
```
Planetary Strength Dashboard:
  Sun      ████████░░ 8/10 (Strong)
  Moon     ██████░░░░ 6/10 (Moderate)
  Mars     ██░░░░░░░░ 2/10 (Weak)
  ...
  
  Click each planet for breakdown:
    Dig Bala:     6/10
    Kaala Bala:   4/10
    Chesta Bala:  7/10
    Sthana Bala:  5/10
    ─────────────
    Total:        22/40 (5.5/10)
```

### Use Case
"When will Jupiter be strong enough to give good results?"
"Why is Saturn weak despite being in own sign?"

### Time Estimate: 1 week

---

## Phase 4: Yoga Detection (284 Yogas)

### What Are Yogas?
Auspicious/inauspicious planetary combinations that modify personality and fate.

### Yogas to Include (prioritized)

**Raja Yogas** (Power/Success) - Top Priority
- Pancha Mahapurusha (5 great person yogas)
- Gaja Kesari (Elephant-Lion yoga)
- Adhi Yoga

**Dhan Yogas** (Wealth) - High Revenue
- All wealth combinations
- Business yogas
- Property yogas

**Special Yogas**
- Vipreet Rajya Yoga (adversity blessing)
- Parivartana Yoga (planet exchange)
- Neech Bhanga Yoga (debilitation cancellation)
- Kemadruma Yoga (poverty)

**Marriage Yogas**
- Anaphora Yoga
- Nadi Dosha combinations

### UI
```
Detected Yogas: 7

1. 🟢 GAJA KESARI YOGA (Major)
   Combination: Jupiter & Moon strong
   Effect: Leadership, prosperity, intellect
   Strength: Strong
   
2. 🟡 PARIVARTANA YOGA (Moderate)
   Combination: Venus-Mars exchange
   Effect: Financial gains through effort
   Strength: Mild
   
... more yogas
```

### Monetization
- Display top 3 free
- Full report (all 7): Premium

### Time Estimate: 2-3 weeks

---

## Phase 5: Dasha-Bhukti Timing System

### What Is Dasha?
The main PREDICTION system in Vedic astrology. Tells which planet's period you're in.

### Vimshottari Dasha (Most Common)
- 120-year cycle starting with Ketu, ending with Ketu
- Each planet has major and sub-periods
- Tells "good" and "bad" times

### Other Dashas (Optional Later)
- Yogini Dasha
- Ashtottari Dasha
- Chakra Dasha
- Tithi Yogini Dasha

### UI
```
Vimshottari Dasha Timeline

Your Current Period: Jupiter Major (2024-2040)
  Start:   Jun 2024
  End:     Jun 2040
  Duration: 16 years

Sub-periods (Bhukti):
  • Mercury    Jun 2024 - Apr 2026
  • Ketu       Apr 2026 - Dec 2026  ← Next
  • Venus      Dec 2026 - Jun 2031
  ... more

Timeline visualization:
  ────────────────────────────────────────
  Su|Ketu|Ve|Su|Mo|Ma|Ra|Ju|Sa|Merc|
  ────────────────────────────────────────
     ↑ You are here (Jupiter period)
```

### Use Cases
"When will I get married?"
"When will my business succeed?"
"Bad time or good time?"

### Time Estimate: 2 weeks

### Why Critical
This is THE timing system everyone uses. People pay for this.

---

## Phase 6: Dosha Detection

### What Are Doshas?
"Defects" or "afflictions" that indicate potential problems.

### Main Doshas
- **Mangal Dosha** (Mars affliction) - Marriage problem
- **Rajju Dosha** - Relationship incompatibility
- **Darika Dosha** - Relationship obstruction
- **Nadi Dosha** - Incompatibility with partner
- **Pitra Dosha** - Ancestral curse

### UI
```
Doshas Found: 2

⚠️ MANGAL DOSHA (Moderate)
   Mars in 7th/8th/12th house
   Effect on: Marriage, relationships
   Severity: Moderate
   Remedies:
     • Mangal Shanti puja
     • Wear red coral
     • Perform Hanuman puja

✅ NO RAJJU DOSHA

```

### Time Estimate: 1-2 weeks

---

## Phase 7: Transits & Predictions

### What It Shows
- Where planets are TODAY
- Upcoming transits (next 1-3 months)
- Impact on your chart

### Features
- Real-time planet positions
- Transit calendar
- Saturn/Jupiter returns
- New/Full moon dates
- Eclipse dates

### UI
```
Today's Transits (May 23, 2024)

Mercury  0° Gemini  (In your 3rd house)
Venus    18° Taurus (In your 2nd house)
Mars     5° Aries   (In your 1st house)
...

Upcoming Important Transits:
  Jun 5:   Mars enters Taurus
  Jun 10:  Jupiter aspects Saturn
  Jul 1:   Saturn direct
```

### Time Estimate: 2-3 weeks

---

## Phase 8: Marriage Compatibility

### What It Shows
- Two charts compared
- Compatibility score
- Strengths/challenges

### Main Compatibility Check
**Guna Milan** (36 points system)
- Varna (caste, prestige): 1 point
- Vasya (control/attraction): 2 points
- Tara (star): 3 points
- Yoni (sexual compatibility): 4 points
- Graha Maitri (planet friendship): 5 points
- Gana (temperament): 6 points
- Bhakoot (zodiac relationship): 7 points
- Nadi (pulse/constitution): 8 points

Score: 18+ Good, 15+ Acceptable, <15 Challenging

### UI
```
Compatibility Report: Anurag ♂️ + Priya ♀️

Overall Match: 28/36 (78%) ✅ GOOD

Breakdown:
  Varna:        ✅ 1/1  (Perfect)
  Vasya:        ✅ 2/2  (Perfect)
  Tara:         ⚠️  1/3  (Challenging)
  Yoni:         ✅ 3/4  (Good)
  Graha Maitri: ⚠️  2/5  (Moderate)
  Gana:         ✅ 6/6  (Perfect)
  Bhakoot:      ✅ 7/7  (Perfect)
  Nadi:         ❌ 0/8  (Dosha found)

Summary:
  ✅ Great emotional compatibility
  ⚠️  Some adjustment needed in communication
  ✅ Strong physical attraction
  ❌ Nadi dosha present - needs remedy
```

### Revenue Opportunity
- Free: Basic score (28/36)
- Premium: Full analysis + remedies (₹199)

### Time Estimate: 1-2 weeks

---

## Phase 9: Panchanga (Daily Calendar)

### What It Shows
- Auspicious/inauspicious times each day
- Daily ritual information
- Best times for starting ventures

### Components
1. **Tithi** (Lunar day) - 30 per month
2. **Nakshatra** (Star) - 27 per month
3. **Yoga** (Time period) - auspicious/inauspicious
4. **Karana** (Half-tithi) - portent of day
5. **Vaara** (Day) - weekday

### UI
```
May 24, 2024 - Thursday

Sunrise:  6:15 AM
Sunset:   6:42 PM
Duration: 12h 27m

Tithi:       Shukla Pratipada (Waxing 1st day)
Nakshatra:   Rohini (Bull constellation)
Yoga:        Siddha (Auspicious)
Karana:      Bava
Vaara:       Brihaspati (Jupiter day)

✅ Auspicious Times:
  Brahma Muhurta: 5:45-6:15 AM
  Abhijit Muhurta: 12:00-12:30 PM
  Rahu Kalam: 3:00-4:30 PM (Avoid)

💡 Ideal for:
  ✅ Auspicious ceremonies
  ✅ Business dealings
  ✅ Travel
  ❌ Avoid surgery
```

### Time Estimate: 1 week

---

## Recommended Implementation Order

### Week 1-2: Phase 1 ✅
Migrate to PyJHora

### Week 3-4: Phase 2 🚀 QUICK WIN
Add D9 Navamsha chart

### Week 5: Phase 3
Bala strength display

### Week 6-7: Phase 4 START
Begin yoga detection (Raja yogas first)

### Week 8-9: Phase 4 CONTINUE
Complete yoga detection (all 284)

### Week 10-11: Phase 5
Dasha-Bhukti timeline

### Week 12+: Phase 6-8
Doshas, transits, compatibility

---

## What Users Want Most

**Ranked by commercial value:**
1. 💰 Marriage compatibility (₹199/report)
2. 💰 Dasha predictions (₹149/report)
3. 💰 Yoga analysis (₹99/report)
4. 🎁 D9 Navamsha (Free + attracts users)
5. 🎁 Dosha detection (Free, builds credibility)

---

## Quick Wins (Do in Next 2 Weeks)

After PyJHora migration:

1. **D9 Navamsha chart** - 3 hours
   - Essential divisional chart
   - Users expect this
   - Easy implementation

2. **Bala (Strength) display** - 2 hours
   - Simple bar chart
   - High perceived value
   - Differentiates from competitors

3. **Raja Yogas list** - 2 hours
   - Top 5 most auspicious yogas
   - High user interest
   - Revenue potential

4. **Dasha timeline** - 4 hours
   - Vimshottari main periods
   - Shows current dasha
   - Prediction engine

**Total: 11 hours → 4 major features → MVP++**

---

## Success Metrics

- [ ] PyJHora migration complete
- [ ] D9 chart rendering
- [ ] Bala calculations displaying
- [ ] Raja Yogas detecting
- [ ] Dasha timeline showing
- [ ] User can save reports

---

## Notes

- PyJHora has EVERYTHING built-in
- Focus on UI/UX, not calculations
- Start with free features (D1, D9, basic yogas)
- Upsell to premium for detailed reports
- Build differentiator: better UI than competitors
