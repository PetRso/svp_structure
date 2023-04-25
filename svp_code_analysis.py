"""
Analýza štruktúry vzdelávacieho programu
"""
import streamlit as st
import pandas as pd
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

@st.cache_data(ttl=600)
def load_data(sheet_name):
    """
    sheets_url = st.secrets["public_gsheets_url"]
    """
    sheets_url = st.secrets["public_gsheets_url"]  # existujú dva tvary
    csv_url = sheets_url.replace("edit?usp=sharing", f"gviz/tq?tqx=out:csv&sheet={sheet_name}")
    df = pd.read_csv(csv_url)
    return df


def tranform_data(df):
    df = df.ffill()
    df.kod = df.kod.str.replace(',', ';')
    df.kod = df.kod.str.split(';')  # multiple codes to list
    df = df.explode('kod')  # co kod, to riadok
    df.kod = df.kod.str.strip()
    df['komponent'] = df['komponent'].astype(str)
    df['komponent'] = df['komponent'].str.capitalize()
    df['typ'] = df['typ'].str.capitalize()
    df['definicia'] = df['definicia'].str.replace(r'[-·]', '')
    df['definicia'] = df['definicia'].str.strip()
    return df

@st.cache_data(ttl=600)
def load_more_sheets(sheets):
    """Spojí viac tabuliek do jednej."""
    df = pd.DataFrame()
    for sheet in sheets:
        df_sheet = load_data(sheet)
        df_sheet = tranform_data(df_sheet)
        df = pd.concat([df, df_sheet], ignore_index=True)
    return df


def standardy_as_items(standardy, cast=None):
    """Zobrazí štandardy ako odrážky."""
    for standard in standardy:
        standard = re.sub("[-·]", "", standard)
        if cast:
            st.markdown(f"- {standard} [{cast}]")
        else:  # vykonovy standard
            st.markdown(f"- {standard}")
    # st.markdown("\n")


def word_cloud(kody):
    wordcloud = WordCloud().generate(kody)
    plt.figure(figsize=(8, 8), facecolor=None)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    st.pyplot(plt)

# Výber predmetu a cyklu
predmety = {'Slovenský jazyk a literatúra': 'SJL', "Matematika": 'MAT'}

# Selector
# st.subheader('Analýza štruktúry ŠVP')
colPredmet, colCyklus = st.columns(2)
with colPredmet:
    sheet = st.selectbox('Predmet', predmety.keys(), label_visibility='collapsed')  # sheet = 'Matematika'
with colCyklus:
    cyklus = st.selectbox('Cyklus', ['1.cyklus', '2.cyklus', '3.cyklus'], label_visibility='collapsed', index=0)
# kodovanie = st.selectbox('Kodovanie', ['Kódovanie pomocou kľúčových slov (kod)', 'Kódovanie pomocou identifikátorov (prepojenie_id)'], label_visibility='collapsed', index=0)


df = load_data(predmety[sheet])  # df = load_data('MAT')
df_prierez = load_data('Prierezove_gramotnosti')

# if kodovanie == 'Kódovanie pomocou identifikátorov (prepojenie_id)':
#     df["kod"] = df['id'].fillna('') + '; ' + df['prepojenie_id'].fillna('')
#     df_prierez["kod"] = df_prierez['id'].fillna('') + '; ' + df_prierez['prepojenie_id'].fillna('')
#     df["kod"] = df["kod"].str.strip(r'[; ]')
#     df_prierez["kod"] = df_prierez["kod"].str.strip(r'[; ]')

df = tranform_data(df)
df_prierez = tranform_data(df_prierez)

kody_standardov = list(df.loc[df.typ == 'Výkonový štandard', "kod"].unique())
kody_cielov = list(df.loc[df.typ == 'Ciele vzdelávania', "kod"].unique())

tab1, tab2 = st.tabs(['Analýza štandardov', 'Analýza tagov/kódov'])

