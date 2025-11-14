#!/usr/bin/env python3
import streamlit as st

# ---------- Constants ----------
RBC_STOCK_CONC_M_per_mL = 50.0
RBC_ANCHORED_PER_UNIT_M = 4.0
ANCHOR_EFFICIENCY = 0.50
ANCHOR_RBC_YIELD = 0.60
BB_RATIO = 2.0
RBC_OVERALL_YIELD = 0.40
DOPE_PEG_BB01_STOCK = 1
DPB_WORKING_CONC = 100
POST_ANCHOR_WASH_VOL = 10
BARCODE_BACKBONE = 0.5
CD3_BC_PMOL = 1.18
CD28_BC_PMOL = 0.78
CD137_BC_PMOL = 0.156
BC_SA_STOCK = 1
CD3_CONC = 3.3
CD28_CONC = 3.3
CD137_CONC = 0.66
POST_HYBRIDIZATION_WASH_VOL = 30

DPB_PER_M_STANDARD = 4.0
PROT_RATIO_BC1_STANDARD = 4.0
PROT_RATIO_BC2_STANDARD = 4.0

DPB_PER_M_CUSTOM = 16.0
PROT_RATIO_BC1_CUSTOM = 2.0
PROT_RATIO_BC2_CUSTOM = 4.0

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

# ---------- Streamlit app ----------
st.title("PCI3 Assembly Calculator")

# --- create tabs at the top of the app ---
tab_standard, tab_custom = st.tabs(["Standard T-cell Activation", "Custom"])

with tab_standard:
    st.title("Standard T-cell Activation")
    # Input: Required RBC (M)
    pci3_needed = st.number_input("1) How many PCI3 needed (million):", min_value=1.0, value=40.0, key = "standrd_PCI")

    def RBC_vol_needed(pci3_needed, RBC_OVERALL_YIELD):
        raw_RBC = pci3_needed / RBC_OVERALL_YIELD
        raw_RBC_vol = raw_RBC / RBC_STOCK_CONC_M_per_mL * 1000
        return {
        "Raw_RBC_amount": raw_RBC,
        "Raw_RBC_vol": raw_RBC_vol
        }

    req_rbc_vol = RBC_vol_needed(pci3_needed, RBC_OVERALL_YIELD)
    st.write(f"Raw RBC Volume Required (50M/mL): {req_rbc_vol['Raw_RBC_vol']:.1f}")
    raw_rbc = req_rbc_vol['Raw_RBC_amount']

    def DPB1_anchoring(req_rbc_vol, DPB_PER_M_STANDARD, DOPE_PEG_BB01_STOCK, DPB_WORKING_CONC, POST_ANCHOR_WASH_VOL, ANCHOR_EFFICIENCY, ANCHOR_RBC_YIELD):
        raw_rbc = req_rbc_vol['Raw_RBC_amount']
        raw_rbc_vol = req_rbc_vol['Raw_RBC_vol']
        dpb1_vol = raw_rbc * DPB_PER_M_STANDARD / DOPE_PEG_BB01_STOCK
        anchoring_pbs_vol = 1000 * raw_rbc * DPB_PER_M_STANDARD / (2* DPB_WORKING_CONC) - dpb1_vol
        total_reaction_vol = raw_rbc_vol + dpb1_vol + anchoring_pbs_vol
        washing_pbs_vol = total_reaction_vol * POST_ANCHOR_WASH_VOL
        dpb1_on_rbc_pmol = raw_rbc * DPB_PER_M_STANDARD * ANCHOR_EFFICIENCY * ANCHOR_RBC_YIELD
        return {
        "dpb1_vol": dpb1_vol,
        "anchoring_pbs_vol": anchoring_pbs_vol,
        "total_reaction_vol": total_reaction_vol,        
        "washing_pbs_vol":  washing_pbs_vol,
        "dpb1_on_rbc_pmol":  dpb1_on_rbc_pmol,
        }

    anchoring = DPB1_anchoring(req_rbc_vol, DPB_PER_M_STANDARD, DOPE_PEG_BB01_STOCK, DPB_WORKING_CONC, POST_ANCHOR_WASH_VOL, ANCHOR_EFFICIENCY, ANCHOR_RBC_YIELD)

    st.write(f"Anchoring Solution DPB1 Vol: {anchoring['dpb1_vol']:.1f} uL")
    st.write(f"Anchoring Solution PBS Vol: {anchoring['anchoring_pbs_vol']:.1f} uL")
    st.write(f"Post Anchoring Washing PBS Vol: {anchoring['washing_pbs_vol']:.1f} uL")

    def binding(anchoring, BARCODE_BACKBONE, CD3_BC_PMOL, BC_SA_STOCK, CD3_CONC, CD28_BC_PMOL, CD28_CONC, CD137_BC_PMOL, CD137_CONC):
        dpb1_on_rbc_pmol = anchoring['dpb1_on_rbc_pmol']
        BC_1_pmol = dpb1_on_rbc_pmol * BARCODE_BACKBONE
        anti_CD3_pmol = BC_1_pmol * CD3_BC_PMOL
        BC1_volume = BC_1_pmol / BC_SA_STOCK
        anti_CD3_vol = anti_CD3_pmol / CD3_CONC
        binding1_total_vol = anti_CD3_vol + BC1_volume
        BC_2_pmol = dpb1_on_rbc_pmol * BARCODE_BACKBONE
        anti_CD28_pmol = BC_2_pmol * CD28_BC_PMOL
        anti_CD137_pmol = BC_2_pmol * CD137_BC_PMOL
        BC2_volume = BC_2_pmol / BC_SA_STOCK
        anti_CD28_vol = anti_CD28_pmol / CD28_CONC
        anti_CD137_vol = anti_CD137_pmol / CD137_CONC
        binding2_total_vol = BC2_volume + anti_CD28_vol
        total_binding_vol = binding1_total_vol + binding2_total_vol

        return {
        "BC1_volume": BC1_volume,
        "anti_CD3_vol": anti_CD3_vol,
        "BC2_volume": BC2_volume,        
        "anti_CD28_vol":  anti_CD28_vol,
        "anti_CD137_vol":  anti_CD137_vol,
        "binding1_total_vol": binding1_total_vol,
        "binding2_total_vol": binding2_total_vol
        }

    binding_values = binding(anchoring, BARCODE_BACKBONE, CD3_BC_PMOL, BC_SA_STOCK, CD3_CONC, CD28_BC_PMOL, CD28_CONC, CD137_BC_PMOL, CD137_CONC)
    st.write(f"BC1-SA Volume: {binding_values['BC1_volume']:.1f} uL")
    st.write(f"anti-CD3 Volume: {binding_values['anti_CD3_vol']:.1f} uL")
    st.write(f"BC2-SA Volume: {binding_values['BC2_volume']:.1f} uL")
    st.write(f"anti-CD28 Volume: {binding_values['anti_CD28_vol']:.1f} uL")
    st.write(f"anti-CD137 Volume: {binding_values['anti_CD28_vol']:.1f} uL")

    def hydbridization(req_rbc_vol, binding_values, ANCHOR_RBC_YIELD, POST_HYBRIDIZATION_WASH_VOL):
        raw_rbc = req_rbc_vol['Raw_RBC_amount']
        anchored_RBC_M = raw_rbc * ANCHOR_RBC_YIELD
        raw_rbc_vol = req_rbc_vol['Raw_RBC_vol']
        anchored_RBC_uL = raw_rbc_vol
        BC1_vol = binding_values["binding1_total_vol"]
        BC2_vol = binding_values["binding2_total_vol"]
        total_hybridization_mix = BC1_vol + BC2_vol
        hybridization_PBS_vol = anchored_RBC_uL * POST_HYBRIDIZATION_WASH_VOL
        resuspention_PBS_vol = raw_rbc_vol

        return {
        "hybridization_PBS_vol": hybridization_PBS_vol,
        }

    hydbridization_values = hydbridization(req_rbc_vol, binding_values, ANCHOR_RBC_YIELD, POST_HYBRIDIZATION_WASH_VOL)
    st.write(f"Hybridization Wash PBS Volume: {hydbridization_values['hybridization_PBS_vol']:.1f} uL")


