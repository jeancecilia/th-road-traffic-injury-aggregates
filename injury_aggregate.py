import argparse, json, sys, os, math
import pandas as pd
import numpy as np
from datetime import datetime

def read_csv_any(path, encs):
    last = None
    for enc in encs:
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as e:
            last = e
    raise last

def parse_th_date(series, dayfirst=True):
    dt = pd.to_datetime(series, errors="coerce", dayfirst=dayfirst)
    # Buddhist year fix: if year >= 2400, subtract 543
    years = dt.dt.year
    mask = years >= 2400
    if mask.any():
        dt.loc[mask] = dt.loc[mask] - pd.DateOffset(years=543)
    return dt

def derive_period(df, dcol):
    df["year"]   = dcol.dt.year
    df["month"]  = dcol.dt.month
    df["quarter"]= dcol.dt.to_period("Q").astype(str)  # e.g., 2018Q1
    # Make quarter label like YYYY-Qn
    df["quarter"] = df["year"].astype(str) + "-Q" + ((dcol.dt.quarter).astype(str))

def icd_vehicle_map(code):
    if not isinstance(code, str) or len(code) < 3: return "Unspecified"
    code = code.upper().strip()
    if not code.startswith("V"): return "Non-road or unspecified"
    try:
        v = int(code[1:3])
    except:
        return "Unspecified"
    # Ranges
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

def norm_bool(x, yes, no, unk):
    if pd.isna(x): return np.nan
    s = str(x).strip().lower()
    if s in [v.lower() for v in yes]: return 1
    if s in [v.lower() for v in no]:  return 0
    if s in [v.lower() for v in unk]: return np.nan
    # try numeric
    try:
        f = float(s)
        if f == 1: return 1
        if f == 0: return 0
    except:
        pass
    return np.nan

def any_token_hit(val, tokens):
    if pd.isna(val): return False
    s = str(val).lower()
    return any(tok.lower() in s for tok in tokens)

