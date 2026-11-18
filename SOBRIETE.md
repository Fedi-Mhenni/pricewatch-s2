# SOBRIETE.md · PriceWatch

Nom : MHENNI FEDI
Machine de mesure (OS, processeur, RAM allouée à Docker) : Linux, Intel Core i5-10210U @ 1,60 GHz (8 cœurs logiques), 7,5 Go de RAM, pas de limite Docker

## Séance 2 · Le job sous contrainte

Cible : 256 Mo de RAM, 1 CPU, moins de 30 s, résultat identique.

| Étape                | Limites (RAM · CPU) | Pic de RAM (Mo) | Temps réel (s) | Temps CPU (s) | Ratio CPU / réel | Code de sortie | OOMKilled |
| -------------------- | ------------------- | --------------- | -------------- | ------------- | ---------------- | -------------- | --------- |
| 01. Ligne de base    | aucune              | 1580            | 21,1           | 22,5          | 1,07             | 0              | false     |
| 02a. Sous contrainte | 256m · 1            | tué (>256)      | -              | -             | -                | 137            | true      |
| 02b. CPU réduit      | aucune · 0.5        | 1582            | 56,5           | 29,4          | 0,52             | 0              | false     |
| 03. Optimisation RAM | 256m · 1            | 130             | 4,1            | 4,8           | 1,17             | 0              | false     |
| 04. Optimisation CPU | 256m · 1            | 128             | 4,0            | 4,8           | 1,22             | 0              | false     |
| 05. Dimensionné      | 192m · 1            | 129             | 3,7            | 4,6           | 1,24             | 0              | false     |
| Bonus. 1 CPU         | 192m · 1            | 131             | 3,8            | 4,6           | 1,23             | 0              | false     |
| Bonus. 0,5 CPU       | 192m · 0.5          | 127             | 11,5           | 6,7           | 0,58             | 0              | false     |
| Bonus. 0,25 CPU      | 192m · 0.25         | 132             | 50,4           | 14,6          | 0,29             | 0              | false     |

### Ce que nous avons changé, et pourquoi (une ligne par changement)

Étape 03 (mesures sans limite) :

- 03a : `df.copy()` remplacé par `work = df` (copie inutile). Pic de RAM : 1580 → 1429 Mo. Sortie identique.
- 03b : `usecols=["date","shop","product","price"]` (`source_id` et `comment` inutiles). Pic : 1429 → 1154 Mo. Sortie identique.
- 03c : `category` pour `shop` et `product`. Pic : 1154 → 1132 Mo, gain faible. Sortie identique.
- 03d : lecture par morceaux (`chunksize=200_000`), on garde min, max, somme et nombre, puis moyenne = somme ÷ nombre. Pic : 1132 → 130 Mo, temps réel 17,5 → 4,1 s. Écart : 1 ligne sur 8400 (yaourt-nature-x4, Toulouse-Capitole, 2022-12), price_mean 2.03 au lieu de 2.02, dans la tolérance d'un centime.

- 04 : les `apply` sont remplacés par des opérations vectorisées (`.str[:7]`, `price / 1.055`). Mesuré isolément sur la version sans morceaux (sans limite, car pic de 505 Mo > 256 Mo) : temps réel 18,1 → 4,0 s, temps CPU 19,5 → 5,5 s, pic 1119 → 505 Mo, sortie identique. La ligne 04 du tableau est la mesure du script final sous 256m · 1.
- Bonus : comparaison à 1, 0,5 et 0,25 CPU (192m). Le temps réel passe de 3,8 s à 11,5 s puis 50,4 s, le ratio CPU / réel suit la limite (1,23 ; 0,58 ; 0,29), le pic de RAM reste à ~130 Mo et aucun job n'est tué : le CPU est freiné, pas tué. À 0,25 CPU, le job dépasse les 30 s autorisées : on garde donc 1 CPU (ou au minimum 0,5) pour ce job.

### Dimensionnement retenu

Commande de lancement finale :

    docker run --memory=192m --memory-swap=192m --cpus=1 -v "$PWD/data:/data" pw-job

Justification (pic mesuré, marge choisie) : pic mesuré ≈ 129 Mo (stable sur 3 runs : 128, 129, 130). Limite = 192 Mo, soit pic × 1,49, dans la fourchette 1,3 à 1,5 du cours. Trop juste, le job serait tué si les données grossissent (137). Trop large (256 Mo), on bloquerait de la place pour rien sur un serveur partagé. Le CPU reste à 1 : le job finit en environ 4 s pour 30 s autorisées.

### Ce que nous en retenons (3 lignes maximum)

- La RAM limitait le job : tué à 256 Mo (137), alors que le CPU seul ne fait que ralentir (56,5 s à 0,5 CPU).
- Le gros gain RAM vient de la lecture par morceaux (1132 → 130 Mo), pas de `category` (−22 Mo) ; le gros gain de temps vient des `apply` supprimés (18,1 → 4,0 s).
- On choisit la limite à partir du pic mesuré, plus une marge (192 Mo), pas au hasard.
