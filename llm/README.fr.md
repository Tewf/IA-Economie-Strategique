# Les LLM comme joueurs

> [Read in English](README.md)

> Des fondations. Rien ici n'a été lancé comme expérience et aucun résultat
> n'est versionné. Ce qui existe, c'est le joueur, le panel, le texte des
> scénarios, et les raisons de chacun.

Le stage a lu Horton, Filippas et Manning (2023) et nomme l'homo silicus dans sa
conclusion. Il ne l'a jamais appliqué. Ce dossier est cette méthode, sur des
modèles assez petits pour tourner sur cette machine, jouant les jeux que le
cadre du rapport définit.

C'est le frère de [`../mirror_neurons/`](../mirror_neurons/), à dessein.
`OllamaPlayer` expose `observe_and_learn` et `select_action`, les deux mêmes
méthodes que `HebbianMirrorNeuronAgent` : un même banc d'essai peut donc
accueillir l'un ou l'autre. La différence tient à ce que ces appels signifient,
l'un mettant à jour un poids, l'autre ajoutant un tour à une transcription pour
interroger un modèle.

## Les fichiers

| | |
|---|---|
| [`ollama_player.py`](ollama_player.py) | Le joueur. Dialogue avec Ollama en HTTP et conserve chaque réponse entière |
| [`panel_config.py`](panel_config.py) | Les cinq modèles locaux, leurs tailles et les réglages d'échantillonnage |
| [`prompts/`](prompts/) | Un scénario par jeu. Dans cette méthode, l'invite est l'expérience |
| [`design-notes/`](design-notes/) | Ce que la méthode peut montrer et ce qu'elle ne peut pas, et pourquoi le cheap talk et l'explicabilité sont l'enjeu |

## L'exécuter

Ollama doit tourner. Rien ne quitte la machine et rien ne coûte quoi que ce soit.

```sh
curl -s 127.0.0.1:11434/api/tags     # tout modèle de panel_config.py doit y figurer
python -c "import ollama_player"     # bibliothèque standard seule, aucune installation
```

La carte fait 8 Go : chaque modèle du panel y tient seul, aucun couple n'y tient
à deux, et une exécution sur le panel est donc séquentielle par modèle. Ne pas
en lancer une pendant l'enregistrement d'un cours, ni pendant que Cycles ou
ComfyUI occupe le GPU.

## Ce qui manque délibérément

Les bancs d'essai de l'ultimatum et du dictateur. Leurs invites sont écrites,
car le texte du scénario est la part qui mérite discussion, mais les boucles de
jeu ne le sont pas : ces deux jeux servent aussi à
[`../mirror_neurons/`](../mirror_neurons/), et leur donner un foyer commun est
une décision de structure plutôt qu'un fichier à expédier. Voir
[`../mirror_neurons/design-notes/what-the-agent-cannot-do.md`](../mirror_neurons/design-notes/what-the-agent-cannot-do.md).

Les notes de conception et les invites restent en anglais : traduire une invite
changerait l'expérience que mènent les modèles.

## Crédits

Horton, Filippas et Manning (2023) est la référence 5 du stage lui-même,
résumée dans `../original/Litterature/Summary/`. Fish, Gonczarowski et Shorrer
(2024) ainsi que Calvano et al. (2020) sont des lectures ultérieures, hors
travail de stage. Les citations complètes sont dans
[`design-notes/homo-silicus.md`](design-notes/homo-silicus.md).
