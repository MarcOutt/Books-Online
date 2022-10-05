##########################################################
#                                                        #
#                      BOOKS ONLINE                      #
#                                                        #
##########################################################
import shutil

import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path

BASE_URL = "http://books.toscrape.com/"
CATALOGUE_URL = "http://books.toscrape.com/catalogue/"


def nettoyer_text(texte):
    """ Permet d'interpreter le symbole de la livre'

    Args:
        texte : texte à nettoyer

    Returns:
        str : texte nettoyé

    """
    return texte.replace("Â£", "£")


def nettoyer_url(url):
    """ Permet de supprimer les points et les slash en trop

    Args:
        url : url récupérée sur le site

    Returns:
        str : url nettoyée
    """
    return url.replace("../../../", "")


def creation_fichier_principal():
    dossier_books_to_scraps = Path.cwd() / "Books_to_scraps"
    try:
        dossier_books_to_scraps.mkdir()
    except FileExistsError:
        print("")
    return dossier_books_to_scraps


def zip_dossier():
    filename = "books_to_scraps"
    format = "zip"
    directory = dossier_principal
    shutil.make_archive(filename, format, directory)
    print("Formatage du dossier complété")


def recuperer_image(url_image, dossier_categorie, titre_du_livre):
    """ Permet de récupérer les images des livres

    Args:
        url_image : url récupéré sur le site
        dossier_categorie: dossier catégorie
        titre_du_livre : titre du livre

    Returns:
            rien
    """

    response = requests.get(url_image)
    titre_du_livre_nettoye = ''.join(filter(str.isalnum, titre_du_livre))
    nom_du_fichier = titre_du_livre_nettoye + ".jpg"
    dossier_image = dossier_categorie / nom_du_fichier
    if response.status_code == 200:
        with open(dossier_image, 'wb') as f:
            f.write(response.content)


def initialisation_bs(url_site):
    """ Initialisation de beautifulSoup

    Args:
        url_site : url_site

    Returns :
            soup : initialisation de bs4

    """
    response = requests.get(url_site)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def enregistrer_fichier_csv(livres, fichier_csv):
    """ enregistre les infos des livres dans un fichier csv

    Args:
        livres : liste des livres
        fichier_csv: fichier_csv

    Returns:
            rien
    """

    try:
        liste_livres = livres[1]
    except IndexError:
        liste_livres = livres[0]
    header = []
    for key in liste_livres["infos_livre"].keys():
        header.append(key)

    with open(fichier_csv, 'a', newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        writer.writeheader()
        for livre in livres:
            infos_livre = livre["infos_livre"]
            writer.writerow(infos_livre)
    print("Téléchargement de la catégorie => terminé")
    print()


def extraire_infos_livre(url_livre, dossier_categorie):
    """ extrait les infos des livres

    Args:
        url_livre : url d un livre
        dossier_categorie : dossier correspondant à la catégorie du livre

    Returns:
            livres :  la liste des infos des livres
    """
    soup = initialisation_bs(url_livre)
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

    infos_livre = {
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
    return infos_livre


def extraire_liste_livres(url_categorie, categorie):
    """ extrait la liste des livres

    Args:
        url_categorie : url des catégories
        categorie: nom de la catégorie

    Returns:
        liste : toute la liste et les infos des livres d'une catégorie

    """
    soup = initialisation_bs(url_categorie)
    section_livre = soup.find("section")
    ol_livres = section_livre.find("ol", class_="row")
    li_livres = ol_livres.find_all("li")
    liste = []
    dossier_categorie = dossier_principal / categorie
    try:
        dossier_categorie.mkdir()
    except FileExistsError:
        a = "déjà existant"
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
    """

    Args:
        url: url catégorie
        liste: liste des infos des livres
        categorie: nom de la catégorie

    Returns:
        scrape_page: récursif pour ajouter les autres catégories au scrapping

    """
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
        data_file = dossier_principal / fichier_csv
        data_file.touch()
        enregistrer_fichier_csv(liste, data_file)


def extraire_url_categories(url):
    """ permet de récupérer les urls des catégories

    Args:
        url: url accueil du site

    Returns:
        rien
    """
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
        categorie_nettoye_2 = categorie_nettoye.replace('\n', "")
        href = a["href"]
        lien = BASE_URL + href
        print("Téléchargement de la catégorie: " + categorie_nettoye_2)
        categorie_scraper = scrape_page(lien, liste, categorie_nettoye_2)
    print("Téléchargement terminé")


def menu_principal():
    """ choix pour lancer les programmes

    Returns:
            rien
    """
    print(""" 

            SYSTEME DE SURVEILLANCE DES PRIX

                        MENU

        1 - EXTRAIRE LES LIVRES PAR CATEGORIE
        2 - CREER UN DOSSIER ZIP DE L'EXTRACTION
        3 - QUITTER L'APPLICATION

        """)

    user = input("Veuillez faire votre choix: ")
    try:
        user_int = int(user)
        if user_int == 1:
            extraire_url_categories(BASE_URL)
            menu_principal()
        elif user_int == 2:
            zip_dossier()
            menu_principal()
        elif user_int == 3:
            print("Au revoir")
            exit()
        else:
            print("Veuillez entrer un nombre entre 1 et 3")
    except ValueError:
        print("Veuillez mettre un nombre entre 1 et 3")


liste = []
dossier_principal = creation_fichier_principal()
menu_principal()
