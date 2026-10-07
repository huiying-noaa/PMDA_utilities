#!/usr/bin/env python3
"""
MPAS Multi-Variable Absolute Mass Interior Summation Utility
Loops through a wildcard-matched series of history files and logs 
absolute interior mass (μg) over time into individual files per species.
"""

import os
import sys
import glob
import yaml
import numpy as np
from netCDF4 import Dataset

def calculate_absolute_interior_mass_timeseries(grid_file_path, data_file_list, variable_list, output_dir="mass_results"):
    """
    Computes absolute tracer mass (μg) for a series of MPAS data files.
    Saves a clean time-series report file for each individual species.
    """
    # 1. Verify structural files and paths
    if not os.path.exists(grid_file_path):
        print(f"Error: Grid file not found at {grid_file_path}")
        return

    history_files = data_file_list

    os.makedirs(output_dir, exist_ok=True)
    print(f"Results will be printed to directory: '{output_dir}/'")

    # 2. Extract static mesh properties from the Grid file
    print("\n--- Reading Static MPAS Mesh Properties & Masking ---")
    with Dataset(grid_file_path, 'r') as nc_grid:
        core_grid_vars = ['bdyMaskCell', 'areaCell']
        for var in core_grid_vars:
            if var not in nc_grid.variables:
                print(f"Error: Core variable '{var}' missing from Grid file.")
                return

        bdy_mask = nc_grid.variables['bdyMaskCell'][:]
        area_cell = nc_grid.variables['areaCell'][:]
        n_cells = len(bdy_mask)
        
        # FIX: Extract the 1D array from the tuple to maintain horizontal size
        interior_indices = np.where(bdy_mask == 0)[0]
        num_interior = len(interior_indices)
        area_interior = area_cell[interior_indices]
        
        print(f"Total Mesh Cells: {n_cells} | Pure Interior Cells (bdyMaskCell == 0): {num_interior}")

        # Check if zgrid is static and lives in the grid file
        has_static_zgrid = 'zgrid' in nc_grid.variables
        if has_static_zgrid:
            zgrid_static = nc_grid.variables['zgrid'][:]

    # 3. Initialize memory log dictionary for tracking species timeseries data
    results_tracker = {var: [] for var in variable_list}

    # 4. Loop over every discovered history file
    print("\n--- Commencing Multi-File Processing Loop ---")
    for file_idx, file_path in enumerate(history_files):
        file_name = os.path.basename(file_path)
        print(f"[{file_idx + 1}/{len(history_files)}] Processing: {file_path}")

        try:
            with Dataset(file_path, 'r') as nc_data:
                # Validate common dynamic variables
                if 'rho' not in nc_data.variables:
                    print(f"  -> Skipping {file_name}: 'rho' field missing.")
                    continue

                rho_field = nc_data.variables['rho']
                n_times = rho_field.shape[0]

                # Resolve zgrid vertical layer interfaces (dynamic vs static)
                if not has_static_zgrid:
                    if 'zgrid' not in nc_data.variables:
                        print(f"  -> Skipping {file_name}: 'zgrid' vertical tracking completely missing.")
                        continue
                    zgrid_source = nc_data.variables['zgrid']
                
                # Check each requested tracer inside this file
                for var_name in variable_list:
                    if var_name not in nc_data.variables:
                        print(f"  -> Warning: '{var_name}' not found in {file_name}. Logged as NaN.")
                        for t in range(n_times):
                            results_tracker[var_name].append((file_path, t, np.nan))
                        continue

                    var_field = nc_data.variables[var_name]

                    # Loop through time states inside the specific netCDF file
                    for t in range(n_times):
                        # Extract vertical coordinate thickness
                        if has_static_zgrid:
                            zgrid_slice = zgrid_static[t, :, :] if len(zgrid_static.shape) == 3 else zgrid_static
                        else:
                            zgrid_slice = zgrid_source[t, :, :] if len(zgrid_source.shape) == 3 else zgrid_source

                        # Calculate layer metric depth via difference array
                        delta_z = np.diff(zgrid_slice, axis=1)

                        # Filter variables down to the interior geometry using 1D index array
                        delta_z_interior = delta_z[interior_indices, :]
                        rho_interior = rho_field[t, interior_indices, :]
                        mixing_ratio_interior = var_field[t, interior_indices, :]

                        # Core physical integration math
                        cell_volume = area_interior[:, np.newaxis] * delta_z_interior
                        dry_air_mass = rho_interior * cell_volume
                        aerosol_mass_cell = mixing_ratio_interior * dry_air_mass
                        
                        total_absolute_mass_μg = np.sum(aerosol_mass_cell)

                        # Log calculations into memory dictionary
                        results_tracker[var_name].append((file_path, t, total_absolute_mass_μg))

        except Exception as e:
            print(f"  -> Critical failure reading {file_name}: {e}")
            continue

    # 5. Print results into a single file for each species
    print("\n--- Writing Aggregated Reports ---")
    for var_name in variable_list:
        output_file_path = os.path.join(output_dir, f"total_mass_{var_name}.csv")
        
        with open(output_file_path, 'w') as f:
            f.write("source_file,timestep_index,total_interior_mass_μg\n")
            for record in results_tracker[var_name]:
                f.write(f"{record[0]},{record[1]},{record[2]:.8e}\n")
                
        print(f"  Successfully wrote report: {output_file_path}")


if __name__ == "__main__":
    # Aerosol variables to sum
    aerosols_list = ['dust_fine', 'dust_coarse', 'smoke_fine']
    
    # Grid
    mesh_grid_file = "/gpfs/f6/bil-fire2-oar/scratch/Huiying.Luo/workflow_260608/rrfs-workflow/fix/conus12km/conus12km.grid.nc"
    
    # File List Option 1: from pattern
    #data_file_pattern = "/gpfs/f6/bil-fire2-oar/scratch/Huiying.Luo/workflow_260928wf/Test2/hrly_12km/stmp/2024051*/rrfs_fcst_00_v2.1.4/det/history.2024-05-*.nc"
    #history_files = sorted(glob.glob(data_file_pattern))
    #if not history_files:
    #    print(f"Error: No history files found matching pattern: {data_file_pattern}")             
    #print(f"Found {len(history_files)} history data files to process from pattern.")

    # File List Option 2: file list from yaml
    yaml_config_path = "config_plot_historyTest6_1.yaml" 
    with open(yaml_config_path, 'r') as f:
        config = yaml.safe_load(f)
    history_files = config['dataset']['files']
    print(f"Found {len(history_files)} history data files to process from yaml.")

    # Execute computation
    calculate_absolute_interior_mass_timeseries(
        grid_file_path=mesh_grid_file, 
        data_file_list=history_files, 
        variable_list=aerosols_list,
        output_dir="mass_results_0928Test6_1hr"
    )

