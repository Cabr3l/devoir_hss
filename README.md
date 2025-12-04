# Devoir de HSS - Cabrel TIOTSOP

Site web statique présentant le résumé d'un article scientifique lu dans le cadre du cours de HSS_51H05_EP.

## Description

Ce site web présente un résumé détaillé de l'article **"What Does Physical Rotation Reveal About Mental Rotation?"** de Gardony, Taylor & Brunyé (2014). L'article compare la rotation mentale et la rotation physique dans des tâches de comparaison de figures 3D de type Shepard-Metzler.

## Article résumé

**Titre** : What Does Physical Rotation Reveal About Mental Rotation?  
**Auteurs** : Gardony, Taylor & Brunyé  
**Année** : 2014

### Résumé

L'article examine la relation entre rotation mentale et rotation physique en comparant les performances dans des tâches de comparaison de figures 3D de type Shepard-Metzler. Les résultats montrent que les deux processus partagent des mécanismes communs (effet de disparité angulaire similaire), mais révèlent un compromis vitesse/précision : la rotation mentale est plus rapide mais moins précise, tandis que la rotation physique est plus lente mais plus fiable.

**Découverte principale** : Les participants ne convergent pas vers un alignement exact (0°) mais vers des "différences canoniques" (~49° pour les essais "same", ~113° pour les essais "different"), suggérant que la rotation vise à atteindre un point de vue optimal plutôt qu'un alignement parfait.

### Pour tester les expériences en local avec les fichiers python qui ont été téléchargés :

Pour installer les dépendances :
```bash
pip install -r requirements.txt
```

Pour exécuter les analyses :
```bash
cd experiments
python experience_pygame_3d.py  # Expérience Pygame 3D avec PyOpenGL
```

Le script génère un graphique sauvegardé au format PNG.


### Analyses Python
- **experience_pygame_3d.py** : Calcule et visualise l'effet de disparité angulaire (ADE), montrant la corrélation entre l'écart angulaire initial et le temps de réponse


## Références

Gardony, A. L., Taylor, H. A., & Brunyé, T. T. (2014). What Does Physical Rotation Reveal About Mental Rotation? *Psychological Science*, 25(3), 605-612.

Ganis, G. & Kievit, R. (2015). A New Set of Three-Dimensional Shapes for Investigating Mental Rotation Processes: Validation Data and Stimulus Set. Journal of Open Psychology Data, 3: e3, DOI: http://dx.doi.org/10.5334/jopd.a. 
## Licence


