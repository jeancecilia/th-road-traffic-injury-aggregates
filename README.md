# Data Monster: Thailand Injury Data Analysis

This repository contains scripts and data for analyzing injury data in Thailand, with a focus on road traffic incidents.

## Repository Structure

```
datasets/injury-th/
  injury_bkk_quarter.csv          # Quarterly injury cases in Bangkok
  injury_province_year.csv        # Yearly injury cases by province
  injury_mode_mix_bkk_year.csv    # Vehicle type distribution in Bangkok by year
  injury_age_sex_bkk_year.csv     # Age and sex distribution in Bangkok by year
  injury_risk_factors_bkk_quarter.csv  # Risk factors analysis in Bangkok by quarter
  bangkok_quarterly_cases.png     # Visualization of quarterly cases
  mode_mix_share_by_year.png      # Visualization of vehicle type distribution
  top10_provinces_latest_year.csv # Top 10 provinces by injury rate
  qa_summary.json                 # Data quality assessment
  commons_captions.csv            # Standardized captions for visualizations
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jeancecilia/data_monster.git
   cd data_monster
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the data processing script:
```bash
python injury_aggregate.py --input is2018.csv --config config_injury.json
```

## Data Sources

- Raw data: `is2018.csv` (not included in repository due to size)
- Configuration: `config_injury.json`

## License

[Specify your license here]
