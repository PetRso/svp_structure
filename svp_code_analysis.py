import streamlit as st
import pandas as pd


@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("edit?usp=sharing", "gviz/tq?tqx=out:csv&sheet_name=Sheet1")
    return pd.read_csv(csv_url)

df = load_data(st.secrets["public_gsheets_url"])


