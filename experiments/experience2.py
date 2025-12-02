#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expérience 2 - Analyse des trajectoires de rotation physique
==============================================================
Cette expérience analyse la dynamique temporelle de la rotation physique,
en examinant comment la disparité angulaire évolue au cours du temps.

Selon Gardony et al. (2014), les participants ne convergent pas vers 0°
mais vers des "différences canoniques" : ~49° pour les essais "same" et ~113° pour "different".
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def normaliser_trajectoire(temps, disparites, n_points=100):
    """
    Normalise une trajectoire de rotation en n_points échantillons.
    
    Args:
        temps: Array des temps d'échantillonnage
        disparites: Array des disparités angulaires à chaque instant
        n_points: Nombre de points pour la normalisation
    
    Returns:
        tuple: (temps_normalise, disparites_normalisees)
    """
    if len(temps) < 2:
        return np.linspace(0, 1, n_points), np.full(n_points, disparites[0] if len(disparites) > 0 else 0)
    
    # Normaliser le temps entre 0 et 1
    temps_norm = (temps - temps.min()) / (temps.max() - temps.min() + 1e-10)
    
    # Interpolation pour obtenir n_points échantillons
    if len(temps) > 1:
        interp_func = interp1d(temps_norm, disparites, kind='linear', 
                               bounds_error=False, fill_value='extrapolate')
        temps_normalise = np.linspace(0, 1, n_points)
        disparites_normalisees = interp_func(temps_normalise)
    else:
        temps_normalise = np.linspace(0, 1, n_points)
        disparites_normalisees = np.full(n_points, disparites[0])
    
    return temps_normalise, disparites_normalisees

def analyser_convergence(trajectoires_same, trajectoires_different):
    """
    Analyse la convergence vers les différences canoniques.
    
    Args:
        trajectoires_same: Liste de trajectoires normalisées pour essais "same"
        trajectoires_different: Liste de trajectoires normalisées pour essais "different"
    
    Returns:
        dict: Statistiques de convergence
    """
    # Calculer les disparités finales (dernier quartile)
    finales_same = [t[-25:] for t in trajectoires_same if len(t) >= 25]
    finales_different = [t[-25:] for t in trajectoires_different if len(t) >= 25]
    
    if finales_same:
        moyenne_same = np.mean([np.mean(f) for f in finales_same])
        std_same = np.std([np.mean(f) for f in finales_same])
    else:
        moyenne_same = std_same = 0
    
    if finales_different:
        moyenne_different = np.mean([np.mean(f) for f in finales_different])
        std_different = np.std([np.mean(f) for f in finales_different])
    else:
        moyenne_different = std_different = 0
    
    return {
        'canonical_same': moyenne_same,
        'std_same': std_same,
        'canonical_different': moyenne_different,
        'std_different': std_different
    }

