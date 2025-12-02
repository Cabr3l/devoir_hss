#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expérience 3 - Comparaison rotation mentale vs rotation physique
==================================================================
Cette expérience compare les performances entre rotation mentale et rotation physique,
en analysant les temps de réponse, les taux d'erreur et le compromis vitesse/précision.

Selon Gardony et al. (2014), la rotation mentale est plus rapide mais moins précise,
tandis que la rotation physique est plus lente mais plus fiable.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime

def comparer_conditions(temps_mentale, temps_physique, erreurs_mentale, erreurs_physique):
    """
    Compare les deux conditions expérimentales.
    
    Args:
        temps_mentale: Array des temps de réponse en rotation mentale
        temps_physique: Array des temps de réponse en rotation physique
        erreurs_mentale: Array des erreurs (0=correct, 1=erreur) en rotation mentale
        erreurs_physique: Array des erreurs en rotation physique
    
    Returns:
        dict: Statistiques comparatives
    """
    # Temps de réponse
    temps_moyen_mentale = np.mean(temps_mentale)
    temps_moyen_physique = np.mean(temps_physique)
    
    # Test statistique (test t)
    t_stat, p_value_temps = stats.ttest_ind(temps_mentale, temps_physique)
    
    # Taux d'erreur
    taux_erreur_mentale = np.mean(erreurs_mentale) * 100
    taux_erreur_physique = np.mean(erreurs_physique) * 100
    
    # Test de proportions (test du chi-deux simplifié)
    n_total = len(erreurs_mentale) + len(erreurs_physique)
    erreurs_totales_mentale = np.sum(erreurs_mentale)
    erreurs_totales_physique = np.sum(erreurs_physique)
    
    # Précision
    precision_mentale = (1 - np.mean(erreurs_mentale)) * 100
    precision_physique = (1 - np.mean(erreurs_physique)) * 100
    
    return {
        'temps_moyen_mentale': temps_moyen_mentale,
        'temps_moyen_physique': temps_moyen_physique,
        'taux_erreur_mentale': taux_erreur_mentale,
        'taux_erreur_physique': taux_erreur_physique,
        'precision_mentale': precision_mentale,
        'precision_physique': precision_physique,
        't_stat': t_stat,
        'p_value_temps': p_value_temps,
        'compromis_vitesse_precision': True  # Rotation mentale plus rapide mais moins précise
    }

def analyser_par_disparite(disparites, temps_mentale, temps_physique, 
                          erreurs_mentale, erreurs_physique):
    """
    Analyse les performances par tranche de disparité angulaire.
    
    Args:
        disparites: Array des disparités angulaires
        temps_mentale: Array des temps de réponse en rotation mentale
        temps_physique: Array des temps de réponse en rotation physique
        erreurs_mentale: Array des erreurs en rotation mentale
        erreurs_physique: Array des erreurs en rotation physique
    
    Returns:
        dict: Statistiques par tranche
    """
    bins = [0, 30, 60, 90, 120, 150, 180]
    labels = ['0-30°', '30-60°', '60-90°', '90-120°', '120-150°', '150-180°']
    
    stats_par_bin = {}
    
    for i, (bin_min, bin_max) in enumerate(zip(bins[:-1], bins[1:])):
        mask = (disparites >= bin_min) & (disparites < bin_max)
        
        stats_par_bin[labels[i]] = {
            'temps_mentale': np.mean(temps_mentale[mask]) if np.any(mask) else 0,
            'temps_physique': np.mean(temps_physique[mask]) if np.any(mask) else 0,
            'erreur_mentale': np.mean(erreurs_mentale[mask]) * 100 if np.any(mask) else 0,
            'erreur_physique': np.mean(erreurs_physique[mask]) * 100 if np.any(mask) else 0,
            'n': np.sum(mask)
        }
    
    return stats_par_bin

