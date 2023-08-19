import codecs
import shutil
import html
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from typing import List, Dict

import menu

BASE_URL = "http://books.toscrape.com/"
CATALOGUE_URL = "http://books.toscrape.com/catalogue/"


def clean_url(url: str) -> str:
    """
    Cleans a URL by removing the '../../../' substring.

    Args:
        url (str): The URL to be cleaned.

    Returns:
        str: The cleaned URL.
    """
    return url.replace("../../../", "")


def create_main_directory() -> Path:
    """
       Creates a main directory named 'Books_to_scraps' if it doesn't already exist.

       This function checks if the 'Books_to_scraps' directory exists in the current working directory.
       If the directory doesn't exist, it creates it.

       Returns:
           Path: The path to the created or existing 'Books_to_scraps' directory.
       """
    main_directory = Path.cwd() / "Books_to_scraps"
    if not Path(main_directory).exists():
        main_directory.mkdir()
    return main_directory


def zip_folder() -> None:
    """
    Zips the main directory into a ZIP archive.

    This function creates a ZIP archive of the 'Books_to_scraps' main directory.

    Returns:
        None
    """
    filename = "../Books_to_scraps"
    archive_format = "zip"
    directory = main_directory
    shutil.make_archive(filename, archive_format, directory)
    print("Folder formatting completed")


def retrieve_image(url_image: str, category_directory: Path, book_title: str) -> None:
    """
    Retrieves an image from a URL and saves it in the specified category directory.

    Args:
        url_image (str): The URL of the image to retrieve.
        category_directory (Path): The path to the directory for the book's category.
        book_title (str): The title of the book.

    Returns:
        None
    """
    response = requests.get(url_image)
    response.raise_for_status()
    cleaned_book_title = ''.join(filter(str.isalnum, book_title))
    file_name = cleaned_book_title + ".jpg"
    image_path = category_directory / file_name

    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)


def initialize_bs(url_site: str) -> BeautifulSoup:
    """
    Initializes a BeautifulSoup object from a URL.

    Args:
        url_site (str): The URL of the website to initialize.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.
    """
    response = requests.get(url_site)
    response.raise_for_status()
    response.encoding = 'utf-8'
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


def save_csv_file(books: List[Dict[str, Dict[str, str]]], csv_file_path: Path) -> None:
    """
    Saves book information to a CSV file.

    Args:
        books (List[Dict[str, Dict[str, str]]]): A list of dictionaries containing book information.
        csv_file_path (str): The path to the CSV file to be created or appended.

    Returns:
        None
    """
    try:
        first_book = books[0]
        print(first_book)
        header = list(first_book["book_info"].keys())
    except IndexError:
        print("No books to save.")
        return

    with codecs.open(str(csv_file_path), 'a', encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=header)
        if csv_file.tell() == 0:  # Check if file is empty
            writer.writeheader()
        for book in books:
            book_infos = book["book_info"]
            writer.writerow(book_infos)
    print("Category download => completed\n")


