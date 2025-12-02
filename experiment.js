// Configuration de l'expérience
const CONFIG = {
    totalTrials: 30,
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
    lastRotationTime: null,
    trialResults: [], // Stocker les résultats de chaque essai
    figureSet: null, // Ensemble de 30 figures prédéfinies
    resultsShown: false, // Flag pour éviter l'affichage multiple des résultats
    isProcessingAnswer: false, // Flag pour éviter les clics multiples
    charts: [] // Stocker les instances de graphiques pour éviter les doublons
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
    // Générer l'ensemble de 30 figures
    state.figureSet = generateFigureSet();
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

// Création d'une figure Shepard-Metzler avec configuration personnalisée
function createShepardMetzlerFigure(config) {
    const group = new THREE.Group();
    const { isMirror, arms, blocks, symmetry } = config;
    
    const centralMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x1e3c72 
    });
    
    // Axe central
    const centralAxis = new THREE.BoxGeometry(0.3, 2, 0.3);
    const axis = new THREE.Mesh(centralAxis, centralMaterial);
    group.add(axis);
    
    // Créer les bras selon la configuration
    arms.forEach((arm, index) => {
        const { position, size, orientation } = arm;
        let geometry;
        
        if (orientation === 'vertical') {
            geometry = new THREE.BoxGeometry(size.width, size.height, size.depth);
        } else {
            geometry = new THREE.BoxGeometry(size.width, size.height, size.depth);
        }
        
        const mesh = new THREE.Mesh(geometry, centralMaterial);
        
        // Appliquer la transformation miroir si nécessaire
        let finalPos = { ...position };
        if (isMirror && orientation === 'horizontal') {
            finalPos.x = -finalPos.x;
        }
        
        mesh.position.set(finalPos.x, finalPos.y, finalPos.z || 0);
        group.add(mesh);
    });
    
    // Ajouter les blocs supplémentaires
    blocks.forEach(block => {
        const blockGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
        const blockMesh = new THREE.Mesh(blockGeometry, centralMaterial);
        let pos = { ...block.position };
        if (isMirror) {
            pos.x = -pos.x;
        }
        blockMesh.position.set(pos.x, pos.y, pos.z || 0);
        group.add(blockMesh);
    });
    
    return group;
}

// Génération de 30 configurations de figures différentes
function generateFigureSet() {
    const figures = [];
    
    // Générer 15 configurations de base
    const baseConfigs = [];
    for (let i = 0; i < 15; i++) {
        baseConfigs.push(generateFigureConfig(i));
    }
    
    // 15 figures "same" (identiques) - utiliser les configs de base
    for (let i = 0; i < 15; i++) {
        figures.push({
            id: i,
            isMirror: false,
            config: JSON.parse(JSON.stringify(baseConfigs[i])) // Deep copy
        });
    }
    
    // 15 figures "different" (en miroir) - utiliser les mêmes configs mais marquées comme miroir
    for (let i = 0; i < 15; i++) {
        figures.push({
            id: i + 15,
            isMirror: true,
            config: JSON.parse(JSON.stringify(baseConfigs[i])) // Même config mais isMirror=true
        });
    }
    
    // Mélanger l'ordre pour randomiser
    return shuffleArray(figures);
}