with tab_custom:
    st.title("Custom PCI3 Assembly Calculator")

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



    def required_row(per_unit, pci3_needed):
        return {k: v * pci3_needed for k, v in per_unit.items()}

    def vol_from_pmol(pmol, stock_uM):
        return pmol / stock_uM if stock_uM and stock_uM > 0 else None

    def pick_protein_from_groups(label, key_prefix):
        group = st.selectbox(f"{label} — Choose Group", list(PROTEIN_GROUPS.keys()), key=f"{key_prefix}_group")
        protein = st.selectbox(f"{label} — Choose Protein", PROTEIN_GROUPS[group], key=f"{key_prefix}_protein")
        return protein


# Input: Required RBC (M)
    pci3_needed = st.number_input("1) How many PCI3 needed (million):", min_value=1.0, value=40.0, key = "cus_PCI")

    # BC1 Section
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

    # BC2 Section
    st.header("Proteins on BC2")
    primary_bc2 = pick_protein_from_groups("Primary BC2 Protein", "primary_bc2")
    req_pmol_bc2_primary = st.number_input(f"Required pmol for {primary_bc2}:", min_value=0.0, step=0.1, value=9.6, key="primary_bc2_pmol")

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

    st.subheader("BC2")
    for name, pmol in bc2_proteins:
        stock = STOCKS.get(name, 0)
        if stock > 0:
            vol = pmol / stock
            st.write(f"{name} (stock {stock} µM): Vol/unit {vol:.2f} µL | Total {vol * pci3_needed:.2f} µL")
        else:
            st.write(f"{name}: stock conc not defined — volume cannot be calculated")
