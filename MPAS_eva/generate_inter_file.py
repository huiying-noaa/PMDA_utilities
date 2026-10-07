import xarray as xr
import numpy as np

# -----------------------------
# User input
# -----------------------------
fileA = "/gpfs/f6/bil-fire2-oar/scratch/Huiying.Luo/workflow_260903/Test5/hrly_12km/stmp/20240512/rrfs_jedivar_01_v2.1.4/det/jedivar_01/rho22.nc"
fileB = "/gpfs/f6/bil-fire2-oar/scratch/Huiying.Luo/workflow_260903/Test5/hrly_12km/stmp/20240512/rrfs_jedivar_01_v2.1.4/det/jedivar_01/mpasout_cp.nc"
outfile = "rho22_ratio.nc"

# -----------------------------
# Load datasets
# -----------------------------
dsA = xr.open_dataset(fileA)
dsB = xr.open_dataset(fileB)

# -----------------------------
# Extract rho
# -----------------------------
rhoA = dsA["rho"]
rhoB = dsB["rho"]

# -----------------------------
# Compute ratio safely
# -----------------------------
rho_ratio = xr.where(rhoB != 0.0, rhoA / rhoB, np.nan)
rho_ratio = rho_ratio.rename("rho_ratio")

# -----------------------------
# Build output dataset
# -----------------------------
ds_out = xr.Dataset(
    {
        "rho_ratio": rho_ratio
    },
    coords={
        "nCells": dsA["nCells"],
        "nVertLevels": dsA["nVertLevels"]
    }
)

# -----------------------------
# Copy MPAS metadata if present
# -----------------------------
for attr in dsA.attrs:
    ds_out.attrs[attr] = dsA.attrs[attr]

# -----------------------------
# Save
# -----------------------------
ds_out.to_netcdf(outfile)
print(f"Created {outfile}")
