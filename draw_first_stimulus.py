import pygame
from pygame.locals import *
import json
import os

from OpenGL.GL import *
from OpenGL.GLU import *

def load_all_stimuli(json_path="stimuli_data.json"):
    """Charge tous les stimuli depuis le fichier JSON. Chaque stimulus contient figure_left et figure_right."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    if not data:
        raise ValueError("Aucun stimulus trouvé dans le fichier")
    
    return data

def draw_figure_from_data(figure_data, rotation):
    """Dessine une figure à partir de ses données (vertices, edges, faces) avec rotations."""
    vertices = figure_data['vertices']
    edges = figure_data['edges']
    faces = figure_data['faces']
    
    # Rotation initiale pour redresser la figure (les coordonnées Y sont négatives dans les patterns)
    glRotatef(-90, 1, 0, 0)  # Rotation autour de X pour mettre la figure debout
    
    # Appliquer les rotations depuis le JSON (rotation autour de Y pour l'angle de vue)
    glRotatef(rotation['y'], 0, 1, 0)  # Rotation autour de Y selon l'angle de l'image
    
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

# Charger tous les stimuli
all_stimuli = load_all_stimuli()
current_index = 0
json_path = "stimuli_data.json"

# Rotation de la figure de droite
right_rotation_x = 0.0
right_rotation_y = 0.0
mouse_dragging = False
last_mouse_pos = None

def save_stimulus_to_json():
    """Sauvegarde le stimulus actuel dans le JSON."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    data[current_index] = all_stimuli[current_index]
    
    # Sauvegarder avec le format un objet par ligne
    with open(json_path, 'w') as f:
        f.write('[\n')
        for i, obj in enumerate(data):
            obj_str = json.dumps(obj, separators=(',', ':'))
            f.write(obj_str)
            if i < len(data) - 1:
                f.write(',')
            f.write('\n')
        f.write(']')
    
    print(f"✓ Sauvegardé dans {json_path}")

print(f"Nombre total de stimuli: {len(all_stimuli)}")
print(f"Stimulus actuel: {current_index + 1}/{len(all_stimuli)}")
print("Contrôles:")
print("  - Souris: faire glisser pour tourner la figure de droite")
print("  - S: Same (figures identiques, is_mirror=false)")
print("  - D: Different (figures miroir, is_mirror=true)")
print("  - Flèches gauche/droite: naviguer entre les stimuli")

pygame.init()

display = (1200, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0.0, 0.0, 0.0, 1.0)  # Fond noir

# Police pour afficher le texte
font = pygame.font.Font(None, 36)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                # Stimulus suivant
                current_index = (current_index + 1) % len(all_stimuli)
                stimulus = all_stimuli[current_index]
                right_rotation_x = 0.0
                right_rotation_y = 0.0
                print(f"Stimulus {current_index + 1}/{len(all_stimuli)}: {stimulus['id']} (angle: {stimulus['angle']})")
            elif event.key == pygame.K_LEFT:
                # Stimulus précédent
                current_index = (current_index - 1) % len(all_stimuli)
                stimulus = all_stimuli[current_index]
                right_rotation_x = 0.0
                right_rotation_y = 0.0
                print(f"Stimulus {current_index + 1}/{len(all_stimuli)}: {stimulus['id']} (angle: {stimulus['angle']})")
            elif event.key == pygame.K_s:
                # Same - figures identiques
                all_stimuli[current_index]['is_mirror'] = False
                save_stimulus_to_json()
                print(f"✓ Réponse: SAME (is_mirror=false)")
            elif event.key == pygame.K_d:
                # Different - figures miroir
                all_stimuli[current_index]['is_mirror'] = True
                save_stimulus_to_json()
                print(f"✓ Réponse: DIFFERENT (is_mirror=true)")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                mouse_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                
                # Rotation de la figure de droite
                right_rotation_y += dx * 0.5
                right_rotation_x += dy * 0.5
                
                last_mouse_pos = event.pos
    
    # Charger le stimulus actuel
    stimulus = all_stimuli[current_index]
    rotation = stimulus.get('rotation', {'x': 0, 'y': 0, 'z': 0})
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Configurer la projection à chaque frame
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 100)
    
    # Configurer la vue
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Positionner la caméra pour voir les figures correctement (comme dans les images)
    glTranslatef(0, 0, -12)  # Distance de la caméra
    glRotatef(25, 1, 0, 0)   # Rotation vers le bas pour voir les figures
    
    # Figure de gauche
    glPushMatrix()
    glTranslatef(-4, 0, 0)
    draw_figure_from_data(stimulus['figure_left'], rotation)
    glPopMatrix()
    
    # Figure de droite (avec rotation interactive)
    glPushMatrix()
    glTranslatef(4, 0, 0)
    # Appliquer les rotations supplémentaires de la souris
    glRotatef(right_rotation_x, 1, 0, 0)
    glRotatef(right_rotation_y, 0, 1, 0)
    draw_figure_from_data(stimulus['figure_right'], rotation)
    glPopMatrix()
    
    # Afficher les informations du stimulus
    pygame.display.flip()
    pygame.time.wait(10)

