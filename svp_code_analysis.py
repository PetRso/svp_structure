"""
Analýza štruktúry vzdelávacích predmetov

Postup
1. vyberiem predmet a cyklus
2. predmet + doménová gramotnosť
3. predmet + doménová gramotnosť + prierezová gramotnosť

Čo chcem vidieť?
- aké témy (kody) existujú
- Sú všetky štandardy prepojené na gramotnosti alebo ciele?
- doplnok: aké témy sa vyskytujú najčastejšie?

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
    sheets_url = st.secrets["public_gsheets_url"]
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

def kody_statistiky(kody: list):
    kody_pocty = pd.Series(kody).value_counts()
    kody_pocty = kody_pocty.sort_index()
    return kody_pocty

def standardy_as_items(standardy, cast=None):
    for standard in standardy:
        standard = re.sub("[-·]", "", standard)
        if cast:
            st.markdown(f"- {standard} [{cast}]")
        else:  # vykonovy standard
            st.markdown(f"- {standard}")
    # st.markdown("\n")

# select subject
predmety = {'Slovenský jazyk a literatúra': 'SJL', "Matematika": 'MAT'}
sheet = st.selectbox('Predmet', predmety.keys())  # sheet = 'Matematika'
cyklus = st.selectbox('Cyklus', ['1.cyklus', '2.cyklus', '3.cyklus'], label_visibility='collapsed', index=0)
kodovanie = st.selectbox('Kodovanie', ['Kódovanie pomocou kľúčových slov (kod)', 'Kódovanie pomocou identifikátorov (prepojenie_id)'], label_visibility='collapsed', index=0)

# load data
df = load_data(predmety[sheet])  # df = load_data('MAT')
df_prierez = load_data('Prierezove_gramotnosti')

if kodovanie == 'Kódovanie pomocou identifikátorov (prepojenie_id)':
    df["kod"] = df['id'].fillna('') + '; ' + df['prepojenie_id'].fillna('')
    df_prierez["kod"] = df_prierez['id'].fillna('') + '; ' + df_prierez['prepojenie_id'].fillna('')
    df["kod"] = df["kod"].str.strip(r'[; ]')
    df_prierez["kod"] = df_prierez["kod"].str.strip(r'[; ]')

df = tranform_data(df)
df_prierez = tranform_data(df_prierez)

# results
with st.expander("Existujúce prepojenia na cieľ (kontrola prepojení)"):  #todo pridaj prierezove gramot
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
    kody_standardov = list(df.loc[df.typ == 'Výkonový štandard', "kod"].unique())
    definicie_vymazat = df.loc[df.kod.isin(kody_standardov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
    dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # ciele a gramotnosti, ktorym chybaju prepojenia na vykony
    dfx = dfx[dfx.typ == 'Ciele vzdelávania']  # iba vykonove standardy
    groups = dfx.groupby('definicia')
    for definicia, row in groups:
        st.markdown(f'- {definicia} {list(row.kod)}')

with st.expander("Ktoré výkonové štandardy nemajú prepojenie na cieľ?"):
    kody_cielov = list(df.loc[df.typ == 'Ciele vzdelávania', "kod"].unique())
    definicie_vymazat = df.loc[df.kod.isin(kody_cielov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
    dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # standardy a gramotnosti, ktorym chybaju prepojenia
    dfx = dfx[dfx.typ == 'Výkonový štandard']  # iba vykonove standardy
    groups = dfx.groupby('definicia')
    for definicia, row in groups:
        st.markdown(f'- {definicia} {list(row.kod)}')

# chýbajúce prepojenia doménových gramotností na ciele
with st.expander("Ktoré doménové gramotnosti nemajú prepojenie na výkonové štandardy?"):
    kody_standardov = list(df.loc[df.typ == 'Výkonový štandard', "kod"].unique())
    definicie_vymazat = df.loc[df.kod.isin(kody_standardov), 'definicia']  # Vymaz definicie, ktore maju prepojenie na ciel. Staci jedno prepojenie.
    dfx = df[~df.definicia.isin(list(definicie_vymazat))]  # ciele a gramotnosti, ktorym chybaju prepojenia na vykony
    dfx = dfx[dfx.typ != 'Ciele vzdelávania']  # iba vykonove standardy
    groups = dfx.groupby('definicia')
    for definicia, row in groups:
        st.markdown(f'- {definicia} {list(row.kod)}')  # ({row.komponent.iloc[0]})')


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


with st.expander("Prepojenia cez kód"):  # existujúce prepojenia navzájom
    kod = st.selectbox('Vyber kod', df.kod.unique(), label_visibility='collapsed')
    st.markdown("##### Vzdelávacie štandardy a doménová gramotnosť")
    st.write(df.loc[df.kod == kod, ['typ', 'definicia']].set_index('typ'))
    st.markdown("##### Prierezová gramotnosť")
    st.write(df_prierez.loc[df_prierez.kod == kod, ['predmet', 'definicia', 'typ']].set_index('predmet'))


# todo medizpredmetne vzťahy

# with st.expander("Kódy - štatistika"):
#     st.write(df['kod'].value_counts())

    # wordcloud = WordCloud().generate(" ".join(kody))
    # plt.figure(figsize = (8, 8), facecolor = None)
    # plt.imshow(wordcloud)
    # plt.axis("off")
    # plt.tight_layout(pad = 0)
    # st.pyplot(plt)

    ## Ukáž existujúce prepojenia
    # Očakávanie - kody sú v cieľoch, gramotnostiach aj štandardoch

    # charakteristika
    # postojový rámec
    # procesuálny rámec
    # gradácia