# Données, attribution et transformations

## Source

**UCDP Conflict Termination Dataset, version 4-2024**, niveau conflit.
La version interne des lignes est `4.2024002`.

[CSV original](https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv)

[Manuel de codage](https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Codebook.pdf)

[Centre de téléchargement et licence](https://ucdp.uu.se/downloads/)

`source.csv` est l'instantané original utilisé, identique octet par octet au
téléchargement enregistré. Les empreintes SHA-256 et la date de récupération
figurent dans `provenance.json`. Le script contrôle l'empreinte avant traitement.

## Licence et attribution

Les données UCDP sont mises à disposition sous **Creative Commons Attribution
4.0 International (CC BY 4.0)**, selon le centre de téléchargement UCDP.

<https://creativecommons.org/licenses/by/4.0/>

L'attribution vaut également pour les données dérivées et le graphique dans
`output/`, distribués ici sous CC BY 4.0. La licence MIT du code ne remplace
pas la licence des données. Aucune approbation par UCDP n'est impliquée.

Citation demandée :

Kreutz, Joakim (2010). *How and When Armed Conflicts End: Introducing the UCDP
Conflict Termination Dataset*. Journal of Peace Research, 47(2), 243–250.

<https://doi.org/10.1177/0022343309353108>

## Transformations effectuées

1. Lecture des 2 752 lignes annuelles du fichier source.
2. Sélection des 507 lignes `c_epterm == 1`, dernières années actives 1946–2023.
3. Conservation des identifiants, acteurs de la dernière année active, dates,
   précision des dates, version et codes d'issue. Ajout de libellés français.
4. Regroupement des codes 3 et 4 en « victoire militaire d'un camp ».
5. Agrégation selon la dernière année active : décennies, avec périodes
   partielles 1946–1949 et 2020–2023.
6. Calcul des parts dans chaque période et production du graphique.

### Filtre optionnel `--wars-only`

Après la sélection des terminaisons, conserver uniquement les épisodes dont
au moins une ligne annuelle porte `intensity_level == 2`. Ce code signifie
**au moins 1 000 morts liés aux combats dans une année**, pas un bilan cumulé.
La sélection relie les lignes par `conflict_id` + `c_ep_startyear`, sans utiliser
`c_epid` seul. Elle retient 131 fins d'épisodes et garde les codes d'issue initiaux.
La fin reste définie par le passage sous 25 morts dans l'année suivante.

Les sorties ne sont pas des données officielles UCDP : ce sont des extractions
et une visualisation réalisées pour ce dépôt. Les codes originaux ne sont pas
recodés en fonction d'une interprétation historique indépendante.

Le script n'effectue pas de déduplication sur `c_epid`, non unique dans cet
instantané. Voir les explications et limites dans le README principal.