def visualiser_trajectoires(trajectoires_same, trajectoires_different, convergence_stats):
    """
    Visualise les trajectoires de rotation et la convergence.
    
    Args:
        trajectoires_same: Liste de trajectoires normalisées pour essais "same"
        trajectoires_different: Liste de trajectoires normalisées pour essais "different"
        convergence_stats: Statistiques de convergence
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Graphique 1: Trajectoires individuelles - Same
    ax1 = axes[0, 0]
    temps_norm = np.linspace(0, 1, 100)
    for traj in trajectoires_same[:10]:  # Afficher seulement les 10 premières
        ax1.plot(temps_norm, traj, alpha=0.3, color='#2a5298', linewidth=1)
    
    # Trajectoire moyenne
    if trajectoires_same:
        traj_moyenne_same = np.mean(trajectoires_same, axis=0)
        ax1.plot(temps_norm, traj_moyenne_same, color='#1e3c72', linewidth=3, 
                label='Moyenne')
        ax1.axhline(y=convergence_stats['canonical_same'], color='#dc143c', 
                   linestyle='--', linewidth=2, label=f"Différence canonique (~{convergence_stats['canonical_same']:.0f}°)")
    
    ax1.set_xlabel('Temps normalisé', fontsize=12)
    ax1.set_ylabel('Disparité angulaire (°)', fontsize=12)
    ax1.set_title('Trajectoires - Essais "Same"', fontsize=14, color='#1e3c72')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim([0, 180])
    
    # Graphique 2: Trajectoires individuelles - Different
    ax2 = axes[0, 1]
    for traj in trajectoires_different[:10]:
        ax2.plot(temps_norm, traj, alpha=0.3, color='#dc143c', linewidth=1)
    
    if trajectoires_different:
        traj_moyenne_diff = np.mean(trajectoires_different, axis=0)
        ax2.plot(temps_norm, traj_moyenne_diff, color='#b71c1c', linewidth=3, 
                label='Moyenne')
        ax2.axhline(y=convergence_stats['canonical_different'], color='#1e3c72', 
                   linestyle='--', linewidth=2, label=f"Différence canonique (~{convergence_stats['canonical_different']:.0f}°)")
    
    ax2.set_xlabel('Temps normalisé', fontsize=12)
    ax2.set_ylabel('Disparité angulaire (°)', fontsize=12)
    ax2.set_title('Trajectoires - Essais "Different"', fontsize=14, color='#1e3c72')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim([0, 180])
    
    # Graphique 3: Comparaison des convergences
    ax3 = axes[1, 0]
    categories = ['Same', 'Different']
    valeurs = [convergence_stats['canonical_same'], convergence_stats['canonical_different']]
    erreurs = [convergence_stats['std_same'], convergence_stats['std_different']]
    colors = ['#2a5298', '#dc143c']
    
    bars = ax3.bar(categories, valeurs, yerr=erreurs, color=colors, 
                   edgecolor='white', linewidth=2, capsize=10, alpha=0.8)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.set_ylabel('Disparité angulaire finale (°)', fontsize=12)
    ax3.set_title('Différences canoniques', fontsize=14, color='#1e3c72')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Ajouter les valeurs sur les barres
    for bar, val in zip(bars, valeurs):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + erreurs[categories.index(bar.get_x())],
                f'{val:.1f}°', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Graphique 4: Distribution des disparités finales
    ax4 = axes[1, 1]
    if trajectoires_same and trajectoires_different:
        finales_same_flat = [t[-1] for t in trajectoires_same]
        finales_diff_flat = [t[-1] for t in trajectoires_different]
        
        ax4.hist(finales_same_flat, bins=20, alpha=0.6, color='#2a5298', 
                label='Same', edgecolor='white')
        ax4.hist(finales_diff_flat, bins=20, alpha=0.6, color='#dc143c', 
                label='Different', edgecolor='white')
        ax4.axvline(x=convergence_stats['canonical_same'], color='#1e3c72', 
                   linestyle='--', linewidth=2)
        ax4.axvline(x=convergence_stats['canonical_different'], color='#b71c1c', 
                   linestyle='--', linewidth=2)
    
    ax4.set_xlabel('Disparité angulaire finale (°)', fontsize=12)
    ax4.set_ylabel('Fréquence', fontsize=12)
    ax4.set_title('Distribution des disparités finales', fontsize=14, color='#1e3c72')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('resultat_experience2.png', dpi=150, bbox_inches='tight')
    print("Graphique sauvegardé dans 'resultat_experience2.png'")
    plt.show()

if __name__ == "__main__":
    print("=" * 70)
    print("Expérience 2 - Analyse des trajectoires de rotation physique")
    print("=" * 70)
    print("\nSimulation basée sur les résultats de Gardony et al. (2014)")
    print("Analyse de la convergence vers les différences canoniques\n")
    
    np.random.seed(42)
    
    # Simulation de trajectoires de rotation
    n_essais_same = 30
    n_essais_different = 30
    
    trajectoires_same = []
    trajectoires_different = []
    
    # Générer des trajectoires pour essais "same"
    # Convergence vers ~49° selon l'article
    for i in range(n_essais_same):
        disparite_initiale = np.random.uniform(0, 180)
        temps = np.linspace(0, 3, 50)  # 3 secondes, échantillonnage à ~17 Hz
        
        # Modèle de convergence vers 49°
        cible = 49
        disparites = disparite_initiale * np.exp(-temps / 1.5) + cible * (1 - np.exp(-temps / 1.5))
        disparites += np.random.normal(0, 5, len(disparites))  # Bruit
        
        temps_norm, disparites_norm = normaliser_trajectoire(temps, disparites)
        trajectoires_same.append(disparites_norm)
    
    # Générer des trajectoires pour essais "different"
    # Convergence vers ~113° selon l'article
    for i in range(n_essais_different):
        disparite_initiale = np.random.uniform(0, 180)
        temps = np.linspace(0, 3, 50)
        
        # Modèle de convergence vers 113°
        cible = 113
        disparites = disparite_initiale * np.exp(-temps / 1.5) + cible * (1 - np.exp(-temps / 1.5))
        disparites += np.random.normal(0, 8, len(disparites))  # Plus de variabilité
        
        temps_norm, disparites_norm = normaliser_trajectoire(temps, disparites)
        trajectoires_different.append(disparites_norm)
    
    # Analyse de convergence
    convergence_stats = analyser_convergence(trajectoires_same, trajectoires_different)
    
    print("Résultats de l'analyse:")
    print(f"\nEssais 'Same':")
    print(f"  Différence canonique: {convergence_stats['canonical_same']:.1f}°")
    print(f"  Écart-type: {convergence_stats['std_same']:.1f}°")
    
    print(f"\nEssais 'Different':")
    print(f"  Différence canonique: {convergence_stats['canonical_different']:.1f}°")
    print(f"  Écart-type: {convergence_stats['std_different']:.1f}°")
    
    print(f"\nObservation:")
    print(f"  Les participants ne convergent PAS vers 0° (alignement parfait)")
    print(f"  mais vers des différences angulaires 'canoniques' qui offrent")
    print(f"  un point de vue optimal pour comparer les figures.")
    
    # Visualisation
    print("\nGénération des graphiques...")
    visualiser_trajectoires(trajectoires_same, trajectoires_different, convergence_stats)
    
    print("\nExpérience terminée!")

