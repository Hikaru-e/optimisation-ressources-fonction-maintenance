## Introduction

Cette application permet d'optimiser l'allocation des tâches de maintenance en fonction des ressources humaines et des outils disponibles. Saisissez les tâches, les ressources humaines et les outils pour voir comment optimiser leur utilisation.

## Fonctionnalités

- **Saisie manuelle des données** : Permet de saisir manuellement les tâches, les ressources humaines, les outils, leurs disponibilités, et les dépendances entre les tâches.
- **Importation des données depuis un fichier CSV** : Permet d'importer toutes les données nécessaires depuis un fichier CSV, ou de les importer séparément pour les tâches, les ressources humaines et les outils.
- **Optimisation des tâches** : Utilise un modèle d'optimisation pour assigner les tâches de manière optimale aux ressources humaines disponibles en respectant les contraintes de disponibilité et les dépendances entre les tâches.
- **Affichage des résultats** : Affiche les résultats sous forme de tableau et de diagramme de Gantt pour visualiser la planification des tâches.

## Installation

1. Clonez le dépôt GitHub :

   git clone https://github.com/Hikaru-e/optimisation-ressources-fonction-maintenance.git` 

2.  Naviguez vers le répertoire du projet :
    
    `cd optimisation-ressources-maintenance` 
    
3.  Installez les dépendances nécessaires :
    
    `pip install -r requirements.txt` 
    

## Utilisation

1.  Lancez l'application Streamlit :

    `streamlit run app.py` 
    
2.  Sélectionnez une option pour importer les données :
    
    -   **Manuel** : Saisissez manuellement les tâches, les ressources humaines et les outils.
    -   **Importer un seul fichier** : Importez un fichier CSV contenant toutes les données nécessaires.
    -   **Importer chaque fichier séparément** : Importez des fichiers CSV séparés pour les tâches, les ressources humaines et les outils.
3.  Cliquez sur le bouton **Optimiser** pour effectuer l'optimisation et afficher les résultats.
    

## Format des fichiers CSV

### Fichier unique

Le fichier CSV doit contenir les colonnes suivantes :

-   `Tâche` : Nom de la tâche
-   `Durée` : Durée de la tâche en heures
-   `Ressource Humaine` : Nom de la ressource humaine
-   `Disponibilité` : Disponibilité de la ressource humaine en heures
-   `Outillage` : Nom de l'outillage
-   `Disponibilité des outils` : Disponibilité de l'outillage en heures
-   `Dépendances` : Tâches prérequises (séparées par des virgules)
-   `Priorité` : Priorité de la tâche (1 à 10)

### Fichier séparé pour les tâches

Le fichier CSV doit contenir les colonnes suivantes :

-   `Tâche` : Nom de la tâche
-   `Durée` : Durée de la tâche en heures
-   `Dépendances` : Tâches prérequises (séparées par des virgules)
-   `Priorité` : Priorité de la tâche (1 à 10)

### Fichier séparé pour les ressources humaines

Le fichier CSV doit contenir les colonnes suivantes :

-   `Ressource Humaine` : Nom de la ressource humaine
-   `Disponibilité` : Disponibilité de la ressource humaine en heures

### Fichier séparé pour les outils

Le fichier CSV doit contenir les colonnes suivantes :

-   `Outillage` : Nom de l'outillage
-   `Disponibilité des outils` : Disponibilité de l'outillage en heures