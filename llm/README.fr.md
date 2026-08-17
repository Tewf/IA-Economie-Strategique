# Les LLM comme joueurs

> [Read in English](README.md)

> **La grille a été jouée : 220 matchs, cinq modèles, le 2026-08-17.** Les
> chiffres sont dans [Ce que la grille a trouvé](#ce-que-la-grille-a-trouvé) et
> les tableaux dans [`results/`](results/). Tout ce qui se déduit du journal brut
> en est redérivé à chaque poussée.

Le stage a lu Horton, Filippas et Manning (2023) et nomme l'homo silicus dans sa
conclusion. Il ne l'a jamais appliqué. Ce dossier est cette méthode, sur des
modèles assez petits pour tourner sur cette machine, jouant les jeux que le
cadre du rapport définit.

C'est le frère de [`../mirror_neurons/`](../mirror_neurons/README.fr.md), à
dessein. `OllamaPlayer` expose `observe_and_learn` et `select_action`, les deux
mêmes méthodes que `HebbianMirrorNeuronAgent` : un même banc d'essai peut donc
accueillir l'un ou l'autre. Tous deux mesurent la réciprocité avec
[`../reciprocity.py`](../reciprocity.py), placé à la racine pour qu'une seule
définition serve aux deux et que la comparaison ne puisse pas dériver.

## La question à laquelle le dispositif doit répondre

Deux imitateurs conservent le régime où on les a placés, 700 parties sur 700
([`../mirror_neurons/results/self_play_lock_in.csv`](../mirror_neurons/results/self_play_lock_in.csv)).
Ils n'ont aucun canal pour un message, et rien sur quoi un message pourrait agir.

Un modèle de langage a ce canal gratuitement. Donc : **placer deux modèles dans
un régime qu'ils n'ont pas choisi, et voir si un message non contraignant leur
permet d'en sortir.** Chaque paire commence sur un tour de coopération mutuelle,
un tour de défection mutuelle, ou rien du tout, avec et sans cheap talk.

**La moitié de cela est une réplication, et se présente comme telle.** Injecter
un historique coopératif synthétique est le volet *memory sanitization* de
[The Memory Curse](https://arxiv.org/abs/2605.08060), qui a montré qu'il
restaure la coopération, et le fait que le cheap talk augmente la coopération
des modèles de langage est établi par ailleurs. Ce qui reste introuvable, c'est
l'injection symétrique, celle d'un historique de défection, croisée avec le
canal, et mesurée contre un mécanisme qui ne peut démontrablement pas en sortir.
Ce que ce dossier peut et ne peut pas affirmer, et la référence à laquelle se
comparer, sont dans
[`design-notes/what-is-already-known/`](design-notes/what-is-already-known/).

## Ce que la grille a trouvé

220 matchs joués le 2026-08-17, 210 lisibles et 10 perdus, tous phi3:mini. Taux
de coopération en auto-affrontement sur 30 tours, 4 matchs par cellule :

| modèle | neutre, silence | neutre, cheap talk | ouverture coopérative, silence | coopérative, cheap talk | **défection imposée, silence** | **défection imposée, cheap talk** |
|---|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 1,00 | 1,00 | 1,00 | 1,00 | **0,00** | **1,00** |
| mistral:7b | 1,00 | 1,00 | 1,00 | 1,00 | **0,99** | **0,74** |
| gemma3:4b | 0,89 | 1,00 | 0,76 | 1,00 | **0,00** | **0,00** |
| qwen3:8b | **0,00** | 1,00 | 1,00 | 1,00 | **0,00** | **0,00** |
| phi3:mini | 0,58 | 1,00 | 0,57 | 0,95 | 0,54 | 0,91 |

**Trois des quatre modèles lisibles sont entièrement capturés par un régime
qu'ils n'ont pas choisi.** Placés sur une ouverture de défection mutuelle sans
canal, qwen2.5, gemma3 et qwen3 font défection sur les 30 tours, 4 matchs sur 4,
taux de coopération exactement nul. C'est le cliquet de l'imitateur reproduit
dans un modèle de langage.

**Un message non contraignant brise cette capture chez exactement un des trois.**
qwen2.5 passe de 0,00 à 1,00, 4 fois sur 4. gemma3 et qwen3 ne bougent pas d'un
pouce. Et mistral n'est jamais capturé : il sort de l'ouverture défective en
silence, 0,99, et le message *abaisse* ce chiffre à 0,74.

La réponse à la question posée plus haut est donc que deux agents parlants
peuvent sortir d'un régime imposé, mais que **le canal n'est ni nécessaire ni
suffisant** : mistral en sort sans canal, gemma3 et qwen3 y restent avec. Quels
modèles en sont capables est un fait sur les modèles, rapporté comme les notes de
conception l'exigent : une variation entre modèles, présentée comme une variation
entre modèles, et non comme une propriété des modèles de langage.

**Le silence n'est pas un traitement unique non plus.** qwen3:8b fait défection
sur les 30 tours depuis une ouverture *neutre* en silence, 4 fois sur 4, là où
tous les autres coopèrent. Pour ce modèle, le cheap talk n'est pas ce qui permet
de sortir d'un régime défectif : c'est ce qui empêche qu'il se forme. gemma3 est
instable de la même manière, 2 de ses 4 matchs silencieux partis d'une ouverture
coopérative dégénérant en défection mutuelle. Là où le cheap talk n'affronte pas
une ouverture imposée, il stabilise parfaitement : 1,00 partout.

### Contre les stratégies d'Axelrod

Score par tour, modèle d'abord, mêmes cinq adversaires et même indice de
réciprocité que [`../mirror_neurons/`](../mirror_neurons/README.fr.md), pour que
les deux moitiés forment un seul tableau :

| modèle | Tit For Tat | Grudger | Win-Stay Lose-Shift | Defector | Alternator |
|---|---|---|---|---|---|
| qwen2.5:7b-instruct | 3,00 - 3,00 | 3,00 - 3,00 | 3,00 - 3,00 | 0,95 - 1,20 | 2,20 - 2,37 |
| mistral:7b | 3,00 - 3,00 | 3,00 - 3,00 | 3,00 - 3,00 | **0,41 - 3,37** | 1,50 - 4,00 |
| gemma3:4b | 2,80 - 2,76 | 2,80 - 2,76 | 3,00 - 2,71 | 0,97 - 1,13 | 1,50 - 4,00 |
| qwen3:8b | **1,13 - 0,97** | 1,13 - 0,97 | **3,00 - 0,50** | 1,00 - 1,00 | **3,00 - 0,50** |
| phi3:mini | 2,43 - 2,38 | 0,73 - 3,35 | 2,07 - 2,65 | 0,42 - 3,33 | 1,98 - 2,73 |

Les deux mêmes dispositions que les cellules d'auto-affrontement. qwen2.5 et
mistral tiennent le 3,00 mutuel contre tout réciprocateur ; qwen3 ne coopère avec
rien (0,00 contre les cinq), ce qui lui rapporte 3,00 contre 0,50 face aux deux
stratégies exploitables et lui coûte 1,13 face aux vindicatives que les
coopérateurs exploitent à 3,00. Reconnaître un défecteur pur sépare de nouveau le
panel : qwen2.5 et gemma3 cessent d'alimenter Defector (0,05 et 0,03 de
coopération), tandis que **mistral coopère avec lui 59 % du temps, lui offrant
3,37 par tour pour 0,41 gagné** — la pire cellule de la grille.

### La raison annoncée correspond-elle au coup joué

Le prompt demande une raison. Sur les tours dont le raisonnement nomme une
action, fréquence à laquelle le coup s'y conforme : qwen3 0,996 (1359 tours),
gemma3 0,937 (1303), qwen2.5 0,935 (1000), phi3 0,695 (511), **mistral 0,630
(478)**. mistral contredit son propre raisonnement dans 37 % des tours où il en
énonce un, ce qui, avec ses 938 lectures indulgentes, est la réserve attachée à
chacun de ses chiffres ci-dessus.

### Deux réserves qui font partie du résultat

- **phi3:mini est rapporté comme illisible, non comme un résultat.** 10 matchs
  sur 44 perdus à une moyenne de 16,2 tours, aucune condition silencieuse ne se
  stabilisant, et un prompt le plus long à 8023 tokens contre les 8192 demandés —
  **169 tokens de marge**, là où mistral en avait 5540 et qwen3 6211. Il est
  passé à 169 tokens de redéclencher la troncature qui avait invalidé un run
  antérieur.
- **Le panel est de cinq modèles de 4B à 8B sur une carte de 8 Go.** Là où ces
  résultats diffèrent de Horton et al. ou de Bauer et al., la taille des modèles
  reste une explication vivante, impossible à écarter depuis ce dépôt.

L'effet d'ordre des gains observé au premier stage contre Alternator ne se
généralise pas au panel : gemma3 et mistral sont exploités dans les deux ordres,
qwen3 l'exploite dans les deux. Il reste rapporté pour ce qu'il a toujours été :
la preuve que contrebalancer l'ordre des gains valait la peine, une instance de
Fish, Gonczarowski et Shorrer (2024), et non un résultat sur les modèles de
langage.

## Ce qui s'exécute, et ce que cela coûte

```sh
export PYTHONPATH=.
python llm/preflight_checks.py            # hors ligne, sans rien, ~2 secondes
python llm/run_experiment.py --plan       # la grille, sans la jouer
python llm/preflight_checks.py --online   # test de fumée, 5 modèles, via Ollama
python llm/run_experiment.py              # la grille. Des heures. Reprenable
python llm/run_analysis.py && python llm/plot_results.py   # hors ligne
```

220 matchs de 30 tours : 120 en auto-affrontement sur trois ouvertures et les
deux conditions, et 100 contre les cinq stratégies Axelrod que l'agent hebbien a
également affrontées. 13 800 appels de modèle. C'est le test de fumée qui
transforme ce chiffre en estimation honnête, car il mesure la cadence par modèle
sur cette carte au lieu de la supposer, et le 17 août 2026 il a chiffré la
grille à **3,3 h**. La grille a ensuite demandé **4,81 h de temps de match**
sommées depuis le journal, plus les refroidissements entre matchs et entre
stages. L'estimation était basse par modèle, et l'ordre se trompait sur le modèle
bon marché : phi3:mini a été le plus coûteux des cinq, 1,67 h pour ses 44 matchs
contre 0,89 h à qwen3:8b, ses prompts étant longs et dix de ses matchs ayant
consommé des tours avant d'échouer au parsing.

**Ne pas lancer la grille si quoi que ce soit d'autre veut le GPU.** Un seul
modèle tient à la fois, et enchaîner les changements en boucle serrée est ce qui
a mis cette machine à terre le 15 août 2026.

## Pourquoi le journal brut et les tables sont séparés

`results/matches.jsonl` contient une ligne par match terminé, chaque réponse
entière, le raisonnement conservé à part de la réponse. Il coûte des heures de
carte et n'est jamais régénéré. Chaque CSV à côté en est dérivé par
[`measurements.py`](measurements.py), qui n'est que de l'arithmétique :
l'intégration continue les redérive à chaque poussée et échoue à la moindre
différence. Le dossier hebbien obtient cette garantie en rejouant le tournoi ;
celui-ci ne le peut pas, alors il l'obtient en gardant la moitié coûteuse brute
et la moitié vérifiable bon marché.

Cette séparation rend aussi la campagne reprenable : chaque match a une clé, et
une clé déjà présente dans le journal est ignorée. Une panne ne coûte que le
match en cours.

## Les fichiers

| | |
|---|---|
| [`ollama_player.py`](ollama_player.py) | Le joueur. Dialogue avec Ollama, conserve chaque réponse entière, et lit la ligne `ACTION:` au lieu de deviner d'après la prose |
| [`bot_opponent.py`](bot_opponent.py) | Une stratégie Axelrod assise comme joueur, pour que modèles et imitateur affrontent les mêmes adversaires |
| [`iterated_game.py`](iterated_game.py) | La boucle de match. Le cheap talk est simultané : les deux écrivent à l'aveugle, puis entendent, puis agissent |
| [`stub_player.py`](stub_player.py) | Un joueur scripté, pour que tout ce qui précède se teste carte éteinte |
| [`panel_config.py`](panel_config.py) · [`grid_config.py`](grid_config.py) | Les cinq modèles et leur échantillonnage ; les matchs à jouer |
| [`prompt_loader.py`](prompt_loader.py) | Rend une invite en contrebalançant l'ordre des gains d'une répétition à l'autre |
| [`run_experiment.py`](run_experiment.py) · [`run_analysis.py`](run_analysis.py) · [`plot_results.py`](plot_results.py) | Jouer la grille ; dériver les tables ; tracer les figures |
| [`machine_gate.py`](machine_gate.py) · [`run_ownership.py`](run_ownership.py) | Si cette machine peut encaisser un match de plus, et qui tient la carte pendant ce temps. Les deux sont autant des comptes rendus d'incident que du code |
| [`preflight_checks.py`](preflight_checks.py) | Dix-neuf vérifications hors ligne et le test de fumée. Refuse de démarrer tant que le banc d'essai n'a pas fait ses preuves |
| [`prompts/`](prompts/) | Un scénario par jeu. Dans cette méthode, l'invite est l'expérience |
| [`design-notes/`](design-notes/) | Ce que la méthode peut montrer et ce qu'elle ne peut pas, et pourquoi le cheap talk et l'explicabilité sont l'enjeu |

## Ce qui manque délibérément

Les bancs d'essai de l'ultimatum et du dictateur. Leurs invites sont écrites, car
le texte du scénario est la part qui mérite discussion, mais les boucles de jeu
ne le sont pas : ces deux jeux servent aussi à
[`../mirror_neurons/`](../mirror_neurons/README.fr.md), et leur donner un foyer
commun est une décision de structure plutôt qu'un fichier à expédier. Voir
[`../mirror_neurons/design-notes/what-the-agent-cannot-do.md`](../mirror_neurons/design-notes/what-the-agent-cannot-do.md),
où le jeu du dictateur est le cas qui sépare les deux dossiers : l'imitateur y
est muet, un modèle ne l'est pas.

Les notes de conception et les invites restent en anglais : traduire une invite
changerait l'expérience que mènent les modèles.

## Crédits

Horton, Filippas et Manning (2023) est la référence 5 du stage lui-même,
résumée dans `../original/Litterature/Summary/`. Fish, Gonczarowski et Shorrer
(2024) ainsi que Calvano et al. (2020) sont des lectures ultérieures, hors
travail de stage. Les citations complètes sont dans
[`design-notes/homo-silicus.md`](design-notes/homo-silicus.md).
