#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Expérience Pygame + PyOpenGL - Rotation 3D
==========================================

Expérience de rotation mentale/physique avec deux conditions :
- Essais avec rotation activée
- Essais sans rotation

Deux figures 3D sont affichées depuis stimuli_data.json :
- La figure de gauche est la cible (fixe).
- La figure de droite peut être tournée avec la souris (si rotation activée).

Contrôles (quand rotation activée) :
- Clic gauche + glisser : faire tourner la figure de droite (3D)
- S : répondre "same" (identiques)
- D : répondre "different" (miroir)
- Échap : quitter

Quand rotation désactivée, seule la réponse (S/D) est possible.
"""

import json
import os
import random
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *


# Configuration
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700


@dataclass
class TrialResult:
    """Résultat d'un essai."""
    trial_number: int
    stimulus_id: str
    is_mirror: bool
    user_response: bool  # True = different, False = same
    response_time: float
    is_correct: bool
    rotation_enabled: bool
    disparity: float = 0.0
    initial_angle: float = 0.0  # ADE initial (angle de rotation du stimulus)


def load_stimuli(json_path="../stimuli_data.json"):
    """Charge tous les stimuli depuis le fichier JSON."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, json_path)
    
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    return data


def draw_figure_from_data(figure_data, rotation, additional_rot_x=0, additional_rot_y=0):
    """Dessine une figure à partir de ses données avec rotations."""
    vertices = figure_data['vertices']
    edges = figure_data['edges']
    faces = figure_data['faces']
    
    # Rotation initiale pour redresser la figure
    glRotatef(-90, 1, 0, 0)
    
    # Appliquer les rotations depuis le JSON
    glRotatef(rotation['y'], 0, 1, 0)
    
    # Rotations supplémentaires (pour la figure de droite interactive)
    if additional_rot_x != 0 or additional_rot_y != 0:
        glRotatef(additional_rot_x, 1, 0, 0)
        glRotatef(additional_rot_y, 0, 1, 0)
    
    # Dessiner les faces (bleu transparent)
    glColor4f(0.0, 0.0, 1.0, 0.5)
    glBegin(GL_QUADS)
    for face in faces:
        for vertex_idx in face:
            vertex = vertices[vertex_idx]
            glVertex3fv(vertex)
    glEnd()
    
    # Dessiner les arêtes (bleu plus foncé)
    glColor4f(0.0, 0.4, 0.8, 1.0)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex_idx in edge:
            vertex = vertices[vertex_idx]
            glVertex3fv(vertex)
    glEnd()


def calculate_angular_disparity(initial_angle_y, user_rot_x, user_rot_y):
    """Calcule la disparité angulaire entre la rotation initiale et la rotation utilisateur.
    
    Args:
        initial_angle_y: Angle initial de rotation autour de l'axe Y (en degrés)
        user_rot_x: Rotation utilisateur autour de l'axe X (en degrés)
        user_rot_y: Rotation utilisateur autour de l'axe Y (en degrés)
    
    Returns:
        Disparité angulaire totale en degrés
    """
    import math
    # Calculer l'angle total de rotation utilisateur (norme du vecteur de rotation)
    # Pour une rotation 3D, on calcule l'angle total comme la norme du vecteur de rotation
    total_rotation = math.sqrt(user_rot_x * user_rot_x + user_rot_y * user_rot_y)
    
    # La disparité est l'angle total de rotation appliqué par l'utilisateur
    # par rapport à la position initiale
    return total_rotation


def generate_trial_set(stimuli, n_with_rotation=10, n_without_rotation=10):
    """Génère un ensemble d'essais avec conditions."""
    # Filtrer les stimuli qui ont is_mirror défini (non None)
    valid_stimuli = [s for s in stimuli if s.get('is_mirror') is not None]
    
    if len(valid_stimuli) < (n_with_rotation + n_without_rotation):
        print(f"Attention: Seulement {len(valid_stimuli)} stimuli valides disponibles")
        valid_stimuli = stimuli[:n_with_rotation + n_without_rotation]
    
    # Mélanger
    random.shuffle(valid_stimuli)
    
    trials = []
    for i, stimulus in enumerate(valid_stimuli[:n_with_rotation + n_without_rotation]):
        rotation_enabled = i < n_with_rotation
        trials.append({
            'stimulus': stimulus,
            'rotation_enabled': rotation_enabled,
            'is_mirror': stimulus.get('is_mirror', False)
        })
    
    return trials


