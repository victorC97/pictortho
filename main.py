import bs4.element
import requests
from bs4 import BeautifulSoup
import unidecode
from typing import Optional
from fake_useragent import UserAgent
import time
import re
import pandas as pd
from tqdm import tqdm
import os

strip_pronoms = ["j'", "je ", "tu ", "il ", "elle ", "nous ", "vous ", "ils ", "elles "]
strip_whitespaces = ["  "]


class ARASAAC:

    def __init__(self, locale: str = "fr", save_directory: str = "pictos"):
        self.base = "https://api.arasaac.org/api"
        self.locale = locale
        self.save_directory = save_directory

    def get_pictograms(self):
        endpoint = f"/pictograms/all/{self.locale}"
        request = requests.get(self.base + endpoint)
        try:
            return request.json()
        except Exception as e:
            print("""get_pictograms can't render a json file.""")
            return []

    def get_pictogram(self, identifier: int):
        endpoint_png = f"/pictograms/{identifier}"
        request_png = requests.get(self.base + endpoint_png)
        filename = f"{self.save_directory}/{identifier}.png"
        try:
            with open(filename, "wb") as file:
                file.write(request_png.content)
        except Exception as e:
            print(f"""get_pictogram can't save {identifier} png file.""")


def get_verb_page(verb: str) -> Optional[BeautifulSoup]:
    url = f"https://leconjugueur.lefigaro.fr/conjugaison/verbe/{unidecode.unidecode(verb)}.html"
    user_agent = UserAgent()
    headers = {"User-Agent": str(user_agent.random)}
    q = requests.get(url, headers=headers)
    if q.status_code == 200:
        html_text = q.text
        html_text = html_text.replace("<b>", "").replace("</b>", "").replace("<br />", " ")
        soup = BeautifulSoup(html_text, parser="html.parser", features="lxml")
        time.sleep(1)
        return soup
    else:
        return None


def find_blocs(soup: BeautifulSoup) -> list:
    conjug_blocs = soup.find_all("div", attrs={"class": "conjugBloc"})
    return conjug_blocs


def get_conjug_from_bloc(bloc: bs4.element.Tag) -> list:
    contents = bloc.contents
    if len(contents) == 2:
        temp = contents[0].get("id")
        forms = contents[1].text
        res = []
        if temp == "temps0":
            for pattern in strip_pronoms:
                forms = re.sub(pattern, " ", forms, 1)
            res = [form for form in forms.split(" ") if form != ""]
            if len(res) == 12:
                res = [res[i] + " " + res[i + 1] for i in range(0, len(res), 2)]
            elif len(res) == 8:
                res = res[:3] + [res[3] + " " + res[4], res[5] + " " + res[6], res[7]]
        return res
    else:
        return []


def append_conjugaison(verb: str, conjugaisons: pd.DataFrame):
    soup = get_verb_page(verb)
    if soup:
        blocs = find_blocs(soup)
        text = verb.split(" ")[0] if verb.split(" ")[0] != "se" else verb.split(" ")[0] + " " + verb.split(" ")[1]
        for bloc in blocs:
            forms = get_conjug_from_bloc(bloc)
            if forms != []:
                for form in forms:
                    conjugaisons.loc[len(conjugaisons)] = [form, text]


def get_conjugaison_csv():
    table = pd.read_csv("table.csv", sep="\t", index_col="index")
    conjugaisons = pd.DataFrame(columns=["Mots conjugués", "Infinitif"])
    try:
        table.progress_apply(
            lambda row: append_conjugaison(row["Mots écrits"], conjugaisons) if "1" in row["Conjugaison"].split(
                ",") else -1, axis=1)
    except Exception as e:
        conjugaisons.to_csv("conjugaison.csv", sep=";", index=False)
    conjugaisons.to_csv("conjugaison.csv", sep=";", index=False)


def save_all_pictos(save_directory: str):
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)
    client = ARASAAC(save_directory=save_directory)
    all = client.get_pictograms()
    try:
        for picto in tqdm(all):
            client.get_pictogram(picto["_id"])
    except Exception as e:
        return picto


def main():
    get_conjugaison_csv()


if __name__ == '__main__':
    tqdm.pandas()
    main()
