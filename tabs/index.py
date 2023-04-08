from .utils import *
import streamlit_freegrid as sfg


def index():
    if "table" not in st.session_state:
        load_table()
    if "index_result" not in st.session_state:
        st.session_state["index_result"] = st.session_state["table"].iloc[0:100]
    search_text = st.text_input("Recherche",
                                help="Filtrez grâce à des expressions régulières\n\nExemple : ^fri désigne tous les mots commençant par fri.\n\nAttention, n'utilisez pas des expressions régulières trop générales (exemple : les mots contenant e), le serveur ne supporte pas autant de données.",
                                key="index_search_text")
    if search_text != "":
        st.session_state["index_result"] = st.session_state["table"][
            st.session_state["table"]["word"].str.contains(search_text.lower())]
    else:
        st.session_state["index_result"] = st.session_state["table"].iloc[0:100]

    sfg.streamlit_freegrid(
        df=st.session_state["index_result"],
        types={
            "image": {"type": "image"},
            "schematic": {"type": "bool"},
            "aac": {"type": "bool"},
            "aacColor": {"type": "bool"},
            "hair": {"type": "bool"},
            "skin": {"type": "bool"},
            "sex": {"type": "bool"},
            "violence": {"type": "bool"},
        },
        hide=["schematic", "aac", "aacColor", "hair", "skin", "sex", "violence", "downloads"],
        labels={
            "word": "Mots",
            "image": "Pictogramme",
            "_id": "Identifiant ARASAAC",
            "categories": "Catégories"
        },
        pageSize=30,
        height=480,
        key="index_sfg_result"
    )
