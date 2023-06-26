import streamlit as st
import pandas as pd
import ast
from rapidfuzz import fuzz

st.set_page_config(page_title="Digitálny ŠVP", page_icon=":school:")

@st.cache_data()
def load_standardy():
    """
    sheets_url = st.secrets["public_gsheets_url"]
    """
    sheets_url = st.secrets["public_gsheets_url"]  # existujú dva tvary
    csv_url = sheets_url.replace("edit?usp=sharing", f"gviz/tq?tqx=out:csv&sheet=vzdelavacie_standardy")
    df = pd.read_csv(csv_url).set_index('id')
    df['definicia'] = df['definicia_nova_po_korekture']
    return df


def standardy_as_items_with_id(standardy):
    """Zobrazí štandardy ako odrážky."""
    text = ''
    if len(standardy) == 1:
        text = standardy.iloc[0]
        text = text[0].capitalize() + text[1:] + '.'
    else:
        for i, standard in standardy.items():
            text += f"- {standard}\n"
    st.markdown(text, unsafe_allow_html=True)

def divide_by_typ_standardu(df):
    typy_standardov = df.typ_standardu.dropna().unique().tolist()
    if (len(typy_standardov) > 0):
        for typ_standardu in typy_standardov:  # cinnost, pojem
            st.markdown(f'###### {typ_standardu}')
            standardy_as_items_with_id(
                df.loc[df.typ_standardu == typ_standardu, "definicia"])
    else:
        standardy_as_items_with_id(df["definicia"])

# definícia predmetov
vos = {'Jazyk a komunikácia - prvý jazyk': ['Slovenský jazyk a literatúra', 'Maďarský jazyk a literatúra',
                                            'Nemecký jazyk a literatúra', 'Rómsky jazyk a literatúra',
                                            'Rusínsky jazyk a literatúra', 'Ruský jazyk a literatúra',
                                            'Ukrajinský jazyk a literatúra'],
       'Jazyk a komunikácia - druhý jazyk': ['Slovenský jazyk a slovenská literatúra',
                                            'Slovenský jazyk ako druhý jazyk'],
       'Jazyk a komunikácia - cudzí jazyk': ['Cudzí jazyk'],
       'Matematika a informatika': ['Matematika', 'Informatika'],
       'Človek a príroda': [],
       'Človek a spoločnosť': ['Človek a spoločnosť', 'Náboženstvo Cirkvi bratskej',
                               'Náboženstvo Gréckokatolíckej cirkvi', 'Náboženstvo Pravoslávnej cirkvi',
                               'Náboženstvo Reformovanej kresťanskej cirkvi', 'Náboženstvo Rímskokatolíckej cirkvi',
                               'Náboženstvo Evanjelickej cirkvi a. v.'],
       'Človek a svet práce': [],
       'Umenie a kultúra': ['Hudobná výchova', 'Výtvarná výchova'],
       'Zdravie a pohyb': []}

# definícia skratiek pre id
predmety_kody = {'Slovenský jazyk a literatúra': 'sk',
    'Maďarský jazyk a literatúra':'hu',
    'Nemecký jazyk a literatúra':'de',
    'Rómsky jazyk a literatúra':'ry',
    'Rusínsky jazyk a literatúra':'ri',
    'Ruský jazyk a literatúra':'ru',
    'Ukrajinský jazyk a literatúra':'uk',
    'Slovenský jazyk a slovenská literatúra':'sj',
    'Slovenský jazyk ako druhý jazyk':'dj',
    'Cudzí jazyk':'cj',
    'Matematika':'mt',
    'Informatika':'if',
    'Človek a spoločnosť':'cs',
    'Človek a príroda': 'cp',
    'Človek a svet práce': 'sp',
    'Hudobná výchova':'hv',
    'Výtvarná výchova':'vv',
    'Zdravie a pohyb': 'zp'}

predmety_vykony_pod_cielmi = ['Človek a príroda', 'Informatika', 'Matematika', 'Človek a spoločnosť']
predmety_ciele_pod_komponentmi = ['Slovenský jazyk a literatúra']

df = load_standardy()

# vyber predmet a cyklus
# predmety = df.predmet.unique()
cykly = [1, 2, 3]
tabs_cykly = {'cyklus 1 (r.1-3)': 1, 'cyklus 2 (r.4-5)':2, 'cyklus 3 (r.6-9)':3}

st.sidebar.markdown('# Digitálny ŠVP')

query = st.sidebar.text_input('Vyhľadávanie', '', key=1)

if query:
    df["res"] = [fuzz.token_set_ratio(t, query) for t in df.definicia]  # TODO use processes
    df = df.sort_values("res", ascending=False)
    st.dataframe(df.loc[df.res > 50, ['predmet', 'definicia', 'typ', 'cyklus']], use_container_width=True)
