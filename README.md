[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17538574.svg)](https://doi.org/10.5281/zenodo.17538574)

> **Canonical dataset page (EN/TH): https://bangkokfamilylawyer.com/datasets-injury-th/**

# Thailand Road‑Traffic Injury Aggregates 2018 (Bangkok & Provinces)
**Version:** v2025-11 (2018 Data Release)

Aggregated quarterly and yearly indicators derived from Thailand's DDC Injury Surveillance (IS) raw file for 2018 (`is2018.csv`). This repository provides comprehensive 2018 data rollups built from rows with valid parsed event dates. Only aggregates are published—no person‑level data is included.

---

## Files (CSVs)
- `outputs/national_quarter_2018.csv` — All‑Thailand cases by quarter for 2018
- `outputs/sex_2018.csv` — National cases by sex (male/female/unknown) for 2018
- `outputs/age_bins_2018.csv` — National cases by age group (0–14, 15–24, 25–44, 45–64, 65+) for 2018
- `outputs/hour_of_day_2018.csv` — National cases by hour of day (0–23) for 2018
- `outputs/province_2018.csv` — Province total cases for 2018
- `outputs/bkk_quarter_2018.csv` — Bangkok (กรุงเทพมหานคร) cases by quarter for 2018
- `outputs/bkk_top_amphoe_2018.csv` — Top 20 Bangkok districts by cases for 2018
- `outputs/mode_mix_bkk_2018.csv` — Bangkok mode mix by vehicle type for 2018
- `outputs/head_injury_2018.csv` — Head injury statistics for 2018

## QA Files
- `outputs/qa_summary_2018.json` — Summary of 2018 data coverage
  - `total_rows_raw`, `rows_with_parsed_event_date`, `share_parsed`, `year_filter`, `columns_present`
- `outputs/qa_year_counts_2018.csv` — Row counts by year (showing 2018 focus)
- `outputs/qa_coverage_province_2018.csv` — Coverage by province: `rows_parsed`, province total `rows_raw`, and `share_parsed_vs_prov_total`

## Figures (PNGs)
- `outputs/figures/national_quarter_2018.png` — Quarterly national case counts for 2018
- `outputs/figures/sex_distribution_2018.png` — Gender distribution of cases for 2018
- `outputs/figures/age_bins_2018.png` — Age group distribution for 2018
- `outputs/figures/hour_of_day_2018.png` — Hourly distribution of cases for 2018
- `outputs/figures/bkk_quarter_2018.png` — Bangkok quarterly cases for 2018
- `outputs/figures/bkk_top_amphoe_2018.png` — Top 20 districts in Bangkok by case count for 2018
- `outputs/figures/mode_mix_bkk_2018.png` — Vehicle type distribution in Bangkok for 2018
- `outputs/figures/head_injury_2018.png` — Head injury statistics for 2018
- `outputs/figures/top10_provinces_2018.png` — Top 10 provinces by case count for 2018

---

## Data Access
This dataset is available at: [https://bangkokfamilylawyer.com/datasets-injury-th/](https://bangkokfamilylawyer.com/datasets-injury-th/)

---

## Quick start (What’s inside the CSVs)
**Common fields**
- `year` (2018 for all files)
- `quarter` (format `2018-Qn` where n=1-4)
- `prov` (province) in province‑level tables
- Measures: `cases` (counts). Some tables include shares or percentages.

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

## How to Cite

### Concept (all versions)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17538574.svg)](https://doi.org/10.5281/zenodo.17538574)

### This specific release (v2025-11.1)
**Plain text citation (EN):**  
Jean Maurice Cecilia Menzel (2025). Thailand Road-Traffic Injury Aggregates (Bangkok & Provinces) [dataset]. Zenodo. https://doi.org/10.5281/zenodo.17538573 (CC BY 4.0)

**BibTeX:**
```bibtex
@dataset{menzel_2025_th_injury_aggregates,
  author    = {Jean Maurice Cecilia Menzel},
  title     = {Thailand Road-Traffic Injury Aggregates (Bangkok \& Provinces)},
  year      = {2025},
  publisher = {Zenodo},
  version   = {v2025-11.1},
  doi       = {10.5281/zenodo.17538573},
  url       = {https://doi.org/10.5281/zenodo.17538573}
}
```

**TH:**  
AppDev Bangkok (2568). *ตารางข้อมูลสรุปการบาดเจ็บจากอุบัติเหตุทางถนน พ.ศ. 2561 (กรุงเทพฯ และจังหวัดต่าง ๆ).* อ้างอิงจากชุดข้อมูลเฝ้าระวังการบาดเจ็บของกรมควบคุมโรค เผยแพร่ภายใต้ CC BY 4.0

---

## Versioning & Durability
- Version tag: v2025-11
- Changelog: document schema/logic changes and added years.
- Archive: snapshot this page and each CSV on the Wayback Machine; keep `archive_url` references on your dataset page.

---

## Contact
Questions or corrections: **info@appdevbangkok.com** (EN/TH).
