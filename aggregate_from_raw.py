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

# Focus analysis on 2018 data only
YEAR_FILTER = 2018  # Set to 2018 to focus on the main year with complete data

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
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    out = df_2018.groupby("quarter", dropna=False).size().reset_index(name="cases").sort_values("quarter")
    out.to_csv(os.path.join(OUT_DIR, "national_quarter.csv"), index=False)
    plt.figure(figsize=(12, 5))
    plt.bar(out["quarter"], out["cases"], color="#4C78A8")
    plt.title("National injury cases by quarter (2018)")
    plt.xlabel("Quarter"); plt.ylabel("Cases"); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "national_quarter_cases.png")); plt.close()
    return out


def agg_sex_year(df: pd.DataFrame) -> pd.DataFrame:
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    sex_norm = normalize_sex(df_2018["sex"]) if "sex" in df_2018.columns else pd.Series(["unknown"] * len(df_2018))
    tmp = df_2018.assign(sex_norm=sex_norm)
    out = (
        tmp.groupby(["sex_norm"], dropna=False).size().reset_index(name="cases")
    )
    # Add year column for consistency
    out["year"] = 2018
    out = out.rename(columns={"sex_norm": "sex"})
    out = out[["sex", "year", "cases"]]
    out.to_csv(os.path.join(OUT_DIR, "sex_year.csv"), index=False)
    
    # Create visualization
    plt.figure(figsize=(10, 5))
    plt.bar(out["sex"], out["cases"], color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    plt.title("Injury cases by sex (2018)")
    plt.xlabel("Sex"); plt.ylabel("Cases"); plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "sex_national_by_year.png")); plt.close()
    return out


def agg_province_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    prov_col = None
    for cand in ["prov", "province", "prov_name", "prov_th"]:
        if cand in df.columns:
            prov_col = cand; break
    if prov_col is None:
        return None
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    out = df_2018.groupby(prov_col, dropna=False).size().reset_index(name="cases")
    out = out.rename(columns={prov_col: "prov"})
    # Add year column for consistency
    out["year"] = 2018
    out = out[["prov", "year", "cases"]]
    out.to_csv(os.path.join(OUT_DIR, "province_year.csv"), index=False)
    return out


def agg_bkk_quarter(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    prov_col = "prov" if "prov" in df.columns else None
    if prov_col is None:
        return None
    bkk_name = "กรุงเทพมหานคร"
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    bkk = df_2018.loc[df_2018[prov_col].astype(str) == bkk_name]
    out = bkk.groupby(["quarter"], dropna=False).size().reset_index(name="cases").sort_values("quarter")
    # Filter to only include 2018 quarters
    out = out[out["quarter"].str.startswith("2018")]
    out.to_csv(os.path.join(OUT_DIR, "bkk_quarter.csv"), index=False)
    plt.figure(figsize=(10, 4))
    plt.plot(out["quarter"], out["cases"], marker="o")
    plt.title(f"Bangkok (กรุงเทพมหานคร) cases by quarter (2018)")
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
    # Filter for 2018 data only and Bangkok
    df_2018 = df[df["year"] == 2018].copy()
    bkk = df_2018.loc[df_2018["prov"].astype(str) == "กรุงเทพมหานคร"].copy()
    if len(bkk) == 0:
        return None
    bkk["vehicle_type"] = bkk[icd_col].map(icd_vehicle_map)
    out = bkk.groupby("vehicle_type", dropna=False).size().reset_index(name="cases")
    out["share_of_total"] = out["cases"] / out["cases"].sum()
    # Add year column for consistency
    out["year"] = 2018
    out = out[["year", "vehicle_type", "cases", "share_of_total"]]
    out.to_csv(os.path.join(OUT_DIR, "mode_mix_bkk_year.csv"), index=False)
    
    # Plot the distribution
    plt.figure(figsize=(12, 6))
    out_sorted = out.sort_values("share_of_total", ascending=False)
    plt.bar(out_sorted["vehicle_type"], out_sorted["share_of_total"] * 100, color="#4C78A8")
    plt.title("Bangkok mode distribution (2018)")
    plt.xlabel("Vehicle type"); plt.ylabel("Percentage of cases")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "mode_mix_bkk_share_by_year.png"))
    plt.close()
    return out


