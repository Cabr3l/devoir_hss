// Configuration de l'expérience
const CONFIG = {
    totalTrials: 10,
    minAngularDisparity: 0,
    maxAngularDisparity: 180
};

// État de l'expérience
let state = {
    currentTrial: 0,
    startTime: null,
    isRotating: false,
    correctAnswers: 0,
    totalTime: 0,
    currentPair: null,
    rotationTrajectory: [],
    lastRotationTime: null
};

// Scènes Three.js
let sceneTarget, sceneResponse;
let cameraTarget, cameraResponse;
let rendererTarget, rendererResponse;
let figureTarget, figureResponse;
let controls = {
    isDragging: false,
    previousMousePosition: { x: 0, y: 0 }
};

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    initThreeJS();
    setupEventListeners();
    startNewTrial();
    animate();
});

// Initialisation de Three.js pour les deux canvas
function initThreeJS() {
    // Canvas cible (fixe)
    const canvasTarget = document.getElementById('canvas-target');
    rendererTarget = new THREE.WebGLRenderer({ canvas: canvasTarget, antialias: true });
    rendererTarget.setSize(500, 500);
    sceneTarget = new THREE.Scene();
    cameraTarget = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    cameraTarget.position.set(5, 5, 5);
    cameraTarget.lookAt(0, 0, 0);
    
    // Canvas réponse (rotatable)
    const canvasResponse = document.getElementById('canvas-response');
    rendererResponse = new THREE.WebGLRenderer({ canvas: canvasResponse, antialias: true });
    rendererResponse.setSize(500, 500);
    sceneResponse = new THREE.Scene();
    cameraResponse = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    cameraResponse.position.set(5, 5, 5);
    cameraResponse.lookAt(0, 0, 0);
    
    // Éclairage
    const light1 = new THREE.DirectionalLight(0xffffff, 0.8);
    light1.position.set(5, 5, 5);
    const light2 = new THREE.DirectionalLight(0xffffff, 0.4);
    light2.position.set(-5, -5, -5);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
    
    sceneTarget.add(light1);
    sceneTarget.add(light2);
    sceneTarget.add(ambientLight);
    
    sceneResponse.add(light1.clone());
    sceneResponse.add(light2.clone());
    sceneResponse.add(ambientLight.clone());
    
    // Grille de référence
    const gridHelper = new THREE.GridHelper(10, 10, 0x888888, 0xcccccc);
    sceneTarget.add(gridHelper);
    sceneResponse.add(gridHelper.clone());
}

// Création d'une figure Shepard-Metzler simplifiée
function createShepardMetzlerFigure(isMirror = false) {
    const group = new THREE.Group();
    
    // Structure principale : un axe central avec des bras
    const centralAxis = new THREE.BoxGeometry(0.3, 2, 0.3);
    const centralMaterial = new THREE.MeshPhongMaterial({ 
        color: isMirror ? 0xdc143c : 0x1e3c72 
    });
    const axis = new THREE.Mesh(centralAxis, centralMaterial);
    group.add(axis);
    
    // Bras supérieur
    const arm1 = new THREE.BoxGeometry(0.3, 1, 0.3);
    const arm1Mesh = new THREE.Mesh(arm1, centralMaterial);
    arm1Mesh.position.set(0, 1.5, 0);
    group.add(arm1Mesh);
    
    // Bras latéraux
    const sideArm1 = new THREE.BoxGeometry(1, 0.3, 0.3);
    const sideArm1Mesh = new THREE.Mesh(sideArm1, centralMaterial);
    sideArm1Mesh.position.set(isMirror ? -0.5 : 0.5, 0.5, 0);
    group.add(sideArm1Mesh);
    
    const sideArm2 = new THREE.BoxGeometry(1, 0.3, 0.3);
    const sideArm2Mesh = new THREE.Mesh(sideArm2, centralMaterial);
    sideArm2Mesh.position.set(isMirror ? 0.5 : -0.5, -0.5, 0);
    group.add(sideArm2Mesh);
    
    // Bras inférieur
    const arm2 = new THREE.BoxGeometry(0.3, 1, 0.3);
    const arm2Mesh = new THREE.Mesh(arm2, centralMaterial);
    arm2Mesh.position.set(0, -1.5, 0);
    group.add(arm2Mesh);
    
    // Blocs supplémentaires pour complexité
    const block1 = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    const block1Mesh = new THREE.Mesh(block1, centralMaterial);
    block1Mesh.position.set(isMirror ? -0.8 : 0.8, 0.5, 0);
    group.add(block1Mesh);
    
    const block2 = new THREE.BoxGeometry(0.3, 0.3, 0.3);
    const block2Mesh = new THREE.Mesh(block2, centralMaterial);
    block2Mesh.position.set(isMirror ? 0.8 : -0.8, -0.5, 0);
    group.add(block2Mesh);
    
    return group;
}

