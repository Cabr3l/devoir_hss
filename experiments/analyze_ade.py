#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse de l'ADE (Angle de Disparité Égocentrique)
Trace les courbes d'analyse avec corrélations pour les réponses correctes et incorrectes.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import pearsonr, linregress

def load_results(json_path="experiment_results.json"):
    """Charge les résultats de l'expérience."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)
    
    if not os.path.exists(full_path):
        print(f"Erreur: Fichier {full_path} introuvable")
        print("Veuillez d'abord exécuter experience_pygame_3d.py pour générer les résultats.")
        return None
    
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    return data


def calculate_correlation(x, y):
    """Calcule la corrélation de Pearson entre x et y."""
    if len(x) < 2:
        return 0.0, 1.0
    r, p = pearsonr(x, y)
    return r, p


def analyze_ade(results):
    """Analyse l'ADE et génère les graphiques."""
    if not results:
        print("Aucun résultat à analyser")
        return
    
    # Séparer les résultats corrects et incorrects
    correct_results = [r for r in results if r['is_correct']]
    incorrect_results = [r for r in results if not r['is_correct']]
    
    # Extraire les données
    correct_angles = [r['initial_angle'] for r in correct_results]
    correct_times = [r['response_time'] for r in correct_results]
    
    incorrect_angles = [r['initial_angle'] for r in incorrect_results]
    incorrect_times = [r['response_time'] for r in incorrect_results]
    
    # Calculer les corrélations et régressions
    if len(correct_angles) >= 2:
        r_correct, p_correct = calculate_correlation(correct_angles, correct_times)
        # Régression linéaire complète pour les corrects
        slope_correct, intercept_correct, r_correct_reg, p_correct_reg, std_err_correct = linregress(correct_angles, correct_times)
    else:
        r_correct, p_correct = 0.0, 1.0
        slope_correct, intercept_correct, r_correct_reg, p_correct_reg, std_err_correct = 0.0, 0.0, 0.0, 1.0, 0.0
    
    if len(incorrect_angles) >= 2:
        r_incorrect, p_incorrect = calculate_correlation(incorrect_angles, incorrect_times)
        # Régression linéaire complète pour les incorrects
        slope_incorrect, intercept_incorrect, r_incorrect_reg, p_incorrect_reg, std_err_incorrect = linregress(incorrect_angles, incorrect_times)
    else:
        r_incorrect, p_incorrect = 0.0, 1.0
        slope_incorrect, intercept_incorrect, r_incorrect_reg, p_incorrect_reg, std_err_incorrect = 0.0, 0.0, 0.0, 1.0, 0.0
    
    # Créer la figure avec fond gris
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor('#D0D0D0')  # Fond gris
    ax.set_facecolor('#D0D0D0')
    
    # Tracer les points et courbes
    if correct_angles and len(correct_angles) > 0:
        # Points corrects
        ax.scatter(correct_angles, correct_times, 
                  color='green', alpha=0.7, s=60, label='Réponses correctes', zorder=3, edgecolors='darkgreen', linewidths=0.5)
        
        # Régression linéaire pour les corrects
        if len(correct_angles) >= 2:
            x_line_correct = np.linspace(min(correct_angles), max(correct_angles), 100)
            y_line_correct = slope_correct * x_line_correct + intercept_correct
            ax.plot(x_line_correct, y_line_correct, 
                   "g-", linewidth=2.5, alpha=0.9, 
                   label=f'Régression correctes: r={r_correct_reg:.3f}, p={p_correct_reg:.4f}')
    
    if incorrect_angles and len(incorrect_angles) > 0:
        # Points incorrects
        ax.scatter(incorrect_angles, incorrect_times, 
                  color='red', alpha=0.7, s=60, label='Réponses incorrectes', zorder=3, edgecolors='darkred', linewidths=0.5)
        
        # Régression linéaire pour les incorrects
        if len(incorrect_angles) >= 2:
            x_line_incorrect = np.linspace(min(incorrect_angles), max(incorrect_angles), 100)
            y_line_incorrect = slope_incorrect * x_line_incorrect + intercept_incorrect
            ax.plot(x_line_incorrect, y_line_incorrect, 
                   "r-", linewidth=2.5, alpha=0.9, 
                   label=f'Régression incorrectes: r={r_incorrect_reg:.3f}, p={p_incorrect_reg:.4f}')
    
    # Configuration du graphique
    ax.set_xlabel('Angle de Disparité Initiale (ADE) [°]', fontsize=12, fontweight='bold', color='black')
    ax.set_ylabel('Temps de Réponse [s]', fontsize=12, fontweight='bold', color='black')
    ax.set_title('Analyse de l\'ADE: Corrélation Angle-Temps de Réponse', 
                fontsize=14, fontweight='bold', pad=20, color='black')
    ax.grid(True, alpha=0.4, linestyle='--', color='white')
    ax.legend(loc='best', fontsize=10, framealpha=0.95, facecolor='white', edgecolor='black')
    
    # Style des axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.tick_params(colors='black')
    
    # Afficher les statistiques dans une boîte de texte
    stats_text = f'Réponses correctes: {len(correct_results)}\n'
    stats_text += f'Réponses incorrectes: {len(incorrect_results)}\n\n'
    if len(correct_angles) >= 2:
        stats_text += f'RÉGRESSION CORRECTES:\n'
        stats_text += f'  r = {r_correct_reg:.3f}\n'
        stats_text += f'  p = {p_correct_reg:.4f}\n'
        stats_text += f'  pente = {slope_correct:.4f}\n'
        stats_text += f'  ordonnée = {intercept_correct:.3f}\n\n'
    if len(incorrect_angles) >= 2:
        stats_text += f'RÉGRESSION INCORRECTES:\n'
        stats_text += f'  r = {r_incorrect_reg:.3f}\n'
        stats_text += f'  p = {p_incorrect_reg:.4f}\n'
        stats_text += f'  pente = {slope_incorrect:.4f}\n'
        stats_text += f'  ordonnée = {intercept_incorrect:.3f}'
    
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Sauvegarder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "resultat_experience_pygame_3d_ade.png")
    plt.savefig(output_path, dpi=300, facecolor='#D0D0D0', bbox_inches='tight')
    print(f"✓ Graphique sauvegardé dans {output_path}")
    
    # Afficher les statistiques
    print("\n" + "="*60)
    print("STATISTIQUES ADE - RÉGRESSION LINÉAIRE")
    print("="*60)
    print(f"Réponses correctes: {len(correct_results)}")
    print(f"Réponses incorrectes: {len(incorrect_results)}")
    if len(correct_angles) >= 2:
        print(f"\nRÉGRESSION CORRECTES:")
        print(f"  Coefficient de corrélation r = {r_correct_reg:.3f}")
        print(f"  p-valeur = {p_correct_reg:.4f}")
        print(f"  Pente = {slope_correct:.4f} s/°")
        print(f"  Ordonnée à l'origine = {intercept_correct:.3f} s")
        print(f"  Erreur standard = {std_err_correct:.4f}")
    if len(incorrect_angles) >= 2:
        print(f"\nRÉGRESSION INCORRECTES:")
        print(f"  Coefficient de corrélation r = {r_incorrect_reg:.3f}")
        print(f"  p-valeur = {p_incorrect_reg:.4f}")
        print(f"  Pente = {slope_incorrect:.4f} s/°")
        print(f"  Ordonnée à l'origine = {intercept_incorrect:.3f} s")
        print(f"  Erreur standard = {std_err_incorrect:.4f}")
    print("="*60)
    
    plt.show()


def main():
    """Fonction principale."""
    results = load_results()
    if results:
        analyze_ade(results)
    else:
        print("\nPour générer les résultats, exécutez d'abord:")
        print("  cd experiments")
        print("  python experience_pygame_3d.py")


if __name__ == "__main__":
    main()

