# Les LLM comme joueurs

> [Read in English](README.md)

> **Le banc d'essai est prêt et l'expérience n'a pas été lancée.** Chaque appel
> de modèle demande le GPU : rien ici n'y a touché. Ce qui est vérifié, c'est
> tout ce qui relève de la logique plutôt que du modèle, et ce l'est à chaque
> poussée.

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
[`design-notes/what-is-already-known.md`](design-notes/what-is-already-known.md).

## Ce qui s'exécute, et ce que cela coûte

```sh
export PYTHONPATH=.
python llm/preflight_checks.py            # hors ligne, sans rien, ~2 secondes
python llm/run_experiment.py --plan       # la grille, sans la jouer
python llm/preflight_checks.py --online   # test de fumée, 5 modèles, via Ollama
python llm/run_experiment.py              # la grille. Des heures. Reprenable
python llm/run_analysis.py && python llm/plot_results.py   # hors ligne
```

275 matchs de 30 tours : 150 en auto-affrontement sur trois ouvertures et les
deux conditions, et 125 contre les cinq stratégies Axelrod que l'agent hebbien a
également affrontées. 17 250 appels de modèle. C'est le test de fumée qui
transforme ce chiffre en estimation honnête, car il mesure la cadence par modèle
sur cette carte au lieu de la supposer.

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
| [`preflight_checks.py`](preflight_checks.py) | Douze vérifications hors ligne et le test de fumée. Refuse de démarrer tant que le banc d'essai n'a pas fait ses preuves |
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
