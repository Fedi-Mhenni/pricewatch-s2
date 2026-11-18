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
| 03. Optimisation RAM | 256m · 1            |                 |                |               |                  |                |           |
| 04. Optimisation CPU | 256m · 1            |                 |                |               |                  |                |           |
| 05. Dimensionné      | ? · ?               |                 |                |               |                  |                |           |
| Bonus                |                     |                 |                |               |                  |                |           |

### Ce que nous avons changé, et pourquoi (une ligne par changement)

-

### Dimensionnement retenu

Commande de lancement finale :

    docker run ...

Justification (pic mesuré, marge choisie) :

### Ce que nous en retenons (3 lignes maximum)
