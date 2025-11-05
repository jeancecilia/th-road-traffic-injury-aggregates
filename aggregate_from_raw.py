import os
from typing import Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

RAW_FILE = "is2018.csv"
OUT_DIR = "outputs"
FIG_DIR = os.path.join(OUT_DIR, "figures")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# Set Thai-capable font fallback to avoid glyph warnings (best-effort)
rcParams["font.family"] = [
    "Tahoma",
    "Segoe UI",
    "DejaVu Sans",
]
rcParams["axes.unicode_minus"] = False

# Optional: focus analysis on a single year for cleaner outputs
YEAR_FILTER = None  # set to a year like 2018 to restrict, or None for all years

# ---------------------- Utilities ----------------------

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Derive event_date from adate with fallback to hdate. Handle Buddhist years per-row.
    Returns a copy with event_date, year, quarter columns; rows with no event_date are removed.
    """
    df = df.copy()

    def _to_dt(s: pd.Series) -> pd.Series:
        dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
        # Apply per-row Buddhist year correction to avoid vectorized DateOffset overflow
        def _fix(ts):
            if pd.isna(ts):
                return ts
            try:
                if ts.year > 2400:
                    # use datetime.replace to subtract 543 years safely
                    return ts.replace(year=ts.year - 543)
            except Exception:
                return pd.NaT
            return ts
        return dt.apply(_fix)

    adate = _to_dt(df["adate"]) if "adate" in df.columns else pd.Series(pd.NaT, index=df.index)
    hdate = _to_dt(df["hdate"]) if "hdate" in df.columns else pd.Series(pd.NaT, index=df.index)

    event_date = adate.fillna(hdate)
    df["event_date"] = event_date
    df = df.loc[df["event_date"].notna()].copy()

    df["year"] = df["event_date"].dt.year
    df["quarter"] = df["year"].astype(str) + "-Q" + df["event_date"].dt.quarter.astype(str)
    return df


def normalize_sex(s: pd.Series) -> pd.Series:
    mapping = {
        "m": "male", "male": "male", "ชาย": "male", "1": "male", 1: "male",
        "f": "female", "female": "female", "หญิง": "female", "2": "female", 2: "female",
        "x": "unknown", "u": "unknown", "unk": "unknown", "unknown": "unknown", "ไม่ทราบ": "unknown",
        "0": "unknown", 0: "unknown", "": "unknown", None: "unknown",
    }
    return s.astype(str).str.strip().str.lower().map(mapping).fillna("unknown")


def icd_vehicle_map(code: Optional[str]) -> str:
    if not isinstance(code, str) or len(code) < 2:
        return "Unspecified"
    c = code.strip().upper()
    if not c.startswith("V"):
        return "Non-road or unspecified"
    # normalize like V20.1 -> V20
    digits = "".join(ch for ch in c[1:] if ch.isdigit())
    if len(digits) < 2:
        return "Unspecified"
    try:
        v = int(digits[:2])
    except Exception:
        return "Unspecified"
    if   1 <= v <= 9:   return "Pedestrian"
    if  10 <= v <= 19:  return "Bicycle"
    if  20 <= v <= 29:  return "Motorcycle"
    if  30 <= v <= 39:  return "Three-wheeler"
    if  40 <= v <= 49:  return "Car"
    if  50 <= v <= 59:  return "Pickup/Van"
    if  60 <= v <= 69:  return "Truck/Heavy"
    if  70 <= v <= 79:  return "Bus"
    if  v == 80:        return "Animal/Animal-drawn"
    if  81 <= v <= 82:  return "Rail/Tram/Other non-motor"
    if  83 <= v <= 86:  return "ATV/Industrial"
    if  87 <= v <= 88:  return "Multiple/Unspecified person"
    if  v == 89:        return "Unspecified motor vehicle"
    return "Unspecified"


# ---------------------- Aggregations ----------------------

def agg_national_quarter(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("quarter", dropna=False).size().reset_index(name="cases").sort_values("quarter")
    out.to_csv(os.path.join(OUT_DIR, "national_quarter.csv"), index=False)
    plt.figure(figsize=(12, 5))
    plt.bar(out["quarter"], out["cases"], color="#4C78A8")
    plt.title("National injury cases by quarter")
    plt.xlabel("Quarter"); plt.ylabel("Cases"); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "national_quarter_cases.png")); plt.close()
    return out


def agg_sex_year(df: pd.DataFrame) -> pd.DataFrame:
    sex_norm = normalize_sex(df["sex"]) if "sex" in df.columns else pd.Series(["unknown"] * len(df))
    tmp = df.assign(sex_norm=sex_norm)
    out = (
        tmp.groupby(["year", "sex_norm"], dropna=False).size().reset_index(name="cases")
           .pivot(index="year", columns="sex_norm", values="cases").fillna(0).reset_index()
    )
    out.to_csv(os.path.join(OUT_DIR, "sex_year.csv"), index=False)
    cols = [c for c in ["male", "female", "unknown"] if c in out.columns]
    plt.figure(figsize=(10, 5))
    out.set_index("year")[cols].plot(kind="bar", stacked=True, ax=plt.gca())
    plt.title("National injury cases by sex and year")
    plt.xlabel("Year"); plt.ylabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "sex_national_by_year.png")); plt.close()
    return out


def agg_province_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    prov_col = None
    for cand in ["prov", "province", "prov_name", "prov_th"]:
        if cand in df.columns:
            prov_col = cand; break
    if prov_col is None:
        return None
    out = df.groupby([prov_col, "year"], dropna=False).size().reset_index(name="cases")
    out = out.rename(columns={prov_col: "prov"})
    out.to_csv(os.path.join(OUT_DIR, "province_year.csv"), index=False)
    return out


def agg_bkk_quarter(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    prov_col = "prov" if "prov" in df.columns else None
    if prov_col is None:
        return None
    bkk_name = "กรุงเทพมหานคร"
    bkk = df.loc[df[prov_col].astype(str) == bkk_name]
    out = bkk.groupby(["quarter"], dropna=False).size().reset_index(name="cases").sort_values("quarter")
    out.to_csv(os.path.join(OUT_DIR, "bkk_quarter.csv"), index=False)
    plt.figure(figsize=(10, 4))
    plt.plot(out["quarter"], out["cases"], marker="o")
    plt.title("Bangkok (กรุงเทพมหานคร) cases by quarter")
    plt.xlabel("Quarter"); plt.ylabel("Cases"); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "bkk_quarter_cases.png")); plt.close()
    return out


def agg_mode_mix_bkk_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    if "prov" not in df.columns:
        return None
    icd_col = "icdcause" if "icdcause" in df.columns else None
    if icd_col is None:
        # auto-detect first column containing 'icd'
        cands = [c for c in df.columns if "icd" in str(c).lower()]
        if cands:
            icd_col = cands[0]
    if icd_col is None:
        return None
    bkk = df.loc[df["prov"].astype(str) == "กรุงเทพมหานคร"].copy()
    bkk["vehicle_type"] = bkk[icd_col].map(icd_vehicle_map)
    out = bkk.groupby(["year", "vehicle_type"], dropna=False).size().reset_index(name="cases")
    out["share_of_total"] = out["cases"] / out.groupby("year")["cases"].transform("sum")
    out.to_csv(os.path.join(OUT_DIR, "mode_mix_bkk_year.csv"), index=False)
    # simple plot
    pivot = out.pivot(index="vehicle_type", columns="year", values="share_of_total").fillna(0)
    plt.figure(figsize=(12, 6))
    pivot.plot(kind="bar", ax=plt.gca())
    plt.title("Bangkok mode mix share by year")
    plt.xlabel("Vehicle type"); plt.ylabel("Share of total")
    plt.tight_layout(); plt.savefig(os.path.join(FIG_DIR, "mode_mix_bkk_share_by_year.png")); plt.close()
    return out


def agg_age_bins_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Cases by age bins per year, with stacked bar figure."""
    if "age" not in df.columns:
        return None
    age = pd.to_numeric(df["age"], errors="coerce")
    bins = [0, 14, 24, 44, 64, 200]
    labels = ["0-14", "15-24", "25-44", "45-64", "65+"]
    tmp = df.assign(age_group=pd.cut(age, bins=bins, labels=labels, right=True, include_lowest=True))
    out = tmp.groupby(["year", "age_group"], dropna=False, observed=False).size().reset_index(name="cases")
    out.to_csv(os.path.join(OUT_DIR, "age_bins_year.csv"), index=False)
    # plot stacked
    pivot = out.pivot(index="year", columns="age_group", values="cases").fillna(0)
    plt.figure(figsize=(12, 6))
    pivot.plot(kind="bar", stacked=True, ax=plt.gca())
    plt.title("Cases by age group and year")
    plt.xlabel("Year"); plt.ylabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "age_bins_by_year.png")); plt.close()
    return out


