#!/usr/bin/env python3
import streamlit as st

# ---------- Constants ----------
RBC_STOCK_CONC_M_per_mL = 50.0
RBC_ANCHORED_PER_UNIT_M = 4.0
ANCHOR_EFFICIENCY = 0.50
ANCHOR_RBC_YIELD = 0.60
BB_RATIO = 2.0

DPB_PER_M_STANDARD = 4.0
PROT_RATIO_BC1_STANDARD = 4.0
PROT_RATIO_BC2_STANDARD = 4.0

DPB_PER_M_CUSTOM = 16.0
PROT_RATIO_BC1_CUSTOM = 2.0
PROT_RATIO_BC2_CUSTOM = 4.0

# Stock concentrations (µM)
STOCKS = {
    "SA-BC": 1.0,
    "Mono Streptavidin": 2.0,
    "anti-CD3": 3.3,
    "anti-CD28": 3.3,
    "anti-CD137": 0.66,
    "CD19 Antigen": 5.9,
    "ctrl IgG1": 3.3,
    "OX40L": 3.9,
    "anti-CD8": 3.3,
    "anti-CD4": 3.3,
    "IL21": 1.0,
    "IL-2": 1.0,
    "anti-CD81": 3.3,
    "anti-CD9": 3.3,
    "anti-CD53": 3.3,
    "anti CD80": 0.0,
    "anti CD86": 0.0,
    "CD27 Ligand": 0.0,
    "ICOS Ligand": 0.0,
}

PROTEIN_GROUPS = {
    "Streptavidin": ["Mono Streptavidin", "SA-BC"],
    "T-cell Antibodies": ["anti-CD3", "anti-CD28", "anti-CD137", "anti-CD8", "anti-CD4"],
    "B-cell / Other Antibodies": ["CD19 Antigen", "ctrl IgG1", "anti-CD81", "anti-CD9", "anti-CD53"],
    "Cytokines / Ligands": ["IL21", "IL-2", "OX40L", "anti CD80", "anti CD86", "CD27 Ligand", "ICOS Ligand"]
}

# ---------- Calculation helpers ----------
def per_unit_values(dpb_per_m, prot_ratio_bc1, prot_ratio_bc2):
    anchoring_dope = dpb_per_m * RBC_ANCHORED_PER_UNIT_M
    post_anchor = anchoring_dope * ANCHOR_EFFICIENCY
    post_anchor_wash = post_anchor * ANCHOR_RBC_YIELD
    barcode_per_unit = post_anchor_wash / BB_RATIO
    proteins_bc1 = barcode_per_unit * prot_ratio_bc1
    proteins_bc2 = barcode_per_unit * prot_ratio_bc2
    return {
        "DOPE_pmol": anchoring_dope,
        "Barcode1_pmol": barcode_per_unit,
        "Proteins_BC1_pmol": proteins_bc1,
        "Barcode2_pmol": barcode_per_unit,
        "Proteins_BC2_pmol": proteins_bc2
    }

def required_row(per_unit, pci3_needed):
    return {k: v * pci3_needed for k, v in per_unit.items()}

def vol_from_pmol(pmol, stock_uM):
    return pmol / stock_uM if stock_uM and stock_uM > 0 else None

def pick_protein_from_groups(label, key_prefix):
    group = st.selectbox(f"{label} — Choose Group", list(PROTEIN_GROUPS.keys()), key=f"{key_prefix}_group")
    protein = st.selectbox(f"{label} — Choose Protein", PROTEIN_GROUPS[group], key=f"{key_prefix}_protein")
    return protein

# ---------- Streamlit app ----------
st.title("PCI3 Assembly Calculator")

# Input: Required RBC (M)
pci3_needed = st.number_input("1) How many PCI3 needed (million):", min_value=1.0, value=40.0)

# BC1 Section (always required)
st.header("Proteins on BC1")
st.markdown("**Fixed Protein:** SA-BC (1.0 µM)")
req_pmol_bc1_fixed = st.number_input("Required pmol for SA-BC:", min_value=0.0, value=2.4)

