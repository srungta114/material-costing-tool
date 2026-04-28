import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 1. Credentials Dictionary (Missing 'b' has been restored!)
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

# 2. Authenticate directly
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(gsheet_creds, scopes=scopes)
    client = gspread.authorize(creds)
    
    # 3. Open the Sheet
    SHEET_ID = "1ZTI3G97SSOcowXJyHpncFFSlGyS5VSLJublqLpAxVIk"
    sh = client.open_by_key(SHEET_ID)
except Exception as e:
    st.error(f"Authentication Failed: {e}")
    st.stop()

# 4. Helper function to load your data
@st.cache_data(ttl=60)
def load_products():
    worksheet = sh.worksheet("Product_Master")
    return pd.DataFrame(worksheet.get_all_records())

df_master = load_products()
df_master.columns = df_master.columns.str.strip()

# ---- REST OF YOUR APP UI CODE GOES BELOW THIS LINE ----# Rest of your code follows...
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
        try:
            # 1. Target your specific 'Purchases' tab
            # Ensure your Google Sheet has a tab named exactly this!
            purchases_sheet = sh.worksheet("Purchases")
            
            # 2. Convert the pandas DataFrame into a raw list of lists
            # We fill any empty cells with blank text so Google Sheets doesn't crash
            df_bill_clean = df_bill.fillna("")
            data_to_append = df_bill_clean.values.tolist()
            
            # 3. Append the rows instantly to the bottom of the sheet
            purchases_sheet.append_rows(data_to_append)
            
            st.success("✅ Bill successfully recorded in Google Sheets!")
            st.balloons()
            st.session_state.bill_items = [] # Clear the app memory for the next bill
            st.rerun()
            
        except Exception as e:
            st.error(f"Save failed: {e}")
