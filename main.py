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

strip_pronoms = ["j'", "je ", "tu ", "il ", "elle ", "nous ", "vous ", "ils ", "elles "]
strip_whitespaces = ["  "]


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
    blocs = find_blocs(soup)
    text = verb.split(" ")[0]
    for bloc in blocs:
        forms = get_conjug_from_bloc(bloc)
        if forms != []:
            for form in forms:
                conjugaisons.loc[len(conjugaisons)] = [form, text]


def main():
    table = pd.read_excel("table.xlsx", header=0)
    conjugaisons = pd.DataFrame(columns=["Mots conjugués", "Infinitif"])
    table["Mots écrits"].progress_apply(lambda verb: append_conjugaison(verb, conjugaisons))
    conjugaisons.to_csv("conjugaison.csv", sep=";", index=False)


if __name__ == '__main__':
    tqdm.pandas()
    main()
