import streamlit as st
from pathlib import Path
import pandas as pd
import re
import copy
from docx.oxml import OxmlElement
from docx.oxml.shared import qn

static_folder = Path("static")


def get_static_file(filename: str):
    return static_folder / filename


def load_table():
    st.session_state.table = pd.read_csv(get_static_file("table.csv"), sep="\t")
    st.session_state.table["image"] = st.session_state["table"]["image"].apply(lambda img: "pictos/" + img)


def reset(tab: str):
    to_remove = [key for key in st.session_state if re.match(tab, key)]
    for key in to_remove:
        del st.session_state[key]


def replace_regex_char(word: str):
    return word.replace("?", "\?").replace(".", "\.").replace("^", "\^").replace("$", "\$").replace("[", "\[").replace(
        "]", "\]").replace("(", "\(").replace(")", "\)").replace("{", "\{").replace("}", "\}").replace("!", "\!")


def translate(sentence_input: str):
    temp_sentence = copy.deepcopy(sentence_input)
    temp_sentence = temp_sentence.lower()
    temp_sentence = temp_sentence.replace(" l'", " l' ").replace("j'", "je ")
    temp_sentence = [el[:-1] if el[-1] == "." or el[-1] == "," else el for el in re.split(" ", temp_sentence) if
                     el != ""]
    matches = {}
    j = 0
    while j < len(temp_sentence):
        for k in range(0, len(temp_sentence) - j):
            words = " ".join(temp_sentence[j:j + k + 1])
            if words == "l'":
                data = st.session_state.table[
                    st.session_state.table["word"].str.fullmatch("le") | st.session_state.table["word"].str.fullmatch(
                        "la")]
            else:
                data = st.session_state.table[st.session_state.table["word"].str.fullmatch(replace_regex_char(words))]
            if data.shape[0] != 0:
                if str(j) not in matches:
                    matches[str(j)] = {"words": words, "data": data}
                else:
                    # Remove doublon aliments de dinette -> aliments de dinette + dinette : we need to remove dinette
                    if len(words) > len(matches[str(j)]["words"]):
                        matches[str(j)] = {"words": words, "data": data}
        j += len(matches[str(j)]["words"].split(" ")) if str(j) in matches else 1
    result = [{"words": matches[key]["words"], "data": matches[key]["data"]} for key in matches]
    return result


def set_cell_border(cell, **kwargs):
    """
    Set cell`s border
    Usage:

    set_cell_border(
        cell,
        top={"sz": 12, "val": "single", "color": "#FF0000", "space": "0"},
        bottom={"sz": 12, "color": "#00FF00", "val": "single"},
        start={"sz": 24, "val": "dashed", "shadow": "true"},
        end={"sz": 12, "val": "dashed"},
    )
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()

    # check for tag existnace, if none found, then create one
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)

    # list over all available tags
    for edge in ('start', 'top', 'end', 'bottom', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)

            # check for tag existnace, if none found, then create one
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)

            # looks like order of attributes is important
            for key in ["sz", "val", "color", "space", "shadow"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))
