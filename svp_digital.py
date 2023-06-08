import streamlit as st
import pandas as pd

@st.cache_data()
def load_standardy():
    """
    sheets_url = st.secrets["public_gsheets_url"]
    """
    sheets_url = st.secrets["public_gsheets_url"]  # existujú dva tvary
    csv_url = sheets_url.replace("edit?usp=sharing", f"gviz/tq?tqx=out:csv&sheet=vzdelavacie_standardy")
    df = pd.read_csv(csv_url).set_index('id')
    # df.index.str[:2].isin(['hu', 'de', 'ry', 'ri', 'ru', 'uk'])
    return df


def standardy_as_items_with_id(standardy):
    """Zobrazí štandardy ako odrážky."""
    text = ''
    for i, standard in standardy.items():
        # text += f"- {standard} [{i}] \n"  # s id
        text += f"- {standard}\n"
    st.markdown(text)

vos = {'Jazyk a komunikácia - prvý jazyk': ['Slovenský jazyk a literatúra', 'Maďarský jazyk a literatúra', 'Nemecký jazyk a literatúra', 'Rómsky jazyk a literatúra', 'Rusínsky jazyk a literatúra', 'Ruský jazyk a literatúra', 'Ukrajinský jazyk a literatúra'],
        'Jazyk a komunikácia - druý jazyk': ['Slovenský jazyk a slovenská literatúra', 'Slovenský jazyk ako druhý jazyk'],
        'Jazyk a komunikácia - cudzí jazyk': ['Cudzí jazyk'],
        'Matematika a informatika': ['Matematika', 'Informatika'],
        'Človek a príroda': [],
        'Človek a spoločnosť': [],
        'Človek a svet práce': [],
        'Umenie a kultúra': ['Hudobná výchova', 'Výtvarná výchova'],
        'Zdravie a pohyb': []}

df = load_standardy()

# vyber predmet a cyklus
# predmety = df.predmet.unique()
cykly = [1, 2, 3]
tabs_cykly = ['cyklus 1 (r.1-3)', 'cyklus 1 (r.4-6)', 'cyklus 3 (r.6-9)']

st.markdown('### Digitálny ŠVP')

vo = st.selectbox('Vzdelávacia oblasť', vos)
if vos[vo]:
    predmet = st.selectbox('Predmet', vos[vo])  # label_visibility='collapsed'
else:
    predmet = vo

tabs_cykly = st.tabs(tabs_cykly)  # [f'cyklus {c}' for c in cykly]

# vyber ciele pre predmet a cyklus
for cyklus, tab_cyklus in zip(cykly, tabs_cykly):
    with tab_cyklus:
        dfx = df[(df.cyklus == cyklus) & (df.predmet == predmet)]
        komponenty = dfx.komponent.dropna().unique().tolist()

        tabs_komponenty = st.tabs(komponenty)

        for komponent, tab_komponent in zip(komponenty, tabs_komponenty):
            with tab_komponent:
                with st.expander("Ciele"):
                    dfy = dfx[dfx.index.str.contains('-c-')]
                    standardy_as_items_with_id(dfy["definicia_nova_po_korekture"])
                with st.expander("Výkonový štandard"):
                    dfy = dfx[(dfx.komponent == komponent) & dfx.index.str.contains('-v-')]
                    standardy_as_items_with_id(dfy["definicia_nova_po_korekture"])
                # obsahove standardy
                dfy = dfx[(dfx.komponent == komponent) & dfx.index.str.contains('-o-')]
                # téma obsahového štandardu
                temy = dfy.tema..dropna().unique().tolist()
                # if len(temy) > 1:
                #     tabs_temy = st.tabs(temy)
                #     for tema, tab_tema in zip(temy, tabs_temy):
                #         with tab_tema:
                #             dfl = dfy[dfy.tema == tema]
                #             standardy_as_items_with_id(dfl["definicia_nova_po_korekture"])
                if len(temy) > 1:
                    for tema in temy:
                        with st.expander(f'Obsahový štandard: {tema}'):
                            dfl = dfy[dfy.tema == tema]
                            typy_temy = dfl.typ_standardu.dropna().unique().tolist()
                            if len(typy_temy) > 1:  # ma typy tem
                                for typ_temy in typy_temy:
                                    dfl = dfl[dfl.typ_standardu == typ_temy]
                                    st.markdown('\n')
                                    st.markdown(f'##### {typ_temy}')
                                    standardy_as_items_with_id(dfl["definicia_nova_po_korekture"])
                            else:
                                standardy_as_items_with_id(dfl["definicia_nova_po_korekture"])
                else:  # nemá témy
                    with st.expander("Obsahový štandard"):
                        standardy_as_items_with_id(dfy["definicia_nova_po_korekture"])