def agg_age_bins_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Cases by age bins for 2018, with bar chart figure."""
    if "age" not in df.columns:
        return None
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    age = pd.to_numeric(df_2018["age"], errors="coerce")
    bins = [0, 14, 24, 44, 64, 200]
    labels = ["0-14", "15-24", "25-44", "45-64", "65+"]
    tmp = df_2018.assign(age_group=pd.cut(age, bins=bins, labels=labels, right=True, include_lowest=True))
    out = tmp.groupby("age_group", dropna=False).size().reset_index(name="cases")
    # Add year column for consistency
    out["year"] = 2018
    out = out[["age_group", "year", "cases"]]
    out.to_csv(os.path.join(OUT_DIR, "age_bins_year.csv"), index=False)
    
    # Plot the distribution
    plt.figure(figsize=(12, 6))
    plt.bar(out["age_group"], out["cases"], color="#4C78A8")
    plt.title("Cases by age group (2018)")
    plt.xlabel("Age group"); plt.ylabel("Number of cases")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "age_bins_by_year.png"))
    plt.close()
    return out


def agg_hour_of_day(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Cases by hour-of-day for 2018, using event_date hour with fallback to atime hour."""
    if "event_date" not in df.columns:
        return None
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    hours = df_2018["event_date"].dt.hour
    if hours.isna().mean() > 0.5 and "atime" in df_2018.columns:
        atime = pd.to_datetime(df_2018["atime"], errors="coerce", dayfirst=True)
        hours = hours.fillna(atime.dt.hour)
    out = hours.value_counts(dropna=False).sort_index().rename_axis("hour").reset_index(name="cases")
    out = out[out["hour"].notna()].copy()
    out["hour"] = out["hour"].astype(int)
    # Add year column for consistency
    out["year"] = 2018
    out = out[["hour", "year", "cases"]]
    out.to_csv(os.path.join(OUT_DIR, "hour_of_day.csv"), index=False)
    
    # Plot the distribution
    plt.figure(figsize=(12, 5))
    plt.bar(out["hour"], out["cases"], color="#4C78A8")
    plt.title("Cases by hour of day (2018)")
    plt.xlabel("Hour of day (0-23)")
    plt.ylabel("Number of cases")
    plt.xticks(range(0, 24))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "hour_of_day.png"))
    plt.close()
    return out


