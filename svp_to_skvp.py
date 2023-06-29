import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Rozdelenie štandardov do ročníkov", layout="wide")

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


def format_definicia(text_orig):
    """Funkcia ošetruje viac výkonov v jednom alebo vnorené komponenty."""
    text = ''
    if '::' in text_orig:  # má definíciu napr. aktíva: ...
        text_orig = text_orig.split('::')  # definicia ma v sebe typ napr. mat reprezentacie
        typ = text_orig[0].strip()
        text += f'###### &nbsp;&nbsp;&nbsp;&nbsp;{typ.capitalize()}\n'  # typ definicie
        text_orig = text_orig[1]  # definicia # TODO test, existuje iba jedna :
    text_orig = text_orig.split(';')  # viac standardov v jednom poly
    text_orig = [x.strip() for x in text_orig]
    for txt in text_orig:
        text += f'- {txt}\n'  # .capitalize()
    return text


def standardy_as_items_with_id(standardy):
    """Zobrazí štandardy ako odrážky."""
    if len(standardy) == 1:  # jeden riadok
        text_orig = standardy.iloc[0]
        text = format_definicia(text_orig)
    else:
        text = ''
        for i, text_orig in standardy.items():
            text += format_definicia(text_orig)
    st.markdown(text, unsafe_allow_html=True)


def divide_by_typ_standardu(df):
    typy_standardov = df.typ_standardu.dropna().unique().tolist()
    if (len(typy_standardov) > 0):
        for typ_standardu in typy_standardov:  # cinnost, pojem
            st.markdown(f'\n###### {typ_standardu}')
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
                 'Maďarský jazyk a literatúra': 'hu',
                 'Nemecký jazyk a literatúra': 'de',
                 'Rómsky jazyk a literatúra': 'ry',
                 'Rusínsky jazyk a literatúra': 'ri',
                 'Ruský jazyk a literatúra': 'ru',
                 'Ukrajinský jazyk a literatúra': 'uk',
                 'Slovenský jazyk a slovenská literatúra': 'sj',
                 'Slovenský jazyk ako druhý jazyk': 'dj',
                 'Cudzí jazyk': 'cj',
                 'Matematika': 'mt',
                 'Informatika': 'if',
                 'Človek a spoločnosť': 'cs',
                 'Človek a príroda': 'cp',
                 'Človek a svet práce': 'sp',
                 'Hudobná výchova': 'hv',
                 'Výtvarná výchova': 'vv',
                 'Zdravie a pohyb': 'zp'}

predmety_vykony_pod_cielmi = ['Človek a príroda', 'Informatika', 'Matematika', 'Človek a spoločnosť']
predmety_ciele_pod_komponentmi = ['Slovenský jazyk a literatúra']

df = load_standardy()

# vyber predmet a cyklus
# predmety = df.predmet.unique()
cykly = [1, 2, 3]
tabs_cykly = {'cyklus 1 (r.1-3)': 1} #, 'cyklus 2 (r.4-5)': 2, 'cyklus 3 (r.6-9)': 3}

st.sidebar.markdown('# Rozdelenie ŠVP do ročníkov')

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
    tabs_cykly = {'Komunikačná úroveň 1 (základná)': 1, 'Komunikačná úroveň 2 (rozširujúca)': 2}
elif predmet == 'Cudzí jazyk':
    tabs_cykly = {'cyklus 1 (r.1-3)': 1} # , 'cyklus 2 (r.4-5)': 2, 'cyklus 3 - prvý jazyk (r.6-9)': 3, 'cyklus 3 - druhý jazyk (r.6-9)': 4}
    jazyky = ['Anglický jazyk', 'Francúzsky jazyk', 'Nemecký jazyk', 'Ruský jazyk', 'Španielsky jazyk',
              'Taliansky jazyk']
    jazyk = st.sidebar.selectbox('Jazyk', jazyky)
    jazyky.remove(jazyk)  # iba jazyky, ktore nechcem

cyklus = tabs_cykly[st.sidebar.selectbox('Cyklus', tabs_cykly.keys())]

st.sidebar.warning("Momentálne sa pracuje iba s obsahovými štandardami pre 1.cyklus.")

# výber dát
idx = df.index.str.contains(f'{predmety_kody[predmet]}{cyklus}-o-')
dfx = df[idx]
if predmet == 'Cudzí jazyk':
    dfx = dfx[~dfx.typ_standardu.isin(jazyky)]  # iba pre vybraný jazyk, alebo pre všetky

dfx.loc[:, '1'] = True
dfx.loc[:, '2'] = True
dfx.loc[:, '3'] = True

cols_to_xlsx = ['typ', 'komponent', 'tema', 'typ_standardu']
cols_to_st = ['definicia', '1', '2', '3']

st.info('Označ, ktoré obsahové štandardy sa majú preberať v ktorom ročníku.')
st.data_editor(dfx[cols_to_st], hide_index=True)

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

col_not = ['prepojenie_prierez', 'prepojenia', 'prepojenia ciel na ciel']
df_xlsx = to_excel(dfx[cols_to_xlsx + cols_to_st])
st.download_button(label='📥 Download',
                   data=df_xlsx ,
                   file_name= 'rozdelene_standardy.xlsx')
