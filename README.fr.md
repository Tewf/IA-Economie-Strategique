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

## Ce qu'il a produit

| | |
|---|---|
| <img src="tournament/leaderboard.png" width="300" alt="Seize agents classés par score cumulé"> | **[7e et 8e sur 16](tournament/)** au tournoi d'avril 2025, L2 MIASHS UGA, face à treize agents d'autres étudiants. `stage_test` marque 6 163 877 et `nash_equilibrium` 1 490 429. Six agents les devancent, les trois premiers de plus de cinquante ordres de grandeur. |
| <img src="equilibrium/equilibrium_comparison.png" width="300" alt="Le match, et ce qu'il coûte"> | **[La stratégie bat Nash en tête-à-tête](equilibrium/)**, 3,5552 contre 3,1521. Elle le fait en cédant du gain absolu : face au même adversaire, jouer Nash rapporte 3,8889. Gagner un match et marquer le plus de points sont deux objectifs distincts, d'où la 7e place. |
| <img src="mirror_neurons/update_shape.png" width="300" alt="La mise à jour est logistique"> | **[L'imitation comme mise à jour de poids](mirror_neurons/)**. Observer une action multiplie son poids puis renormalise, et le Tit-for-Tat émerge sans avoir été programmé. Six figures, rejouées et graine fixée. |

Les constantes des deux agents engagés sortent directement du notebook
d'équilibre, arrondies. L'analyse et le Prolog soumis sont le même objet, ce qui
est la meilleure preuve ici que le travail se tient de bout en bout.

## Comment ce dépôt est organisé

Deux couches. Le stage est conservé exactement tel qu'il a été rendu, et les
corrections sont posées à côté plutôt que par-dessus.

| | |
|---|---|
| [`original/`](original/) | Tout ce qui a été rendu en mai 2025, octet pour octet : rapport, diapositives, bibliographie, agents Prolog, notebooks. Rien de modifié, y compris ce qui est faux, que ce dossier recense |
| [`equilibrium/`](equilibrium/) | L'analyse d'équilibre recalculée avec la bonne condition |
| [`mirror_neurons/`](mirror_neurons/) | La simulation rejouée pour qu'elle se termine, avec graine fixée et figures légendées |
| [`tournament/`](tournament/) | Le classement, qui se trouvait page 1 d'un journal de 636 pages |

Les corrections ne renversent pas les conclusions du stage. Le résultat en
tête-à-tête tient et se reproduit exactement. Ce qui change, c'est que la
dérivation derrière lui a été refaite avec une condition correcte sur un
simplexe, que les affirmations non étayées par le code sont nommées, et que les
résultats enfouis sont visibles.

## Ordre de lecture

1. [`original/RapportDeStageFinal.pdf`](original/RapportDeStageFinal.pdf), le
   rapport, neuf pages
2. [`tournament/`](tournament/) pour ce que les agents ont fait
3. [`equilibrium/`](equilibrium/) pour l'analyse qui les sous-tend
4. [`original/Litterature/`](original/Litterature/) pour l'état de l'art, sous
   forme de résumés rédigés à partir des articles et non des articles eux-mêmes

## Crédits

Les articles publiés sont référencés et non redistribués, et l'énoncé du projet
Prolog appartient à son cours. Voir [NOTICE](original/NOTICE).

Un manque à signaler : Ng (2023), *When communicative AIs are cooperative
actors*, est résumé dans `original/Litterature/Summary/` et analysé dans le
rapport, mais n'apparaît pas dans la bibliographie de ce dossier. Celle-ci liste
neuf articles ; celui-ci en est un dixième.
