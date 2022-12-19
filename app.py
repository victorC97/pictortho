import streamlit as st
import pandas as pd
import re
import docx
from docx.shared import Inches
from tempfile import NamedTemporaryFile
import copy


# UTILS
def add_sentence():
    st.session_state.sentences[st.session_state.count] = {"id": st.session_state.count, "role": "remove"}
    st.session_state.count += 1


def delete_sentence(i):
    def delete_sentencei():
        del st.session_state.sentences[i]
        del st.session_state[f"sentence{i}"]
        del st.session_state[f"sentence{i}_remove"]

    return delete_sentencei


def get_pictos(sentence):
    res = []
    # Replace verb to standard form
    temp_sentence = copy.deepcopy(sentence)
    temp_sentence = temp_sentence.lower()
    for word in st.session_state.verbs["Infinitif"]:
        temp_sentence = re.subn(word, st.session_state.verbs["Infinitif"][word], temp_sentence)[0]
    # Match words
    for word in st.session_state.table["Pictogrammes"]:
        search_temp = copy.deepcopy(temp_sentence)
        match = re.search(word, search_temp)
        last_pos = 0
        count = 0
        while match:
            a, b = match.span()
            res.append({"word": word, "span": (a + count, b + count)})
            last_pos = match.span()[1]
            count = count + last_pos
            search_temp = search_temp[last_pos:]
            match = re.search(word, search_temp)
    # Remove doublon aliments de dinette -> aliments de dinette + dinette : need to remove dinette
    remove = []
    for i in range(len(res)):
        o = res[i]
        o_span = o["span"]
        others = res[:i] + res[i + 1:]
        for other in others:
            other_span = other["span"]
            if o_span[0] >= other_span[0] and o_span[1] <= other_span[1]:
                remove.append(o["word"])
    res = [o for o in res if o["word"] not in remove]
    # Sort result
    res_data = {"word": [], "order": [], "picto": []}
    for o in res:
        res_data["word"].append(o["word"])
        res_data["order"].append(int(o["span"][0]))
        res_data["picto"].append(st.session_state.table["Pictogrammes"][o["word"]])
    res_df = pd.DataFrame(res_data).sort_values(by="order").reset_index(drop=True)
    return res_df


# HEADERS AND BEAUTIFY
st.set_page_config(page_title="Pictortho", layout="wide", page_icon="icon.png")

with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.image("logo.jpg", output_format="JPEG", width=200)

# NEEDED VARIABLES

if "table" not in st.session_state:
    st.session_state.table = pd.read_excel("table.xlsx", header=0)
    st.session_state.table["Mots écrits"] = st.session_state.table["Mots écrits"].apply(lambda wrd: wrd.strip())
    st.session_state.table["Pictogrammes"] = st.session_state.table["Pictogrammes"].apply(lambda path: path.strip())
    st.session_state.table = st.session_state.table.set_index("Mots écrits").to_dict()

if "verbs" not in st.session_state:
    st.session_state.verbs = pd.read_csv("conjugaison.csv", sep=";").set_index("Mots conjugués").to_dict()

if "sentences" not in st.session_state:
    st.session_state.sentences = {"0": {"id": 0, "role": "add"}}

if "count" not in st.session_state:
    st.session_state.count = 1

st.session_state.something = False

document = docx.Document()
document.add_heading('PictOrtho', 0)

st.markdown("#### Phrases à traduire :")

count = 1
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
        st.session_state.something = True
        st.session_state.sentences[key]["res"] = get_pictos(st.session_state[f"sentence{key}"])
        document.add_paragraph("").add_run(f"{count}\\.").bold = True
        document.add_paragraph(st.session_state[f"sentence{key}"])
        count += 1
        grid = document.add_paragraph()
        r = grid.add_run()
        for i in range(0, st.session_state.sentences[key]["res"].shape[0], 5):
            st.session_state.sentences[key]["columns"].append(st.columns(5))
            for index, row in st.session_state.sentences[key]["res"].iloc[i:i + 5].iterrows():
                with st.session_state.sentences[key]["columns"][i % 5][index % 5]:
                    st.image(f"pictos/{row['picto']}", width=200)
                    r.add_picture(f"pictos/{row['picto']}", width=Inches(1.2), height=Inches(1.2))
                    r.add_text(" ")

with NamedTemporaryFile() as tmp:
    document.save(tmp.name)
    tmp.seek(0)
    stream = tmp.read()
    download = st.download_button(label="Télécharger", data=stream,
                                  file_name=f"pictortho_{tmp.name.split('.')[0].split('/')[-1]}.docx",
                                  mime="application/msword")