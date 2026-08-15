# Comparaison d’un nouvel équilibre (Stage_test) avec l’équilibre de Nash

Ce dépôt présente une étude autour d’un équilibre que nous appelons **Stage_test**, formulé dans le cadre d’un jeu stratégique inspiré de la théorie des jeux. Nous expliquons sa construction dans Stage_test.pdf, puis une analyse dans Equilibrium_Analysis.

L’équilibre Stage_test et Nash ont été déterminé dans la **version 1** du jeu, puis testé dans la **version 2** contre d’autres algorithmes développés par des étudiants.

Les résultats de ces confrontations sont disponibles dans data2, issu d’un tournoi d’algorithmes.

## 📊 Résultats expérimentaux

### Scores cumulés – Stage_test

| Score_IA | Score_Adversaire | Nom de l’adversaire |
|----------|------------------|----------------------|
| 2644     | 2780             | lesCowBoys           |
| 1953733  | 491400           | lesStrateges         |
| 234      | 378              | naenae               |
| 4196006  | 1400353          | syntax_terror        |
| 341      | 523              | un_pain_pita         |
| 6000     | 4194467          | youxi                |

### Scores cumulés – Équilibre de Nash

| Score_IA | Score_Adversaire | Nom de l’adversaire |
|----------|------------------|----------------------|
| 661      | 1414             | stage_test           |
| 16849    | 9821             | lesCowBoys           |
| 2121     | 30494            | lesStrateges         |
| 371      | 468              | naenae               |
| 391899   | 97754            | syntax_terror        |
| 596      | 930              | un_pain_pita         |
| 427361   | 904060           | youxi                |

## 🗂 Structure du dépôt

- `data2/` : résultats des confrontations  
- `stage_test/` : définition l’équilibre proposé  
- `Equilibrium_Analysis/` : code de l’équilibre proposé  
- `README.md` : ce fichier

