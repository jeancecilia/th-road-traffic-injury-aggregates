import os
import shutil

def rename_files():
    # Define the base directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(base_dir, 'outputs')
    figures_dir = os.path.join(outputs_dir, 'figures')
    
    # Mapping of old filenames to new filenames
    file_mapping = {
        # CSV files
        'age_bins_year.csv': 'age_bins_2018.csv',
        'bkk_quarter.csv': 'bkk_quarter_2018.csv',
        'bkk_top_amphoe.csv': 'bkk_top_amphoe_2018.csv',
        'head_injury_year.csv': 'head_injury_2018.csv',
        'hour_of_day.csv': 'hour_of_day_2018.csv',
        'mode_mix_bkk_year.csv': 'mode_mix_bkk_2018.csv',
        'national_quarter.csv': 'national_quarter_2018.csv',
        'province_year.csv': 'province_2018.csv',
        'qa_coverage_province_year.csv': 'qa_coverage_province_2018.csv',
        'qa_year_counts.csv': 'qa_year_counts_2018.csv',
        'sex_year.csv': 'sex_2018.csv',
        'top10_provinces_latest_year.csv': 'top10_provinces_2018.csv',
        
        # Figure files
        'figures/age_bins_by_year.png': 'figures/age_bins_2018.png',
        'figures/bkk_quarter_cases.png': 'figures/bkk_quarter_2018.png',
        'figures/bkk_top_amphoe.png': 'figures/bkk_top_amphoe_2018.png',
        'figures/head_injury_share_by_year.png': 'figures/head_injury_2018.png',
        'figures/hour_of_day.png': 'figures/hour_of_day_2018.png',
        'figures/mode_mix_bkk_share_by_year.png': 'figures/mode_mix_bkk_2018.png',
        'figures/national_quarter_cases.png': 'figures/national_quarter_2018.png',
        'figures/sex_national_by_year.png': 'figures/sex_distribution_2018.png',
        'figures/top10_provinces_latest_year.png': 'figures/top10_provinces_2018.png'
    }
    
    # Rename files
    for old_name, new_name in file_mapping.items():
        old_path = os.path.join(outputs_dir, old_name) if not old_name.startswith('figures/') else \
                  os.path.join(base_dir, 'outputs', old_name)
        new_path = os.path.join(outputs_dir, new_name) if not new_name.startswith('figures/') else \
                  os.path.join(base_dir, 'outputs', new_name)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        
        try:
            if os.path.exists(old_path):
                shutil.move(old_path, new_path)
                print(f"Renamed: {old_name} -> {new_name}")
            else:
                print(f"Warning: File not found - {old_path}")
        except Exception as e:
            print(f"Error renaming {old_name}: {str(e)}")

if __name__ == "__main__":
    print("Renaming files to include 2018 in filenames...")
    rename_files()
    print("File renaming completed.")
