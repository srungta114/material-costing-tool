import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFIGURATION (This could also be loaded from a Google Sheet) ---
# Example of how your grouped data is handled
PRODUCT_MASTER = {
    "Raw Materials": {
        "Metals": ["Steel Rod 10mm", "Aluminum Sheet"],
        "Chemicals": ["Industrial Solvent", "Epoxy Resin"]
    },
    "Packaging": {
        "Boxes": ["Corrugated Box XL", "Small Mailer"],
        "Labels": ["Adhesive Roll"]
    }
}

# Mapping for items with different Purchase/Sales units
# Format: { Product: (Purchase Unit, Sales Unit, Default Conversion) }
UNIT_MAPPING = {
    "Steel Rod 10mm": ("Kg", "Pc", 5.5),  # 1 Pc = 5.5 Kg
    "Industrial Solvent": ("Drum", "Litre", 200), # 1 Drum = 200 Litres
}

st.title("📦 Advanced Material Costing Ledger")

# --- STEP 1: CATEGORIZATION ---
st.subheader("Item Classification")
c1, c2, c3 = st.columns(3)

group = c1.selectbox("Group", list(PRODUCT_MASTER.keys()))
sub_group = c2.selectbox("Sub-Group", list(PRODUCT_MASTER[group].keys()))
product = c3.selectbox("Product", PRODUCT_MASTER[group][sub_group])

# Check for special units
p_unit, s_unit, conv_factor = UNIT_MAPPING.get(product, ("Kg", "Kg", 1.0))

# --- STEP 2: QUANTITY & COSTING ---
st.info(f"Unit Info: Purchased in **{p_unit}**, Tracked/Sold in **{s_unit}**")

with st.form("costing_form"):
    col1, col2, col3 = st.columns(3)
    
    qty_purchased = col1.number_input(f"Total Quantity ({p_unit})", min_value=0.01)
    
    # If units are different, allow user to confirm the piece count
    if p_unit != s_unit:
        qty_sales = col2.number_input(f"Equivalent Quantity ({s_unit})", value=qty_purchased * conv_factor)
    else:
        qty_sales = qty_purchased
        
    rate_purchase = col3.number_input(f"Purchase Rate (per {p_unit})", min_value=0.0)

    st.markdown("---")
    st.write("### Regulatory & Logistics (Per Kg/Unit)")
    f1, f2, f3 = st.columns(3)
    excise_val = f1.number_input("Excise Duty", help="Fixed amt per purchase unit")
    trans_val = f2.number_input("Transport", help="Fixed amt per purchase unit")
    labour_val = f3.number_input("Labour", help="Fixed amt per purchase unit")

    st.write("### Discounts")
    d_type = st.selectbox("Type", ["None", "Per Unit", "Percentage (%)"])
    d_val = st.number_input("Discount Value")

    submit = st.form_submit_button("Record Purchase")

if submit:
    # Logic for Landed Cost
    subtotal = (rate_purchase + excise_val + trans_val + labour_val)
    
    if d_type == "Per Unit":
        taxable = subtotal - d_val
    elif d_type == "Percentage (%)":
        taxable = subtotal * (1 - (d_val/100))
    else:
        taxable = subtotal
        
    total_landed = (taxable * qty_purchased) * 1.13 # 13% Fixed VAT
    
    # Calculate Cost per Sales Unit
    cost_per_sales_unit = total_landed / qty_sales
    
    st.success(f"Landed Cost per {s_unit}: **{round(cost_per_sales_unit, 2)}**")
    
    # --- SAVE TO SHEET ---
    # (Same logic as previous version, adding Group/Sub-Group columns)