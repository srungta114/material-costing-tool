import streamlit as st
import pandas as pd

# --- 1. CONFIGURATION & DATA LOADING ---
def get_csv_url(base_url, gid):
    # Converts the standard sheet URL into a direct CSV export for a specific tab
    if "/edit" in base_url:
        return base_url.split("/edit")[0] + f"/export?format=csv&gid={gid}"
    return base_url

# Replace these with your actual values
SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
PRODUCT_MASTER_GID = "573342116"  # <--- UPDATE THIS GID FROM YOUR BROWSER URL

@st.cache_data(ttl=60)
def load_products():
    csv_url = get_csv_url(SHEET_URL, PRODUCT_MASTER_GID)
    df = pd.read_csv(csv_url)
    # Clean up column headers (removes hidden spaces)
    df.columns = df.columns.str.strip()
    return df

try:
    df_master = load_products()
except Exception as e:
    st.error(f"Error loading Product Master: {e}")
    st.stop()

st.title("🏗️ Material Costing & Inventory Ledger")

# --- 2. SESSION STATE FOR MULTI-ITEM BILLS ---
if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

# --- 3. BILL HEADER (Seller Info) ---
st.header("1. Bill Details")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    seller_name = c1.text_input("Seller Company Name")
    bill_no = c2.text_input("Bill No.")
    purchase_date = c3.date_input("Purchase Date")

# --- 4. ITEM ENTRY (Auto-Selection Logic) ---
st.header("2. Add Material")
with st.container(border=True):
    # User selects Item Name first
    product_list = sorted(df_master['Item_Name'].unique())
    selected_product = st.selectbox("Select Product", product_list)

    # Automatically find the metadata for the selected item
    item_info = df_master[df_master['Item_Name'] == selected_product].iloc[0]
    
    group = item_info['Group']
    sub_group = item_info['Sub-Group']
    p_unit = item_info['Purchase_Unit']
    s_unit = item_info['Sales_Unit']
    conv_fact = item_info['Conversion_Factor']

    # Display the auto-selected Group and Sub-Group
    st.write(f"**Classification:** {group} > {sub_group}")
    st.info(f"**Unit Logic:** Purchased in {p_unit} | Sales tracked in {s_unit}")

    # Costing Inputs
    i1, i2, i3 = st.columns(3)
    qty_p = i1.number_input(f"Total Quantity ({p_unit})", min_value=0.0, step=0.1)
    rate_p = i2.number_input(f"Purchase Rate (per {p_unit})", min_value=0.0)
    
    # Auto-calculate suggested sales quantity
    qty_s = i3.number_input(f"Calculated Qty ({s_unit})", value=float(qty_p * conv_fact))

    st.write("---")
    st.caption("Additional Costs & Discounts (Calculated per Purchase Unit)")
    f1, f2, f3 = st.columns(3)
    excise = f1.number_input("Excise Duty", min_value=0.0)
    trans = f2.number_input("Transport Cost", min_value=0.0)
    labour = f3.number_input("Labour Cost", min_value=0.0)
    
    d1, d2 = st.columns(2)
    d_type = d1.selectbox("Discount Type", ["None", "Per Unit", "Percentage (%)"])
    d_val = d2.number_input("Discount Value", min_value=0.0)

    if st.button("➕ Add Item to Bill"):
        # Cost Calculation Logic
        base_rate = rate_p + excise + trans + labour
        
        if d_type == "Per Unit":
            taxable = base_rate - d_val
        elif d_type == "Percentage (%)":
            taxable = base_rate * (1 - (d_val/100))
        else:
            taxable = base_rate
        
        landed_rate_p = taxable * 1.13 # 13% Fixed VAT
        total_item_val = landed_rate_p * qty_p
        cost_per_s_unit = total_item_val / qty_s if qty_s > 0 else 0

        # Add to memory
        st.session_state.bill_items.append({
            "Seller": seller_name,
            "Bill_No": bill_no,
            "Date": str(purchase_date),
            "Group": group,
            "Sub-Group": sub_group,
            "Material": selected_product,
            "Qty_Purchase": qty_p,
            "Unit_Purchase": p_unit,
            "Qty_Sales": qty_s,
            "Unit_Sales": s_unit,
            "Rate_Purchase": rate_p,
            "Excise_Kg": excise,
            "Transport_Kg": trans,
            "Labour_Kg": labour,
            "Landed_Rate_Purchase": round(landed_rate_p, 2),
            "Cost_Pc": round(cost_per_s_unit, 2),
            "Total_Item_Cost": round(total_item_val, 2)
        })
        st.success(f"Added {selected_product} to bill.")

# --- 5. REVIEW AND SAVE ---
if st.session_state.bill_items:
    st.header("3. Bill Review")
    df_bill = pd.DataFrame(st.session_state.bill_items)
    st.dataframe(df_bill[['Material', 'Qty_Purchase', 'Unit_Purchase', 'Total_Item_Cost']])
    
    st.metric("Total Bill Amount (Incl. 13% VAT)", f"{df_bill['Total_Item_Cost'].sum():,.2f}")

    if st.button("💾 Save Final Bill to Sheets"):
        # Note: You can use the gsheets connection here if you have 
        # write permissions set up, otherwise this displays a success message.
        # For full write support, ensure Service Account JSON is in Secrets.
        st.success("Data prepared for saving! (Check GSheets integration)")
        st.session_state.bill_items = []