# Add more proteins dynamically to BC1
st.subheader("Add Additional Proteins to BC1")
if "bc1_entries" not in st.session_state:
    st.session_state.bc1_entries = []
if st.button("➕ Add Protein to BC1"):
    st.session_state.bc1_entries.append(len(st.session_state.bc1_entries))

bc1_proteins = []
for i in st.session_state.bc1_entries:
    prot_name = pick_protein_from_groups("BC1 Protein", f"bc1_{i}")
    req_pmol = st.number_input(f"Required pmol for {prot_name}:", min_value=0.0, step=0.1, key=f"bc1_pmol_{i}")
    bc1_proteins.append((prot_name, req_pmol))

st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='color:#2E86C1; font-weight:700;'>Optional Step:</h2>"
    "<h3 style='margin-top:-10px;'>Include BC2 Proteins?</h3>",
    unsafe_allow_html=True
)

include_bc2 = st.checkbox("Include BC2 Proteins?", value=False)

bc2_proteins = []
if include_bc2:
    st.header("Proteins on BC2")
    primary_bc2 = pick_protein_from_groups("Primary BC2 Protein", "primary_bc2")
    req_pmol_bc2_primary = st.number_input(
        f"Required pmol for {primary_bc2}:",
        min_value=0.0,
        step=0.1,
        value=9.6,
        key="primary_bc2_pmol"
    )

    # Add more proteins dynamically to BC2
    st.subheader("Add Additional Proteins to BC2")
    if "bc2_entries" not in st.session_state:
        st.session_state.bc2_entries = []
    if st.button("➕ Add Protein to BC2"):
        st.session_state.bc2_entries.append(len(st.session_state.bc2_entries))

    bc2_proteins = [(primary_bc2, req_pmol_bc2_primary)]
    for i in st.session_state.bc2_entries:
        prot_name = pick_protein_from_groups("BC2 Protein", f"bc2_{i}")
        req_pmol = st.number_input(f"Required pmol for {prot_name}:", min_value=0.0, step=0.1, key=f"bc2_pmol_{i}")
        bc2_proteins.append((prot_name, req_pmol))


# ---------- Calculations ----------
per_std = per_unit_values(DPB_PER_M_STANDARD, PROT_RATIO_BC1_STANDARD, PROT_RATIO_BC2_STANDARD)
per_cus = per_unit_values(DPB_PER_M_CUSTOM, PROT_RATIO_BC1_CUSTOM, PROT_RATIO_BC2_CUSTOM)
req_std = required_row(per_std, pci3_needed)
req_cus = required_row(per_cus, pci3_needed)

# ---------- Display ----------
# ---------- Display ----------
st.markdown("---")
st.header("STANDARD")

# Core model-derived values (shared physical constants)
per_std = per_unit_values(DPB_PER_M_STANDARD, PROT_RATIO_BC1_STANDARD, PROT_RATIO_BC2_STANDARD)
req_std = required_row(per_std, pci3_needed)

st.write(f"DOPE pmol: {req_std['DOPE_pmol']:.2f} pmol")
st.write(f"Barcode1 pmol: {req_std['Barcode1_pmol']:.2f} pmol")
st.write(f"Barcode2 pmol: {req_std['Barcode2_pmol']:.2f} pmol")

# BC1 per-protein calculations
st.subheader("BC1 Protein Calculations")
for name, pmol in [("SA-BC", req_pmol_bc1_fixed)] + bc1_proteins:
    # Each protein uses the same model chain but scaled to its own pmol input
    per_unit_individual = per_unit_values(DPB_PER_M_STANDARD, PROT_RATIO_BC1_STANDARD, PROT_RATIO_BC2_STANDARD)
    req_individual = required_row(per_unit_individual, pci3_needed)
    calc_pmol = req_individual["Proteins_BC1_pmol"] * (pmol / req_pmol_bc1_fixed if req_pmol_bc1_fixed else 0)
    st.write(f"{name}: {calc_pmol:.2f} pmol (calculated from required {pmol:.2f})")