def agg_hour_of_day(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Cases by hour-of-day, using event_date hour with fallback to atime hour."""
    if "event_date" not in df.columns:
        return None
    hours = df["event_date"].dt.hour
    if hours.isna().mean() > 0.5 and "atime" in df.columns:
        atime = pd.to_datetime(df["atime"], errors="coerce", dayfirst=True)
        hours = hours.fillna(atime.dt.hour)
    out = hours.value_counts(dropna=False).sort_index().rename_axis("hour").reset_index(name="cases")
    out = out[out["hour"].notna()].copy()
    out["hour"] = out["hour"].astype(int)
    out.to_csv(os.path.join(OUT_DIR, "hour_of_day.csv"), index=False)
    plt.figure(figsize=(10, 4))
    plt.bar(out["hour"], out["cases"], color="#4C78A8")
    plt.title("Cases by hour of day")
    plt.xlabel("Hour (0-23)"); plt.ylabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "hour_of_day.png")); plt.close()
    return out


def agg_bkk_top_amphoe(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Top 20 Bangkok amphoe by cases with horizontal bar figure."""
    if "prov" not in df.columns:
        return None
    bkk = df.loc[df["prov"].astype(str) == "กรุงเทพมหานคร"].copy()
    amph_col = None
    for cand in ["aampur", "amphoe", "district"]:
        if cand in bkk.columns:
            amph_col = cand; break
    if amph_col is None:
        return None
    out = bkk.groupby(amph_col, dropna=False).size().reset_index(name="cases").sort_values("cases", ascending=False).head(20)
    out = out.rename(columns={amph_col: "amphoe"})
    out.to_csv(os.path.join(OUT_DIR, "bkk_top_amphoe.csv"), index=False)
    plt.figure(figsize=(10, 8))
    plt.barh(out["amphoe"][::-1].astype(str), out["cases"][::-1], color="#4C78A8")
    plt.title("Bangkok: Top 20 amphoe by cases")
    plt.xlabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "bkk_top_amphoe.png")); plt.close()
    return out


