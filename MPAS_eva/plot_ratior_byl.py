import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

ratio_file = "rho22_ratio.nc"

# Load dataset
ds = xr.open_dataset(ratio_file)

# Extract rho_ratio and remove any leading Time dimension
rho_ratio = ds["rho_ratio"]
rho_ratio = rho_ratio.squeeze()   # removes size-1 dimensions

# Now rho_ratio should be (nCells, nVertLevels)
min_by_layer = rho_ratio.min(dim="nCells").values.flatten()
max_by_layer = rho_ratio.max(dim="nCells").values.flatten()

levels = np.arange(rho_ratio.sizes["nVertLevels"])

fig, ax = plt.subplots(figsize=(6, 4))

ax.plot(min_by_layer, levels, label="Min", color="blue")
ax.plot(max_by_layer, levels, label="Max", color="red")

ax.set_xlabel("ρ ratio value")
ax.set_ylabel("Vertical level index")
ax.set_title("Min/Max of ρ ratio by layer")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig("rho22_ratio_minmax_by_layer.png", dpi=150)
plt.close()

print("Saved rho22_ratio_minmax_by_layer.png")