// Génération d'une paire de figures avec disparité angulaire
function generateFigurePair() {
    const isMirror = Math.random() < 0.5;
    const angularDisparity = CONFIG.minAngularDisparity + 
        Math.random() * (CONFIG.maxAngularDisparity - CONFIG.minAngularDisparity);
    
    // Créer les figures
    figureTarget = createShepardMetzlerFigure(false);
    figureResponse = createShepardMetzlerFigure(isMirror);
    
    // Orientation initiale de la cible (aléatoire)
    const targetRotation = new THREE.Euler(
        Math.random() * Math.PI * 2,
        Math.random() * Math.PI * 2,
        Math.random() * Math.PI * 2
    );
    figureTarget.rotation.copy(targetRotation);
    
    // Orientation initiale de la réponse (avec disparité angulaire)
    const responseRotation = new THREE.Euler(
        targetRotation.x + (angularDisparity * Math.PI / 180) * (Math.random() - 0.5),
        targetRotation.y + (angularDisparity * Math.PI / 180) * (Math.random() - 0.5),
        targetRotation.z + (angularDisparity * Math.PI / 180) * (Math.random() - 0.5)
    );
    figureResponse.rotation.copy(responseRotation);
    
    // Ajouter aux scènes
    sceneTarget.add(figureTarget);
    sceneResponse.add(figureResponse);
    
    return {
        isMirror: isMirror,
        angularDisparity: angularDisparity,
        targetRotation: targetRotation,
        responseRotation: responseRotation
    };
}

// Calcul de la disparité angulaire entre deux quaternions
function calculateAngularDisparity(q1, q2) {
    const dot = Math.abs(q1.dot(q2));
    const angle = 2 * Math.acos(Math.min(1, dot));
    return angle * 180 / Math.PI;
}

// Démarrer un nouvel essai
function startNewTrial() {
    if (state.currentTrial >= CONFIG.totalTrials) {
        showResults();
        return;
    }
    
    state.currentTrial++;
    state.startTime = Date.now();
    state.isRotating = false;
    state.rotationTrajectory = [];
    state.lastRotationTime = Date.now();
    
    // Nettoyer les scènes précédentes
    if (figureTarget) sceneTarget.remove(figureTarget);
    if (figureResponse) sceneResponse.remove(figureResponse);
    
    // Générer nouvelle paire
    state.currentPair = generateFigurePair();
    
    // Réinitialiser la rotation de la figure réponse
    figureResponse.rotation.set(0, 0, 0);
    
    // Mettre à jour l'UI
    document.getElementById('trial-number').textContent = state.currentTrial;
    document.getElementById('angular-disparity').textContent = 
        Math.round(state.currentPair.angularDisparity);
    
    // Réinitialiser le timer
    updateTimer();
}