def extract_book_info(book_url: str, category_folder: Path) -> dict:
    """Extracts book information.
    Args:
        book_url (str): URL of a book.
        category_folder (Path): Folder corresponding to the book's category.
    Returns:
        book_info (dict): Dictionary containing book information.
    """
    soup = initialize_bs(book_url)

    # Get the title
    title = soup.find("h1").text

    # Book category
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

    # Book description
    article_product_page = soup.find("article", class_="product_page")
    product_description = article_product_page.find("p", recursive=False)
    if product_description:
        product_description = article_product_page.find("p", recursive=False).text
    else:
        product_description = "not provided"

    # Image URL
    div_item = soup.find("div", class_="item")
    img_item = div_item.find("img")
    img_src = img_item["src"]
    img_url = BASE_URL + img_src
    retrieve_image(img_url, category_folder, title)

    # Retrieve book information
    product_info = soup.find("table", class_="table table-striped")
    product_info_td = product_info.find_all("td")

    # UPC
    universal_product_code = product_info_td[0].text

    # VAT
    price_including_tax = product_info_td[3].text
    price_including_tax_clean = html.unescape(price_including_tax)

    # Excluding VAT
    price_excluding_tax = product_info_td[2].text
    price_excluding_tax_clean = html.unescape(price_excluding_tax)

    # Availability
    number_available = product_info_td[5].text

    # Review count
    number_review = product_info_td[6].text

    book_info = {
        "title": title,
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
    return book_info


def extract_book_list(category_url: str, category_name: str) -> list:
    """
    Extracts the list of books from a category.

    Args:
        category_url (str): URL of the category.
        category_name (str): Name of the category.

    Returns:
        list: List containing book information for a category.
    """
    soup = initialize_bs(category_url)
    book_section = soup.find("section")
    book_list_ol = book_section.find("ol", class_="row")
    book_list_items = book_list_ol.find_all("li")
    book_list = []
    category_folder = main_directory / category_name
    if not Path(category_folder).exists():
        category_folder.mkdir()

    for item in book_list_items:
        # Get the book's URL
        img_container_div = item.find("div", class_="image_container")
        book_link = img_container_div.find("a")
        href = book_link["href"]
        cleaned_href = clean_url(href)
        book_url = CATALOGUE_URL + cleaned_href

        # Extract book information
        book_info = extract_book_info(book_url, category_folder)

        # Append the information to the list
        book_list.append({"book_info": book_info})
    return book_list


def scrape_page(url: str, book_list: list, category: str) -> None:
    """
    Scrapes books from a category's page.

    Args:
        url (str): URL of the category.
        book_list (list): List of book information.
        category (str): Category name.

    Returns:
        None
    """
    soup = initialize_bs(url)
    books = extract_book_list(url, category)
    book_list += books
    section = soup.find("section")
    next_li = section.find("li", class_="next")

    if next_li is not None:
        a = next_li.find("a")
        href = a["href"]
        last_part = url.split("/")[-1]
        url_without_last_part = url.replace(last_part, "")
        next_page_url = url_without_last_part + href
        scrape_page(next_page_url, book_list, category)
    else:
        csv_filename = category + ".csv"
        csv_file_path = main_directory / csv_filename
        csv_file_path.touch()
        save_csv_file(book_list, csv_file_path)


def extract_category_urls(base_url: str) -> None:
    """
    Extracts the URLs of categories.

    Args:
        base_url (str): Base URL of the website.

    Returns:
        None
    """
    soup = initialize_bs(base_url)
    div_container_fluid = soup.find("div", class_="container-fluid")
    div_side_categories = div_container_fluid.find("div", class_="side_categories")
    ul_nav = div_side_categories.find("ul", class_="nav")
    ul = ul_nav.find("ul")
    li_list = ul.find_all("li")

    for category_item in li_list:
        a = category_item.find("a")
        category_name = a.text
        cleaned_category_name = category_name.replace(' ', "")
        cleaned_category_name_2 = cleaned_category_name.replace('\n', "")
        href = a["href"]
        category_url = BASE_URL + href
        print("Téléchargement en cours de la catégorie: " + cleaned_category_name_2)
        scrape_page(category_url, book_list, cleaned_category_name_2)
    print("Téléchargement terminé")


def main_menu():
    """ Main menu for launching programs.
    Returns:
            None
    """
    user = input("Veuillez faire votre choix: ")
    try:
        user_int = int(user)
        if user_int == 1:
            extract_category_urls(BASE_URL)
            main_menu()
        elif user_int == 2:
            zip_folder()
            main_menu()
        elif user_int == 3:
            print("Au revoir")
            exit()
        else:
            print("Veuillez entrer un nombre entre 1 et 3")
    except ValueError:
        print("Veuillez mettre un nombre entre 1 et 3")


book_list = []
main_directory = create_main_directory()
menu.display_menu()
main_menu()
