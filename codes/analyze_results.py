import openmc
import numpy as np

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# 1. Source Parameters
# Activity: 0.5 Ci
# Yield: 1.75e6 n/s/Ci (Approximate for PuBe)
ACTIVITY_CI = 0.5
YIELD_PER_CI = 1.75e6        
SOURCE_RATE = ACTIVITY_CI * YIELD_PER_CI  # Total n/s emission

# 2. Geometry Parameters
# These must match the simulation inputs exactly
DET_AREA = 0.048        # cm^2 (4.8 mm^2)
DET_THICKNESS = 0.15    # cm (1.5 mm)
DET_VOLUME = DET_AREA * DET_THICKNESS # cm^3

# 3. Exposure Time
TIME_HOURS = 24.0
TIME_SECONDS = TIME_HOURS * 3600.0

# ==============================================================================
# DATA PROCESSING
# ==============================================================================
try:
    sp = openmc.StatePoint('statepoint.100.h5')
except Exception:
    print("Error: Statepoint file not found.")
    exit()

tally = sp.get_tally(name="cr39_flux")
df = tally.get_pandas_dataframe()

# SCALING FACTOR
# OpenMC Tally (t) is [particle-cm] per source particle.
# Real Flux (phi) [n/cm^2/s] = (t / Volume) * Source_Rate
phi_scale = SOURCE_RATE / DET_VOLUME

print(f"\n{'='*110}")
print(f" NEUTRON EXPOSURE REPORT (PRC STANDARD)")
print(f" {'='*110}")
print(f" Source Rate : {SOURCE_RATE:.2e} n/s")
print(f" Detector    : CR-39 Area={DET_AREA} cm², Thickness={DET_THICKNESS} cm")
print(f" Exposure    : {TIME_HOURS} Hours")
print(f" Shielding   : 42um PP + 20um PE (Modeled in Transport)")
print(f" {'-'*110}")
print(f" {'Energy Group':<18} | {'Range':<18} | {'Flux (n/cm²/s)':<22} | {'Total Neutrons (N)':<22}")
print(f" {'':<18} | {'':<18} | {'(Mean +/- SD)':<22} | {'(Flux * Time * Area)':<22}")
print(f" {'-'*110}")

labels = ["Thermal", "Epithermal", "Intermediate", "Fast"]
ranges = ["< 0.025 eV", "0.025-0.5 eV", "0.5 eV-100 keV", "> 100 keV"]

total_flux_val = 0.0
total_flux_var = 0.0
total_n_val = 0.0
total_n_var = 0.0

for i, row in df.iterrows():
    raw_mean = row['mean']
    raw_std  = row['std. dev.']
    
    # 1. Calculate Real Flux (Phi)
    # Unit: n / cm^2 / s
    phi = raw_mean * phi_scale
    phi_unc = raw_std * phi_scale
    
    # 2. Calculate Total Neutrons (N)
    # Formula: N = Flux * Time * Area
    # Unit: Dimensionless (Count)
    n_count = phi * TIME_SECONDS * DET_AREA
    n_unc = phi_unc * TIME_SECONDS * DET_AREA
    
    # Accumulate Totals (Summing Variances)
    total_flux_val += phi
    total_flux_var += phi_unc**2
    total_n_val += n_count
    total_n_var += n_unc**2
    
    label = labels[i] if i < 4 else "Other"
    rng = ranges[i] if i < 4 else "--"
    
    print(f" {label:<18} | {rng:<18} | {phi:.3e} +/- {phi_unc:.1e} | {n_count:.3e} +/- {n_unc:.1e}")

# Final Totals
total_flux_unc = np.sqrt(total_flux_var)
total_n_unc = np.sqrt(total_n_var)

print(f" {'-'*110}")
print(f" {'INTEGRAL TOTAL':<41} | {total_flux_val:.3e} +/- {total_flux_unc:.1e} | {total_n_val:.3e} +/- {total_n_unc:.1e}")
print(f" {'='*110}\n")

print("NOTE FOR MANUSCRIPT:")
print("1. 'Flux' is the volume-averaged scalar flux inside the CR-39 layer.")
print("2. 'Total Neutrons (N)' represents the total number of neutrons entering the detector area over 24h.")
print("   Calculation: N = Flux * Exposure_Time * Detector_Area.")