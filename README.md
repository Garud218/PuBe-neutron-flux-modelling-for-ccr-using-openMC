# PuBe Neutron Flux Modelling for Compact Cylindrical Reactor (CCR) Using OpenMC

This repository contains a complete, reproducible OpenMC simulation workflow to model neutron flux from a **Plutonium-Beryllium (PuBe)** neutron source placed inside a simplified **Compact Cylindrical Reactor (CCR)** geometry.

## Objective

The primary goals of this project are:

- Realistic modeling of neutron emission from a PuBe source using a standard energy spectrum  
- Simulation of neutron transport, scattering, absorption and moderation inside a compact cylindrical geometry  
- Calculation and visualization of neutron flux (both spatial distribution and energy spectrum)  
- Providing an educational / research-oriented example of neutron Monte Carlo modeling with OpenMC  

Applications include neutron source characterization, preliminary shielding studies, detector response estimation, and nuclear engineering education.

## Setup Description

### Geometry Overview
- **Core vessel**: Simplified cylindrical shape (example: radius 10–15 cm, height 20–30 cm)  
- **Wall material**: Stainless steel, aluminum, or equivalent (thin wall approximation possible)  
- **Moderator / reflector**: Water, polyethylene, heavy water, graphite, or combination (configurable)  
- **Source position**: PuBe source placed at the geometric center (coaxial)  
- **Boundary conditions**: Reflective on outer surfaces or void (vacuum) — configurable in `pube_geom.py`  
- **Coordinate system**: Cylindrical (r, φ, z) symmetry often exploited
  
![Experimental setup](https://github.com/Garud218/PuBe-neutron-flux-modelling-for-ccr-using-openMC/blob/main/setup/exp_setup.png)

### Neutron Source – PuBe
- Reaction types: (α,n) on ⁹Be + spontaneous fission of ²³⁹Pu  
- Average neutron energy: ≈ 4.5 MeV  
- Spectrum: Broad continuous distribution (peak ~1–5 MeV, tail extending to ~11 MeV)  
- Emission: Approximately isotropic  
- Spatial distribution: modeled as point source or small cylindrical volume (configurable)

### Detectors / Tallies
- Energy-dependent flux tallies (typically 50–200 bins from thermal to fast)  
- Spatial mesh tallies (2D radial-axial or 3D Cartesian)  
- Cell flux tallies at selected locations (e.g. 5 cm, 10 cm, 15 cm from center)  
- Optional: reaction rate tallies (absorption, capture, fission, etc.)

## Repository Contents

| File / Folder              | Purpose                                                                 |
|----------------------------|-------------------------------------------------------------------------|
| `pube_geom.py`             | Defines geometry, materials, PuBe source, tallies, simulation settings |
| `analyze_results.py`       | Reads `statepoint.h5`, extracts tallies, creates plots & tables        |
| `results/`                 | Output folder: plots (.png), CSV data, text summaries                  |
| `images/`                  | Setup diagrams, example flux plots, spectrum comparisons               |

## Important Assumptions & Simplifications

- Neutron-only transport (no coupled photon transport)  
- Continuous-energy treatment (ENDF/B-VIII.0)  
- Room temperature (≈ 294–300 K) — no temperature feedback / Doppler broadening  
- PuBe spectrum taken from standard IAEA / literature tabulation  
- Isotropic point-like or small-volume source  
- No time dependence, no burnup, no delayed neutrons  
- Sufficient histories used for statistical uncertainty < 5–10% in most tallies

## Nuclear Data References

- **PuBe neutron spectrum**: IAEA Nuclear Data Services – IAEA-NDS-0213 “Neutron Source Spectra”  
  → https://www-nds.iaea.org/  
- **Cross-section library**: ENDF/B-VIII.0 (default in modern OpenMC installations)  
- **General isotopic data**: NNDC (National Nuclear Data Center), Brookhaven  
- Classic PuBe spectrum reference: Anderson et al. (1970), Nucl. Instrum. Methods 70, 287

Thanks to the **IAEA** for making PuBe neutron spectrum data publicly available.

## Installation & Running

### Requirements

- Python 3.8+  
- OpenMC ≥ 0.13 (with Python API)  
- Python packages: numpy, matplotlib, h5py, pandas  
- Recommended: Spack package manager

Official links:  
→ https://docs.openmc.org/  
→ https://openmc.org/

### Spack-based Installation (Linux / macOS / WSL recommended)

```bash
# Install (only needed once)
spack install openmc
spack install py-openmc

# Load environment every new terminal session
spack load openmc
spack load py-openmc
```

### 1. Generate OpenMC XML input files
```bash
python3 pube_geom.py
```

### 2. Run Monte Carlo transport
```bash
openmc
```

### 3. Post-process results & create plots
```bash
python3 analyze_results.py
```

Example Output Visuals

![Results](https://github.com/Garud218/PuBe-neutron-flux-modelling-for-ccr-using-openMC/blob/main/results/results.png)

OpenMC development team — excellent open-source Monte Carlo code (MIT license)
→ https://openmc.org/
IAEA Nuclear Data Section — neutron source spectrum data
OpenMC community (Discourse forum, GitHub) for support and examples

## Citation
If you use or build upon this work, please cite:

```
@misc{kumar2026experimentaldeterminationslowneutrondetection,
      title={Experimental Determination of Slow-Neutron Detection Efficiency and Background Discrimination in Mixed Radiation Fields Using Differential CR-39 Track Detectors}, 
      author={Ankit Kumar and Tushar Verma and Pankaj Jain and Raj Ganesh Pala and K. P. Rajeev},
      year={2026},
      eprint={2601.14441},
      archivePrefix={arXiv},
      primaryClass={nucl-ex},
      url={https://arxiv.org/abs/2601.14441}, 
}
```
Direct DOI link: https://doi.org/10.48550/arXiv.2601.14441

License
MIT License — feel free to use, modify, share.
Pull requests, issues, and suggestions are very welcome!
