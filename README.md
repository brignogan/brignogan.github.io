
Ce site est une adaptation du template jekyll [Creative Theme](http://startbootstrap.com/template-overviews/creative/)

#comment ajouter une recette dans
cree un fichier text avec extension '.md' avec le format suivant (format markdown) .

```
---
layout: post
title: Kaiserschmarren
tag_category: autriche
tag_plat: na
image: img/recette/kaiserschmarren.png
temps_preparation: 15
temps_cuisson: 15
temps_repos: ‘-‘
nbre_personne: ‘pour 4 personnes’
---
Cette recette vient de Maëlle (Vienne)

### Ingredients
* 4 œufs
* 130 g de farine
* 175 mL de lait
* 1 pincée de sel
* 1/2 c. à c. de levure chimique
* 2 c. à s. de sucre en poudre
* 1 sachet de sucre vanillé
* selon les goûts, raisins secs ou canneberges préalablement macérés dans le rhum
* sucre glace (pour saupoudrer)
* beurre (pour faire revenir à la poêle)


### Preparation
* Séparer les blancs d’œufs. Mélanger les jaunes d’œufs, les sucres, la farine, la levure, le sel et le lait. Laisser reposer et pendant ce temps battre les blancs en neige très ferme. Les incorporer à la pâte. Rajouter les raisins secs.
* Faire fondre le beurre dans une poêle à température moyenne. Verser la pâte pour remplir le fond de la poêle. Faire dorer, retourner, rajouter du beurre, quand le deuxième coté est doré, à l'aide d'une spatule, découper en morceaux de 3-4 cm de long et 1-2 cm de large.
* Le temps de cuire toute la pâte, réserver au chaud recouvert d'une feuille d'aluminium dans le four à basse température.
* Juste avant de servir, saupoudrer de sucre glace. Les kaiserschmarren s’accompagnent de « Zwetschkenröster » (genre de marmelade de quetsches) et d'« Apfelmuss » (compote de pommes).


### Vin
Déguster avec un bon café.  

### Note
C’est un dessert typiquement autrichien.  
```

les entrees des variables de l entete du fichier sont:
```
layout: post
title: le titre de la recette
tag_category: autriche, famille, bretagne, maroc
tag_plat: na, sauce,entree,platViande,platPoisson,dessert
image: img/recette/...  le fichier de l'image doit etre dans ce repertoire
temps_preparation:  temps en minute ou '-' si pas pertinent
temps_cuisson:      temps en minute ou '-' si pas pertinent
temps_repos:        temps en minute ou '-' si pas pertinent
nbre_personne:      chaine de charactere entre '' example 'pour 4 personnes'
```
