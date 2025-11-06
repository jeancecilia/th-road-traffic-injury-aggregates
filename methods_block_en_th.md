# Methods (EN/TH — paste‑ready)

## EN — Methods
**Source dataset.** 2018 Injury Surveillance data published by the Injury Prevention Division, DDC (Thailand). This analysis focuses exclusively on 2018 data from the `is2018.csv` file. We cite the official dataset page and keep archived copies of the files used.

**Ingestion & cleaning.** We read the raw CSV; parsed dates day‑first; converted Buddhist years to Gregorian (−543). The primary date for aggregation is **arrival date (`adate`)** with fallback to **hospital date (`hdate`)**. Rows without any valid date or outside 2018 were excluded from the analysis.

**Aggregation.** We derived `quarter (2018-Qn)` and `month` from the event date. Province information was extracted from the `prov` field (Bangkok = `กรุงเทพมหานคร`). We generated comprehensive outputs including national quarterly data, province totals, Bangkok district-level data, and various demographic breakdowns specifically for 2018.

**Derivations.** For the 2018 dataset, `vehicle_type` was derived from **ICD‑10 V‑codes** (`icdcause`): V01–V09 pedestrian, V10–V19 bicycle, V20–V29 motorcycle, V40–V49 car, V50–V59 pickup/van, V60–V69 truck/heavy, V70–V79 bus, etc. Risk factors including `alcohol`, `helmet`, and `seatbelt` usage were normalized to yes/no/unknown when present in the source data. A conservative `death_flag` was detected through keyword searches across outcome-related fields (`diser/staer/staward/er/er_t`).

**Rates (2018).** All rates are calculated for the 2018 calendar year. `alcohol_share` represents the proportion of cases where alcohol was involved out of all applicable cases. `helmet_rate` shows the proportion of motorcycle riders/passengers wearing helmets. `seatbelt_rate` indicates seatbelt usage among occupants of cars/vans/pickups/buses/trucks. Population-based rates (`per100k`) are included where provincial population data is available for 2018.

**Privacy.** We publish **aggregates only**. Any rare small cells may be rounded/suppressed. No person‑level data is exposed.

**License.** Source data remains under the license stated by DDC. Our compilation (tables, charts, narrative) is **CC BY 4.0**.

---

## TH — วิธีวิจัย
**ชุดข้อมูลต้นทาง** มาจากการเฝ้าระวังการบาดเจ็บของกองป้องกันการบาดเจ็บ กรมควบคุมโรค (ประเทศไทย) โดยอ้างอิงลิงก์ทางการ และจัดเก็บลิงก์สำรอง (archive) ของไฟล์ที่ใช้

**การเตรียมข้อมูล** อ่านไฟล์ CSV รายปี แปลงวันที่แบบวัน/เดือน/ปี และแปลงปีพุทธศักราชเป็นคริสต์ศักราช (ลบ 543) วันที่หลักที่ใช้สรุปคือ **วันมาถึง (`adate`)** และสำรองด้วย **วันของโรงพยาบาล (`hdate`)** หากไม่มีวันที่ที่ถูกต้อง แถวนั้นจะไม่ถูกนำไปรวมในตารางตามเวลา

**การสรุปผล** สร้างตัวแปร `ไตรมาส (2561-Qn)` และ `เดือน` จากวันที่เกิดเหตุ ดึงข้อมูลจังหวัดจาก `prov` (กรุงเทพฯ = `กรุงเทพมหานคร`) และจัดทำผลลัพธ์ครอบคลุม ได้แก่ ข้อมูลสรุปรายไตรมาสทั้งประเทศ ข้อมูลสรุปรายจังหวัด การกระจายตัวของประเภทผู้ใช้ถนนในกรุงเทพฯ ข้อมูลอายุและเพศของผู้บาดเจ็บ และการวิเคราะห์ปัจจัยเสี่ยงต่างๆ สำหรับปี 2561

**ตัวแปรอนุพันธ์** สำหรับปี 2561 ประเภทผู้ใช้ถนน (`vehicle_type`) ได้มาจากรหัส **ICD‑10 กลุ่ม V** (`icdcause`) เช่น V20–V29 = รถจักรยานยนต์, V40–V49 = รถยนต์ เป็นต้น ฟิลด์ปัจจัยเสี่ยง (`alcohol`, `helmet`, `seatbelt`) ถูกแปลงค่าเป็น ใช่/ไม่ใช่/ไม่ทราบ เมื่อมีในชุดข้อมูลต้นทาง ค่าการเสียชีวิต (`death_flag`) ตรวจจับแบบระมัดระวังด้วยการค้นหาคีย์เวิร์ดในฟิลด์ผลลัพธ์ (`diser/staer/staward/er/er_t`).

**อัตราต่าง ๆ (ปี 2561)** `alcohol_share` = จำนวน "ใช่" / จำนวนที่พอจะประเมินได้; `helmet_rate` = อัตราการสวมหมวกนิรภัยในกลุ่ม **ผู้ใช้รถจักรยานยนต์**; `seatbelt_rate` = อัตราการคาดเข็มขัดนิรภัยในกลุ่ม **ผู้โดยสารรถยนต์/รถตู้/รถกระบะ/รถบัส/รถบรรทุก** `per100k` คำนวณจากจำนวนประชากรจังหวัดปี 2561‑รายปี

**ความเป็นส่วนตัว** เผยแพร่เฉพาะ **ข้อมูลสรุป** เท่านั้น และอาจปัดเศษ/ซ่อนค่าที่มีจำนวนน้อยมากเพื่อป้องกันการระบุตัวตน

**สัญญาอนุญาต** ข้อมูลต้นทางเป็นไปตามสัญญาอนุญาตของหน่วยงาน (DDC) ส่วนการสรุป/จัดรูปแบบโดยเรา เผยแพร่ภายใต้ **CC BY 4.0**
