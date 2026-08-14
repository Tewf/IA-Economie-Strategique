# IA & tarification stratégique — stage de recherche au GAEL

> [Read in English](README.md)

L'intelligence artificielle rend-elle la collusion *plus* ou *moins* probable ?

Ce dépôt rassemble le travail réalisé lors d'un stage de recherche au **GAEL**
(Grenoble Applied Economics Laboratory, UGA / INRAE), portant sur la capacité
d'agents artificiels à soutenir des comportements coopératifs dans des jeux de
concurrence par les prix répétés — le cadre où la collusion tacite apparaît
chez les humains.

| | |
|---|---|
| **Stagiaire** | Mohamed Hamlil, L2 MIASHS, Université Grenoble Alpes |
| **Encadrants** | Alexis Garapin (UGA) et Olivier Bonroy (INRAE) |
| **Laboratoire** | GAEL — Grenoble Applied Economics Laboratory |
| **Période** | 23 janvier – 14 avril 2025 |

## La question

Dans un jeu de prix répété, les joueurs humains convergent souvent vers des prix
tacitement collusifs plutôt que vers l'équilibre concurrentiel. Si la
tarification est déléguée à des algorithmes, cette tendance subsiste-t-elle,
disparaît-elle, ou s'intensifie-t-elle ? Le stage aborde la question par trois
voies : la littérature d'économie expérimentale, un modèle théorique de
l'imitation, et un agent en fonctionnement.

## Contenu

| Chemin | Description |
|---|---|
| [`RapportDeStageFinal.pdf`](RapportDeStageFinal.pdf) | **Le rapport de stage** — commencer ici |
| [`Presentation.pdf`](Presentation.pdf) | Diapositives de la soutenance |
| [`Litterature/`](Litterature/) | Bibliographie annotée, et mes notes de lecture dans `Summary/` sur quatre des articles |
| [`Neurones_Mirroirs/`](Neurones_Mirroirs/) | Les neurones miroirs comme mécanisme des comportements mimétiques et coopératifs — démarche rédigée et implémentation Jupyter |
| [`Projet_Prolog/`](Projet_Prolog/) | Un agent Prolog pour un jeu concurrentiel répété, confronté aux agents d'autres étudiants lors d'un tournoi, et une étude de l'équilibre stratégique vers lequel les comportements convergent |

Le projet Prolog est un projet semestriel mené en parallèle ; il figure ici
parce qu'il constitue le pendant appliqué de la question théorique du stage :
vers quelle stratégie un agent artificiel converge-t-il réellement lorsqu'il
cherche à maximiser son gain face à d'autres qui font de même.

## Crédits

Les articles publiés cités dans [`Litterature/`](Litterature/README.md) sont
référencés et non redistribués, et l'énoncé du projet Prolog appartient à son
cours. Voir [NOTICE](NOTICE).
