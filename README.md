# PriceWatch · TP2 : le job sous contrainte

Objectif : faire tenir le job d'import dans 256 Mo de RAM et 1 CPU, en moins de 30 s, sans changer son résultat.
Mesures et justifications : voir `SOBRIETE.md`.

## Commandes utilisées

### Construire l'image

    docker build -t pw-job .

Construit l'image `pw-job` à partir du Dockerfile. À refaire après chaque modification du script (le Dockerfile copie `job/`).

### Générer les données (une seule fois)

    docker run --rm -v "$PWD/data:/data" pw-job python job/generate_history.py

Lance le script dans un conteneur. `-v` branche mon dossier `data/` sur `/data` : le fichier de 231 Mo reste sur ma machine après la fin du conteneur. `--rm` supprime le conteneur ensuite.
Appris : un conteneur est jetable, un volume permet de garder les données.

### Mesurer la ligne de base (sans limite)

    docker run --name pw -v "$PWD/data:/data" pw-job

Appris : 1580 Mo de pic et un ratio CPU / réel de 1,07, donc un job qui calcule, avec la RAM comme problème.

### Garder la référence

    cp data/out/monthly.csv data/out/reference.csv
    cmp data/out/monthly.csv data/out/reference.csv

Copie le résultat correct, puis compare octet par octet après chaque modification.
Appris : un seul écart d'un centime (ligne 8353) après les morceaux, toléré par l'énoncé.

### Lancer sous contrainte

    docker run --name pw --memory=256m --memory-swap=256m --cpus=1 -v "$PWD/data:/data" pw-job

`--memory` plafonne la RAM, `--memory-swap` égal interdit le swap, `--cpus` limite le temps de processeur.

### Lire la fin d'un conteneur

    docker inspect --format '{{.State.ExitCode}} {{.State.OOMKilled}}' pw
    docker rm pw

Donne le code de sortie et si le conteneur a été tué pour manque de mémoire. `rm` libère le nom `pw`.
Appris : 137 + `true` = tué (SIGKILL, 128 + 9). La RAM est incompressible : tué. Avec `--cpus=0.5`, le job finit (56,5 s) : le CPU est compressible, il est freiné.

### Observer en direct

    docker stats

(dans un 2e terminal) Affiche CPU % et mémoire utilisée / limite d'un conteneur en cours.

### Dimensionner

    docker run --name pw --memory=192m --memory-swap=192m --cpus=1 -v "$PWD/data:/data" pw-job

Limite = pic mesuré (≈ 129 Mo) × 1,3 à 1,5. Appris : trop juste, le job meurt ; trop large, on bloque de la place pour rien.

### Comparer plusieurs limites de CPU (bonus)

    docker run --name pw --memory=192m --memory-swap=192m --cpus=0.5 -v "$PWD/data:/data" pw-job

Appris : le ratio CPU / réel suit la limite, le temps augmente (3,8 → 11,5 → 50,4 s), rien n'est tué.

## Refaire mes mesures

1. `docker build -t pw-job .`
2. Générer les données (une fois).
3. Lancer le job avec les limites voulues et noter les 3 lignes affichées.
4. `cmp` contre `reference.csv`.
