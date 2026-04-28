import streamlit as st
import pandas as pd

# This bypasses the gsheets connection library for reading
# It converts your Google Sheet URL into a direct CSV download link
def get_csv_url(base_url):
    # This ensures we pull the SPECIFIC tab, not just the first one
    # Replace '12345678' with the ACTUAL gid from your Product_Master tab URL
    target_gid = "573342116" 
    if "/edit" in base_url:
        return base_url.split("/edit")[0] + f"/export?format=csv&gid={target_gid}"
    return base_url

# Load Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
csv_url = get_csv_url(sheet_url)

@st.cache_data(ttl=600)
def load_products():
    # We add a try-block to catch the exact error
    try:
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets. Error: {e}")
        return pd.DataFrame()

df_master = load_products()

st.title("📑 Multi-Item Material Costing Tool")

# --- SESSION STATE FOR MULTIPLE ITEMS ---
if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

# --- SECTION 1: BILL HEADER (Seller Info) ---
st.header("1. Bill Header")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    seller_name = c1.text_input("Seller Company Name")
    bill_no = c2.text_input("Bill No.")
    purchase_date = c3.date_input("Purchase Date")

# --- SECTION 2: ITEM ENTRY ---
st.header("2. Add Items")
with st.container(border=True):
    # Dynamic Dropdowns based on Excel logic
    col1, col2, col3 = st.columns(3)
    group = col1.selectbox("Group", df_master['Group'].unique())
    
    sub_groups = df_master[df_master['Group'] == group]['Sub-Group'].unique()
    sub_group = col2.selectbox("Sub-Group", sub_groups)
    
    products = df_master[(df_master['Group'] == group) & (df_master['Sub-Group'] == sub_group)]['Item_Name'].unique()
    product_name = col3.selectbox("Product", products)

    # Get specific item details for units
    item_details = df_master[df_master['Item_Name'] == product_name].iloc[0]
    p_unit = item_details['Purchase_Unit']
    s_unit = item_details['Sales_Unit']
    conv_fact = item_details['Conversion_Factor']

    st.write(f"**Units:** Purchased in {p_unit}, Sold/Tracked in {s_unit}")

    # Costing Inputs
    i1, i2, i3 = st.columns(3)
    qty_p = i1.number_input(f"Quantity ({p_unit})", min_value=0.0, step=0.1)
    rate_p = i2.number_input(f"Rate (per {p_unit})", min_value=0.0)
    
    # Auto-calculate sales qty but allow override
    qty_s = i3.number_input(f"Quantity ({s_unit})", value=qty_p * conv_fact)

    st.write("---")
    st.caption("Additional Costs & Discounts (Per Purchase Unit)")
    f1, f2, f3, f4 = st.columns(4)
    excise = f1.number_input("Excise", min_value=0.0)
    trans = f2.number_input("Transport", min_value=0.0)
    labour = f3.number_input("Labour", min_value=0.0)
    
    d_type = f4.selectbox("Discount Type", ["None", "Per Unit", "Percentage (%)"])
    d_val = st.number_input("Discount Value", min_value=0.0)

    if st.button("➕ Add Item to Bill"):
        # Calculation Logic
        sub_total_per_unit = rate_p + excise + trans + labour
        if d_type == "Per Unit":
            taxable = sub_total_per_unit - d_val
        elif d_type == "Percentage (%)":
            taxable = sub_total_per_unit * (1 - (d_val/100))
        else:
            taxable = sub_total_per_unit
        
        landed_rate = taxable * 1.13 # 13% VAT
        total_item_cost = landed_rate * qty_p
        cost_per_s_unit = total_item_cost / qty_s if qty_s > 0 else 0

        # Store in session memory
        st.session_state.bill_items.append({
            "Seller": seller_name,
            "Bill_No": bill_no,
            "Date": str(purchase_date),
            "Group": group,
            "Sub-Group": sub_group,
            "Material": product_name,
            "Qty_Purchase": qty_p,
            "Unit_Purchase": p_unit,
            "Qty_Sales": qty_s,
            "Unit_Sales": s_unit,
            "Rate_Purchase": rate_p,
            "Excise_Kg": excise,
            "Transport_Kg": trans,
            "Labour_Kg": labour,
            "Landed_Rate_Purchase": round(landed_rate, 2),
            "Cost_Pc": round(cost_per_s_unit, 2),
            "Total_Item_Cost": round(total_item_cost, 2)
        })

# --- SECTION 3: BILL PREVIEW & SAVE ---
if st.session_state.bill_items:
    st.header("3. Bill Review")
    df_preview = pd.DataFrame(st.session_state.bill_items)
    st.table(df_preview[['Material', 'Qty_Purchase', 'Unit_Purchase', 'Total_Item_Cost']])
    
    st.metric("Total Bill Value", f"{df_preview['Total_Item_Cost'].sum():,.2f}")

    if st.button("💾 Final Save to Google Sheets"):
        existing_data = conn.read(worksheet="Purchases")
        updated_df = pd.concat([existing_data, df_preview], ignore_index=True)
        conn.update(worksheet="Purchases", data=updated_df)
        
        st.success("Entire bill saved successfully!")
        st.session_state.bill_items = [] # Clear the bill
        st.rerun()

    if st.button("🗑️ Clear Bill"):
        st.session_state.bill_items = []
        st.rerun()