# BC2 per-protein calculations
if include_bc2:
    # all BC2 calculations + display
    st.subheader("BC2 Protein Calculations")
    for name, pmol in bc2_proteins:
        per_unit_individual = per_unit_values(DPB_PER_M_STANDARD, PROT_RATIO_BC1_STANDARD, PROT_RATIO_BC2_STANDARD)
        req_individual = required_row(per_unit_individual, pci3_needed)
        calc_pmol = req_individual["Proteins_BC2_pmol"] * (pmol / bc2_proteins[0][1] if bc2_proteins[0][1] else 0)
        st.write(f"{name}: {calc_pmol:.2f} pmol (calculated from required {pmol:.2f})")


# ---------- CUSTOM ----------
st.markdown("---")
st.header("CUSTOM")

per_cus = per_unit_values(DPB_PER_M_CUSTOM, PROT_RATIO_BC1_CUSTOM, PROT_RATIO_BC2_CUSTOM)
req_cus = required_row(per_cus, pci3_needed)

st.write(f"DOPE pmol: {req_cus['DOPE_pmol']:.2f} pmol")
st.write(f"Barcode1 pmol: {req_cus['Barcode1_pmol']:.2f} pmol")
st.write(f"Barcode2 pmol: {req_cus['Barcode2_pmol']:.2f} pmol")

# BC1 Custom per-protein
st.subheader("BC1 Protein Calculations (Custom)")
for name, pmol in [("SA-BC", req_pmol_bc1_fixed)] + bc1_proteins:
    per_unit_individual = per_unit_values(DPB_PER_M_CUSTOM, PROT_RATIO_BC1_CUSTOM, PROT_RATIO_BC2_CUSTOM)
    req_individual = required_row(per_unit_individual, pci3_needed)
    calc_pmol = req_individual["Proteins_BC1_pmol"] * (pmol / req_pmol_bc1_fixed if req_pmol_bc1_fixed else 0)
    st.write(f"{name}: {calc_pmol:.2f} pmol (calculated from required {pmol:.2f})")

# BC2 Custom per-protein
if include_bc2:
    # all BC2 calculations + display
    st.subheader("BC2 Protein Calculations (Custom)")
    for name, pmol in bc2_proteins:
        per_unit_individual = per_unit_values(DPB_PER_M_CUSTOM, PROT_RATIO_BC1_CUSTOM, PROT_RATIO_BC2_CUSTOM)
        req_individual = required_row(per_unit_individual, pci3_needed)
        calc_pmol = req_individual["Proteins_BC2_pmol"] * (pmol / bc2_proteins[0][1] if bc2_proteins[0][1] else 0)
        st.write(f"{name}: {calc_pmol:.2f} pmol (calculated from required {pmol:.2f})")
# ---------- STOCK VOLUMES ----------
st.markdown("---")
st.header("Stock Volumes for Proteins (µL)")
st.subheader("BC1")
for name, pmol in [("SA-BC", req_pmol_bc1_fixed)] + bc1_proteins:
    stock = STOCKS.get(name, 0)
    if stock > 0:
        vol = pmol / stock
        st.write(f"{name} (stock {stock} µM): Vol/unit {vol:.2f} µL | Total {vol * pci3_needed:.2f} µL")
    else:
        st.write(f"{name}: stock conc not defined — volume cannot be calculated")
if include_bc2:
    # all BC2 calculations + display
    st.subheader("BC2")
    for name, pmol in bc2_proteins:
        stock = STOCKS.get(name, 0)
        if stock > 0:
            vol = pmol / stock
            st.write(f"{name} (stock {stock} µM): Vol/unit {vol:.2f} µL | Total {vol * pci3_needed:.2f} µL")
        else:
            st.write(f"{name}: stock conc not defined — volume cannot be calculated")
