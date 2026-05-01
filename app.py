import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Actuarial Pricing Model", layout="wide", page_icon="📈")

# Custom CSS for "Financial Emerald & Slate" Theme
st.markdown("""
<style>
.big-font {font-size: 32px !important; color: #064E3B; font-weight: bold;}
.metric-box {
    background-color: #ECFDF5; 
    padding: 20px; 
    border-radius: 10px; 
    border-left: 6px solid #059669;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.metric-title { font-weight: 600; color: #064E3B; font-size: 16px; }
.metric-value { font-size: 28px; color: #059669; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Data Loading & Preprocessing
@st.cache_data
def load_data():
    df = pd.read_csv("Thai_Life_Table_Data_Complete.csv")
    # Mapping Thai values to English for the engine to process seamlessly
    df['Gender'] = df['เพศ'].map({'หญิง': 'Female', 'ชาย': 'Male'})
    df['qx'] = df['1000q(x)'] / 1000
    return df

df_life = load_data()

# 3. Sidebar Parameters
st.sidebar.title("⚙️ Parameters")
gender_input = st.sidebar.selectbox("Gender", ["Female", "Male"])
age_input = st.sidebar.slider("Entry Age", 0, 80, 30)
interest_rate = st.sidebar.slider("Interest Rate (%)", 1.0, 10.0, 3.0, 0.1) / 100
sum_assured = st.sidebar.number_input("Sum Assured (THB)", min_value=100000, value=1000000, step=100000)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Scenario Analysis")
death_age = st.sidebar.slider("Simulated Age of Death", age_input + 1, 99, 60)

# 4. Actuarial Calculation Engine
def calculate_model(df, gender, age, i, S):
    # Filter by mapped English gender and age
    df_calc = df[(df['Gender'] == gender) & (df['อายุ'] >= age)].copy()
    if df_calc.empty: return 0, pd.DataFrame()
    
    lx_start = df_calc['l(x)'].iloc[0]
    df_calc['k'] = np.arange(len(df_calc))
    df_calc['v_k_plus_1'] = 1 / ((1 + i) ** (df_calc['k'] + 1))
    df_calc['prob_die'] = df_calc['d(x)'] / lx_start
    df_calc['PV_Benefit'] = S * df_calc['v_k_plus_1'] * df_calc['prob_die']
    
    return df_calc['PV_Benefit'].sum(), df_calc

nsp, df_result = calculate_model(df_life, gender_input, age_input, interest_rate, sum_assured)

# 5. Main Dashboard UI
st.markdown('<p class="big-font">Whole Life Insurance Pricing Model</p>', unsafe_allow_html=True)

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Net Single Premium</div><div class="metric-value">฿ {nsp:,.2f}</div></div>', unsafe_allow_html=True)
with col2:
    life_exp = df_result['e°(x)'].iloc[0]
    st.markdown(f'<div class="metric-box"><div class="metric-title">Life Expectancy</div><div class="metric-value">{life_exp:.2f} Years</div></div>', unsafe_allow_html=True)
with col3:
    years_invested = death_age - age_input
    pv_at_death = sum_assured / ((1 + interest_rate) ** years_invested)
    st.markdown(f'<div class="metric-box"><div class="metric-title">PV of Benefit at Age {death_age}</div><div class="metric-value">฿ {pv_at_death:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📈 Discounted Cash Flow (Risk Exposure)")

# Chart rendering with Emerald color
chart_data = df_result.set_index('อายุ')[['PV_Benefit']]
st.area_chart(chart_data, color="#059669")
