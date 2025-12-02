#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expérience 1 - Analyse de l'effet de disparité angulaire (ADE)
================================================================
Cette expérience analyse l'effet de disparité angulaire (Angular Disparity Effect)
dans les tâches de rotation mentale et physique, comme décrit dans Gardony et al. (2014).

L'ADE se manifeste par une corrélation positive entre l'écart angulaire initial
entre deux figures et le temps de réponse nécessaire pour déterminer si elles sont identiques.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def calculer_ade(disparites_angulaires, temps_reponse):
    """
    Calcule l'effet de disparité angulaire (ADE) en corrélant
    les disparités angulaires initiales avec les temps de réponse.
    
    Args:
        disparites_angulaires: Array des écarts angulaires initiaux (en degrés)
        temps_reponse: Array des temps de réponse (en secondes)
    
    Returns:
        dict: Dictionnaire contenant corrélation, pente, et statistiques
    """
    disparites = np.array(disparites_angulaires)
    temps = np.array(temps_reponse)
    
    # Calcul de la corrélation de Pearson
    correlation, p_value = stats.pearsonr(disparites, temps)
    
    # Régression linéaire
    slope, intercept, r_value, p_val, std_err = stats.linregress(disparites, temps)
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        'std_err': std_err
    }

def visualiser_ade(disparites_angulaires, temps_reponse, ade_results, condition="Rotation"):
    """
    Visualise l'effet de disparité angulaire.
    
    Args:
        disparites_angulaires: Array des écarts angulaires initiaux
        temps_reponse: Array des temps de réponse
        ade_results: Résultats de l'analyse ADE
        condition: Nom de la condition (ex: "Mentale" ou "Physique")
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Graphique de dispersion avec ligne de régression
    ax1.scatter(disparites_angulaires, temps_reponse, 
                color='#1e3c72', alpha=0.6, s=50)
    
    # Ligne de régression
    x_line = np.linspace(disparites_angulaires.min(), disparites_angulaires.max(), 100)
    y_line = ade_results['slope'] * x_line + ade_results['intercept']
    ax1.plot(x_line, y_line, '--', color='#dc143c', linewidth=2, 
             label=f"Régression (r={ade_results['correlation']:.3f})")
    
    ax1.set_xlabel('Disparité angulaire initiale (°)', fontsize=12)
    ax1.set_ylabel('Temps de réponse (s)', fontsize=12)
    ax1.set_title(f'ADE - {condition}\n' + 
                  f'r = {ade_results["correlation"]:.3f}, p = {ade_results["p_value"]:.4f}',
                  fontsize=14, color='#1e3c72')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Histogramme des temps de réponse par tranche de disparité
    bins = [0, 30, 60, 90, 120, 150, 180]
    labels = ['0-30°', '30-60°', '60-90°', '90-120°', '120-150°', '150-180°']
    bin_indices = np.digitize(disparites_angulaires, bins) - 1
    
    temps_moyens = []
    for i in range(len(bins) - 1):
        mask = bin_indices == i
        if np.any(mask):
            temps_moyens.append(np.mean(temps_reponse[mask]))
        else:
            temps_moyens.append(0)
    
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(labels)))
    bars = ax2.bar(labels, temps_moyens, color=colors, edgecolor='white', linewidth=1.5)
    ax2.set_xlabel('Tranches de disparité angulaire', fontsize=12)
    ax2.set_ylabel('Temps de réponse moyen (s)', fontsize=12)
    ax2.set_title(f'Temps moyen par tranche - {condition}', fontsize=14, color='#1e3c72')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Ajouter les valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('resultat_experience1.png', dpi=150, bbox_inches='tight')
    print("Graphique sauvegardé dans 'resultat_experience1.png'")
    plt.show()

if __name__ == "__main__":
    print("=" * 70)
    print("Expérience 1 - Analyse de l'effet de disparité angulaire (ADE)")
    print("=" * 70)
    print("\nSimulation basée sur les résultats de Gardony et al. (2014)")
    print("Condition: Rotation mentale et rotation physique\n")
    
    # Simulation de données basées sur les résultats de l'article
    np.random.seed(42)
    n_essais = 100
    
    # Génération de disparités angulaires uniformément distribuées entre 0° et 180°
    disparites = np.random.uniform(0, 180, n_essais)
    
    # Simulation des temps de réponse avec ADE (corrélation ~0.36 pour rotation mentale)
    # Temps de base + effet linéaire de la disparité + bruit
    temps_base = 2.0  # Temps de base en secondes
    pente_ade = 0.015  # Augmentation de ~15ms par degré
    temps_mentale = temps_base + pente_ade * disparites + np.random.normal(0, 0.5, n_essais)
    temps_mentale = np.maximum(temps_mentale, 0.5)  # Temps minimum
    
    # Rotation physique: plus lente mais même pattern
    temps_physique = temps_base + 0.8 + pente_ade * disparites + np.random.normal(0, 0.4, n_essais)
    temps_physique = np.maximum(temps_physique, 0.8)
    
    # Analyse pour rotation mentale
    print("Analyse - Rotation mentale:")
    ade_mentale = calculer_ade(disparites, temps_mentale)
    print(f"  Corrélation (r): {ade_mentale['correlation']:.3f}")
    print(f"  P-value: {ade_mentale['p_value']:.4f}")
    print(f"  Pente: {ade_mentale['slope']:.4f} s/°")
    print(f"  R²: {ade_mentale['r_squared']:.3f}")
    
    # Analyse pour rotation physique
    print("\nAnalyse - Rotation physique:")
    ade_physique = calculer_ade(disparites, temps_physique)
    print(f"  Corrélation (r): {ade_physique['correlation']:.3f}")
    print(f"  P-value: {ade_physique['p_value']:.4f}")
    print(f"  Pente: {ade_physique['slope']:.4f} s/°")
    print(f"  R²: {ade_physique['r_squared']:.3f}")
    
    # Comparaison
    print("\nComparaison:")
    print(f"  Différence de corrélation: {abs(ade_mentale['correlation'] - ade_physique['correlation']):.3f}")
    print(f"  Temps moyen - Mentale: {np.mean(temps_mentale):.2f} s")
    print(f"  Temps moyen - Physique: {np.mean(temps_physique):.2f} s")
    
    # Visualisation
    print("\nGénération des graphiques...")
    visualiser_ade(disparites, temps_mentale, ade_mentale, "Rotation Mentale")
    visualiser_ade(disparites, temps_physique, ade_physique, "Rotation Physique")
    
    print("\nExpérience terminée!")
    print("\nInterprétation:")
    print("- L'ADE est présent dans les deux conditions (corrélations positives significatives)")
    print("- Les deux conditions montrent une relation linéaire similaire")
    print("- La rotation physique est généralement plus lente mais montre le même pattern")

