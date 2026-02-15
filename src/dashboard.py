import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from src.data_loader import get_reference_and_production_batch
import yaml

st.set_page_config(page_title="Data Drift Monitor",layout="wide")

def load_config():
    with open("config.yaml","r") as f:
        return yaml.safe_load(f)

def get_latest_report(report_dir):
    reports=sorted([f for f in os.listdir(report_dir) if f.endswith('.json')])
    return os.path.join(report_dir,reports[-1]) if reports else None

st.title("Data Drift Monitoring Dashboard")
config=load_config()
report_path=get_latest_report(config['paths']['report_output'])

if not report_path:
    st.error("no drift report found")
    st.stop()

with open(report_path,"r") as f:
    drift_data=json.load(f)

drifted_featues=[k for k,v in drift_data.items() if v['drift']]
total_features=len(drift_data)

m1,m2,m3=st.columns(3)
m1.metric("feature Monitored",total_features)
m2.metric("drifted features",len(drifted_featues),delta=len(drifted_featues),delta_color="inverse")
m3.metric("Status","CRITICAL" if drifted_featues else "HEALTHY")

st.subheader("Detailed Drift Report")
results_df=pd.DataFrame.from_dict(drift_data,orient='index')

st.dataframe(results_df.style.map(lambda x: 'background-color: #ff4b4b' if x is True else '', subset=['drift']))

st.subheader("Feature Distribution Comparison")
selected_feature=st.selectbox("Select a feature to visualize shift",drift_data.keys())

ref_df,prod_df=get_reference_and_production_batch(
    config['paths']['reference_data'],
    os.path.join(config['paths']['production_dir'], sorted(os.listdir(config['paths']['production_dir']))[-1])
)

if selected_feature:
    fig=go.Figure()

    fig.add_trace(go.Histogram(
        x=ref_df[selected_feature],
        name='Reference(Training)',
        marker_color='#3366CC',
        opacity=0.6
    ))
    fig.add_trace(go.Histogram(
        x=prod_df[selected_feature],
        name='Production(Live)',
        marker_color='#FF9900',
        opacity=0.6
    ))
    fig.update_layout(
        barmode='overlay',
        title=f"distribution shift for : {selected_feature}",
        xaxis_title="Value",
        yaxis_title="Frequency",
        template="plotly_white"
    )

    st.plotly_chart(fig,use_container_width=True)
    
    info=drift_data[selected_feature]
    if info['drift']:
        st.error(f"ALERT: {selected_feature} has drifted! ({info['metric']}={info['value']:.4f}) ")
    else:
        st.success(f"{selected_feature} is stable")

