import streamlit as st
import pandas as pd
import re
import docx
from docx.shared import Inches
from tempfile import NamedTemporaryFile
import copy
import base64
import streamlit_select_image as stsi
from streamlit_elements import elements, mui, html, lazy, sync

# HEADERS AND BEAUTIFY
st.set_page_config(page_title="Pictortho", layout="wide", page_icon="icon.png")

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

with open('logo.svg', 'r') as svg:
    b64 = base64.b64encode(svg.read().encode('utf-8')).decode("utf-8")

with open('logo_ARASAAC.png', 'rb') as f:
    arasaac = base64.b64encode(f.read())

# NEEDED VARIABLES

if "table" not in st.session_state:
    st.session_state.table = pd.read_csv("table.csv", sep="\t", index_col=0)
    # GETTING LISTS
    commas_columns = ["_id", "Pictogramme", "Conjugaison", "schematic", "sex", "violence", "aac", "aacColor", "skin",
                      "hair", "downloads"]
    double_point_columns = ["Catégories"]
    for column in commas_columns:
        st.session_state.table[column] = st.session_state.table[column].apply(
            lambda string: string.split(",") if type(string) is str else string)
    for column in double_point_columns:
        st.session_state.table[column] = st.session_state.table[column].apply(
            lambda string: string.split(":") if type(string) is str else string)

if "verbs" not in st.session_state:
    st.session_state.verbs = pd.read_csv("conjugaison.csv", sep=";").set_index("Mots conjugués")
    st.session_state.verbs = st.session_state.verbs[~st.session_state.verbs.index.duplicated(keep='first')]

if "sentences" not in st.session_state:
    st.session_state.sentences = {"0": {"id": 0, "role": "add"}}

if "count" not in st.session_state:
    st.session_state.count = 1


# UTILS
def add_sentence():
    st.session_state.sentences[str(st.session_state.count)] = {"id": st.session_state.count, "role": "remove"}
    st.session_state.count += 1


def delete_sentence(i):
    def delete_sentencei():
        del st.session_state.sentences[str(i)]
        del st.session_state[f"sentence{i}"]
        del st.session_state[f"sentence{i}_remove"]

    return delete_sentencei


def get_pictos(sentence):
    res = []
    # Replace verb to standard form
    temp_sentence = copy.deepcopy(sentence)
    temp_sentence = temp_sentence.lower()
    temp_sentence = [el[:-1] if el[-1] == "." else el for el in re.split(" ", temp_sentence)]
    for j in range(len(temp_sentence)):
        verb_match = st.session_state.verbs[st.session_state.verbs.index.str.fullmatch(temp_sentence[j])]
        if verb_match.shape[0] != 0:
            temp_sentence[j] = verb_match.iloc[0]["Infinitif"]
    # Match words
    res = {}
    j = 0
    while j < len(temp_sentence):
        for k in range(0, len(temp_sentence) - j):
            words = " ".join(temp_sentence[j:j + k + 1])
            find_res = st.session_state.table[st.session_state.table.index.str.fullmatch(words)]
            if find_res.shape[0] != 0:
                if str(j) not in res:
                    res[str(j)] = {"words": words, "data": find_res}
                else:
                    # Remove doublon aliments de dinette -> aliments de dinette + dinette : we need to remove dinette
                    if len(words) > len(res[str(j)]["words"]):
                        res[str(j)] = {"words": words, "data": find_res}
        j += len(res[str(j)]["words"].split(" ")) if str(j) in res else 1
    return [res[key]["data"] for key in res]

def go_to_github():
    link = "https://github.com/victorC97/pictortho"


# APP START

with elements("app-bar"):
    with mui.Box(sx={"flexGrow": 1}, mx={0}):
        with mui.AppBar(position="static", sx={"backgroundColor": "#FFFFFF"}):
            with mui.Toolbar(display="flex", sx={"justifyContent": "space-between", "padding": 2}):
                mui.Box(
                    html.img(src=f"data:image/svg+xml;base64,{b64[:-2]}", alt="pictortho", width="120px"),
                    mui.Typography("écrit grâce à", variant="h4", color="black"),
                    html.img(src=f"data:image/png;base64,{arasaac.decode()}", width="300px"),
                    display="flex", alignItems="center"
                )

st.markdown("#### Titre du document :")

title = st.text_input("Titre du document :", label_visibility="collapsed")

st.markdown("#### Phrases à traduire :")

stream = None
nb_line = 1
for key in st.session_state.sentences:
    info = st.session_state.sentences[key]
    line = st.columns([33, 1])
    with line[0]:
        st.session_state.sentences[key]["sentence"] = st.text_input(label=f"sentence{key}", value="",
                                                                    label_visibility="collapsed", key=f"sentence{key}")
    with line[1]:
        if info["role"] == "add":
            st.button(label="\+", key="add_sentence", on_click=lambda: add_sentence())
        elif info["role"] == "remove":
            st.button(label=" \- ", key=f"sentence{key}_remove", on_click=delete_sentence(key))
    st.session_state.sentences[key]["columns"] = []
    if st.session_state[f"sentence{key}"] != "":
        with st.spinner("Traduction en cours..."):
            st.session_state.sentences[key]["res"] = get_pictos(st.session_state[f"sentence{key}"])
        for i in range(0, len(st.session_state.sentences[key]["res"]), 8):
            st.session_state.sentences[key]["columns"].append(st.columns(8))
            for index in range(len(st.session_state.sentences[key]["res"][i:i + 8])):
                with st.session_state.sentences[key]["columns"][i % 8][index % 8]:
                    infos = st.session_state.sentences[key]["res"][i:i + 8][index]
                    select_im = stsi.st_select_image(options=[f"pictos/{info}" for info in infos["Pictogramme"].iloc[0]],
                                         label=f"{infos['Mots écrits'].iloc[0]}", no_choice=True, key=f"sentence{key}_si_{i}_{index}_{infos['Mots écrits'].iloc[0]}")

if st.button("Générer"):
    with st.spinner("Génération du document Word..."):
        document = docx.Document()
        document.add_heading(title, 0)
        for key in st.session_state.sentences:
            document.add_paragraph("").add_run(f"{nb_line}\\.").bold = True
            document.add_paragraph(st.session_state[f"sentence{key}"])
            nb_line += 1
            grid = document.add_paragraph()
            r = grid.add_run()
            for i in range(0, len(st.session_state.sentences[key]["res"]), 8):
                for index in range(len(st.session_state.sentences[key]["res"][i:i + 8])):
                    if st.session_state[f'sentence{key}_si_{i}_{index}'] != "":
                        r.add_picture(f"{st.session_state[f'sentence{key}_si_{i}_{index}']}", width=Inches(1.2), height=Inches(1.2))
                        r.add_text(" ")

    with NamedTemporaryFile() as tmp:
        document.save(tmp.name)
        tmp.seek(0)
        stream = tmp.read()

if stream:
    download = st.download_button(label="Télécharger", data=stream,
                                  file_name=f"pictortho_{tmp.name.split('.')[0].split('/')[-1]}.docx",
                                  mime="application/msword")

for i in range(10):
    st.markdown("")

st.markdown(f'<div style="text-align: center;">Tous pictogrammes présents sur Pictortho provient de la base de données d\'<a href="https://arasaac.org">ARASAAC</a>.</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align: center;">Pictortho est disponible en libre accès sur <a href="https://arasaac.org">Github</a>.</div>', unsafe_allow_html=True)
