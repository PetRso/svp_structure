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
    # df.index.str[:2].isin(['hu', 'de', 'ry', 'ri', 'ru', 'uk'])
    return df


def standardy_as_items_with_id(standardy):
    """Zobrazí štandardy ako odrážky."""
    text = ''
    if len(standardy) == 1:
        text = standardy.iloc[0]
        text = text.capitalize() + '.'
    else:
        for i, standard in standardy.items():
            # text += f"- {standard} [{i}] \n"  # s id
            text += f"- {standard}\n"
    st.markdown(text)

vos = {'Jazyk a komunikácia - prvý jazyk': ['Slovenský jazyk a literatúra', 'Maďarský jazyk a literatúra', 'Nemecký jazyk a literatúra', 'Rómsky jazyk a literatúra', 'Rusínsky jazyk a literatúra', 'Ruský jazyk a literatúra', 'Ukrajinský jazyk a literatúra'],
        'Jazyk a komunikácia - druý jazyk': ['Slovenský jazyk a slovenská literatúra', 'Slovenský jazyk ako druhý jazyk'],
        'Jazyk a komunikácia - cudzí jazyk': ['Cudzí jazyk'],
        'Matematika a informatika': ['Matematika', 'Informatika'],
        'Človek a príroda': [],
        'Človek a spoločnosť': ['Človek a spoločnosť', 'Náboženstvo Cirkvi bratskej', 'Náboženstvo Gréckokatolíckej cirkvi', 'Náboženstvo Pravoslávnej cirkvi',
       'Náboženstvo Reformovanej kresťanskej cirkvi', 'Náboženstvo Rímskokatolíckej cirkvi', 'Náboženstvo Evanjelickej cirkvi a. v.'],
        'Človek a svet práce': [],
        'Umenie a kultúra': ['Hudobná výchova', 'Výtvarná výchova'],
        'Zdravie a pohyb': []}

predmety_vykony_pod_cielmi = ['Človek a príroda', 'Informatika', 'Matematika', 'Človek a spoločnosť']
predmety_ciele_pod_komponentmi = ['Slovenský jazyk a literatúra']

df = load_standardy()

# vyber predmet a cyklus
# predmety = df.predmet.unique()
cykly = [1, 2, 3]
tabs_cykly = ['cyklus 1 (r.1-3)', 'cyklus 2 (r.4-5)', 'cyklus 3 (r.6-9)']

st.markdown('### Digitálny ŠVP')

query = st.sidebar.text_input('Vyhľadávanie', '', key=1)

if query:
    df["res"] = [fuzz.token_set_ratio(t, query) for t in df.definicia]  # TODO use processes
    df = df.sort_values("res", ascending=False)
    st.dataframe(df.loc[df.res > 50, ['predmet','definicia', 'typ', 'cyklus']], use_container_width=True)
else:
    col1, col2 = st.columns(2)
    with col1:
        vo = st.selectbox('Vzdelávacia oblasť', vos)
    with col2:
        if vos[vo]:
            predmet = st.selectbox('Predmet', vos[vo])  # label_visibility='collapsed'
        else:
            predmet = vo

    if predmet in predmety_vykony_pod_cielmi:
        ciele_a_vykony_su_nezavisle = True
    else:
        ciele_a_vykony_su_nezavisle = False

    tabs_cykly = st.tabs(tabs_cykly)  # [f'cyklus {c}' for c in cykly]

    # vyber ciele pre predmet a cyklus
    for cyklus, tab_cyklus in zip(cykly, tabs_cykly):
        with tab_cyklus:
            st.markdown("\n")

            dfx = df[(df.cyklus == cyklus) & (df.predmet == predmet)]
            komponenty = dfx.komponent.dropna().unique().tolist()

            st.markdown("##### Ciele")
            ciel = st.selectbox('Cieľ', dfx.loc[dfx.index.str.contains("-c-"), "definicia"], index=0, label_visibility='collapsed')
            
            if ciele_a_vykony_su_nezavisle:
                with st.expander(f"Výkonové štandardy k cieľu"):
                    prepojenia = dfx.loc[dfx.definicia == ciel, "prepojenia"]
                    prepojenie_vs = ast.literal_eval(prepojenia.iloc[0])
                    standardy_as_items_with_id(dfx.loc[prepojenie_vs, "definicia"])

                st.markdown("\n")
                st.markdown("##### Obsahové štandardy pre komponenty")
            else:
                st.markdown("##### Komponenty")

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
                            standardy_as_items_with_id(dfy["definicia"])
                    # obsahove standardy
                    dfy = dfx[(dfx.komponent == komponent) & dfx.index.str.contains('-o-')]
                    # téma obsahového štandardu
                    temy = dfy.tema.dropna().unique().tolist()
                    if len(temy) > 1:
                        for tema in temy:
                            with st.expander(f'Obsahový štandard: {tema}'):
                                dfl = dfy[dfy.tema == tema]
                                typy_temy = dfl.typ_standardu.dropna().unique().tolist()
                                if len(typy_temy) > 1:  # ma typy tem
                                    for typ_temy in typy_temy:
                                        dftyp = dfl[dfl.typ_standardu == typ_temy]
                                        st.markdown('\n')
                                        st.markdown(f'###### {typ_temy}')
                                        typy_standardov = dftyp.typ_standardu.unique().tolist()
                                        if len(typy_standardov) > 1:  # TOTO opaku je sa to
                                            for typ_standardu in typy_standardov:  # cinnost, pojem
                                                st.markdown(f'####### {typ_standardu}')
                                                standardy_as_items_with_id(dftyp.loc[dftyp.typ_standardu == typ_standardu, "definicia"])
                                        else:
                                            standardy_as_items_with_id(dftyp["definicia"])
                                else:
                                    typy_standardov = dfl.typ_standardu.unique().tolist()
                                    if len(typy_standardov) > 1:
                                        for typ_standardu in typy_standardov:  # cinnost, pojem
                                            st.markdown(f'####### {typ_standardu}')
                                            standardy_as_items_with_id(dfl.loc[dfl.typ_standardu == typ_standardu, "definicia"])
                                    else:
                                        standardy_as_items_with_id(dftyp["definicia"])
                    else:  # nemá témy
                        if not ciele_a_vykony_su_nezavisle:
                            with st.expander("Obsahový štandard", expanded=True):
                                typy_standardov = dfy.typ_standardu.unique().tolist()
                                if len(typy_standardov) > 1:
                                    for typ_standardu in typy_standardov:  # cinnost, pojem
                                        st.markdown(f'####### {typ_standardu}')
                                        standardy_as_items_with_id(dfy.loc[dfl.typ_standardu == typ_standardu, "definicia"])
                                else:
                                    standardy_as_items_with_id(dfy["definicia"])
                        else:
                            typy_standardov = dfy.typ_standardu.unique().tolist()
                            if len(typy_standardov) > 1:
                                for typ_standardu in typy_standardov:  # cinnost, pojem
                                    st.markdown(f'####### {typ_standardu}')
                                    standardy_as_items_with_id(dfy.loc[dfl.typ_standardu == typ_standardu, "definicia"])
                            else:
                                standardy_as_items_with_id(dfy["definicia"])
