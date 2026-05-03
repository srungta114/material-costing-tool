import streamlit as st
st.set_page_config(page_title="Material Costing", layout="wide")
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CREDENTIALS & AUTHENTICATION ---
gsheet_creds = {
    "type": "service_account",
    "project_id": "engaged-kite-494709-t7",
    "private_key_id": "3246aa828ad06c3520d2e3d5fac5aacebf3d6f75",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDt+weYv7ztXToL
NjSirZptnxgABGlaPvu77WZ6DNS4SO0umo5t5ENjXHnhmip60yEC/hv+5yZFnXkG
aHxWEKktOQFrDxV9uPQs7JSxwb2ObZDH3kx9GeVU+z2Shxo8BOVfOpq62U8Y7l9+
e8l3eBGXLP8J4sSzq3WKb9RBvxxNztDdfDTDOJMXhAe4sKIIwu3sY0Pd4OvMkjGv
CpnWSzmCLgl4e6BdbMQmQsHPNK7Iaiaq7kCBZ9JHUlpg5IJOZRFcGDdxxp/QGZ5q
1l6YZB90HUHB/aUuii6SoHWoylAjhq1wIlO+zrnPPXk+HDiLyYM+Dv8DRrXpW7dF
B9A11xzdAgMBAAECggEAMryRfM0qFhAJazECDUnGUgc4am6GWIVzjXgaYDyCkIyJ
tqUgZwjinhkt6f2Af4GqONVcuh5lUDO3xPg7Q+0W6GuOJBlJ620mb7p7pB8qTuaI
lrgL5iMCe/j5glcX7oJbtY8MxHfGj4nopZJ2HCim1Wx0LlMgvS55p4tafS7ltaeQ
K+MEFyKiiQdIdO+EVenan8bV7+iQSAuJJ1H0gwlbYZ7cmXU/8Gv65KPE7iGep0Wu
kQRqTNWSsXIzLYJ7AhGqn4bGeWgqZr86UlC7hu0pR/bAmj85gavwPfzH6kPI4Q8+
bvQQhwxu7Q9vafnUJk+B7gs/b9FgVjEMWY84wUdI+QKBgQD4jDH71NyxAlNuwSWw
RBHrG5kKY3zwlGJnfxBBY5WA1gBx2MJSOsK5ZinSUbRhWYOLrWntpxgDH9DkxdBX
H3nf+r+MNoF2LrKn09Fb8YJmRZunbm6dMAd/dDvrgxKuX6WUsMaCRoQXSSkq+G7U
a0GMdHrIyK4cD8XcB3R+FAJweQKBgQD1HblFy4LIQmvNBTrTjCMUJVVGkbzFX6WC
gU6y2WE3k3GH6oRjdFvrlRjiQ3hFr1oAI1ROEO/HQdYfjEWNAh4/kAOyI+JVH751
dvD4DLd6ZiBy9PqePccICXIWAyYuCEXunfB3GVadBKHTWe609O0m9a1EfvfauPE0
aETiDmiehQKBgGZ5BrKZVFP2bYegQnWl2u1f93z8/6oAw4GANad/80em84/8mkFk
0Ju3r05zOTdZvI599Mpytcez+mAX3onNBGZ/7zFT15RuNGJVRl/t9qFL2ZzyPtC3
2J+HwJyc8brK3G2tZGqZwCQJmduJicgyYFgUPftCIeaX6i+JM1I31bmhAoGAHw/K
N7cHdrs8D/oWr1I168qjWNMFGfn57mTWhUGY2UMdAv1ME5JeR6dYROwJ5MLI4/WW
LGJnEFgee1b6RVk8Xg+w+DUl7GWebCJLfROXeLJScF7tF3p6q2EPDQ0PHIw92HQ5
Uc5rNHCu1SqzXkkfeG1vrJtua1A+eMax2/e5eEUCgYEAiTrYuQj3tqDYJDlqy3kX
OqTNc+hZnBnJx5LsAphfh6T9B9liot7CE38ezNrovmMJqYcCaDDbz+TC25dbT7qD
yviEcd+Q4+u5Yguo04+gfp2UC9b6ElRvidOBckzwtjLUyVwQxTxXagpQpdh8XynW
S80xx+2STMx8HFga4AUSkMY=
-----END PRIVATE KEY-----""",
    "client_email": "costing-tool-saver@engaged-kite-494709-t7.iam.gserviceaccount.com",
    "client_id": "114472038158489600117",
    "token_uri": "https://oauth2.googleapis.com/token",
}

try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(gsheet_creds, scopes=scopes)
    client = gspread.authorize(creds)
    SHEET_ID = "1ZTI3G97SSOcowXJyHpncFFSlGyS5VSLJublqLpAxVIk"
    sh = client.open_by_key(SHEET_ID)
except Exception as e:
    st.error(f"Authentication Failed: {e}")
    st.stop()


# --- 2. SECURE DATA LOADERS ---
@st.cache_data(ttl=60)
def load_products():
    try:
        worksheet = sh.worksheet("Product_Master")
        df = pd.DataFrame(worksheet.get_all_records())
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Failed to load Product Master: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_purchases_data():
    try:
        purchases_sheet = sh.worksheet("Purchases")
        return pd.DataFrame(purchases_sheet.get_all_records())
    except Exception:
        return pd.DataFrame() 

df_master = load_products()
df_purchases = load_purchases_data()

# Extract unique sellers
if not df_purchases.empty and 'Seller' in df_purchases.columns:
    existing_sellers = sorted([str(s).strip() for s in df_purchases['Seller'].dropna().unique() if str(s).strip() != ""])
else:
    existing_sellers = []

# Initialize Session State
if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []

st.title("🏗️ Material  & Inventory Ledger")


# --- 3. QUICK COSTING SEARCH ---
st.header("🔍 Quick Costing Search")
with st.expander("Search Master Database", expanded=False): 
    if not df_purchases.empty and 'Material' in df_purchases.columns:
        search_materials = sorted(df_purchases['Material'].dropna().unique().tolist())
        search_selection = st.selectbox("Type or select a material to view its latest costing:", ["-- Select Material --"] + search_materials)
        
        if search_selection != "-- Select Material --":
            item_data = df_purchases[df_purchases['Material'] == search_selection].iloc[-1]
            
            st.info(f"**Supplier:** {item_data.get('Seller', 'N/A')} | **Bill No:** {item_data.get('Bill_No', 'N/A')} | **Date:** {item_data.get('Date', 'N/A')}")
            
            # Math & Parsing
            landed_rate = float(item_data.get('Landed_Rate_Purchase', 0))
            true_pre_tax_purchase = landed_rate / 1.13
            cost_pc = float(item_data.get('Cost_Pc', 0))
            
            purch_unit = str(item_data.get('Unit_Purchase', '')).strip()
            sales_unit = str(item_data.get('Unit_Sales', '')).strip()
            qty_p = float(item_data.get('Qty_Purchase', 0))
            qty_s = float(item_data.get('Qty_Sales', 1)) 
            
            is_pcs = sales_unit.lower() in ['pcs', 'pc', 'piece', 'pieces']
            is_kg = purch_unit.lower() in ['kg', 'kgs', 'kilogram', 'kilograms']
            
            # Row 1
            r1_c1, r1_c2, r1_c3 = st.columns(3)
            r1_c1.metric("Landed Cost (Purchase Unit)", f"{landed_rate:.2f} / {purch_unit}")
            r1_c2.metric("Cost per Sales Unit", f"{cost_pc:.2f} / {sales_unit}")
            r1_c3.metric("Last Qty Bought", f"{qty_p} {purch_unit}")
            
            st.write("") 
            
            # Row 2
            row_2_metrics = []
            row_2_metrics.append(("Pre-Tax (Purchase Unit)", f"{true_pre_tax_purchase:.2f}"))
            
            if is_pcs:
                pre_tax_pc = cost_pc / 1.13
                row_2_metrics.append(("Pre-Tax (Sales Unit)", f"{pre_tax_pc:.2f} / {sales_unit}"))
                
            if is_pcs and is_kg and qty_s > 0:
                weight_per_pc = qty_p / qty_s
                row_2_metrics.append(("Weight per Piece", f"{weight_per_pc:.3f} {purch_unit}"))
                
            r2_cols = st.columns(len(row_2_metrics))
            for idx, (label, value) in enumerate(row_2_metrics):
                r2_cols[idx].metric(label, value)
                
    else:
        st.write("No costings saved yet. Add a bill below to start building your database!")

st.divider()


# --- 4. BILL HEADER ---
st.header("1. Bill Details")
with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    
    seller_options = ["➕ Add New Seller..."] + existing_sellers
    selected_seller = c1.selectbox("Seller Company Name", seller_options)
    
    if selected_seller == "➕ Add New Seller...":
        seller_name = c1.text_input("Type New Seller Name Here")
    else:
        seller_name = selected_seller
        
    bill_no = c2.text_input("Bill No.")
    purchase_date = c3.date_input("Purchase Date")


# --- 5. ITEM ENTRY ---
st.header("2. Add Material")
with st.container(border=True):
    if not df_master.empty and 'Item_Name' in df_master.columns:
        product_list = sorted(df_master['Item_Name'].unique())
    else:
        product_list = ["-- No Products Found --"]

    selected_product = st.selectbox("Select Product", product_list)

    if selected_product != "-- No Products Found --":
        item_info = df_master[df_master['Item_Name'] == selected_product].iloc[0]
        
        group = item_info['Group']
        sub_group = item_info['Sub-Group']
        p_unit = item_info['Purchase_Unit']
        s_unit = item_info['Sales_Unit']
        conv_fact = item_info['Conversion_Factor']

        st.write(f"**Classification:** {group} > {sub_group}")
        st.info(f"**Unit Logic:** Purchased in {p_unit} | Sales tracked in {s_unit}")

        i1, i2, i3 = st.columns(3)
        qty_p = i1.number_input(f"Total Quantity ({p_unit})", min_value=0.0, step=0.1)
        rate_p = i2.number_input(f"Purchase Rate (per {p_unit})", min_value=0.0)
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
            base_rate = rate_p + excise + trans + labour
            
            if d_type == "Per Unit":
                taxable = base_rate - d_val
            elif d_type == "Percentage (%)":
                taxable = base_rate * (1 - (d_val/100))
            else:
                taxable = base_rate
            
            landed_rate_p = taxable * 1.13 
            total_item_val = landed_rate_p * qty_p
            cost_per_s_unit = total_item_val / qty_s if qty_s > 0 else 0

            existing_item_index = None
            for i, item in enumerate(st.session_state.bill_items):
                if item["Material"] == selected_product:
                    existing_item_index = i
                    break

            if existing_item_index is not None:
                old_item = st.session_state.bill_items.pop(existing_item_index)
                
                new_qty_p = old_item["Qty_Purchase"] + qty_p
                new_qty_s = old_item["Qty_Sales"] + qty_s
                new_total_cost = old_item["Total_Item_Cost"] + total_item_val
                
                avg_landed_rate = new_total_cost / new_qty_p if new_qty_p > 0 else 0
                avg_cost_pc = new_total_cost / new_qty_s if new_qty_s > 0 else 0

                st.session_state.bill_items.append({
                    "Seller": seller_name,
                    "Bill_No": bill_no,
                    "Date": str(purchase_date),
                    "Group": group,
                    "Sub-Group": sub_group,
                    "Material": selected_product,
                    "Qty_Purchase": new_qty_p,
                    "Unit_Purchase": p_unit,
                    "Qty_Sales": new_qty_s,
                    "Unit_Sales": s_unit,
                    "Rate_Purchase": round((old_item["Rate_Purchase"] + rate_p) / 2, 2), 
                    "Excise_Kg": round((old_item["Excise_Kg"] + excise) / 2, 2),
                    "Transport_Kg": round((old_item["Transport_Kg"] + trans) / 2, 2),
                    "Labour_Kg": round((old_item["Labour_Kg"] + labour) / 2, 2),
                    "Landed_Rate_Purchase": round(avg_landed_rate, 2),
                    "Cost_Pc": round(avg_cost_pc, 2),
                    "Total_Item_Cost": round(new_total_cost, 2)
                })
                st.success(f"🔄 Merged {selected_product} with previous entry. Applied weighted average cost.")
                
            else:
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
                st.success(f"➕ Added {selected_product} to bill.")


# --- 6. REVIEW AND SAVE ---
if st.session_state.bill_items:
    st.header("3. Bill Review")
    df_bill = pd.DataFrame(st.session_state.bill_items)
    st.dataframe(df_bill[['Material', 'Qty_Purchase', 'Unit_Purchase', 'Total_Item_Cost']])
    
    st.metric("Total Bill Amount (Incl. 13% VAT)", f"{df_bill['Total_Item_Cost'].sum():,.2f}")

    if st.button("💾 Save Final Bill & Update Costings"):
        try:
            purchases_sheet = sh.worksheet("Purchases")
            existing_data = purchases_sheet.get_all_records()
            df_existing = pd.DataFrame(existing_data)
            df_new = pd.DataFrame(st.session_state.bill_items)
            
            if not df_existing.empty:
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                df_combined = df_combined.drop_duplicates(subset=['Material'], keep='last')
            else:
                df_combined = df_new
                
            df_combined_clean = df_combined.fillna("")
            data_to_write = [df_combined_clean.columns.values.tolist()] + df_combined_clean.values.tolist()
            
            purchases_sheet.clear() 
            purchases_sheet.update(values=data_to_write, range_name="A1")
            
            st.success("✅ Sheet updated! Old costings were removed and new costings were saved.")
            st.balloons()
            st.session_state.bill_items = [] 
            st.rerun()
            
        except Exception as e:
            st.error(f"Save failed: {e}")
