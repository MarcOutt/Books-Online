##########################################################
#                                                        #
#                      BOOKS ONLINE                      #
#                                                        #
##########################################################

import os

import requests
from bs4 import BeautifulSoup
import csv

CUR_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(CUR_DIR, "infos_livre.csv")
BASE_URL = "http://books.toscrape.com/catalogue/"


def nettoyer_text(t):
    return t.replace("Â£", "£")


def nettoyer_url(u):
    return u.replace("../../../", "/")


def extraire_infos_livre(u):
    # initialisation de BS
    response = requests.get(u)
    soup = BeautifulSoup(response.text, "html.parser")

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
    product_description = article_product_page.find("p", recursive=False).text

    # url image
    div_item = soup.find("div", class_="item")
    img_item = div_item.find("img")
    img_src = img_item["src"]

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
        "image_url": img_src,
        "review_rating": review_rating,
        "product_description": product_description,
        "title": titre,
        "universal_product_code": universal_product_code,
        "price_including_tax": price_including_tax_clean,
        "price_excluding_tax": price_excluding_tax_clean,
        "number_available": number_available,
        "category": category,
        "number_review": number_review
    }

    header = []
    for key in livre.keys():
        header.append(key)

    with open(DATA_FILE, 'a', newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        writer.writerow(livre)

    with open(DATA_FILE, 'r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            print(line)
    return livre


def extraire_liste_livres(u):
    # initialisation de BS
    response = requests.get(u)
    soup = BeautifulSoup(response.text, "html.parser")

    ul_pager = soup.find("ul", class_="pager")
    section_livre = soup.find("section")
    ol_livres = section_livre.find("ol", class_="row")
    li_livres = ol_livres.find_all("li")
    liste = []
    for li in li_livres:
        # récupérer l'url du livre
        div_img_container = li.find("div", class_="image_container")
        livre_li = div_img_container.find("a")
        href = livre_li["href"]
        href_nettoye = nettoyer_url(href)
        print(href_nettoye)
        livre_url = BASE_URL + href_nettoye

        # récupérer les infos du livre
        infos_livre = extraire_infos_livre(livre_url)

        # ajout des éléments dans une liste
        liste.append({"infos_livre": infos_livre})

    section = soup.find("section")
    li = section.find("li", class_="next")
    a = li.find("a")
    next_page = a["href"]
    print(next_page)
    if next_page:
        url = u.replace("index.html", f"{next_page}")
        extraire_infos_livre(url)

    return liste


url = "http://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html"

liste_livres = extraire_liste_livres(url)
print(liste_livres)
