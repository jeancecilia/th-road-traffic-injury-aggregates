# Thailand Road‑Traffic Injury Aggregates (Bangkok & Provinces)
**Version:** v2025-11  

Aggregated quarterly and yearly indicators derived from Thailand’s DDC Injury Surveillance open data. This package includes Bangkok‑focused trends, province‑year totals, mode mix, age/sex splits, and risk‑factor rates (if mapped). Only **aggregate** tables are published—**no person‑level rows**.

---

## Files
- `injury_bkk_quarter.csv` — Bangkok quarterly rollup (`year`, `quarter`, `cases`, `deaths`, optional `alcohol_share`, `helmet_rate`, `seatbelt_rate`, `per100k`)*
- `injury_province_year.csv` — Province × year totals with optional `per100k`
- `injury_mode_mix_bkk_year.csv` — Bangkok mode mix by year (`vehicle_type`, `cases`, `share_of_total`)
- `injury_age_sex_bkk_year.csv` — Bangkok age‑group × sex counts (and optional `per100k` if pop by age‑sex is available)
- `injury_risk_factors_bkk_quarter.csv` — Bangkok quarterly risk summaries (alcohol/helmet/seatbelt), if risk fields mapped
- `bangkok_quarterly_cases.png` — Chart for quick embedding
- `mode_mix_share_by_year.png` — Chart for quick embedding
- `top10_provinces_latest_year.csv` — Convenience table for the latest year
- `qa_summary.json` — Lightweight QA notes (column checks, nulls, share‑of‑total sanity)
- `commons_captions.csv` — EN/TH captions for Wikimedia Commons uploads

\* `per100k` appears when `province_population.csv` was provided during aggregation.

---

## Quick start (What’s inside the CSVs)
**Columns you’ll commonly see**
- `year`, `quarter` (format `YYYY-Qn`), sometimes `month`
- `prov` (province) in province‑level tables
- `vehicle_type` in mode‑mix tables (derived from ICD‑10 V‑codes)
- Measures: `cases`, `deaths`, `alcohol_share`, `helmet_rate`, `seatbelt_rate`, `per100k`

**Vehicle type mapping (from ICD‑10 V01–V89)**
- V01–V09 Pedestrian • V10–V19 Bicycle • V20–V29 Motorcycle • V30–V39 Three‑wheeler • V40–V49 Car  

- V50–V59 Pickup/Van • V60–V69 Truck/Heavy • V70–V79 Bus • V80 Animal • V81–V82 Rail/Tram/Other • V83–V86 ATV/Industrial • V87–V89 Mixed/Unspecified

---

## Methods (summary)
- **Source dataset:** DDC Injury Surveillance (open data catalog).
- **Date logic:** Primary `adate` (arrival), fallback `hdate`; parse day‑first; convert Buddhist years to Gregorian (−543).
- **Time buckets:** derive `year`, `quarter` (`YYYY-Qn`), and `month`.
- **Geography:** province from `prov`; Bangkok filter = `กรุงเทพมหานคร`.
- **Derivations:** `vehicle_type` from `icdcause` V‑ranges; risk rates normalized to yes/no/unknown when the config flags (`alcohol`, `helmet`, `seatbelt`) are mapped.
- **Outcomes:** `death_flag` via conservative keyword search across `diser/staer/staward/er/er_t` (exact mapping may vary by year).
- **Population join:** optional province‑year population for `per100k`.
- **Privacy:** only aggregates are published; rare small cells may be rounded/suppressed.

See **Methods block (EN/TH)** in `methods_block_en_th.md` for paste‑ready website content.

---

## License & Attribution
- **Source data:** Injury Prevention Division, Department of Disease Control (DDC), Ministry of Public Health — license as stated on the dataset page (often **CC BY**). Always cite the official dataset page and archive links.
- **Compilation:** © Kaizen Kode — released under **CC BY 4.0** for the aggregation logic, schema, charts, and narrative. Underlying records retain the original rights of the source agency.
- If you redistribute these aggregates, please include: *“Source data: DDC Injury Surveillance (Thailand). Compilation: Kaizen Kode (CC BY 4.0).”*

---

## Citation (example)
**EN:** Kaizen Kode (2025). *Thailand Road‑Traffic Injury Aggregates (Bangkok & Provinces).* Derived from DDC Injury Surveillance. CC BY 4.0.  

**TH:** Kaizen Kode (2568). *ตารางข้อมูลสรุปการบาดเจ็บจากอุบัติเหตุทางถนน (กรุงเทพฯ และจังหวัดต่าง ๆ).* อ้างอิงจากชุดข้อมูลเฝ้าระวังการบาดเจ็บของกรมควบคุมโรค เผยแพร่ภายใต้ CC BY 4.0

---

## Versioning & Durability
- Version tag: v2025-11
- Changelog: describe any schema/logic changes and new years added.
- Archive: snapshot this page and each CSV on the Wayback Machine; keep `archive_url` references on your dataset page.

---

## Contact
Questions or corrections: **contact@kaizenkode.de** (EN/TH).

---

## (TH) คำอธิบายโดยย่อ
ชุดข้อมูลนี้เป็น **ข้อมูลสรุป (aggregate)** ของอุบัติเหตุทางถนน แยกตามไตรมาส/ปี จังหวัด และประเภทผู้ใช้ถนน (รถจักรยานยนต์ รถยนต์ ฯลฯ) โดยอาศัยข้อมูลเปิดของ **กรมควบคุมโรค (DDC)**  มีเพียงสถิติรวมเท่านั้น **ไม่มีข้อมูลรายบุคคล**  มีไฟล์ CSV สำหรับนำไปวิเคราะห์ต่อ และมีรูปภาพกราฟสำหรับใช้นำเสนอ/เผยแพร่

**วิธีการ (ย่อ):** แปลงวันที่แบบไทยเป็นสากล สร้าง `ปี/ไตรมาส` สรุปตามจังหวัด กำหนดประเภทผู้ใช้ถนนจากรหัส ICD‑10 (V01–V89) และคำนวณอัตรา (เช่น ใส่หมวกนิรภัย/คาดเข็มขัด) หากมีการแมปคอลัมน์ความเสี่ยงไว้  

**สัญญาอนุญาต:** ข้อมูลต้นทางเป็นไปตามเงื่อนไขในเพจของหน่วยงาน  ส่วนการรวบรวม/จัดรูปแบบโดย Kaizen Kode เผยแพร่ภายใต้ **CC BY 4.0**

