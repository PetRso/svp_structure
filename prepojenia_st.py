# -*- coding: utf-8 -*-
"""
Created on Fri May 12 12:50:35 2023

@author: peter.raso
"""

import streamlit as st
import pandas as pd
import re
import ast

# @st.cache()
# def read_data():
#     df_prierez = pd.read_excel('standardy_prierez_gram.xlsx').set_index('id')
#     df = pd.read_excel('standardy_s_prepojeniami.xlsx').set_index('id')
#     df.cyklus = df.cyklus.astype(str)
#     return df_prierez, df


@st.cache_data()
def load_data(sheet_name):
    """
    sheets_url = st.secrets["public_gsheets_url"]
    """
    sheets_url = st.secrets["public_gsheets_url"]  # existujú dva tvary
    csv_url = sheets_url.replace("edit?usp=sharing", f"gviz/tq?tqx=out:csv&sheet=vzdelavacie_standardy")
    df = pd.read_csv(csv_url).set_index('id')
    csv_url = sheets_url.replace("edit?usp=sharing", f"gviz/tq?tqx=out:csv&sheet=prierezove_gramotnosti_reduced")
    df_prierez = pd.read_csv(csv_url).set_index('id')
    return df_prierez, df


def standardy_as_items_with_id(standardy, prierez_gram=None):
    """Zobrazí štandardy ako odrážky."""
    text = ''
    for i, standard in standardy.items():
        text += f"- {standard} [{i}] \n"
        if not prierez_gram.empty:
            for j, prierez in prierez_gram.items():
                text += f"    - _{prierez} [{j}]_ \n"
    st.markdown(text)


df_prierez, df = load_data()  #read_data

# vyber predmet a cyklus
predmety = df.predmet.unique()
cykly = df.cyklus.unique()

st.markdown('#### Prepojenia ŠVP')
st.caption('Prepojenia boli vytvorené open-source jazykovým modelom.')
# st.divider()

colPredmet, colCyklus = st.columns(2)
with colPredmet:
    predmet = st.selectbox('Predmet', predmety)  # label_visibility='collapsed'
with colCyklus:
    cyklus = st.selectbox('Cyklus', cykly)

# vyber ciele pre predmet a cyklus
i = (df.cyklus == cyklus) & (df.predmet == predmet) & (df.index.str.contains("-c-"))
ciel = st.selectbox('Cieľ', df.loc[i,"definicia"], index=0)
ciel = df[i & (df.definicia == ciel)]  # s indexom a zaradenim

if len(ciel) > 1:
    st.write('Warning: Vo výbere existuje viac cieľov.')

# zobraz prepojenia na vykonov na ciele
# prierezove gramotnosti ostanu pod cykonmi alebo cielami
st.markdown("##### Cieľ")
prierezove_gram = ast.literal_eval(ciel["prepojenie_prierez"].iloc[0])
standardy_as_items_with_id(ciel["definicia"], df_prierez.loc[prierezove_gram, "definicia"])

st.markdown("##### Prepojenia na výkonové štandardy")
prepojenie_vs = ast.literal_eval(ciel['prepojenie_vykon_ciele'].iloc[0])

for prep in prepojenie_vs:
    print('a')
    prepoj_prierez = df.loc[prep, "prepojenie_prierez"]  # ciele aj vykony
    prepoj_prierez = ast.literal_eval(prepoj_prierez)
    standardy_as_items_with_id(df.loc[[prep], "definicia"], df_prierez.loc[prepoj_prierez, "definicia"])


# !streamlit run prepojenia_st.py