// Générer une configuration de figure unique
function generateFigureConfig(seed) {
    const rng = seededRandom(seed);
    
    const arms = [];
    const blocks = [];
    
    // Axe central avec bras variés
    // Bras supérieur
    arms.push({
        position: { x: 0, y: 1.5, z: 0 },
        size: { width: 0.3, height: 0.8 + rng() * 0.4, depth: 0.3 },
        orientation: 'vertical'
    });
    
    // Bras latéraux (variation selon seed)
    const sideArmCount = Math.floor(rng() * 3) + 2; // 2-4 bras latéraux
    for (let i = 0; i < sideArmCount; i++) {
        const yPos = sideArmCount > 1 ? -1 + i * (2 / (sideArmCount - 1)) : 0;
        const xPos = (rng() > 0.5 ? 1 : -1) * (0.5 + rng() * 0.5);
        arms.push({
            position: { x: xPos, y: yPos, z: 0 },
            size: { width: 0.6 + rng() * 0.6, height: 0.3, depth: 0.3 },
            orientation: 'horizontal'
        });
    }
    
    // Bras inférieur
    arms.push({
        position: { x: 0, y: -1.5, z: 0 },
        size: { width: 0.3, height: 0.8 + rng() * 0.4, depth: 0.3 },
        orientation: 'vertical'
    });
    
    // Blocs supplémentaires (variation)
    const blockCount = Math.floor(rng() * 4) + 1; // 1-4 blocs
    for (let i = 0; i < blockCount; i++) {
        blocks.push({
            position: {
                x: (rng() > 0.5 ? 1 : -1) * (0.7 + rng() * 0.5),
                y: -1 + rng() * 2,
                z: rng() * 0.3
            }
        });
    }
    
    return { arms, blocks, symmetry: rng() > 0.5 };
}

// Générateur de nombres aléatoires avec seed
function seededRandom(seed) {
    let value = seed;
    return function() {
        value = (value * 9301 + 49297) % 233280;
        return value / 233280;
    };
}