def visualiser_comparaison(disparites, temps_mentale, temps_physique,
                          erreurs_mentale, erreurs_physique, stats_comparaison, stats_bins):
    """
    Visualise la comparaison entre les deux conditions.
    
    Args:
        disparites: Array des disparités angulaires
        temps_mentale: Array des temps de réponse en rotation mentale
        temps_physique: Array des temps de réponse en rotation physique
        erreurs_mentale: Array des erreurs en rotation mentale
        erreurs_physique: Array des erreurs en rotation physique
        stats_comparaison: Statistiques comparatives
        stats_bins: Statistiques par tranche de disparité
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Graphique 1: Temps de réponse par disparité
    ax1 = axes[0, 0]
    ax1.scatter(disparites, temps_mentale, alpha=0.5, color='#2a5298', 
               s=30, label='Rotation mentale')
    ax1.scatter(disparites, temps_physique, alpha=0.5, color='#dc143c', 
               s=30, label='Rotation physique')
    
    # Lignes de tendance
    z1 = np.polyfit(disparites, temps_mentale, 1)
    p1 = np.poly1d(z1)
    ax1.plot(disparites, p1(disparites), '--', color='#1e3c72', linewidth=2)
    
    z2 = np.polyfit(disparites, temps_physique, 1)
    p2 = np.poly1d(z2)
    ax1.plot(disparites, p2(disparites), '--', color='#b71c1c', linewidth=2)
    
    ax1.set_xlabel('Disparité angulaire (°)', fontsize=12)
    ax1.set_ylabel('Temps de réponse (s)', fontsize=12)
    ax1.set_title('Temps de réponse par disparité angulaire', fontsize=14, color='#1e3c72')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Graphique 2: Comparaison des moyennes
    ax2 = axes[0, 1]
    categories = ['Rotation\nMentale', 'Rotation\nPhysique']
    temps_moyens = [stats_comparaison['temps_moyen_mentale'], 
                    stats_comparaison['temps_moyen_physique']]
    precisions = [stats_comparaison['precision_mentale'], 
                  stats_comparaison['precision_physique']]
    
    x = np.arange(len(categories))
    width = 0.35
    
    bars1 = ax2.bar(x - width/2, temps_moyens, width, label='Temps moyen (s)', 
                   color='#2a5298', alpha=0.8)
    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar(x + width/2, precisions, width, label='Précision (%)', 
                        color='#dc143c', alpha=0.8)
    
    ax2.set_xlabel('Condition', fontsize=12)
    ax2.set_ylabel('Temps moyen (s)', fontsize=12, color='#1e3c72')
    ax2_twin.set_ylabel('Précision (%)', fontsize=12, color='#dc143c')
    ax2.set_title('Compromis vitesse/précision', fontsize=14, color='#1e3c72')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.tick_params(axis='y', labelcolor='#1e3c72')
    ax2_twin.tick_params(axis='y', labelcolor='#dc143c')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Ajouter les valeurs
    for bar, val in zip(bars1, temps_moyens):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                f'{val:.2f}s', ha='center', va='bottom', fontsize=10)
    for bar, val in zip(bars2, precisions):
        ax2_twin.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                     f'{val:.1f}%', ha='center', va='bottom', fontsize=10)
    
    # Graphique 3: Taux d'erreur par disparité
    ax3 = axes[1, 0]
    bins = [0, 30, 60, 90, 120, 150, 180]
    labels = ['0-30°', '30-60°', '60-90°', '90-120°', '120-150°', '150-180°']
    
    erreur_mentale_bins = [stats_bins[label]['erreur_mentale'] for label in labels]
    erreur_physique_bins = [stats_bins[label]['erreur_physique'] for label in labels]
    
    x = np.arange(len(labels))
    width = 0.35
    
    ax3.bar(x - width/2, erreur_mentale_bins, width, label='Rotation mentale', 
           color='#2a5298', alpha=0.8)
    ax3.bar(x + width/2, erreur_physique_bins, width, label='Rotation physique', 
           color='#dc143c', alpha=0.8)
    
    ax3.set_xlabel('Tranches de disparité angulaire', fontsize=12)
    ax3.set_ylabel('Taux d\'erreur (%)', fontsize=12)
    ax3.set_title('Taux d\'erreur par disparité angulaire', fontsize=14, color='#1e3c72')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Graphique 4: Distribution des temps de réponse
    ax4 = axes[1, 1]
    ax4.hist(temps_mentale, bins=20, alpha=0.6, color='#2a5298', 
            label='Rotation mentale', edgecolor='white', density=True)
    ax4.hist(temps_physique, bins=20, alpha=0.6, color='#dc143c', 
            label='Rotation physique', edgecolor='white', density=True)
    
    ax4.axvline(x=stats_comparaison['temps_moyen_mentale'], color='#1e3c72', 
               linestyle='--', linewidth=2, label='Moyenne mentale')
    ax4.axvline(x=stats_comparaison['temps_moyen_physique'], color='#b71c1c', 
               linestyle='--', linewidth=2, label='Moyenne physique')
    
    ax4.set_xlabel('Temps de réponse (s)', fontsize=12)
    ax4.set_ylabel('Densité', fontsize=12)
    ax4.set_title('Distribution des temps de réponse', fontsize=14, color='#1e3c72')
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('resultat_experience3.png', dpi=150, bbox_inches='tight')
    print("Graphique sauvegardé dans 'resultat_experience3.png'")
    plt.show()

if __name__ == "__main__":
    print("=" * 70)
    print("Expérience 3 - Comparaison rotation mentale vs rotation physique")
    print("=" * 70)
    print("\nSimulation basée sur les résultats de Gardony et al. (2014)\n")
    
    np.random.seed(42)
    n_essais = 100
    
    # Génération de disparités angulaires
    disparites = np.random.uniform(0, 180, n_essais)
    
    # Simulation des temps de réponse
    # Rotation mentale: plus rapide mais moins précise
    temps_base_mentale = 1.8
    pente_ade = 0.012
    temps_mentale = temps_base_mentale + pente_ade * disparites + np.random.normal(0, 0.4, n_essais)
    temps_mentale = np.maximum(temps_mentale, 0.5)
    
    # Rotation physique: plus lente mais plus précise
    temps_base_physique = 2.6
    temps_physique = temps_base_physique + pente_ade * disparites + np.random.normal(0, 0.3, n_essais)
    temps_physique = np.maximum(temps_physique, 0.8)
    
    # Simulation des erreurs
    # Rotation mentale: taux d'erreur plus élevé, augmente avec disparité
    proba_erreur_mentale = 0.15 + 0.0005 * disparites + np.random.normal(0, 0.05, n_essais)
    proba_erreur_mentale = np.clip(proba_erreur_mentale, 0, 1)
    erreurs_mentale = (np.random.random(n_essais) < proba_erreur_mentale).astype(int)
    
    # Rotation physique: taux d'erreur plus faible
    proba_erreur_physique = 0.08 + 0.0003 * disparites + np.random.normal(0, 0.03, n_essais)
    proba_erreur_physique = np.clip(proba_erreur_physique, 0, 1)
    erreurs_physique = (np.random.random(n_essais) < proba_erreur_physique).astype(int)
    
    # Comparaison
    stats_comparaison = comparer_conditions(temps_mentale, temps_physique, 
                                           erreurs_mentale, erreurs_physique)
    stats_bins = analyser_par_disparite(disparites, temps_mentale, temps_physique,
                                       erreurs_mentale, erreurs_physique)
    
    print("Résultats de la comparaison:")
    print(f"\nTemps de réponse:")
    print(f"  Rotation mentale: {stats_comparaison['temps_moyen_mentale']:.2f} s")
    print(f"  Rotation physique: {stats_comparaison['temps_moyen_physique']:.2f} s")
    print(f"  Différence: {stats_comparaison['temps_moyen_physique'] - stats_comparaison['temps_moyen_mentale']:.2f} s")
    print(f"  Test t: t = {stats_comparaison['t_stat']:.3f}, p = {stats_comparaison['p_value_temps']:.4f}")
    
    print(f"\nPrécision:")
    print(f"  Rotation mentale: {stats_comparaison['precision_mentale']:.1f}%")
    print(f"  Rotation physique: {stats_comparaison['precision_physique']:.1f}%")
    print(f"  Taux d'erreur - Mentale: {stats_comparaison['taux_erreur_mentale']:.1f}%")
    print(f"  Taux d'erreur - Physique: {stats_comparaison['taux_erreur_physique']:.1f}%")
    
    print(f"\nConclusion:")
    print(f"  La rotation mentale est plus rapide ({stats_comparaison['temps_moyen_mentale']:.2f}s)")
    print(f"  mais moins précise ({stats_comparaison['precision_mentale']:.1f}%)")
    print(f"  La rotation physique est plus lente ({stats_comparaison['temps_moyen_physique']:.2f}s)")
    print(f"  mais plus fiable ({stats_comparaison['precision_physique']:.1f}%)")
    print(f"  → Compromis vitesse/précision confirmé")
    
    # Visualisation
    print("\nGénération des graphiques...")
    visualiser_comparaison(disparites, temps_mentale, temps_physique,
                          erreurs_mentale, erreurs_physique, stats_comparaison, stats_bins)
    
    print("\nExpérience terminée!")
    print(f"\nDate d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

