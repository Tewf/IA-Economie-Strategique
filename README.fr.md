# IA & tarification stratégique : stage de recherche au GAEL

[![CI](https://github.com/Tewf/IA-Economie-Strategique/actions/workflows/ci.yml/badge.svg)](https://github.com/Tewf/IA-Economie-Strategique/actions/workflows/ci.yml)
[![Site](https://img.shields.io/badge/pages-tewf.github.io%2FIA--Economie--Strategique-1f6feb)](https://tewf.github.io/IA-Economie-Strategique/index.fr.html)

> [Read in English](README.md)

> [!TIP]
> **Consultable comme un site :
> [tewf.github.io/IA-Economie-Strategique](https://tewf.github.io/IA-Economie-Strategique/index.fr.html)**
> Les résultats et les figures sur une seule page, avec le rapport et les
> diapositives qui s'ouvrent dans le navigateur au lieu de se télécharger.

Dans un jeu de prix répété, les joueurs humains convergent vers des prix
tacitement collusifs plutôt que vers l'équilibre concurrentiel. Savoir si les
algorithmes soutiennent ce comportement, le brisent ou l'intensifient est une
question ouverte en économie industrielle, aux conséquences directes pour la
politique de la concurrence.

Un stage de recherche au **GAEL** (Grenoble Applied Economics Laboratory,
UGA / INRAE) consacré à cette question : état de l'art, modélisation du
mécanisme d'imitation qui pourrait sous-tendre la coopération, et construction
d'agents pour l'observer.

**Le stage ne tranche pas la question**, et son rapport est une étude plutôt
qu'une conclusion. Ce qu'il a produit est ci-dessous, avec les chiffres
réellement atteints.

| | |
|---|---|
| **Stagiaire** | L2 MIASHS, Université Grenoble Alpes |
| **Encadrants** | Alexis Garapin (UGA) et Olivier Bonroy (INRAE) |
| **Laboratoire** | GAEL, Grenoble Applied Economics Laboratory |
| **Dates** | 23 janvier au 14 avril 2025 |

## Le stage, tel qu'il a été rendu

Tout ce qui a été rendu en mai 2025 se trouve dans [`original/`](original/),
octet pour octet. Rien n'y a été modifié, y compris ce qui est faux, que
[ce dossier recense](original/README.md) au lieu de le corriger en silence.

| | |
|---|---|
| [`RapportDeStageFinal.pdf`](original/RapportDeStageFinal.pdf) | Le rapport, neuf pages. À lire en premier |
| [`Presentation.pdf`](original/Presentation.pdf) | Les diapositives de soutenance, 23 pages |
| [`Litterature/`](original/Litterature/) | L'état de l'art, sous forme de résumés rédigés à partir des articles et non des articles eux-mêmes |
| [`Neurones_Mirroirs/`](original/Neurones_Mirroirs/) | Les neurones miroirs comme mécanisme de coopération par imitation, rédaction et simulation |

## Ce qui a suivi, sur mon temps libre

Le stage s'est terminé en avril 2025. Deux morceaux méritaient d'y revenir en
dehors : un équilibre dont la dérivation n'implémentait pas la définition
annoncée, et une simulation qu'on ne pouvait pas exécuter de bout en bout. Les
deux sont refaits à côté de `original/` plutôt que par-dessus.

| | |
|---|---|
| <img src="equilibrium/equilibrium_comparison.png" width="300" alt="Le match, et ce qu'il coûte"> | **[La stratégie bat Nash en tête-à-tête](equilibrium/)**, 3,5552 contre 3,1521. Elle le fait en cédant du gain absolu : face au même adversaire, jouer Nash rapporte 3,8889. Gagner l'écart et maximiser son propre total sont deux objectifs distincts, que la rédaction ne séparait pas. |
| <img src="mirror_neurons/update_shape.png" width="300" alt="La mise à jour est logistique"> | **[L'imitation comme mise à jour de poids](mirror_neurons/)**. Observer une action multiplie son poids puis renormalise, et le Tit-for-Tat émerge sans avoir été programmé. Six figures, rejouées et graine fixée. |

Rien de tout cela ne renverse les conclusions du stage. Le résultat en
tête-à-tête tient et se reproduit exactement. Ce qui change, c'est que la
dérivation derrière lui a été refaite avec une condition correcte sur un
simplexe, que les affirmations non étayées par le code sont nommées, et que les
figures portent enfin les légendes qu'elles calculaient puis jetaient.

## Crédits

Les articles publiés sont référencés et non redistribués. Voir
[NOTICE](original/NOTICE), celui rendu avec le stage et conservé sans
modification : il mentionne donc encore le projet Prolog du cours, qui a depuis
quitté ce dépôt.

Un manque à signaler : Ng (2023), *When communicative AIs are cooperative
actors*, est résumé dans `original/Litterature/Summary/` et analysé dans le
rapport, mais n'apparaît pas dans la bibliographie de ce dossier. Celle-ci liste
neuf articles ; celui-ci en est un dixième.
