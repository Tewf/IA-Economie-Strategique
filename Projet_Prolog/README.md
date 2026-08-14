# Projet Prolog — IA stratégique en jeu concurrentiel

Un agent en **Prolog** conçu pour jouer à un jeu concurrentiel répété, puis
confronté aux agents d'autres étudiants lors d'un tournoi.

🎯 Ce projet semestriel est ici parce qu'il constitue le pendant appliqué de la
question du stage : dans un jeu où chaque agent cherche à maximiser son gain,
vers quel équilibre stratégique les comportements convergent-ils réellement ?

## Contenu

| Fichier | Description |
|---|---|
| [`Code.pl`](Code.pl) | L'agent Prolog complet, utilisable en tournoi |
| [`Algorithme_Explication.pdf`](Algorithme_Explication.pdf) | Fonctionnement de l'IA : logique, stratégie, inspiration théorique |
| [`Convergence des stratégies dans un jeu répété/`](<Convergence des stratégies dans un jeu répété>) | Étude de la convergence des comportements stratégiques — notebook d'analyse d'équilibre et documents associés |

L'énoncé officiel du projet appartient au cours qui l'a produit et n'est pas
redistribué ici ; voir le [NOTICE](../NOTICE).

## Objectifs

- Développer une IA compétitive en Prolog.
- Étudier vers quel équilibre convergent les comportements stratégiques
  (Nash, coopération, domination).
- Mettre les résultats expérimentaux en regard des travaux du stage sur l'IA
  et les comportements stratégiques en économie.

### 💡 Remarque

> Dans la **version 2** du jeu, bien que les gains soient cumulés et visibles,
> chercher à en tirer un avantage direct rend l'IA **prévisible**, donc
> pénalisable : les autres agents peuvent en profiter.
