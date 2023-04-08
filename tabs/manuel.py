from .utils import *
import streamlit.components.v1 as stcv1
import streamlit_appbar as stab


def manuel():
    generate_mode_selection()
    generate_manuel(st.session_state["manuel_mode"])


def generate_manuel(mode):
    if mode == "Traduction":
        instructions = [
            {"instruction": "Ajoutez un titre au document",
             "illustration": get_static_file("manuel_illustrations/traduction/title.png"),
             "width": 200},
            {"instruction": "Ajoutez/supprimez des phrases avec les boutons **\+** et **\-**.",
             "illustration": get_static_file("manuel_illustrations/traduction/sentence.png"),
             "width": 200},
            {"instruction": "Appuyez sur **Entrée** pour traduire les phrases",
             "illustration": get_static_file("manuel_illustrations/traduction/traduction.png"),
             "width": 400},
            {"instruction": "Sélectionnez les pictogrammes que vous voulez afficher.",
             "illustration": get_static_file("manuel_illustrations/traduction/modif.png"),
             "width": 150},
            {"instruction": "Appuyez sur le bouton **Valider** pour générer le document Word de traduction.",
             "illustration": ""},
            {"instruction": "Télécharger le document avec le bouton **Télécharger**.",
             "illustration": ""},
        ]
    elif mode == "TLA":
        instructions = [
            {"instruction": "Configurez la dimension du tableau.",
             "illustration": "",
            },
            {"instruction": "Cliquez sur **Réinitialiser** pour effacer toutes les cases.",
             "illustration": "",
             },
            {"instruction": "Remplissez les cases du tableau.",
             "illustration": "",
             },
            {"instruction": "Glissez la page jusqu'au tableau de pictogrammes et choisissez les pictogrammes désirés.",
             "illustration": "",
             },
            {"instruction": "Si une traduction comporte plusieurs pictogrammes, sélectionnez le mot qui représentera la case. Choisissez enfin votre pictogramme.",
             "illustration": "",
             },
            {"instruction": "Cliquez sur **Valider** pour générer le document. Puis sur **Télécharger** pour récupérer votre document créé.",
             "illustration": "",
             },
        ]
    elif mode == "Index":
        instructions = [
            {"instruction": "Écrivez le mot que vous recherchez dans le filtre **Recherche**.",
             "illustration": get_static_file("manuel_illustrations/index/prefilter.png"),
             "width": 200},
            {"instruction": "Les [expressions régulières](https://fr.wikipedia.org/wiki/Expression_régulière) sont acceptées. Exemple : ^a.*dir$",
             "illustration": get_static_file("manuel_illustrations/index/regex.png"),
             "width": 850},
            {"instruction": "Triez ou filtrez le résultat de la recherche par colonne.",
             "illustration": get_static_file("manuel_illustrations/index/filter.png"),
             "width": 500},
        ]
    else:
        instructions = []
    generate_instructions(instructions)


def generate_instructions(instructions):
    for i in range(0, len(instructions), 3):
        row = st.columns(3)
        for j in range(i, i + 3):
            with row[j % 3]:
                if j < len(instructions):
                    st.markdown(f"{j + 1}. " + instructions[j]["instruction"])
                    if instructions[j]["illustration"].__str__() != "":
                        st.image(instructions[j]["illustration"].__str__(), width=instructions[j]["width"])


def generate_mode_selection():
    manuel_modes = [
        {"name": "Traduction",
         },
        {"name": "TLA",
         },
        {"name": "Index",
         },
    ]
    title = st.container()
    if "manuel_mode" not in st.session_state:
        set_mode(manuel_modes[0]["name"], title)()
    row_modes = st.columns(len(manuel_modes) * 2 + 1)
    for i in range(len(manuel_modes)):
        with row_modes[i * 2 + 1]:
            manuel_btn = st.button(f"{manuel_modes[i]['name']}", key=f"manuel_mode_{manuel_modes[i]['name']}")
            if manuel_btn:
                set_mode(manuel_modes[i]['name'], title)()


def set_mode(mode: str, container):
    def _set_mode():
        st.session_state["manuel_mode"] = mode
        container.markdown(f"#### Manuel d'utilisation {st.session_state['manuel_mode']}")

    return _set_mode
