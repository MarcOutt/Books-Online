[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

![Python Version](https://img.shields.io/badge/Python-3.7-blue.svg)![BeautifulSoup Version](https://img.shields.io/badge/BeautifulSoup-4.9-green.svg)![Requests Version](https://img.shields.io/badge/Requests-2.25.1-orange.svg)
# Books Online - Système de Surveillance des Prix

## Table des matières
---------------------

* [Introduction](#introduction)
* [Exigences du système de surveillance des prix](#exigences-du-système-de-surveillance-des-prix)
* [Pré-requis](#pré-requis)
* [Installation](#installation)
* [Utilisation](#utilisation)


## Introduction
----------------

Le projet Books Online est un système de surveillance des prix de livres sur le site "Books to Scrape". Ce programme Python permet de récupérer différentes informations concernant les livres d'une catégorie, telles que l'URL de la page du produit, le code universel du produit (UPC), le titre, les prix incluant et excluant la taxe, le nombre disponible, la description du produit, la catégorie, la note de la revue et l'URL de l'image du livre.

Ce projet est divisé en plusieurs phases progressives pour étendre ses fonctionnalités :

* **Phase 1** : Extraire les informations d'une page produit spécifique et les enregistrer dans un fichier CSV.
* **Phase 2** : Récupérer les informations de tous les livres d'une catégorie et les enregistrer dans un fichier CSV unique.
* **Phase 3** : Extraire les informations de tous les livres appartenant à toutes les catégories du site et les enregistrer dans des fichiers CSV distincts pour chaque catégorie.
* **Phase 4** : Télécharger et enregistrer le fichier image de chaque page produit visitée.

## Exigences du système de surveillance des prix
-----------------------------------------------

Le projet a été conçu pour satisfaire aux exigences suivantes :

* Extraire les informations d'une page produit spécifique, y compris l'URL, l'UPC, le titre, les prix, la disponibilité, la description, la catégorie, la note de la revue et l'URL de l'image.
* Récupérer les informations de tous les livres d'une catégorie et les enregistrer dans un fichier CSV.
* Extraire les informations de tous les livres de toutes les catégories du site et les enregistrer dans des fichiers CSV distincts pour chaque catégorie.
* Télécharger et enregistrer le fichier image de chaque page produit visitée.

## Pré-requis
-------------

Avant de pouvoir utiliser le projet Books Online, assurez-vous de disposer des éléments suivants :

* Python 3 installé sur votre système : [Téléchargement Python 3](https://www.python.org/downloads/)
* Git installé sur votre système : [Téléchargement Git](https://git-scm.com/book/fr/v2/D%C3%A9marrage-rapide-Installation-de-Git)


## Installation
------------------

1. Téléchargez le projet sur votre répertoire local : 
```
git clone https://github.com/MarcOutt/OC_p12.git
```

2. Mettez en place un environnement virtuel :
   * Créez l'environnement virtuel: `python -m venv venv`
   * Activez l'environnement virtuel :
       * Windows : `venv\Scripts\activate.bat`
       * Unix/MacOS : `source venv/bin/activate`

3. Installez les dépendances du projet :

```
pip install -r requirements.txt
```


## Utilisation
-------------------

* Lancez le programme à partir de votre terminal.
* Faites un choix parmi les options suivantes : 
    1. Extraire les livres par catégorie
    2. Créer un dossier zip de l'extraction
    3. Quitter l'application
* Tapez sur le chiffre correspondant à votre choix et appuyez sur "Entrée".
* Si vous choisissez l'option 1, un fichier CSV sera créé avec toutes les informations des livres à l'intérieur.
* Si vous choisissez l'option 2, un fichier zip sera créé.
* Si vous choisissez l'option 3, le programme s'arrêtera.
