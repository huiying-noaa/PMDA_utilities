#!/usr/bin/env python3
"""
MPAS Mass Visualization Tool
Reads the generated total mass CSV files from multiple experiment folders/patterns,
extracts timestamps from filenames, and creates multi-line plots comparing 
experiments for each species.
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

def plot_mpas_mass_results(data_patterns=None, output_img_dir="mass_plots"):
    """
    Finds all total_mass_*.csv files across different experiment folders/patterns,
    groups them by chemical species, and plots experiments on a shared axis.
    
    Accepts data_patterns as a list of folder paths or glob patterns.
    """
    if data_patterns is None:
        # Default fallback pattern if nothing is provided
        data_patterns = [os.path.join(".", "*", "total_mass_*.csv")]
    elif isinstance(data_patterns, str):
        data_patterns = [data_patterns]

    # 1. FIND ALL CSV FILES ACROSS ALL PATTERNS
    csv_files = []
    for pattern in data_patterns:
        # Handle cases where user passed just a directory by appending the file search
        if os.path.isdir(pattern):
            search_pattern = os.path.join(pattern, "**", "total_mass_*.csv")
            found = glob.glob(search_pattern, recursive=True)
        else:
            found = glob.glob(pattern)
        csv_files.extend(found)

    # Remove duplicates if patterns overlapped
    csv_files = list(set(csv_files))

    if not csv_files:
        print(f"Error: No CSV tables found matching patterns: {data_patterns}. Please check paths.")
        return

    os.makedirs(output_img_dir, exist_ok=True)
    print(f"Found {len(csv_files)} CSV files across all specified patterns.")

    # 2. GROUP FILES BY SPECIES
    species_dict = {}
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        
        # Extract experiment name from parent folder
        exp_name = os.path.basename(os.path.dirname(file_path))
        
        # Clean species name extraction out of filename format
        species_name = file_name.replace("total_mass_", "").replace(".csv", "")
        
        if species_name not in species_dict:
            species_dict[species_name] = []
        species_dict[species_name].append((file_path, exp_name))

    # Helper function to parse timestamps from source files
    def extract_timestamp(filename):
        base = os.path.basename(str(filename))
        return base.replace("history.", "").replace(".nc", "")

    # 3. PLOT EACH SPECIES COMPARING EXPERIMENTS
    for species_name, experiments in species_dict.items():
        print(f"Processing data for species: {species_name}...")
        
        fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
        all_x_labels = []
        has_data = False

        # Sort experiments by name so the legend order remains consistent
        experiments.sort(key=lambda x: x[1])

        for file_path, exp_name in experiments:
            try:
                df = pd.read_csv(file_path)
                if df.empty:
                    print(f"  -> Skipping empty file in {exp_name}: {os.path.basename(file_path)}")
                    continue

                df = df.dropna()
                df['extracted_time'] = df['source_file'].apply(extract_timestamp)
                
                mass_col = 'total_interior_mass_μg'
                x_indices = range(len(df))
                x_labels = df['extracted_time'].tolist()

                if len(x_labels) > len(all_x_labels):
                    all_x_labels = x_labels

                # Plot line for this specific experiment
                ax1.plot(x_indices, df[mass_col], 
                         marker='o', markersize=4, linestyle='-', linewidth=1.5, 
                         label=f'{exp_name}')
                
                has_data = True

            except Exception as e:
                print(f"  -> Failed to read table {file_path}: {e}")

        if not has_data:
            plt.close()
            continue

        # --- Graph Styling ---
        ax1.set_xlabel('Simulation Time (Filename)', fontweight='bold', labelpad=12)
        ax1.set_ylabel('Mass (μg)', fontweight='bold')
        ax1.yaxis.set_major_formatter(plt.FormatStrFormatter('%.3e'))
        ax1.grid(True, linestyle='--', alpha=0.5)

        max_ticks = 10
        if len(all_x_labels) > max_ticks:
            tick_indices = list(range(0, len(all_x_labels), len(all_x_labels) // max_ticks))
        else:
            tick_indices = list(range(len(all_x_labels)))

        ax1.set_xticks(tick_indices)
        ax1.set_xticklabels([all_x_labels[i] for i in tick_indices], rotation=25, ha='right', fontsize=9)

        ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='none')
        plt.title(f"MPAS Interior Domain Mass Comparison: {species_name}", fontsize=14, fontweight='bold', pad=15)
        fig.tight_layout()

        out_img_path = os.path.join(output_img_dir, f"mass_comparison_{species_name}.png")
        plt.savefig(out_img_path, bbox_inches='tight')
        plt.close()
        print(f"  -> Successfully generated comparison plot: {out_img_path}")

if __name__ == '__main__':
    # Define all the paths, wildcard folders, or specific patterns you want to scan:
    my_search_patterns = [
        "mass_results_0928Test*_1hr/*csv"
    ]
    
    plot_mpas_mass_results(data_patterns=my_search_patterns, output_img_dir="mass_plots_1hr")

