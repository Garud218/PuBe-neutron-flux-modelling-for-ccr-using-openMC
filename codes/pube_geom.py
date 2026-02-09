import openmc
import numpy as np

# ==============================================================================
# 1. GEOMETRY & PHYSICS PARAMETERS
# ==============================================================================
# Source: PuBe Cylinder
SOURCE_RADIUS = 0.5      # cm
SOURCE_HEIGHT = 2.4      # cm
GAP_DISTANCE  = 5.0      # cm (Source Surface -> First Layer)

# Detector Stack (Front to Back)
# Layer 1: Polypropylene (42 microns)
THICK_PP = 42.0e-4       # 0.0042 cm
# Layer 2: Polyethylene (20 microns)
THICK_PE = 20.0e-4       # 0.0020 cm
# Layer 3: CR-39 Detector (1.5 mm)
THICK_CR = 0.15          # 0.1500 cm

# Detector Face Area (4.8 mm^2)
DET_AREA = 0.048         # cm^2
DET_SIDE = np.sqrt(DET_AREA)

# Z-Positions (Relative to Source Center)
# Source Center = 0.0
# Source Surface = 0.5
# Front of Stack = 0.5 + 5.0 = 5.5
X_PP_IN  = SOURCE_RADIUS + GAP_DISTANCE    # 5.5000 cm
X_PP_OUT = X_PP_IN + THICK_PP              # 5.5042 cm
X_PE_OUT = X_PP_OUT + THICK_PE             # 5.5062 cm
X_CR_OUT = X_PE_OUT + THICK_CR             # 5.6562 cm

# ==============================================================================
# 2. MATERIALS
# ==============================================================================
materials = openmc.Materials()

# PuBe Source (1.85 g/cc mix)
pube = openmc.Material(name="PuBe_Source")
pube.set_density("g/cm3", 1.85)
pube.add_nuclide("Be9", 1.0)
pube.add_nuclide("Pu239", 1.0e-3) 
materials.append(pube)

# Polypropylene (C3H6) - 0.90 g/cc
pp = openmc.Material(name="PP_Shield")
pp.set_density("g/cm3", 0.90)
pp.add_element("C", 3)
pp.add_element("H", 6)
materials.append(pp)

# Polyethylene (C2H4) - 0.94 g/cc
pe = openmc.Material(name="PE_Shield")
pe.set_density("g/cm3", 0.94)
pe.add_element("C", 2)
pe.add_element("H", 4)
materials.append(pe)

# CR-39 (C12 H18 O7) - 1.32 g/cc
cr39 = openmc.Material(name="CR39_Detector")
cr39.set_density("g/cm3", 1.32)
cr39.add_element("C", 12)
cr39.add_element("H", 18)
cr39.add_element("O", 7)
materials.append(cr39)

# Air
air = openmc.Material(name="Air")
air.set_density("g/cm3", 0.0012)
air.add_element("N", 0.78)
air.add_element("O", 0.21)
materials.append(air)

materials.export_to_xml()

# ==============================================================================
# 3. GEOMETRY
# ==============================================================================
# Surfaces
cyl_src = openmc.ZCylinder(r=SOURCE_RADIUS)
z_src_top = openmc.ZPlane(z0=SOURCE_HEIGHT/2)
z_src_bot = openmc.ZPlane(z0=-SOURCE_HEIGHT/2)

# Detector Stack Planes (X-Axis)
px_1 = openmc.XPlane(x0=X_PP_IN)
px_2 = openmc.XPlane(x0=X_PP_OUT)
px_3 = openmc.XPlane(x0=X_PE_OUT)
px_4 = openmc.XPlane(x0=X_CR_OUT)

# Detector Sides (Y/Z Axis)
py_min = openmc.YPlane(y0=-DET_SIDE/2)
py_max = openmc.YPlane(y0=DET_SIDE/2)
pz_min = openmc.ZPlane(z0=-DET_SIDE/2)
pz_max = openmc.ZPlane(z0=DET_SIDE/2)

# Boundary
boundary = openmc.Sphere(r=50.0, boundary_type='vacuum')

# Regions
reg_src  = -cyl_src & +z_src_bot & -z_src_top
reg_box  = +py_min & -py_max & +pz_min & -pz_max # Transverse shape
reg_pp   = +px_1 & -px_2 & reg_box
reg_pe   = +px_2 & -px_3 & reg_box
reg_cr   = +px_3 & -px_4 & reg_box # TALLY VOLUME
reg_air  = -boundary & ~reg_src & ~reg_pp & ~reg_pe & ~reg_cr

# Cells
cell_src = openmc.Cell(fill=pube, region=reg_src)
cell_pp  = openmc.Cell(fill=pp, region=reg_pp)
cell_pe  = openmc.Cell(fill=pe, region=reg_pe)
cell_cr  = openmc.Cell(fill=cr39, region=reg_cr)
cell_air = openmc.Cell(fill=air, region=reg_air)

geometry = openmc.Geometry([cell_src, cell_pp, cell_pe, cell_cr, cell_air])
geometry.export_to_xml()

# ==============================================================================
# 4. SOURCE (PuBe Spectrum)
# ==============================================================================
source = openmc.IndependentSource()
source.space = openmc.stats.CylindricalIndependent(
    r=openmc.stats.Uniform(0.0, SOURCE_RADIUS),
    phi=openmc.stats.Uniform(0.0, 2*np.pi),
    z=openmc.stats.Uniform(-SOURCE_HEIGHT/2, SOURCE_HEIGHT/2),
    origin=(0.0, 0.0, 0.0)
)
source.angle = openmc.stats.Isotropic()

# PuBe Spectrum (ISO 8529-1 - Experimental Data)
pube_e = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 
                   3.0, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.25, 5.5, 5.75, 
                   6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0]) * 1.0e6 
pube_p = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 
                   0.11, 0.12, 0.13, 0.13, 0.13, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08, 
                   0.07, 0.06, 0.05, 0.05, 0.04, 0.04, 0.04, 0.03, 0.02, 0.01, 0.005, 
                   0.001, 0.0])
pube_p = pube_p / np.sum(pube_p)
source.energy = openmc.stats.Tabular(pube_e, pube_p, interpolation='linear-linear')

settings = openmc.Settings()
settings.source = source
settings.particles = 1000000 # 1 Million for good statistics
settings.batches = 100
settings.run_mode = 'fixed source'
settings.export_to_xml()

# ==============================================================================
# 5. TALLIES
# ==============================================================================
tallies = openmc.Tallies()

# Bins: Thermal, Epithermal, Intermediate, Fast
e_bins = [0.0, 0.0253, 0.5, 1.0e5, 12.0e6]
e_filt = openmc.EnergyFilter(e_bins)
c_filt = openmc.CellFilter(cell_cr) # Tally in CR-39

t_flux = openmc.Tally(name="cr39_flux")
t_flux.filters = [c_filt, e_filt]
t_flux.scores = ['flux']
tallies.append(t_flux)

tallies.export_to_xml()