def analyze_ade_automatically(results_dict):
    """Analyse automatique de l'ADE après l'expérience."""
    if not results_dict:
        return
    
    # Séparer par rotation
    rotables = [r for r in results_dict if r['rotation_enabled']]
    non_rotables = [r for r in results_dict if not r['rotation_enabled']]
    
    # Fonction pour faire un plot
    def make_plot(data, title, filename):
        correct = [r for r in data if r['is_correct']]
        incorrect = [r for r in data if not r['is_correct']]
        
        correct_angles = [r['initial_angle'] for r in correct]
        correct_times = [r['response_time'] for r in correct]
        incorrect_angles = [r['initial_angle'] for r in incorrect]
        incorrect_times = [r['response_time'] for r in incorrect]
        
        # Calculer régressions
        if len(correct_angles) >= 2:
            slope_c, intercept_c, r_c, p_c, _ = linregress(correct_angles, correct_times)
        else:
            slope_c, intercept_c, r_c, p_c = 0, 0, 0, 1
        
        if len(incorrect_angles) >= 2:
            slope_i, intercept_i, r_i, p_i, _ = linregress(incorrect_angles, incorrect_times)
        else:
            slope_i, intercept_i, r_i, p_i = 0, 0, 0, 1
        
        # Plot
        plt.figure(figsize=(8, 6), facecolor='#D0D0D0')
        plt.gca().set_facecolor('#D0D0D0')
        if correct_angles:
            plt.scatter(correct_angles, correct_times, color='green', label=f'Correctes (r={r_c:.3f}, p={p_c:.3f})')
            if len(correct_angles) >= 2:
                x = np.linspace(min(correct_angles), max(correct_angles), 100)
                plt.plot(x, slope_c * x + intercept_c, 'g-')
        if incorrect_angles:
            plt.scatter(incorrect_angles, incorrect_times, color='red', label=f'Incorrectes (r={r_i:.3f}, p={p_i:.3f})')
            if len(incorrect_angles) >= 2:
                x = np.linspace(min(incorrect_angles), max(incorrect_angles), 100)
                plt.plot(x, slope_i * x + intercept_i, 'r-')
        plt.xlabel('Angle (ADE) [°]')
        plt.ylabel('Temps de réponse [s]')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(os.path.dirname(__file__), filename), facecolor='#D0D0D0')
        plt.show()
        
        print(f"{title}: Correctes r={r_c:.3f}, p={p_c:.4f} | Incorrectes r={r_i:.3f}, p={p_i:.4f}")
    
    # Plot 1: Rotables
    if rotables:
        make_plot(rotables, "Avec rotation", "resultat_experience_pygame_3d_ade_rotation.png")
    
    # Plot 2: Non-rotables
    if non_rotables:
        make_plot(non_rotables, "Sans rotation", "resultat_experience_pygame_3d_ade_sans_rotation.png")


def show_results(results):
    """Affiche les résultats de l'expérience."""
    if not results:
        print("Aucun résultat à afficher")
        return
    
    print("\n" + "="*60)
    print("RÉSULTATS DE L'EXPÉRIENCE")
    print("="*60)
    
    total = len(results)
    correct = sum(1 for r in results if r.is_correct)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"Total d'essais: {total}")
    print(f"Réponses correctes: {correct}")
    print(f"Précision: {accuracy:.1f}%")
    
    # Par condition
    with_rotation = [r for r in results if r.rotation_enabled]
    without_rotation = [r for r in results if not r.rotation_enabled]
    
    if with_rotation:
        correct_wr = sum(1 for r in with_rotation if r.is_correct)
        print(f"\nAvec rotation: {correct_wr}/{len(with_rotation)} ({correct_wr/len(with_rotation)*100:.1f}%)")
    
    if without_rotation:
        correct_wor = sum(1 for r in without_rotation if r.is_correct)
        print(f"Sans rotation: {correct_wor}/{len(without_rotation)} ({correct_wor/len(without_rotation)*100:.1f}%)")
    
    # Temps de réponse moyen
    avg_time = sum(r.response_time for r in results) / len(results) if results else 0
    print(f"\nTemps de réponse moyen: {avg_time:.2f}s")
    
    # Disparité angulaire moyenne
    avg_disparity = sum(r.disparity for r in results) / len(results) if results else 0
    print(f"Disparité angulaire moyenne: {avg_disparity:.2f}°")


