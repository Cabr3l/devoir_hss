# Devoir de HSS - Cabrel TIOTSOP

Site web statique présentant le résumé d'un article scientifique lu dans le cadre de l'Ecole polytechnique.

## Description

Ce site web présente un résumé détaillé de l'article **"What Does Physical Rotation Reveal About Mental Rotation?"** de Gardony, Taylor & Brunyé (2014). L'article compare la rotation mentale et la rotation physique dans des tâches de comparaison de figures 3D de type Shepard-Metzler.

Le site inclut :
- Un résumé complet de l'article avec introduction, objectifs, méthodologie, résultats et conclusions
- Une **expérience interactive** permettant aux visiteurs de manipuler des figures 3D avec la souris
- Des fichiers Python pour analyser les données et visualiser les résultats de l'étude

## Structure du projet

```
resume-article/
├── index.html          # Page principale avec le résumé de l'article
├── experiment.html     # Page interactive de l'expérience
├── experiment.js       # Script JavaScript pour la manipulation 3D
├── style.css           # Feuille de style CSS
├── README.md           # Ce fichier
├── requirements.txt    # Dépendances Python
└── experiments/        # Dossier contenant les fichiers Python d'analyse
    ├── experience1.py  # Analyse de l'effet de disparité angulaire (ADE)
    ├── experience2.py  # Analyse des trajectoires de rotation physique
    └── experience3.py  # Comparaison rotation mentale vs rotation physique
```

## Article résumé

**Titre** : What Does Physical Rotation Reveal About Mental Rotation?  
**Auteurs** : Gardony, Taylor & Brunyé  
**Année** : 2014

### Résumé

L'article examine la relation entre rotation mentale et rotation physique en comparant les performances dans des tâches de comparaison de figures 3D de type Shepard-Metzler. Les résultats montrent que les deux processus partagent des mécanismes communs (effet de disparité angulaire similaire), mais révèlent un compromis vitesse/précision : la rotation mentale est plus rapide mais moins précise, tandis que la rotation physique est plus lente mais plus fiable.

**Découverte principale** : Les participants ne convergent pas vers un alignement exact (0°) mais vers des "différences canoniques" (~49° pour les essais "same", ~113° pour les essais "different"), suggérant que la rotation vise à atteindre un point de vue optimal plutôt qu'un alignement parfait.

## Couleurs du site

Le site utilise une palette de couleurs basée sur le bleu, blanc et rouge :
- **Bleu** : `#1e3c72` (bleu foncé), `#2a5298` (bleu moyen)
- **Rouge** : `#dc143c` (rouge vif)
- **Blanc** : `#ffffff` (fond principal)

## Installation et utilisation

### Visualiser le site localement

1. Clonez ce dépôt ou téléchargez les fichiers
2. Ouvrez `index.html` dans votre navigateur web pour voir le résumé
3. Cliquez sur "Lancer l'expérience interactive" pour essayer l'expérience de rotation

### Expérience interactive

L'expérience interactive (`experiment.html`) permet de :
- Manipuler des figures 3D de type Shepard-Metzler avec la souris
- Déterminer si deux figures sont identiques ou en miroir
- Observer les temps de réponse et la précision
- Reproduire les conditions de l'étude originale

**Utilisation** :
- Cliquez et glissez sur la figure de droite pour la faire tourner
- Cliquez sur "IDENTIQUES" ou "EN MIROIR" selon votre jugement
- Les statistiques sont mises à jour en temps réel

### Exécuter les analyses Python

Les scripts Python nécessitent les bibliothèques suivantes :
- `numpy` (calculs numériques)
- `matplotlib` (visualisation)
- `scipy` (analyses statistiques)

Pour installer les dépendances :
```bash
pip install -r requirements.txt
```

Pour exécuter les analyses :
```bash
cd experiments
python experience1.py  # Analyse de l'ADE
python experience2.py  # Analyse des trajectoires
python experience3.py  # Comparaison mental vs physique
```

Chaque script génère un graphique sauvegardé au format PNG.

## Fonctionnalités

### Expérience interactive
- Manipulation 3D avec Three.js
- Enregistrement des temps de réponse
- Calcul de la disparité angulaire
- Statistiques en temps réel

### Analyses Python
- **experience1.py** : Calcule et visualise l'effet de disparité angulaire (ADE), montrant la corrélation entre l'écart angulaire initial et le temps de réponse
- **experience2.py** : Analyse les trajectoires de rotation physique et la convergence vers les différences canoniques
- **experience3.py** : Compare les performances entre rotation mentale et rotation physique, illustrant le compromis vitesse/précision

## Hébergement sur GitHub Pages

Pour héberger ce site sur GitHub Pages :

1. Créez un nouveau dépôt sur GitHub
2. Uploadez tous les fichiers de ce projet
3. Allez dans Settings > Pages
4. Sélectionnez la branche `main` (ou `master`) comme source
5. Le site sera accessible à l'adresse : `https://votre-username.github.io/nom-du-repo/`

**Note** : L'expérience interactive utilise Three.js via CDN, donc une connexion internet est nécessaire pour charger la bibliothèque 3D.

## Technologies utilisées

- **HTML5/CSS3** : Structure et style du site
- **JavaScript** : Logique de l'expérience interactive
- **Three.js** : Rendu 3D des figures Shepard-Metzler
- **Python** : Analyses statistiques et visualisations
- **NumPy/Matplotlib/Scipy** : Bibliothèques scientifiques Python

## Auteur

**Cabrel TIOTSOP**  
Ecole polytechnique

## Références

Gardony, A. L., Taylor, H. A., & Brunyé, T. T. (2014). What Does Physical Rotation Reveal About Mental Rotation? *Psychological Science*, 25(3), 605-612.

## Licence

Ce projet est libre d'utilisation pour des fins éducatives.

