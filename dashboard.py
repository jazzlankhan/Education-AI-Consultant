# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from utils import export_leads_to_csv, export_leads_to_excel
import io

st.set_page_config(page_title="Lead Dashboard", layout="wide")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

tab1, tab2, tab3 = st.tabs(["Leads", "Analytics", "API Logs"])

with tab1:
    st.header("All Leads")
    session = Session()
    df = pd.read_sql("SELECT * FROM leads ORDER BY updated_at DESC", engine)

    col1, col2, col3 = st.columns(3)
    with col1:
        csv = export_leads_to_csv(df)
        st.download_button("Download CSV", csv, "leads.csv", "text/csv")
    with col2:
        excel = export_leads_to_excel(df)
        st.download_button("Download Excel", excel, "leads.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col3:
        if st.button("Refresh Data"):
            st.rerun()  # FIXED: Use st.rerun()

    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("Analytics")
    col1, col2 = st.columns(2)

    with col1:
        status_counts = df["status"].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, title="Lead Status")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        cat_counts = df["category"].value_counts().head(5).reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig2 = px.bar(cat_counts, x='Category', y='Count', title="Top Categories")
        st.plotly_chart(fig2, use_container_width=True)

    colm1, colm2 = st.columns(2)
    with colm1:
        st.metric("Total Leads", len(df))
    with colm2:
        st.metric("Hot Leads", len(df[df["status"] == "hot"]))
    # Add to imports
from sqlalchemy import text

# Update tabs: tab1, tab2, tab3 = st.tabs(["Leads", "Analytics", "API Logs"])

with tab3:
    st.header("API & Message Analytics")
    
    # Query logs
    logs_df = pd.read_sql("SELECT * FROM api_logs ORDER BY created_at DESC", engine)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total API Calls", len(logs_df))
    with col2:
        st.metric("Successful Calls", len(logs_df[logs_df['api_success'] == True]))
    with col3:
        st.metric("Failed Calls", len(logs_df[logs_df['api_success'] == False]))

    # Message Stats
    msg_stats = logs_df[logs_df['message_type'].isin(['received', 'replied', 'unanswered'])]
    received = len(msg_stats[msg_stats['message_type'] == 'received'])
    replied = len(msg_stats[msg_stats['message_type'] == 'replied'])
    unanswered = len(msg_stats[msg_stats['message_type'] == 'unanswered'])

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric("Messages Received", received)
    with col5:
        st.metric("Messages Replied", replied)
    with col6:
        st.metric("Unanswered", unanswered)

    # Charts
    col_a, col_b = st.columns(2)
    with col_a:
        api_status = logs_df['api_success'].value_counts().reset_index()
        api_status.columns = ['Success', 'Count']
        fig_api = px.pie(api_status, names='Success', values='Count', title="API Success Rate")
        st.plotly_chart(fig_api, use_container_width=True)

    with col_b:
        msg_types = msg_stats['message_type'].value_counts().reset_index()
        msg_types.columns = ['Type', 'Count']
        fig_msg = px.bar(msg_types, x='Type', y='Count', title="Message Types")
        st.plotly_chart(fig_msg, use_container_width=True)

    # Response Times
    if not logs_df.empty:
        avg_response = logs_df['response_time_ms'].mean()
        st.metric("Avg Response Time (ms)", f"{avg_response:.2f}")

    # Export Logs
    csv_logs = logs_df.to_csv(index=False).encode('utf-8')
    st.download_button("Export API Logs CSV", csv_logs, "api_logs.csv", "text/csv")