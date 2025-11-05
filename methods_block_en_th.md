# Methods (EN/TH — paste‑ready)

## EN — Methods
**Source dataset.** Injury Surveillance published by the Injury Prevention Division, DDC (Thailand). We cite the official dataset page and keep archived copies of the files we used.

**Ingestion & cleaning.** We read the yearly CSVs; parsed dates day‑first; converted Buddhist years to Gregorian (−543). The primary date for aggregation is **arrival date (`adate`)** with fallback to **hospital date (`hdate`)**. Rows without any valid date were excluded from time‑based tables.

**Aggregation.** We derived `year`, `quarter (YYYY-Qn)`, and `month`. Province came from `prov` (Bangkok = `กรุงเทพมหานคร`). We generated five outputs: Bangkok quarterly, province‑year totals, Bangkok mode mix by year, Bangkok age×sex by year, and Bangkok risk‑factor summaries by quarter.

**Derivations.** `vehicle_type` was derived from **ICD‑10 V‑codes** (`icdcause`): V01–V09 pedestrian, V10–V19 bicycle, V20–V29 motorcycle, V40–V49 car, V50–V59 pickup/van, V60–V69 truck/heavy, V70–V79 bus, etc. Risk fields (`alcohol`, `helmet`, `seatbelt`) were normalized to yes/no/unknown when present in the source schema. A conservative `death_flag` was detected by keyword search across outcome fields (`diser/staer/staward/er/er_t`).

**Rates.** `alcohol_share` = yes / applicable; `helmet_rate` = yes / applicable among **motorcycle** cases; `seatbelt_rate` = yes / applicable among **car/van/pickup/bus/truck** cases. `per100k` is computed only when province‑year population is available.

**Privacy.** We publish **aggregates only**. Any rare small cells may be rounded/suppressed. No person‑level data is exposed.

**License.** Source data remains under the license stated by DDC. Our compilation (tables, charts, narrative) is **CC BY 4.0**.

---

## TH — วิธีวิจัย
**ชุดข้อมูลต้นทาง** มาจากการเฝ้าระวังการบาดเจ็บของกองป้องกันการบาดเจ็บ กรมควบคุมโรค (ประเทศไทย) โดยอ้างอิงลิงก์ทางการ และจัดเก็บลิงก์สำรอง (archive) ของไฟล์ที่ใช้

**การเตรียมข้อมูล** อ่านไฟล์ CSV รายปี แปลงวันที่แบบวัน/เดือน/ปี และแปลงปีพุทธศักราชเป็นคริสต์ศักราช (ลบ 543) วันที่หลักที่ใช้สรุปคือ **วันมาถึง (`adate`)** และสำรองด้วย **วันของโรงพยาบาล (`hdate`)** หากไม่มีวันที่ที่ถูกต้อง แถวนั้นจะไม่ถูกนำไปรวมในตารางตามเวลา

**การสรุปผล** สร้างตัวแปร `ปี` และ `ไตรมาส (YYYY-Qn)` และ `เดือน` ดึงจังหวัดจาก `prov` (กรุงเทพฯ = `กรุงเทพมหานคร`) และจัดทำ 5 เอาต์พุต ได้แก่ สรุปกรุงเทพฯ รายไตรมาส รวมจังหวัด‑รายปี สัดส่วนประเภทผู้ใช้ถนนของกรุงเทพฯ รายปี สรุปอายุ×เพศของกรุงเทพฯ รายปี และสรุปปัจจัยเสี่ยงของกรุงเทพฯ รายไตรมาส

**ตัวแปรอนุพันธ์** ประเภทผู้ใช้ถนน (`vehicle_type`) ได้มาจากรหัส **ICD‑10 กลุ่ม V** (`icdcause`) เช่น V20–V29 = รถจักรยานยนต์, V40–V49 = รถยนต์ เป็นต้น ฟิลด์ปัจจัยเสี่ยง (`alcohol`, `helmet`, `seatbelt`) ถูกแปลงค่าเป็น ใช่/ไม่ใช่/ไม่ทราบ เมื่อมีในสคีมาชุดข้อมูลต้นทาง ค่าการเสียชีวิต (`death_flag`) ตรวจจับแบบระมัดระวังด้วยการค้นหาคีย์เวิร์ดในฟิลด์ผลลัพธ์ (`diser/staer/staward/er/er_t`).

**อัตราต่าง ๆ** `alcohol_share` = จำนวน “ใช่” / จำนวนที่พอจะประเมินได้; `helmet_rate` = อัตราการสวมหมวกนิรภัยในกลุ่ม **รถจักรยานยนต์**; `seatbelt_rate` = อัตราการคาดเข็มขัดในกลุ่ม **รถยนต์/รถตู้/ปิกอัพ/รถโดยสาร/รถบรรทุก**; `per100k` คำนวณเมื่อมีข้อมูลประชากรจังหวัด‑รายปี

**ความเป็นส่วนตัว** เผยแพร่เฉพาะ **ข้อมูลสรุป** เท่านั้น และอาจปัดเศษ/ซ่อนค่าที่มีจำนวนน้อยมากเพื่อป้องกันการระบุตัวตน

**สัญญาอนุญาต** ข้อมูลต้นทางเป็นไปตามสัญญาอนุญาตของหน่วยงาน (DDC) ส่วนการสรุป/จัดรูปแบบโดยเรา เผยแพร่ภายใต้ **CC BY 4.0**
