##########################################################
#                                                        #
#                      BOOKS ONLINE                      #
#                                                        #
##########################################################

import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from tqdm import tqdm

CUR_DIR = Path.cwd()

BASE_URL = "http://books.toscrape.com/"
CATALOGUE_URL = "http://books.toscrape.com/catalogue/"


def nettoyer_text(t):
    return t.replace("Â£", "£")


def nettoyer_url(url):
    return url.replace("../../../", "")


def recuperer_image(url, dossier, titre):
    response = requests.get(url)
    titre_nettoye = ''.join(filter(str.isalnum, titre))
    nom_de_fichier = titre_nettoye + ".jpg"
    fichier = dossier / nom_de_fichier
    if response.status_code == 200:
        with open(fichier, 'wb') as f:
            f.write(response.content)


def initialisation_bs(url):
    # initialisation de BS
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def lire_fichier_csv(datafile):
    with open(datafile, 'r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            print(line)


def enregistrer_fichier_csv(livres, datafile):
    try:
        liste = livres[1]
    except IndexError:
        liste = livres[0]
    header = []
    for key in liste["infos_livre"].keys():
        header.append(key)

    with open(datafile, 'a', newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for livre in livres:
            infos = livre["infos_livre"]
            writer.writerow(infos)


def extraire_infos_livre(url, dossier_categorie):
    soup = initialisation_bs(url)
    # récupérer le titre
    titre = soup.find("h1").text

    # catégorie livre
    ul_breadcrumb = soup.find("ul", class_="breadcrumb")
    ul_breadcrumb_li = ul_breadcrumb.find_all("a")
    category = ul_breadcrumb_li[2].text

    # review rating
    div_col_product_main = soup.find("div", class_="col-sm-6 product_main")
    review_rating = div_col_product_main.find("p", class_="star-rating")
    if review_rating == div_col_product_main.find("p", class_="star-rating One"):
        review_rating = "1 étoile"
    if review_rating == div_col_product_main.find("p", class_="star-rating Two"):
        review_rating = "2 étoiles"
    if review_rating == div_col_product_main.find("p", class_="star-rating Three"):
        review_rating = "3 étoiles"
    if review_rating == div_col_product_main.find("p", class_="star-rating Four"):
        review_rating = "4 étoiles"
    if review_rating == div_col_product_main.find("p", class_="star-rating Five"):
        review_rating = "5 étoiles"

    # description du livre
    article_product_page = soup.find("article", class_="product_page")
    product_description = article_product_page.find("p", recursive=False)
    if product_description:
        product_description = article_product_page.find("p", recursive=False).text
    else:
        product_description = "non renseignée"
    # url image
    div_item = soup.find("div", class_="item")
    img_item = div_item.find("img")
    img_src = img_item["src"]
    img_url = BASE_URL + img_src
    recuperer_image(img_url, dossier_categorie, titre)

    # récupérer infos livre
    product_info = soup.find("table", class_="table table-striped")
    product_info_td = product_info.find_all("td")

    # UPC
    universal_product_code = product_info_td[0].text

    # TVA
    price_including_tax = product_info_td[3].text
    price_including_tax_clean = nettoyer_text(price_including_tax)

    # HT
    price_excluding_tax = product_info_td[2].text
    price_excluding_tax_clean = nettoyer_text(price_excluding_tax)

    # disponibilité
    number_available = product_info_td[5].text

    # review
    number_review = product_info_td[6].text

    livre = {
        "title": titre,
        "category": category,
        "image_url": img_url,
        "review_rating": review_rating,
        "product_description": product_description,
        "universal_product_code": universal_product_code,
        "price_including_tax": price_including_tax_clean,
        "price_excluding_tax": price_excluding_tax_clean,
        "number_available": number_available,
        "number_review": number_review
    }
    return livre


def extraire_liste_livres(url, categorie):
    soup = initialisation_bs(url)
    section_livre = soup.find("section")
    ol_livres = section_livre.find("ol", class_="row")
    li_livres = ol_livres.find_all("li")
    liste = []
    dossier_categorie = Path.cwd() / categorie
    try:
        dossier_categorie.mkdir()
    except FileExistsError:
        print("dossier déjà existant")
    for li in li_livres:
        # récupérer l'url du livre
        div_img_container = li.find("div", class_="image_container")
        livre_li = div_img_container.find("a")
        href = livre_li["href"]
        href_nettoye = nettoyer_url(href)
        livre_url = CATALOGUE_URL + href_nettoye

        # récupérer les infos du livre
        infos_livre = extraire_infos_livre(livre_url, dossier_categorie)

        # ajout des éléments dans une liste
        liste.append({"infos_livre": infos_livre})
    return liste


def scrape_page(url, liste, categorie):

    soup = initialisation_bs(url)
    livres = extraire_liste_livres(url, categorie)
    liste = liste + livres
    section = soup.find("section")
    li_next = section.find("li", class_="next")

    if li_next is not None:
        a = li_next.find("a")
        href = a["href"]
        u = url.split("/")[-1]
        url2 = url.replace(u, "")
        page_suivante = url2 + href
        return scrape_page(page_suivante, liste, categorie)
    else:
        fichier_csv = categorie + ".csv"
        data_file = CUR_DIR / fichier_csv
        data_file.touch()
        enregistrer_fichier_csv(liste, data_file)


def extraire_url_categories(url):
    soup = initialisation_bs(url)
    div_container_fluid = soup.find("div", class_="container-fluid")
    div_side_categories = div_container_fluid.find("div", class_="side_categories")
    ul_nav = div_side_categories.find("ul", class_="nav")
    ul = ul_nav.find("ul")
    li = ul.find_all("li")
    for categorie in li:
        a = categorie.find("a")
        categorie = a.text
        categorie_nettoye = categorie.replace(' ', "")
        categorie_nettoye2 = categorie_nettoye.replace('\n', "")
        href = a["href"]
        lien = BASE_URL + href

        for i in tqdm(range(0, len(li)), disable=False,
                      desc="Téléchargement des livres par catégorie"):
            categorie_scraper = scrape_page(lien, liste, categorie_nettoye2)
    print("Téléchargement terminé")

liste = []
url = "http://books.toscrape.com/index.html"
u = extraire_url_categories(BASE_URL)