// Configuration des événements
function setupEventListeners() {
    const canvasResponse = document.getElementById('canvas-response');
    
    // Rotation avec la souris
    canvasResponse.addEventListener('mousedown', onMouseDown);
    canvasResponse.addEventListener('mousemove', onMouseMove);
    canvasResponse.addEventListener('mouseup', onMouseUp);
    canvasResponse.addEventListener('mouseleave', onMouseUp);
    
    // Boutons de réponse
    document.getElementById('btn-same').addEventListener('click', () => handleAnswer(false));
    document.getElementById('btn-different').addEventListener('click', () => handleAnswer(true));
    document.getElementById('btn-reset').addEventListener('click', startNewTrial);
}

// Gestion de la rotation avec la souris
function onMouseDown(event) {
    controls.isDragging = true;
    controls.previousMousePosition = {
        x: event.clientX,
        y: event.clientY
    };
    state.isRotating = true;
}

function onMouseMove(event) {
    if (!controls.isDragging || !figureResponse) return;
    
    const deltaX = event.clientX - controls.previousMousePosition.x;
    const deltaY = event.clientY - controls.previousMousePosition.y;
    
    // Rotation autour de l'axe Y (horizontal) et X (vertical)
    figureResponse.rotation.y += deltaX * 0.01;
    figureResponse.rotation.x += deltaY * 0.01;
    
    controls.previousMousePosition = {
        x: event.clientX,
        y: event.clientY
    };
    
    // Enregistrer la trajectoire de rotation
    const now = Date.now();
    if (state.lastRotationTime && now - state.lastRotationTime > 20) { // ~50 Hz
        const quaternion = new THREE.Quaternion().setFromEuler(figureResponse.rotation);
        state.rotationTrajectory.push({
            time: (now - state.startTime) / 1000,
            quaternion: quaternion.clone(),
            angularDisparity: calculateAngularDisparity(
                new THREE.Quaternion().setFromEuler(state.currentPair.targetRotation),
                quaternion
            )
        });
        state.lastRotationTime = now;
    }
}

function onMouseUp() {
    controls.isDragging = false;
}

// Gestion de la réponse
function handleAnswer(userSaidMirror) {
    if (!state.currentPair) return;
    
    const responseTime = (Date.now() - state.startTime) / 1000;
    const isCorrect = userSaidMirror === state.currentPair.isMirror;
    
    if (isCorrect) {
        state.correctAnswers++;
    }
    
    state.totalTime += responseTime;
    
    // Mettre à jour les statistiques
    updateStats();
    
    // Passer au prochain essai après un court délai
    setTimeout(() => {
        startNewTrial();
    }, 1500);
}

// Mise à jour des statistiques
function updateStats() {
    document.getElementById('correct-count').textContent = state.correctAnswers;
    
    const avgTime = state.currentTrial > 0 ? 
        (state.totalTime / state.currentTrial).toFixed(2) : '0.0';
    document.getElementById('avg-time').textContent = avgTime;
    
    const accuracy = state.currentTrial > 0 ? 
        Math.round((state.correctAnswers / state.currentTrial) * 100) : 0;
    document.getElementById('accuracy').textContent = accuracy + '%';
}

// Mise à jour du timer
function updateTimer() {
    if (state.startTime) {
        const elapsed = (Date.now() - state.startTime) / 1000;
        document.getElementById('timer').textContent = elapsed.toFixed(1);
        requestAnimationFrame(updateTimer);
    }
}

// Animation
function animate() {
    requestAnimationFrame(animate);
    
    // Rotation automatique légère pour meilleure visualisation
    if (figureTarget && !controls.isDragging) {
        figureTarget.rotation.y += 0.005;
    }
    
    rendererTarget.render(sceneTarget, cameraTarget);
    rendererResponse.render(sceneResponse, cameraResponse);
}

// Afficher les résultats finaux
function showResults() {
    alert(`Expérience terminée !\n\n` +
          `Réponses correctes : ${state.correctAnswers} / ${CONFIG.totalTrials}\n` +
          `Précision : ${Math.round((state.correctAnswers / CONFIG.totalTrials) * 100)}%\n` +
          `Temps moyen : ${(state.totalTime / CONFIG.totalTrials).toFixed(2)} secondes`);
}

