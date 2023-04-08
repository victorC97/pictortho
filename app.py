# IMPORTS
import os
import streamlit as st
import importlib
import inspect
import streamlit_appbar as stab
tabs_modules = list(map(importlib.import_module,
                        ["tabs." + filename.replace(".py", "") for filename in os.listdir("tabs") if
                         filename.replace(".py", "") != "utils"]))

tabs = {}
for tab in tabs_modules:
    for name, obj in inspect.getmembers(tab, inspect.isfunction):
        if name == tab.__name__.replace("tabs.", ""):
            tabs[name] = obj

# HEADERS
st.set_page_config(page_title="PictOrtho", layout="wide", page_icon="static/icon.png")

# BODY
modes = [
        {"name": "traduction",
         "icon": "Create"
         },
        {"name": "tla",
         "icon": "TableView"
         },
        {"name": "manuel",
         "icon": "MenuBook"
         },
        {"name": "index",
         "icon": "List"
         },
]

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = modes[0]["name"]

mode = stab.streamlit_appbar(
    title="PictOrtho",
    modes=modes,
    logo="static/icon.svg",
    bgColor="#FFFBF5",
    txtColor="#000000",
    height=90,
    key="mode",
)

for tab in tabs:
    if mode == tab:
        if mode != st.session_state["active_tab"]:
            st.session_state["active_tab"] = mode
        tabs[tab]()


# FOOTER
with open("static/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

for i in range(15):
    st.markdown("")

st.markdown(
    f'<div style="text-align: center;">Tous pictogrammes présents sur Pictortho proviennent de la base de données d\'<a href="https://arasaac.org">ARASAAC</a> dont les termes d\'utilisations sont accessibles <a href="https://arasaac.org/terms-of-use">ici</a>.</div>',
    unsafe_allow_html=True)
st.markdown(
    f'<div style="text-align: center;">Pictortho est disponible en libre accès sur <a href="https://github.com/victorC97/pictortho">Github</a>.</div>',
    unsafe_allow_html=True)
