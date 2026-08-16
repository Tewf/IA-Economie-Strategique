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

Le stage s'est terminé en avril 2025. Deux dossiers prolongent le rapport plutôt
que d'ouvrir autre chose, et tous deux jouent les jeux du rapport : le dilemme
du prisonnier sous ses formes itérée et séquentielle, le jeu de l'ultimatum
d'Özkes et al. (2024), et le jeu du dictateur des diapositives de soutenance.

| | |
|---|---|
| <img src="mirror_neurons/results/standings.png" width="320" alt="L'agent imitateur termine huitième sur huit"> | **[`mirror_neurons/`](mirror_neurons/README.fr.md), lancé et analysé.** Observer une action multiplie son poids puis renormalise, et le rapport attend que le Tit-for-Tat en émerge sans avoir été programmé. Face à sept adversaires issus de la littérature, **il n'en est rien : sur des matchs de 10 à 100 tours, l'agent termine huitième sur huit, derrière un tirage à pile ou face.** Ce que la mise à jour implémente est un appariement de fréquences, dont l'état tient en un couple de compteurs et ne peut donc pas dépendre du dernier tour. Il ne dépasse le tirage à pile ou face que sur des matchs de plusieurs centaines de tours, en se figeant en joueur constant plutôt qu'en rendant la pareille. |
| | **[`llm/`](llm/README.fr.md), des fondations.** Homo silicus, que le rapport cite dans sa conclusion sans jamais l'appliquer. Cinq modèles à poids ouverts, localement et hors ligne, sur les mêmes jeux. Rien n'a encore été lancé. |

**Sur la question posée en haut de cette page**, le mécanisme des neurones
miroirs entretient la coopération tacite, sans jamais la rompre ni l'intensifier.
Deux imitateurs forment une boucle de rétroaction à deux états absorbants et
rien entre les deux : sur 700 parties, ils se sont figés sur la défection
mutuelle ou sur la coopération mutuelle selon leur point de départ, et jamais
sur autre chose. **Cette** règle d'imitation est un cliquet sur la condition initiale plutôt
qu'une voie vers la collusion, ce qui la sépare des Q-learners de Calvano et al.
(2020), qui trouvent la collusion, eux, en lisant les gains.
[La lecture complète](mirror_neurons/README.fr.md#ce-que-tout-cela-donne), et
ce qui la modifierait.

Les deux dossiers sont frères à dessein, et la portée de ce rapprochement est
étroite : ce rapport a proposé ce mécanisme et affirmé que le Tit-for-Tat en
émerge, donc les deux moitiés éprouvent cette affirmation sur les mêmes
adversaires avec une seule mesure. Asseoir des modèles de langage à côté de
stratégies classiques n'est pas en soi une nouveauté. Les deux joueurs exposent
les deux mêmes méthodes, donc un seul banc d'essai peut accueillir l'un ou l'autre, et la
comparaison intéressante oppose un mécanisme qui ne sait qu'imiter à un autre
qui sait aussi parler et se justifier. Le cheap talk et l'explicabilité sont
deux des huit notions que le rapport définit, et les deux que l'agent hebbien
n'a aucun moyen d'atteindre.

Une analyse d'équilibre se trouvait ici également. Elle est partie avec le
projet Prolog du cours dont elle étudie le jeu, dans
[University-Coursework](https://github.com/Tewf/University-Coursework/tree/main/Bachelor/SecondSemestreLanguage/Prolog/StrategyTournament).
Ce jeu n'apparaît pas dans le rapport de stage.

## Crédits

Les articles publiés sont référencés et non redistribués. Voir
[NOTICE](original/NOTICE), celui rendu avec le stage et conservé sans
modification : il mentionne donc encore le projet Prolog du cours, qui a depuis
quitté ce dépôt.

Un manque à signaler : Ng (2023), *When communicative AIs are cooperative
actors*, est résumé dans `original/Litterature/Summary/` et analysé dans le
rapport, mais n'apparaît pas dans la bibliographie de ce dossier. Celle-ci liste
neuf articles ; celui-ci en est un dixième.
