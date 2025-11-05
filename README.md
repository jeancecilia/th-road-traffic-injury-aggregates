# Thailand Road‑Traffic Injury Aggregates (Bangkok & Provinces)
**Version:** v2025-11

Aggregated quarterly and yearly indicators derived directly from Thailand’s DDC Injury Surveillance (IS) raw file (`is2018.csv`, multi‑year contents). This repository provides all‑year rollups built from rows with a valid parsed event date. Only aggregates are published—no person‑level rows.

---

## Files (CSVs)
- `outputs/national_quarter.csv` — All‑Thailand cases by quarter across all parsed years
- `outputs/sex_year.csv` — National cases by sex (male/female/unknown) by year
- `outputs/age_bins_year.csv` — National cases by age group (0–14, 15–24, 25–44, 45–64, 65+) by year
- `outputs/hour_of_day.csv` — National cases by hour of day (0–23)
- `outputs/province_year.csv` — Province × year total cases
- `outputs/bkk_quarter.csv` — Bangkok (กรุงเทพมหานคร) cases by quarter
- `outputs/bkk_top_amphoe.csv` — Top 20 Bangkok amphoe by cases (if amphoe field available)
- `outputs/mode_mix_bkk_year.csv` — Bangkok mode mix by year (vehicle type share; may be `Unspecified` if ICD values not in V01–V89 format)

## Files (QA)
- `outputs/qa_summary.json` — Summary of coverage
  - `total_rows_raw`, `rows_with_parsed_event_date`, `share_parsed`, `year_filter`, `columns_present`
- `outputs/qa_year_counts.csv` — Parsed rows per year
- `outputs/qa_coverage_province_year.csv` — For each province‑year: `rows_parsed`, province total `rows_raw`, and `share_parsed_vs_prov_total`

## Figures (PNGs)
- `outputs/figures/national_quarter_cases.png`
- `outputs/figures/sex_national_by_year.png`
- `outputs/figures/age_bins_by_year.png`
- `outputs/figures/hour_of_day.png`
- `outputs/figures/bkk_quarter_cases.png`
- `outputs/figures/bkk_top_amphoe.png`
- `outputs/figures/mode_mix_bkk_share_by_year.png` (useful once vehicle mapping is resolved)

---

## Data Access
This dataset is available at: [https://bangkokfamilylawyer.com/datasets-injury-th/](https://bangkokfamilylawyer.com/datasets-injury-th/)

---

## Quick start (What’s inside the CSVs)
**Common fields**
- `year`, `quarter` (format `YYYY-Qn`)
- `prov` (province) in province‑level tables
- Measures: `cases` (counts). Some tables include shares.

**Vehicle type mapping (ICD‑10 V01–V89, when present)**
- V01–V09 Pedestrian • V10–V19 Bicycle • V20–V29 Motorcycle • V30–V39 Three‑wheeler • V40–V49 Car  
- V50–V59 Pickup/Van • V60–V69 Truck/Heavy • V70–V79 Bus • V80 Animal • V81–V82 Rail/Tram/Other • V83–V86 ATV/Industrial • V87–V89 Mixed/Unspecified

Note: If `icdcause` values are not in V01–V89 shapes in the raw, mode mix will appear as `Unspecified`.

---

## Methods (summary)
- **Source dataset:** DDC Injury Surveillance (IS). This repo reads the raw `is2018.csv` provided locally and builds aggregates.
- **Date logic:** Parse `adate` with fallback to `hdate` (day‑first). Per‑row Buddhist year correction (−543) when detected. Rows without a valid event date are excluded from time‑based aggregates.
- **Time buckets:** Derive `year`, `quarter` (`YYYY-Qn`).
- **Geography:** Province from `prov`. Bangkok filter = `กรุงเทพมหานคร`.
- **Demographics:** Age binned into 0–14, 15–24, 25–44, 45–64, 65+; sex normalized to male/female/unknown.
- **Bangkok mode mix:** Map `icdcause` to vehicle types when values match V01–V89; otherwise `Unspecified`.
- **Quality & completeness:** QA files show parsed coverage overall, by year, and by province.
- **Privacy:** Only aggregate tables are produced.

---

## How to reproduce
1. Ensure `is2018.csv` is present in the repo root.
2. Run:
   ```bash
   python aggregate_from_raw.py
   ```
3. Outputs appear under `outputs/` and figures under `outputs/figures/`.

Optional adjustments inside `aggregate_from_raw.py`:
- Set `YEAR_FILTER = None` (default) to include all years, or set to a specific year (e.g., `2018`).
- Provide a population file later if per‑capita rates are desired (not required for current outputs).

---

## License & Attribution
- **Source data:** Injury Prevention Division, Department of Disease Control (DDC), Ministry of Public Health — license as stated by the agency.
- **Compilation:** © AppDev Bangkok — released under **CC BY 4.0** for the aggregation logic, schema, charts, and narrative. Underlying records retain the original rights of the source agency.
- If you redistribute these aggregates, please include: *“Source data: DDC Injury Surveillance (Thailand). Compilation: AppDev Bangkok (CC BY 4.0).”*

---

## Citation (example)
**EN:** AppDev Bangkok (2025). *Thailand Road‑Traffic Injury Aggregates (Bangkok & Provinces).* Derived from DDC Injury Surveillance. CC BY 4.0.

**TH:** AppDev Bangkok (2568). *ตารางข้อมูลสรุปการบาดเจ็บจากอุบัติเหตุทางถนน (กรุงเทพฯ และจังหวัดต่าง ๆ).* อ้างอิงจากชุดข้อมูลเฝ้าระวังการบาดเจ็บของกรมควบคุมโรค เผยแพร่ภายใต้ CC BY 4.0

---

## Versioning & Durability
- Version tag: v2025-11
- Changelog: document schema/logic changes and added years.
- Archive: snapshot this page and each CSV on the Wayback Machine; keep `archive_url` references on your dataset page.

---

## Contact
Questions or corrections: **info@appdevbangkok.com** (EN/TH).