// Mélanger un tableau
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Génération d'une paire de figures avec disparité angulaire
function generateFigurePair() {
    if (!state.figureSet || state.currentTrial > state.figureSet.length) {
        // Fallback si pas de figureSet
        state.figureSet = generateFigureSet();
    }
    
    const figureData = state.figureSet[state.currentTrial - 1];
    const angularDisparity = CONFIG.minAngularDisparity + 
        Math.random() * (CONFIG.maxAngularDisparity - CONFIG.minAngularDisparity);
    
    // Créer la figure cible (toujours non-miroir)
    const targetConfig = { ...figureData.config, isMirror: false };
    figureTarget = createShepardMetzlerFigure(targetConfig);
    
    // Créer la figure réponse (avec ou sans miroir selon figureData)
    const responseConfig = { ...figureData.config, isMirror: figureData.isMirror };
    figureResponse = createShepardMetzlerFigure(responseConfig);
    
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
        isMirror: figureData.isMirror,
        angularDisparity: angularDisparity,
        targetRotation: targetRotation,
        responseRotation: responseRotation,
        figureId: figureData.id
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
    // Vérifier si on a terminé tous les essais
    if (state.currentTrial >= CONFIG.totalTrials) {
        // S'assurer que showResults() n'est appelée qu'une seule fois
        if (!state.resultsShown) {
            showResults(); // showResults() met maintenant resultsShown à true
        }
        return;
    }
    
    state.currentTrial++;
    state.startTime = Date.now();
    state.isRotating = false;
    state.rotationTrajectory = [];
    state.lastRotationTime = Date.now();
    state.isProcessingAnswer = false; // Réinitialiser le flag
    
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
    
    // Rotation intuitive : mouvement horizontal = rotation Y, mouvement vertical = rotation X
    // Inverser les signes pour une rotation naturelle
    figureResponse.rotation.y -= deltaX * 0.01;  // Inversé pour rotation naturelle
    figureResponse.rotation.x -= deltaY * 0.01;   // Inversé pour rotation naturelle
    
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
    // Éviter les appels multiples
    if (!state.currentPair || state.isProcessingAnswer || state.resultsShown) return;
    
    state.isProcessingAnswer = true; // Marquer comme en cours de traitement
    
    // Désactiver les boutons pour éviter les clics multiples
    const btnSame = document.getElementById('btn-same');
    const btnDifferent = document.getElementById('btn-different');
    if (btnSame) btnSame.disabled = true;
    if (btnDifferent) btnDifferent.disabled = true;
    
    const responseTime = (Date.now() - state.startTime) / 1000;
    const isCorrect = userSaidMirror === state.currentPair.isMirror;
    
    if (isCorrect) {
        state.correctAnswers++;
    }
    
    state.totalTime += responseTime;
    
    // Enregistrer les résultats de cet essai
    state.trialResults.push({
        trial: state.currentTrial,
        isMirror: state.currentPair.isMirror,
        userAnswer: userSaidMirror,
        isCorrect: isCorrect,
        responseTime: responseTime,
        angularDisparity: state.currentPair.angularDisparity,
        trajectory: [...state.rotationTrajectory]
    });
    
    // Mettre à jour les statistiques
    updateStats();
    
    // Passer au prochain essai après un court délai
    setTimeout(() => {
        // Réactiver les boutons
        if (btnSame) btnSame.disabled = false;
        if (btnDifferent) btnDifferent.disabled = false;
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
    
    // La figure cible reste fixe (pas de rotation automatique)
    // Seule la figure réponse peut être manipulée par l'utilisateur
    
    rendererTarget.render(sceneTarget, cameraTarget);
    rendererResponse.render(sceneResponse, cameraResponse);
}

// Afficher les résultats finaux avec graphiques
function showResults() {
    // Vérifier si la section de résultats existe déjà OU si resultsShown est déjà true
    if (state.resultsShown || document.getElementById('results-section')) {
        return; // Ne pas créer de doublon
    }
    
    // Marquer immédiatement pour éviter les appels multiples
    state.resultsShown = true;
    
    // Masquer les contrôles et afficher la section de résultats
    const controlsEl = document.querySelector('.controls');
    const canvasEl = document.querySelector('.canvas-container');
    const infoEl = document.querySelector('.info-panel');
    
    if (controlsEl) controlsEl.style.display = 'none';
    if (canvasEl) canvasEl.style.display = 'none';
    if (infoEl) infoEl.style.display = 'none';
    
    // Créer et afficher la section de résultats
    const resultsSection = document.createElement('div');
    resultsSection.id = 'results-section';
    resultsSection.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 30px 0;">
            <h2 style="color: #1e3c72; text-align: center; margin-bottom: 30px;">Résultats de l'expérience</h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-top: 4px solid #2a5298;">
                    <div style="font-size: 2.5em; font-weight: bold; color: #1e3c72;">${state.correctAnswers} / ${CONFIG.totalTrials}</div>
                    <div style="color: #666; margin-top: 10px;">Réponses correctes</div>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-top: 4px solid #dc143c;">
                    <div style="font-size: 2.5em; font-weight: bold; color: #dc143c;">${Math.round((state.correctAnswers / CONFIG.totalTrials) * 100)}%</div>
                    <div style="color: #666; margin-top: 10px;">Précision</div>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-top: 4px solid #2a5298;">
                    <div style="font-size: 2.5em; font-weight: bold; color: #1e3c72;">${(state.totalTime / CONFIG.totalTrials).toFixed(2)}s</div>
                    <div style="color: #666; margin-top: 10px;">Temps moyen</div>
                </div>
            </div>
            
            <div style="margin: 30px 0;">
                <canvas id="chart-ade" style="max-width: 100%; height: 400px;"></canvas>
            </div>
            
            <div style="margin: 30px 0;">
                <canvas id="chart-time" style="max-width: 100%; height: 400px;"></canvas>
            </div>
            
            <div style="margin: 30px 0;">
                <canvas id="chart-accuracy" style="max-width: 100%; height: 400px;"></canvas>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <button class="btn btn-reset" onclick="location.reload()" style="padding: 15px 40px; font-size: 1.2em;">Recommencer l'expérience</button>
            </div>
        </div>
    `;
    
    document.querySelector('.experiment-container').appendChild(resultsSection);
    
    // Générer les graphiques
    generateCharts();
}

// Générer les graphiques avec Chart.js
function generateCharts() {
    // Vérifier si les graphiques existent déjà
    if (state.charts.length > 0) {
        // Détruire les anciens graphiques
        state.charts.forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        state.charts = [];
    }
    
    // Vérifier que les canvas existent
    const adeCanvas = document.getElementById('chart-ade');
    const timeCanvas = document.getElementById('chart-time');
    const accuracyCanvas = document.getElementById('chart-accuracy');
    
    if (!adeCanvas || !timeCanvas || !accuracyCanvas) {
        console.error('Les canvas de graphiques ne sont pas trouvés');
        return;
    }
    
    // Préparer les données
    const sameTrials = state.trialResults.filter(r => !r.isMirror);
    const differentTrials = state.trialResults.filter(r => r.isMirror);
    
    // Graphique 1: Effet de disparité angulaire (ADE)
    const adeCtx = adeCanvas.getContext('2d');
    const adeData = {
        labels: state.trialResults.map(r => `Essai ${r.trial}`),
        datasets: [{
            label: 'Disparité angulaire (°)',
            data: state.trialResults.map(r => r.angularDisparity),
            borderColor: '#1e3c72',
            backgroundColor: 'rgba(30, 60, 114, 0.1)',
            yAxisID: 'y',
            tension: 0.4
        }, {
            label: 'Temps de réponse (s)',
            data: state.trialResults.map(r => r.responseTime * 10), // Multiplier par 10 pour visibilité
            borderColor: '#dc143c',
            backgroundColor: 'rgba(220, 20, 60, 0.1)',
            yAxisID: 'y1',
            tension: 0.4
        }]
    };
    
    const chart1 = new Chart(adeCtx, {
        type: 'line',
        data: adeData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Effet de disparité angulaire (ADE)',
                    font: { size: 18, color: '#1e3c72' }
                },
                legend: { display: true }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Disparité angulaire (°)', color: '#1e3c72' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Temps de réponse (s × 10)', color: '#dc143c' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
    state.charts.push(chart1);
    
    // Graphique 2: Temps de réponse par essai
    const timeCtx = timeCanvas.getContext('2d');
    const timeData = {
        labels: state.trialResults.map(r => `Essai ${r.trial}`),
        datasets: [{
            label: 'Temps de réponse (s)',
            data: state.trialResults.map(r => r.responseTime),
            backgroundColor: state.trialResults.map(r => r.isCorrect ? '#2a5298' : '#dc143c'),
            borderColor: state.trialResults.map(r => r.isCorrect ? '#1e3c72' : '#b71c1c'),
            borderWidth: 2
        }]
    };
    
    const chart2 = new Chart(timeCtx, {
        type: 'bar',
        data: timeData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Temps de réponse par essai (Bleu = Correct, Rouge = Incorrect)',
                    font: { size: 18, color: '#1e3c72' }
                },
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Temps (secondes)', color: '#1e3c72' }
                }
            }
        }
    });
    state.charts.push(chart2);
    
    // Graphique 3: Précision par type d'essai
    const accuracyCtx = accuracyCanvas.getContext('2d');
    const sameCorrect = sameTrials.filter(r => r.isCorrect).length;
    const sameTotal = sameTrials.length;
    const diffCorrect = differentTrials.filter(r => r.isCorrect).length;
    const diffTotal = differentTrials.length;
    
    const accuracyData = {
        labels: ['Essais "Same"', 'Essais "Different"'],
        datasets: [{
            label: 'Réponses correctes',
            data: [
                sameTotal > 0 ? (sameCorrect / sameTotal * 100) : 0,
                diffTotal > 0 ? (diffCorrect / diffTotal * 100) : 0
            ],
            backgroundColor: ['#2a5298', '#dc143c'],
            borderColor: ['#1e3c72', '#b71c1c'],
            borderWidth: 2
        }]
    };
    
    const chart3 = new Chart(accuracyCtx, {
        type: 'bar',
        data: accuracyData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Précision par type d\'essai',
                    font: { size: 18, color: '#1e3c72' }
                },
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Précision (%)', color: '#1e3c72' }
                }
            }
        }
    });
    state.charts.push(chart3);
}