def run_experiment_3d():
    """Fonction principale pour exécuter l'expérience 3D."""
    # Charger les stimuli
    all_stimuli = load_stimuli()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    print(f"Stimuli chargés: {len(all_stimuli)}")

    # Générer l'ensemble d'essais
    trials = generate_trial_set(all_stimuli, n_with_rotation=10, n_without_rotation=10)
    print(f"Essais générés: {len(trials)}")

    # Initialisation Pygame et OpenGL
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Expérience de rotation 3D - PyOpenGL")
    clock = pygame.time.Clock()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.5, 0.5, 0.5, 1.0)  # Fond gris

    # État de l'expérience
    current_trial = 0
    results = []
    start_time = time.time()

    # Rotation de la figure de droite
    response_rot_x = 0.0
    response_rot_y = 0.0
    mouse_dragging = False
    last_mouse_pos = None

    # Préparer le premier essai
    current_trial_data = trials[0]
    rotation_enabled = current_trial_data['rotation_enabled']
    condition = "AVEC ROTATION" if rotation_enabled else "SANS ROTATION"
    print(f"\nEssai 1/{len(trials)} - {condition}")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    # Réponse: Same
                    response_time = time.time() - start_time
                    stimulus = current_trial_data['stimulus']
                    is_correct = not current_trial_data['is_mirror']  # Same = not mirror
                    
                    result = TrialResult(
                        trial_number=current_trial + 1,
                        stimulus_id=stimulus['id'],
                        is_mirror=current_trial_data['is_mirror'],
                        user_response=False,  # False = same
                        response_time=response_time,
                        is_correct=is_correct,
                        rotation_enabled=rotation_enabled,
                        disparity=calculate_angular_disparity(rotation['y'], response_rot_x, response_rot_y),
                        initial_angle=stimulus.get('angle', 0.0)
                    )
                    results.append(result)
                    print(f"✓ Essai {current_trial + 1}: {'CORRECT' if is_correct else 'INCORRECT'} (Same, {response_time:.2f}s)")
                    
                    # Passer au prochain essai
                    current_trial += 1
                    if current_trial >= len(trials):
                        running = False
                        break
                    
                    current_trial_data = trials[current_trial]
                    rotation_enabled = current_trial_data['rotation_enabled']
                    response_rot_x = 0.0
                    response_rot_y = 0.0
                    start_time = time.time()
                    condition = "AVEC ROTATION" if rotation_enabled else "SANS ROTATION"
                    print(f"\nEssai {current_trial + 1}/{len(trials)} - {condition}")
                    
                elif event.key == pygame.K_d:
                    # Réponse: Different
                    response_time = time.time() - start_time
                    stimulus = current_trial_data['stimulus']
                    is_correct = current_trial_data['is_mirror']  # Different = mirror
                    
                    result = TrialResult(
                        trial_number=current_trial + 1,
                        stimulus_id=stimulus['id'],
                        is_mirror=current_trial_data['is_mirror'],
                        user_response=True,  # True = different
                        response_time=response_time,
                        is_correct=is_correct,
                        rotation_enabled=rotation_enabled,
                        disparity=calculate_angular_disparity(rotation['y'], response_rot_x, response_rot_y),
                        initial_angle=stimulus.get('angle', 0.0)
                    )
                    results.append(result)
                    print(f"✓ Essai {current_trial + 1}: {'CORRECT' if is_correct else 'INCORRECT'} (Different, {response_time:.2f}s)")
                    
                    # Passer au prochain essai
                    current_trial += 1
                    if current_trial >= len(trials):
                        running = False
                        break
                    
                    current_trial_data = trials[current_trial]
                    rotation_enabled = current_trial_data['rotation_enabled']
                    response_rot_x = 0.0
                    response_rot_y = 0.0
                    start_time = time.time()
                    condition = "AVEC ROTATION" if rotation_enabled else "SANS ROTATION"
                    print(f"\nEssai {current_trial + 1}/{len(trials)} - {condition}")
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and rotation_enabled:  # Clic gauche
                    mouse_dragging = True
                    last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging and rotation_enabled:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    
                    response_rot_y += dx * 0.5
                    response_rot_x += dy * 0.5
                    
                    last_mouse_pos = event.pos
        
        # Rendu
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Configurer la projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 100)
        
        # Configurer la vue
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Positionner la caméra (dézoomé)
        glTranslatef(0, 0, -18)
        glRotatef(25, 1, 0, 0)
        
        # Obtenir le stimulus actuel
        stimulus = current_trial_data['stimulus']
        rotation = stimulus.get('rotation', {'x': 0, 'y': 0, 'z': 0})
        
        # Figure de gauche (fixe)
        glPushMatrix()
        glTranslatef(-4, 0, 0)
        draw_figure_from_data(stimulus['figure_left'], rotation)
        glPopMatrix()
        
        # Figure de droite (rotatable si rotation activée)
        glPushMatrix()
        glTranslatef(4, 0, 0)
        if rotation_enabled:
            draw_figure_from_data(stimulus['figure_right'], rotation, response_rot_x, response_rot_y)
        else:
            draw_figure_from_data(stimulus['figure_right'], rotation)
        glPopMatrix()
        
        pygame.display.flip()

    pygame.quit()
    
    # Sauvegarder les résultats dans un fichier JSON
    results_dict = []
    for r in results:
        results_dict.append({
            'trial_number': r.trial_number,
            'stimulus_id': r.stimulus_id,
            'is_mirror': r.is_mirror,
            'user_response': r.user_response,
            'response_time': r.response_time,
            'is_correct': r.is_correct,
            'rotation_enabled': r.rotation_enabled,
            'disparity': r.disparity,
            'initial_angle': r.initial_angle
        })
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.join(script_dir, "experiment_results.json")
    with open(results_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"\n✓ Résultats sauvegardés dans {results_path}")
    
    # Afficher les résultats
    show_results(results)
    
    # Effectuer l'analyse ADE automatiquement
    if results:
        print("\n" + "="*60)
        print("ANALYSE ADE AUTOMATIQUE")
        print("="*60)
        analyze_ade_automatically(results_dict)


if __name__ == "__main__":
    run_experiment_3d()

