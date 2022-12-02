import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
tqdm.pandas()

pronoms = ["je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "me", "te", "se"]
aux = ["ai", "as", "a", "avons", "avez", "ont", "avais", "avait", "avions", "aviez", "avaient", "eus", "eut", "eûmes",
       "eûtes", "eurent", "aurais", "aurait", "aurions", "auriez", "auraient", "aurai", "auras", "aura", "aurons",
       "aurez", "auront", "aie", "aies", "ait", "ayons", "ayez", "aient", "eusse", "eusses", "eût", "eussions",
       "eussiez", "eussent", "suis", "es", "est", "sommes", "êtes", "sont", "étais", "était", "étions", "étiez",
       "étaient", "fus", "fut", "fûmes", "fûtes", "furent", "serai", "seras", "sera", "serons", "serez", "seront", "serais",
       "serait", "serions", "seriez", "seraient", "sois", "soit", "soyons", "soyez", "soient", "fusse", "fusses", "fût",
       "fussions", "fussiez", "fussent", "ayant", "avoir", "en", "vais", "vas", "va", "allons", "allez", "vont", "viens",
       "vient", "venons", "venez", "viennent", "étant", "être", "de", "t'es", "s'est", "t'a", "t'a", "m'étais", "t'étais", "s'était", "s'étaient", "-", "s'étant", "s'être"]
subj = ["que", "qu'il", "qu'elle", "qu'ils", "qu'elles"]


def get_conjugaison(mot, dictionary):
    res = requests.get(f"https://leconjugueur.lefigaro.fr/conjugaison/verbe/{mot}.html")
    try:
        if res.status_code == 200:
            soup = BeautifulSoup(res.text.replace("<br />", " "), 'html.parser')
            temps = soup.find_all("div", {"class": "conjugBloc"})
            forms = []
            for temp in temps:
                paragraphs = temp.findAll("p")
                if len(paragraphs) > 1:
                    verbs = [el for el in paragraphs[1].text.replace("j'", "").replace("d'", "").split(" ") if
                             el not in pronoms and el not in aux and el not in subj]
                    for form in verbs:
                        if form not in forms:
                            forms.append(form)
            for form in forms:
                dictionary["Mots conjugués"].append(form)
                dictionary["Infinitif"].append(mot)
            return forms
        time.sleep(3)
    except Exception as e:
        print(e)
        return []


def main():
    # df = pd.read_excel("table.xlsx", header=0)
    # data_conjugaison = {"Mots conjugués": [], "Infinitif": []}
    # df["Mots écrits"].progress_apply(lambda mot: get_conjugaison(mot, data_conjugaison))
    # df_conjugaison = pd.DataFrame(data_conjugaison)
    # df_conjugaison.to_csv("conjugaison.csv", sep=";")
    pass


if __name__ == "__main__":
    main()