def agg_bkk_top_amphoe(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Top 20 Bangkok districts by cases for 2018 with horizontal bar figure."""
    if "prov" not in df.columns:
        return None
    # Filter for 2018 data only and Bangkok
    df_2018 = df[df["year"] == 2018].copy()
    bkk = df_2018.loc[df_2018["prov"].astype(str) == "กรุงเทพมหานคร"].copy()
    if len(bkk) == 0:
        return None
    
    # Try to find the district column
    amph_col = None
    for cand in ["aampur", "amphoe", "district", "ampur"]:
        if cand in bkk.columns:
            amph_col = cand
            break
    if amph_col is None:
        return None
    
    # Clean up district names and count cases
    bkk["district"] = bkk[amph_col].astype(str).str.strip()
    out = (
        bkk.groupby("district", dropna=False)
        .size()
        .reset_index(name="cases")
        .sort_values("cases", ascending=False)
        .head(20)
    )
    
    # Add year column for consistency
    out["year"] = 2018
    out = out[["district", "year", "cases"]]
    out.to_csv(os.path.join(OUT_DIR, "bkk_top_amphoe.csv"), index=False)
    
    # Create the visualization
    plt.figure(figsize=(12, 8))
    plt.barh(
        out["district"][::-1],  # Reverse for descending order
        out["cases"][::-1],
        color="#4C78A8",
        height=0.8
    )
    plt.title("Bangkok: Top 20 districts by cases (2018)", pad=20)
    plt.xlabel("Number of cases", labelpad=10)
    plt.ylabel("District", labelpad=10)
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    
    # Add value labels on the bars
    for i, v in enumerate(out["cases"][::-1]):
        plt.text(v + 5, i, str(v), va="center", fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "bkk_top_amphoe.png"), dpi=120, bbox_inches="tight")
    plt.close()
    
    return out


def agg_head_injury_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Head injury statistics for 2018 with bar chart."""
    if "Head_Injury" not in df.columns:
        return None
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    if len(df_2018) == 0:
        return None
    
    # Process head injury data
    hi = df_2018["Head_Injury"].astype(str).str.strip().str.lower()
    total_cases = len(hi)
    head_injury_cases = hi.eq("hi").sum()
    head_injury_share = head_injury_cases / total_cases if total_cases > 0 else 0
    
    # Create output dataframe
    out = pd.DataFrame({
        "year": [2018],
        "total_cases": [total_cases],
        "head_injury_cases": [head_injury_cases],
        "head_injury_share": [round(head_injury_share, 4)]
    })
    
    out.to_csv(os.path.join(OUT_DIR, "head_injury_year.csv"), index=False)
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    categories = ["All Cases", "Head Injuries"]
    counts = [total_cases, head_injury_cases]
    
    bars = plt.bar(categories, counts, color=["#4C78A8", "#E45756"])
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1000,
                f"{height:,}",
                ha='center', va='bottom')
    
    plt.title("Head Injury Cases (2018)", pad=20)
    plt.ylabel("Number of Cases")
    plt.ylim(0, max(counts) * 1.15)  # Add some padding at the top
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(os.path.join(FIG_DIR, "head_injury_share_by_year.png"), dpi=120)
    plt.close()
    
    return out


def agg_top10_provinces_latest_year(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Top 10 provinces by cases in 2018, with horizontal bar figure."""
    if "prov" not in df.columns:
        return None
    
    # Filter for 2018 data only
    df_2018 = df[df["year"] == 2018].copy()
    if len(df_2018) == 0:
        return None
    
    # Get top 10 provinces by case count
    prov_cases = (
        df_2018.groupby("prov", dropna=False)
        .size()
        .reset_index(name="cases")
        .sort_values("cases", ascending=False)
        .head(10)
    )
    
    # Add year column for consistency
    prov_cases["year"] = 2018
    prov_cases = prov_cases[["prov", "year", "cases"]]
    
    # Save to CSV
    prov_cases.to_csv(os.path.join(OUT_DIR, "top10_provinces_latest_year.csv"), index=False)
    
    # Create visualization
    plt.figure(figsize=(12, 7))
    
    # Sort values in descending order for plotting
    prov_cases = prov_cases.sort_values("cases", ascending=True)
    
    # Create horizontal bar plot
    bars = plt.barh(
        prov_cases["prov"],
        prov_cases["cases"],
        color="#4C78A8",
        height=0.7
    )
    
    # Add value labels on the bars
    for bar in bars:
        width = bar.get_width()
        plt.text(
            width + (0.01 * prov_cases["cases"].max()),  # Position text just outside the bar
            bar.get_y() + bar.get_height() / 2,  # Center text vertically
            f"{int(width):,}",  # Format number with thousands separator
            va="center",
            fontsize=10
        )
    
    plt.title("Top 10 Provinces by Road Traffic Injury Cases (2018)", pad=20)
    plt.xlabel("Number of Cases", labelpad=10)
    plt.ylabel("Province", labelpad=10)
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    
    # Adjust layout to prevent cutoff of labels
    plt.tight_layout()
    
    # Save the figure with high DPI for better quality
    plt.savefig(
        os.path.join(FIG_DIR, "top10_provinces_latest_year.png"),
        dpi=120,
        bbox_inches="tight"
    )
    plt.close()
    
    return prov_cases


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

    # Apply 2018 year filter
    df = df.loc[df["year"] == YEAR_FILTER].copy()
    print(f"Filtering to year {YEAR_FILTER} only: {len(df):,} rows")

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