with tab1:
    with st.expander("Existujúce prepojenia na cieľ"):
        # doménové gramotnosti - ciele - výkonové štandardy - prierezove gramotnosti
        ciel = st.selectbox(f'Vyber cieľ vzdelávania pre {cyklus}:',
                            df.loc[df.typ == 'Ciele vzdelávania', 'definicia'].unique(),
                            label_visibility='collapsed')
        ciel_kod = df.loc[df['definicia'] == ciel, 'kod']
        st.caption(f'cieľ: {ciel}')
        st.caption(f'kód: {list(ciel_kod)}')

        dfx = df.loc[df['kod'].isin(ciel_kod), ['typ', 'definicia', "komponent"]]
        dfx = dfx.drop_duplicates()
        # dfx['definicia'] = dfx['definicia'] + " (" + dfx['komponent'] + ")"

        casti = list(df.typ.unique())  # ['ciele vzdelávania', 'výkonový štandard', 'Jazyková a komunikačná gramotnosť']
        casti.remove('Ciele vzdelávania')  # ciele uz netreba, mali by mať jedinečné kódy

        st.markdown("##### Výkonové štandardy")
        standardy = list(dfx.loc[dfx.typ == 'Výkonový štandard', 'definicia'])
        standardy_as_items(standardy)

        st.markdown("\n")
        st.markdown("##### Doménové gramotnosti")
        casti.remove('Výkonový štandard')
        # zobraznie definícií a štandardov, každa definicia jeden bod
        for cast in casti:
            # st.write(cast.capitalize())
            standardy = list(dfx.loc[dfx.typ == cast, 'definicia'])
            standardy_as_items(standardy, cast)

        # prierezove gramotnosti
        st.markdown("\n")
        st.markdown("##### Prierezové gramotnosti")
        dfx = df_prierez.loc[df_prierez.kod.isin(list(ciel_kod)), ["typ", "komponent", "definicia"]]
        for gramotnost in dfx.komponent.unique():
            # st.markdown(gramotnost)
            standardy = dfx.loc[dfx.komponent == gramotnost, "definicia"]
            standardy_as_items(standardy, gramotnost)

    # chýbajúce prepojenia výkonov na ciele
    with st.expander("Ktoré ciele nemajú prepojenie na výkonové štandardy?"):
        definicie_vymazat = df.loc[df.kod.isin(kody_standardov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
        dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # ciele a gramotnosti, ktorym chybaju prepojenia na vykony
        dfx = dfx[dfx.typ == 'Ciele vzdelávania']  # iba vykonove standardy
        groups = dfx.groupby('definicia')
        for definicia, row in groups:
            st.markdown(f'- {definicia} {list(row.kod)}')

    with st.expander("Ktoré výkonové štandardy nemajú prepojenie na cieľ?"):
        definicie_vymazat = df.loc[df.kod.isin(kody_cielov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
        dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # standardy a gramotnosti, ktorym chybaju prepojenia
        dfx = dfx[dfx.typ == 'Výkonový štandard']  # iba vykonove standardy
        groups = dfx.groupby('definicia')
        for definicia, row in groups:
            st.markdown(f'- {definicia} {list(row.kod)}')

    # chýbajúce prepojenia doménových gramotností na ciele
    with st.expander("Ktoré doménové gramotnosti nemajú prepojenie na výkonové štandardy?"):
        definicie_vymazat = df.loc[df.kod.isin(kody_standardov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
        dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # ciele a gramotnosti, ktorym chybaju prepojenia na vykony
        dfx = dfx[dfx.typ != 'Ciele vzdelávania']  # iba vykonove standardy
        groups = dfx.groupby('definicia')
        for definicia, row in groups:
            st.markdown(f'- {definicia} {list(row.kod)}')  # ({row.komponent.iloc[0]})')

with tab2:
    with st.expander("Prepojenia pomocou kódov"):  # existujúce prepojenia navzájom

        df_prepojenia = pd.DataFrame({'kod': df.kod.unique()}) # naplni sa
        typy_gramotnost = set(df.loc[df.predmet.str.contains('gramotnos'), "typ"].unique())

        for kod in df.kod.unique():
            existujuce_prepojenia = list(df.loc[df.kod == kod, "typ"].unique())  # ake typy zaznamov existuju pre dany kod
            if 'Výkonový štandard' in existujuce_prepojenia:
                df_prepojenia.loc[df_prepojenia.kod == kod, 'vykon'] = True
            if 'Ciele vzdelávania' in existujuce_prepojenia:
                df_prepojenia.loc[df_prepojenia.kod == kod, 'ciele'] = True
            if any(x in typy_gramotnost for x in existujuce_prepojenia):  # ak
                df_prepojenia.loc[df_prepojenia.kod == kod, 'domenova_gram'] = True
            if kod in list(df_prierez.kod):  #existuje v prierezovej gramotnosti?
                df_prepojenia.loc[df_prepojenia.kod == kod, 'prierez_gram'] = True

        # df_prepojenia["stav"] = df_prepojenia[["vykon", "ciele", "gramotnost"]].all(axis=1, skipna=False)
        st.write(df_prepojenia.set_index('kod'))


    with st.expander("Prepojenia cez vybraný kód"):  # existujúce prepojenia navzájom
        kod = st.selectbox('Vyber kod', df.kod.unique(), label_visibility='collapsed')
        st.markdown("##### Vzdelávacie štandardy a doménová gramotnosť")
        st.write(df.loc[df.kod == kod, ['typ', 'definicia']].set_index('typ'))
        st.markdown("##### Prierezová gramotnosť")
        st.write(df_prierez.loc[df_prierez.kod == kod, ['predmet', 'definicia', 'typ']].set_index('predmet'))


    with st.expander("Kódy - štatistika"):
        col1, col2 = st.columns(2, gap="small")
        with col1:
            st.write(df['kod'].value_counts())
        with col2:
            word_cloud(" ".join(list(df['kod'])))

# todo medizpredmetne vzťahy
# with tab3:
#     sheets = list(predmety.values()) + ["Prierezove_gramotnosti"]
#     df = load_more_sheets(sheets)  # vsetko v jednom
#     # word_cloud(" ".join(list(df['kod'])))
#
#     # x os - prierezove gramotnosti
#     # y os - domenove gramotnosti