def agg_head_injury_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Head injury share per year with line figure."""
    if "Head_Injury" not in df.columns:
        return None
    hi = df["Head_Injury"].astype(str).str.strip().str.lower()
    tmp = df.assign(hi_flag=hi.eq("hi"))
    year_counts = tmp.groupby("year").size().rename("cases")
    hi_counts = tmp.groupby("year")["hi_flag"].sum().rename("head_injury_cases")
    out = pd.concat([year_counts, hi_counts], axis=1).reset_index()
    out["head_injury_share"] = (out["head_injury_cases"] / out["cases"]).round(4)
    out.to_csv(os.path.join(OUT_DIR, "head_injury_year.csv"), index=False)
    plt.figure(figsize=(10, 5))
    plt.plot(out["year"], out["head_injury_share"], marker="o")
    plt.title("Head injury share by year")
    plt.xlabel("Year"); plt.ylabel("Share of cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "head_injury_share_by_year.png")); plt.close()
    return out


def agg_top10_provinces_latest_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Top 10 provinces by cases in the latest parsed year, with barh figure."""
    if "prov" not in df.columns:
        return None
    prov_year = df.groupby(["prov", "year"], dropna=False).size().reset_index(name="cases")
    if prov_year.empty:
        return None
    latest_year = int(prov_year["year"].max())
    latest = prov_year[prov_year["year"] == latest_year].copy().sort_values("cases", ascending=False).head(10)
    latest.to_csv(os.path.join(OUT_DIR, "top10_provinces_latest_year.csv"), index=False)
    # figure
    plt.figure(figsize=(10, 6))
    plt.barh(latest["prov"][::-1].astype(str), latest["cases"][::-1], color="#4C78A8")
    plt.title(f"Top 10 provinces by cases in {latest_year}")
    plt.xlabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "top10_provinces_latest_year.png")); plt.close()
    return latest