else:
    vo = st.sidebar.selectbox('Vzdelávacia oblasť', vos)
    if vos[vo]:
        predmet = st.sidebar.selectbox('Predmet', vos[vo])  # label_visibility='collapsed'
    else:
        predmet = vo

    if predmet in predmety_vykony_pod_cielmi:
        ciele_a_vykony_su_nezavisle = True
    else:
        ciele_a_vykony_su_nezavisle = False

    if predmet == 'Slovenský jazyk ako druhý jazyk':
        tabs_cykly = {'Komunikačná úroveň 1 (základná)':1, 'Komunikačná úroveň 2 (rozširujúca)': 2}
    elif predmet == 'Cudzí jazyk':
        tabs_cykly = {'cyklus 1 (r.1-3)': 1, 'cyklus 2 (r.4-5)': 2, 'cyklus 3 - prvý jazyk (r.6-9)': 3, 'cyklus 3 - druhý jazyk (r.6-9)': 4}

    cyklus = tabs_cykly[st.sidebar.selectbox('Cyklus', tabs_cykly.keys())]

    # výber dát
    idx = df.index.str.contains(f'{predmety_kody[predmet]}{cyklus}')
    dfx = df[idx]  # (df.cyklus == cyklus) & (df.predmet == predmet)]

    hlavny_ciel = dfx.loc[dfx.index.str.contains('-hc-'),"definicia"]
    if not hlavny_ciel.empty:
        st.sidebar.info(hlavny_ciel[0])

    komponenty = dfx[dfx.index.str.contains('-o-')].komponent.dropna().unique().tolist()

    st.markdown(f'###  {predmet} - {cyklus}. cyklus')
    st.markdown("##### Ciele")
    ciel = st.selectbox('Cieľ', dfx.loc[dfx.index.str.contains("-c-"), "definicia"], index=0,
                        label_visibility='collapsed')

    if ciele_a_vykony_su_nezavisle:
        with st.expander(f"Výkonové štandardy k cieľu"):
            prepojenia = dfx.loc[dfx.definicia == ciel, "prepojenia"]
            prepojenie_vs = ast.literal_eval(prepojenia.iloc[0])
            standardy_as_items_with_id(dfx.loc[prepojenie_vs, "definicia"])

        st.markdown("\n")

    st.markdown("##### Obsahové štandardy pre komponenty")

    if (predmet == 'Človek a príroda') & (cyklus == 3):
        options = st.multiselect('Ktoré predmety ťa zaujímajú?',
                             ['Fyzika', 'Chémia', 'Biológia'],
                             ['Fyzika', 'Chémia', 'Biológia'])

        if 'Chémia' in options:
            i_ch = dfx.definicia.str.contains('<sup>CH</sup>')
        else:
            i_ch = dfx.definicia.str.contains('xxxx')  # TODO all false
        if 'Fyzika' in options:
            i_f = dfx.definicia.str.contains('<sup>F</sup>')
        else:
            i_f = dfx.definicia.str.contains('xxxx')
        if 'Biológia' in options:
            i_b = dfx.definicia.str.contains('<sup>B</sup>')
        else:
            i_b = dfx.definicia.str.contains('<xxxx')
        dfx = dfx[i_ch | i_b | i_f]

    tabs_komponenty = st.tabs(komponenty)

    for komponent, tab_komponent in zip(komponenty, tabs_komponenty):
        with tab_komponent:
            if not ciele_a_vykony_su_nezavisle:
                # with st.expander("Ciele"):
                #     dfy = dfx[dfx.index.str.contains('-c-')]
                #     standardy_as_items_with_id(dfy["definicia"])
                with st.expander("Výkonový štandard"):
                    dfy = dfx[(dfx.komponent == komponent) & dfx.index.str.contains('-v-')]
                    if dfy.empty:
                        dfy = dfx[dfx.index.str.contains('-v-')]
                    divide_by_typ_standardu(dfy)
                    # standardy_as_items_with_id(dfy["definicia"])
            # obsahove standardy

            dfy = dfx[(dfx.komponent == komponent) & dfx.index.str.contains('-o-')]

            # téma obsahového štandardu
            temy = dfy.tema.dropna().unique().tolist()
            if len(temy) > 0:
                for tema in temy:
                    with st.expander(f'Téma: {tema}'):
                        dfl = dfy[dfy.tema == tema]
                        divide_by_typ_standardu(dfl)
            else:  # nemá témy
                if not ciele_a_vykony_su_nezavisle:
                    with st.expander("Obsahový štandard", expanded=True):
                        divide_by_typ_standardu(dfy)
                else:
                    divide_by_typ_standardu(dfy)