def safe_rate(num, den):
    return (num/den) if den and den>0 else np.nan

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = json.load(open(args.config, "r", encoding="utf-8"))
    encs = cfg["input"]["csv_encoding_candidates"]
    df = read_csv_any(args.input, encs)

    # --- Date handling ---
    dpri = cfg["date"]["primary"]
    df["_date_primary"] = parse_th_date(df[dpri], dayfirst=cfg["input"]["dayfirst"]) if dpri in df.columns else pd.NaT
    dsec = cfg["date"]["fallback"]
    if dsec and dsec in df.columns:
        fallback = parse_th_date(df[dsec], dayfirst=cfg["input"]["dayfirst"])
        df["_date"] = df["_date_primary"].fillna(fallback)
    else:
        df["_date"] = df["_date_primary"]

    # Drop rows without any date
    df = df[~df["_date"].isna()].copy()
    derive_period(df, df["_date"])

    # --- Geography ---
    prov_col = cfg["geo"]["province"]
    if prov_col not in df.columns:
        raise SystemExit(f"Province column '{prov_col}' not found in CSV.")
    bangkok_name = cfg["geo"].get("bangkok_name","กรุงเทพมหานคร")

    # --- Demographics ---
    if cfg["demographics"]["age"] in df.columns:
        bins = cfg["demographics"]["age_bins"]
        labels = cfg["demographics"]["age_labels"]
        df["age_group"] = pd.cut(df[cfg["demographics"]["age"]].astype(float), bins=bins, labels=labels, right=True, include_lowest=True)
    else:
        df["age_group"] = pd.NA

    # --- ICD vehicle mapping ---
    icd_col = cfg["icd10"]["column"]
    df["vehicle_type"] = df[icd_col].map(icd_vehicle_map) if icd_col in df.columns else "Unspecified"

    # --- Risk factors (optional) ---
    risks = cfg["risks"]
    yes, no, unk = risks["values_yes"], risks["values_no"], risks["values_unknown"]

    risk_cols = {}
    for key in ["alcohol","helmet","seatbelt"]:
        col = risks.get(key)
        if col and col in df.columns:
            outcol = f"{key}_flag"
            df[outcol] = df[col].apply(lambda x: norm_bool(x, yes, no, unk))
            risk_cols[key] = outcol

    # --- Death detection (conservative) ---
    death_tokens = cfg["outcomes"]["death_tokens"]
    death_fields = [c for c in cfg["outcomes"]["death_fields"] if c in df.columns]
    if death_fields:
        death_flags = []
        for c in death_fields:
            death_flags.append(df[c].apply(lambda v: 1 if any_token_hit(v, death_tokens) else 0))
        df["death_flag"] = np.maximum.reduce(death_flags)
    else:
        df["death_flag"] = 0

    # --- Population join (optional) ---
    per100k_ready = False
    pop_cfg = cfg.get("population", {})
    if pop_cfg.get("enabled", False) and os.path.exists(pop_cfg["file"]):
        pop = pd.read_csv(pop_cfg["file"])
        df["_year"] = df["year"]
        # province-year join for later aggregations
        per100k_ready = True
    else:
        pop = None

    # Helpers
    def agg_rates(g):
        out = {}
        out["cases"] = len(g)
        out["deaths"] = int(g["death_flag"].sum())
        # alcohol
        if "alcohol_flag" in g:
            den = g["alcohol_flag"].notna().sum()
            num = g["alcohol_flag"].sum(skipna=True)
            out["alcohol_share"] = float(num)/float(den) if den>0 else np.nan
        # helmet (motorcycle only)
        if "helmet_flag" in g:
            m = g[g["vehicle_type"]=="Motorcycle"]
            den = m["helmet_flag"].notna().sum()
            num = m["helmet_flag"].sum(skipna=True)
            out["helmet_rate"] = float(num)/float(den) if den>0 else np.nan
        # seatbelt (cars/vans/pickups/bus/truck)
        if "seatbelt_flag" in g:
            carlike = g[g["vehicle_type"].isin(["Car","Pickup/Van","Bus","Truck/Heavy"])]
            den = carlike["seatbelt_flag"].notna().sum()
            num = carlike["seatbelt_flag"].sum(skipna=True)
            out["seatbelt_rate"] = float(num)/float(den) if den>0 else np.nan
        return pd.Series(out)

    # --- 1) Bangkok quarterly ---
    bkk = df[df[prov_col].astype(str) == bangkok_name].copy()
    gcols = ["year","quarter"]
    bkk_q = bkk.groupby(gcols, dropna=False).apply(agg_rates).reset_index()

    if per100k_ready:
        # Need province-year pop for Bangkok
        p_bkk = pop[pop[pop_cfg["prov_col"]]==bangkok_name]
        bkk_q = bkk_q.merge(p_bkk[[pop_cfg["year_col"], pop_cfg["pop_col"]]].drop_duplicates(),
                            left_on="year", right_on=pop_cfg["year_col"], how="left")
        bkk_q["per100k"] = (bkk_q["cases"]*100000 / bkk_q[pop_cfg["pop_col"]]).round(2)
        bkk_q.drop(columns=[pop_cfg["year_col"], pop_cfg["pop_col"]], inplace=True)

    bkk_q.to_csv(cfg["outputs"]["injury_bkk_quarter"], index=False)

    # --- 2) Province-year ---
    prov_year = df.groupby([prov_col,"year"], dropna=False).apply(agg_rates).reset_index().rename(columns={prov_col:"prov"})
    if per100k_ready:
        prov_year = prov_year.merge(pop, left_on=["prov","year"], right_on=[pop_cfg["prov_col"], pop_cfg["year_col"]], how="left")
        prov_year["per100k"] = (prov_year["cases"]*100000 / prov_year[pop_cfg["pop_col"]]).round(2)
        prov_year.drop(columns=[pop_cfg["prov_col"], pop_cfg["year_col"], pop_cfg["pop_col"]], inplace=True)
    prov_year.to_csv(cfg["outputs"]["injury_province_year"], index=False)

    # --- 3) Mode mix (Bangkok) by year ---
    mode_bkk = bkk.groupby(["year","vehicle_type"], dropna=False).size().reset_index(name="cases")
    total_per_year = mode_bkk.groupby("year")["cases"].transform("sum")
    mode_bkk["share_of_total"] = mode_bkk["cases"] / total_per_year
    mode_bkk.to_csv(cfg["outputs"]["injury_mode_mix_bkk_year"], index=False)

    # --- 4) Age x sex (Bangkok) by year ---
    age_sex_cols = ["year","age_group","sex"]
    for c in ["age_group","sex"]:
        if c not in bkk.columns:
            # still produce schema with NaNs if missing
            bkk[c] = pd.NA
    age_sex = bkk.groupby(age_sex_cols, dropna=False).size().reset_index(name="cases")
    # per100k for age-sex only if user provides that table; otherwise leave as NaN
    age_sex["per100k"] = np.nan
    age_sex.to_csv(cfg["outputs"]["injury_age_sex_bkk_year"], index=False)

    # --- 5) Risk factors (Bangkok) quarterly ---
    cols = ["year","quarter"]
    have_any_risk = any(c in bkk.columns for c in ["alcohol_flag","helmet_flag","seatbelt_flag"])
    if have_any_risk:
        # We'll compute shares within quarter across applicable records
        def risk_quarter(g):
            out = {"cases": len(g)}
            if "alcohol_flag" in g:
                den = g["alcohol_flag"].notna().sum()
                num = g["alcohol_flag"].sum(skipna=True)
                out["alcohol_share"] = float(num)/float(den) if den>0 else np.nan
            if "helmet_flag" in g:
                m = g[g["vehicle_type"]=="Motorcycle"]
                den = m["helmet_flag"].notna().sum()
                num = m["helmet_flag"].sum(skipna=True)
                out["helmet_rate"] = float(num)/float(den) if den>0 else np.nan
            if "seatbelt_flag" in g:
                carlike = g[g["vehicle_type"].isin(["Car","Pickup/Van","Bus","Truck/Heavy"])]
                den = carlike["seatbelt_flag"].notna().sum()
                num = carlike["seatbelt_flag"].sum(skipna=True)
                out["seatbelt_rate"] = float(num)/float(den) if den>0 else np.nan
            return pd.Series(out)
        risk_q = bkk.groupby(cols, dropna=False).apply(risk_quarter).reset_index()
    else:
        risk_q = bkk.groupby(cols, dropna=False).size().reset_index(name="cases")
    risk_q.to_csv(cfg["outputs"]["injury_risk_factors_bkk_quarter"], index=False)

    print("Done. Files written:\n - " + "\n - ".join(cfg["outputs"].values()))

if __name__ == "__main__":
    main()