def qa_parsed_coverage_by_province_year(raw_df: pd.DataFrame, parsed_df: pd.DataFrame) -> None:
    """Write a coverage table: for each province-year, rows_parsed / rows_total."""
    # Determine province column in raw
    prov_col = None
    for cand in ["prov", "province", "prov_name", "prov_th"]:
        if cand in raw_df.columns:
            prov_col = cand; break
    if prov_col is None or "year" not in parsed_df.columns:
        return
    # Total rows per province-year in raw (even if no date)
    raw_year = parsed_df[["event_date"]].copy()
    # recompute year from raw's dates to align? Instead, approximate with parsed year groups only for denominator per prov.
    # Better: use parsed_df for year dimension, but count raw totals per province to gauge relative share by province overall.
    total_by_prov = raw_df.groupby(prov_col, dropna=False).size().reset_index(name="rows_raw")
    parsed_by_prov_year = parsed_df.groupby(["prov", "year"], dropna=False).size().reset_index(name="rows_parsed") if "prov" in parsed_df.columns else None
    if parsed_by_prov_year is None or parsed_by_prov_year.empty:
        return
    cov = parsed_by_prov_year.merge(total_by_prov.rename(columns={prov_col: "prov"}), on="prov", how="left")
    cov["share_parsed_vs_prov_total"] = (cov["rows_parsed"] / cov["rows_raw"]).round(4)
    cov.to_csv(os.path.join(OUT_DIR, "qa_coverage_province_year.csv"), index=False)

# ---------------------- Main ----------------------

def main():
    print("Loading raw data...")
    raw = pd.read_csv(RAW_FILE, encoding="utf-8", low_memory=False)
    print(f"Rows: {len(raw):,}")

    print("Parsing dates and deriving time buckets...")
    df = parse_dates(raw)
    print(f"Rows with valid event_date: {len(df):,}")

    # Optional focus year
    if YEAR_FILTER is not None:
        df = df.loc[df["year"] == YEAR_FILTER].copy()
        print(f"Applying year filter = {YEAR_FILTER}: rows = {len(df):,}")

    print("Building aggregations...")
    agg_national_quarter(df)
    agg_sex_year(df)
    agg_province_year(df)
    agg_bkk_quarter(df)
    agg_mode_mix_bkk_year(df)
    agg_age_bins_year(df)
    agg_hour_of_day(df)
    agg_bkk_top_amphoe(df)
    agg_head_injury_year(df)
    agg_top10_provinces_latest_year(df)

    # QA summary
    try:
        import json
        # completeness relative to raw
        total_rows = int(raw.shape[0])
        parsed_rows = int(df.shape[0]) if YEAR_FILTER is None else int(df.shape[0])
        qa = {
            "total_rows_raw": total_rows,
            "rows_with_parsed_event_date": parsed_rows,
            "share_parsed": round(parsed_rows / total_rows, 4) if total_rows else None,
            "year_filter": YEAR_FILTER,
            "columns_present": list(df.columns),
        }
        with open(os.path.join(OUT_DIR, "qa_summary.json"), "w", encoding="utf-8") as f:
            json.dump(qa, f, ensure_ascii=False, indent=2)
        # Year distribution
        year_counts = df["year"].value_counts().sort_index().rename_axis("year").reset_index(name="rows")
        year_counts.to_csv(os.path.join(OUT_DIR, "qa_year_counts.csv"), index=False)
        # Province coverage summary (parsed vs total rows by province)
        qa_parsed_coverage_by_province_year(raw, df)
    except Exception:
        pass

    print(f"Done. CSVs in '{OUT_DIR}', figures in '{FIG_DIR}'.")


if __name__ == "__main__":
    main()
