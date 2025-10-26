import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Medical Tech ETF Dashboard", layout="wide", page_icon="🏥")

st.title("🏥 Perioperative & Anesthesia Medical Technology ETF")
st.markdown("Real-time portfolio tracking with interactive visualizations")

PORTFOLIO = [
    {'ticker': 'LH', 'name': 'LabCorp', 'allocation': 8, 'sector': 'Diagnostics/Lab'},
    {'ticker': 'TMO', 'name': 'Thermo Fisher Scientific', 'allocation': 10, 'sector': 'Lab Equipment'},
    {'ticker': 'MDT', 'name': 'Medtronic', 'allocation': 10, 'sector': 'Medical Devices'},
    {'ticker': 'BAX', 'name': 'Baxter International', 'allocation': 7, 'sector': 'Perioperative'},
    {'ticker': 'MASI', 'name': 'Masimo Corporation', 'allocation': 6, 'sector': 'Patient Monitoring'},
    {'ticker': 'GEHC', 'name': 'GE HealthCare', 'allocation': 9, 'sector': 'Medical Devices'},
    {'ticker': 'TFX', 'name': 'Teleflex', 'allocation': 5, 'sector': 'Anesthesia Devices'},
    {'ticker': 'ISRG', 'name': 'Intuitive Surgical', 'allocation': 8, 'sector': 'Surgical Robotics'},
    {'ticker': 'SYK', 'name': 'Stryker', 'allocation': 8, 'sector': 'Surgical Equipment'},
    {'ticker': 'ABT', 'name': 'Abbott Laboratories', 'allocation': 7, 'sector': 'Diagnostics/Lab'},
    {'ticker': 'MRK', 'name': 'Merck & Co', 'allocation': 6, 'sector': 'Pharmaceuticals'},
    {'ticker': 'PFE', 'name': 'Pfizer', 'allocation': 4, 'sector': 'Pharmaceuticals'},
    {'ticker': 'ORCL', 'name': 'Oracle', 'allocation': 4, 'sector': 'Healthcare IT'},
    {'ticker': 'VEEV', 'name': 'Veeva Systems', 'allocation': 4, 'sector': 'Healthcare IT'},
]

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

@st.cache_data(ttl=300)
def fetch_portfolio_data():
    data = []
    for stock_info in PORTFOLIO:
        try:
            stock = yf.Ticker(stock_info['ticker'])
            hist = stock.history(period='5d')
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                data.append({
                    'ticker': stock_info['ticker'],
                    'name': stock_info['name'],
                    'sector': stock_info['sector'],
                    'allocation': stock_info['allocation'],
                    'price': current_price,
                    'change_pct': change_pct,
                    'volume': hist['Volume'].iloc[-1]
                })
        except Exception as e:
            st.warning(f"Could not fetch data for {stock_info['ticker']}")
    
    return pd.DataFrame(data)

with st.spinner("Fetching real-time stock data..."):
    df = fetch_portfolio_data()

if not df.empty:
    portfolio_return = (df['change_pct'] * df['allocation'] / 100).sum()
    winners = len(df[df['change_pct'] > 0])
    losers = len(df[df['change_pct'] < 0])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", "$100,000", f"{portfolio_return:+.2f}%")
    with col2:
        st.metric("Daily Return", f"{portfolio_return:+.2f}%")
    with col3:
        st.metric("Winners", winners, f"{winners}/{len(df)}")
    with col4:
        st.metric("Losers", losers, f"{losers}/{len(df)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Allocation")
        fig_allocation = go.Figure(data=[go.Pie(
            labels=df['ticker'],
            values=df['allocation'],
            text=df['name'],
            hovertemplate='<b>%{label}</b><br>%{text}<br>%{value}%<extra></extra>'
        )])
        fig_allocation.update_layout(height=400)
        st.plotly_chart(fig_allocation, use_container_width=True)
    
    with col2:
        st.subheader("Sector Distribution")
        sector_df = df.groupby('sector')['allocation'].sum().reset_index()
        fig_sector = px.pie(sector_df, values='allocation', names='sector', hole=0.4)
        fig_sector.update_layout(height=400)
        st.plotly_chart(fig_sector, use_container_width=True)
    
    st.subheader("Daily Performance")
    df_sorted = df.sort_values('change_pct', ascending=True)
    colors = ['#ef4444' if x < 0 else '#10b981' for x in df_sorted['change_pct']]
    
    fig_performance = go.Figure(data=[go.Bar(
        x=df_sorted['change_pct'],
        y=df_sorted['ticker'],
        orientation='h',
        marker=dict(color=colors),
        text=df_sorted['change_pct'].apply(lambda x: f"{x:+.2f}%"),
        textposition='outside'
    )])
    fig_performance.update_layout(xaxis_title="Change (%)", height=500)
    st.plotly_chart(fig_performance, use_container_width=True)
    
    st.subheader("Portfolio Holdings")
    display_df = df.copy()
    display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}")
    display_df['change_pct'] = display_df['change_pct'].apply(lambda x: f"{x:+.2f}%")
    display_df['allocation'] = display_df['allocation'].apply(lambda x: f"{x}%")
    display_df['volume'] = display_df['volume'].apply(lambda x: f"{x/1e6:.2f}M")
    
    st.dataframe(
        display_df[['ticker', 'name', 'sector', 'price', 'change_pct', 'allocation', 'volume']],
        use_container_width=True,
        hide_index=True
    )
    
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.error("Unable to fetch portfolio data. Please try again.")
