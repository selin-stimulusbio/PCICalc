#!/usr/bin/env python3
import streamlit as st

# ---------- Constants ----------
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

# Protein groups
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

# ---------- Streamlit app ----------
st.title("PCI3 Assembly Calculator")

# Inputs
# Inputs
pci3_needed = st.number_input("1) How many PCI3 needed (million):", min_value=1.0, value=40.0)

bc1_name = "SA-BC"
st.markdown(f"**2) Protein on BC1 is fixed:** {bc1_name}")

group_choice = st.selectbox("Select protein group for BC2:", list(PROTEIN_GROUPS.keys()))
bc2_name = st.selectbox("Select protein within group:", PROTEIN_GROUPS[group_choice])

req_pmol_bc1 = st.number_input(f"4a) Required pmol for {bc1_name}:", min_value=0.0, value=2.4)
req_pmol_bc2 = st.number_input(f"4b) Required pmol for {bc2_name}:", min_value=0.0, value=9.6)


# Per-unit calculations
per_std = per_unit_values(DPB_PER_M_STANDARD, PROT_RATIO_BC1_STANDARD, PROT_RATIO_BC2_STANDARD)
per_cus = per_unit_values(DPB_PER_M_CUSTOM, PROT_RATIO_BC1_CUSTOM, PROT_RATIO_BC2_CUSTOM)

# Required rows
req_std = required_row(per_std, pci3_needed)
req_cus = required_row(per_cus, pci3_needed)

# Display Standard
st.header("STANDARD")
for k, v in req_std.items():
    st.write(f"{k.replace('_',' ')}: {v:.2f} pmol")

# Display Custom
st.header("CUSTOM")
for k, v in req_cus.items():
    st.write(f"{k.replace('_',' ')}: {v:.2f} pmol")

# Stock volumes (based on user input)
st.header("Stock Volumes for Proteins (µL)")
vol_bc1 = vol_from_pmol(req_pmol_bc1, STOCKS["SA-BC"])
vol_bc2 = vol_from_pmol(req_pmol_bc2, STOCKS[bc2_name])
st.write(f"SA-BC (stock {STOCKS['SA-BC']} µM): Vol/unit {vol_bc1:.2f} µL | Total {vol_bc1 * pci3_needed:.2f} µL")
st.write(f"{bc2_name} (stock {STOCKS[bc2_name]} µM): Vol/unit {vol_bc2:.2f} µL | Total {vol_bc2 * pci3_needed:.2f} µL")
