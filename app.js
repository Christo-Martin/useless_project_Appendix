/**
 * MURMOR TOM 3000 — Absurd Audio Processor & Web UI Controller
 */

// Absurdist Quotes Database
const ABSURD_QUOTES = [
    '"Your words are safe. We have destroyed them."',
    '"Communication, but worse."',
    '"Because sometimes you want someone to talk without having to listen."',
    '"Finally, a solution to the problem of people saying things."',
    '"Preserving the voice. Eliminating the point."',
    '"Powered by artificial intelligence and questionable decisions."',
    '"99% speech. 0% useful information."',
    '"Your brain can\'t overthink what it can\'t understand."'
];

const SLIDER_LABELS = {
    1: 'HUMAN SPEECH',
    2: 'FOREIGN-SOUNDING',
    3: 'CONFUSING',
    4: 'GIBBERISH',
    5: 'WHY DID WE BUILD THIS'
};

// Backend URL — change this if your server runs on a different port
const API_BASE = 'http://localhost:8000';

const DRAMATIC_STEPS = [
    "Listening to human conversation...",
    "Transcribing semantic content...",
    "Understanding what was said...",
    "Regretting reading your audio file...",
    "Stripping 100% of useful information...",
    "Extracting pure pitch & expressive prosody...",
    "Synthesizing speech-like nonsense...",
    "Reconstructing absolutely nothing...",
    "Done! Meaning successfully eliminated."
];

// App State
let loadedAudioFile  = null;
let loadedAudioUrl   = null;
let currentLevel     = 3;       // kept in sync with the slider
let mediaRecorder    = null;
let recordedChunks   = [];
let isRecording      = false;
let audioCtx         = null;
let analyserNode     = null;
let animationFrameId = null;

// DOM Elements
document.addEventListener('DOMContentLoaded', () => {
    initQuotesTicker();
    initDragAndDrop();
    initMicRecorder();
    initSlider();
    initSampleButton();
    initProcessButton();
    initUselessButton();
    initAudioVisualizer();
});

// Rotate absurd quotes
function initQuotesTicker() {
    const quoteEl = document.getElementById('random-quote');
    let index = 0;
    setInterval(() => {
        index = (index + 1) % ABSURD_QUOTES.length;
        quoteEl.style.opacity = '0';
        setTimeout(() => {
            quoteEl.textContent = ABSURD_QUOTES[index];
            quoteEl.style.opacity = '1';
        }, 300);
    }, 6000);
}

// Drag & Drop / File Input
function initDragAndDrop() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleSelectedFile(e.target.files[0]);
        }
    });
}

function handleSelectedFile(file) {
    if (!file.type.startsWith('audio/') && !file.name.endsWith('.wav') && !file.name.endsWith('.mp3')) {
        alert("Please select a valid audio file (.wav or .mp3)");
        return;
    }

    loadedAudioFile = file;
    loadedAudioUrl = URL.createObjectURL(file);
    displayInputAudio(loadedAudioUrl, file.name);
}

function displayInputAudio(url, name = "Uploaded Audio") {
    const previewCard = document.getElementById('input-preview-card');
    const player = document.getElementById('audio-input-player');
    const processBtn = document.getElementById('btn-process');
    const canvasStatus = document.getElementById('canvas-status');

    player.src = url;
    previewCard.classList.remove('hidden');
    processBtn.disabled = false;
    canvasStatus.textContent = `LOADED: ${name.toUpperCase()}`;

    // Connect to Visualizer
    setupAudioNode(player);
}

// Microphone Recorder
function initMicRecorder() {
    const recordBtn = document.getElementById('btn-record');
    const recordText = document.getElementById('record-text');

    recordBtn.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];

                mediaRecorder.ondataavailable = (e) => {
                    if (e.data.size > 0) recordedChunks.push(e.data);
                };

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(recordedChunks, { type: 'audio/wav' });
                    loadedAudioFile = new File([audioBlob], "mic-recording.wav", { type: "audio/wav" });
                    loadedAudioUrl = URL.createObjectURL(audioBlob);
                    displayInputAudio(loadedAudioUrl, "Microphone Recording");
                };

                mediaRecorder.start();
                isRecording = true;
                recordBtn.classList.add('recording');
                recordText.textContent = "STOP RECORDING";
                document.getElementById('canvas-status').textContent = "🔴 RECORDING MICROPHONE...";
            } catch (err) {
                alert("Microphone access denied or unsupported by browser.");
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            recordBtn.classList.remove('recording');
            recordText.textContent = "Record Microphone";
        }
    });
}

// Uselessness Level Slider
function initSlider() {
    const slider = document.getElementById('useless-slider');
    const badge  = document.getElementById('slider-level-text');

    const update = () => {
        currentLevel      = parseInt(slider.value, 10);
        badge.textContent = SLIDER_LABELS[currentLevel] || 'CONFUSING';
    };

    slider.addEventListener('input', update);
    update(); // set initial label on page load
}

// Pre-loaded Repository Sample ("Harvard Sentences")
function initSampleButton() {
    const sampleBtn = document.getElementById('btn-sample');

    sampleBtn.addEventListener('click', () => {
        // Use repository sample audio
        const sampleUrl = 'test_audios/harv-test.wav';
        loadedAudioUrl = sampleUrl;
        loadedAudioFile = null; // signifies sample
        displayInputAudio(sampleUrl, "Harvard Test Sample");
    });
}

// Main Processing Execution
function initProcessButton() {
    const processBtn = document.getElementById('btn-process');
    const terminalBox = document.getElementById('processing-box');
    const terminalLog = document.getElementById('terminal-log');
    const resultsSection = document.getElementById('results-section');

    processBtn.addEventListener('click', async () => {
        processBtn.disabled = true;
        terminalBox.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        terminalLog.innerHTML = '';

        // Run dramatic step timer
        let stepIdx = 0;
        const stepInterval = setInterval(() => {
            if (stepIdx < DRAMATIC_STEPS.length) {
                const line = document.createElement('div');
                line.className = 'log-line active';
                line.textContent = `> ${DRAMATIC_STEPS[stepIdx]}`;
                terminalLog.appendChild(line);
                terminalLog.scrollTop = terminalLog.scrollHeight;
                stepIdx++;
            } else {
                clearInterval(stepInterval);
                finishProcessing();
            }
        }, 600);
    });
}

async function finishProcessing() {
    const processBtn     = document.getElementById('btn-process');
    const resultsSection = document.getElementById('results-section');
    const origAudioPlayer = document.getElementById('audio-orig-player');
    const outAudioPlayer  = document.getElementById('audio-output-player');
    const origText        = document.getElementById('text-original');
    const gibText         = document.getElementById('text-gibberish');
    const terminalLog     = document.getElementById('terminal-log');

    const addLog = (msg, cls = 'active') => {
        const line = document.createElement('div');
        line.className = `log-line ${cls}`;
        line.textContent = msg;
        terminalLog.appendChild(line);
        terminalLog.scrollTop = terminalLog.scrollHeight;
    };

    // Show original audio
    const originalAudio = loadedAudioUrl || 'test_audios/harv-test.wav';
    origAudioPlayer.src = originalAudio;

    if (loadedAudioFile) {
        // ── Live server path ────────────────────────────────────────────
        addLog(`> Sending to server at level ${currentLevel} — ${SLIDER_LABELS[currentLevel]}...`);

        const formData = new FormData();
        formData.append('file', loadedAudioFile);  // the audio
        formData.append('level', currentLevel);     // slider value (1-5)

        try {
            const response = await fetch(`${API_BASE}/process`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const err = await response.text();
                throw new Error(`Server error ${response.status}: ${err}`);
            }

            const outBlob = await response.blob();
            outAudioPlayer.src = URL.createObjectURL(outBlob);
            origText.textContent = '"(original audio above)"';
            gibText.textContent  = `"(level ${currentLevel} — ${SLIDER_LABELS[currentLevel]})"`;
            addLog('> Done! Meaning successfully eliminated.');

        } catch (err) {
            addLog(`> Server unreachable — using pre-processed sample.`);
            addLog(`  (${err.message})`);
            // Graceful fallback: play the pre-processed sample from the repo
            outAudioPlayer.src = 'output_audios/dubbed_output.wav';
            origText.textContent = '"The stale smell of old beer lingers..."';
            gibText.textContent  = '"(pre-processed sample — start server for live processing)"';
        }

    } else {
        // ── Static demo path (no file uploaded, GitHub Pages) ──────────
        addLog('> No file uploaded — loading pre-processed sample...');
        outAudioPlayer.src   = 'output_audios/dubbed_output.wav';
        origText.textContent = '"The stale smell of old beer lingers. It takes heat to bring out the odor."';
        gibText.textContent  = '"Duh stal smay o o beer lenge. Et tak heat tu breng u th odor."';
        addLog('> Sample loaded.');
    }

    resultsSection.classList.remove('hidden');
    processBtn.disabled = false;
    animateMeaningMeter();
}

function animateMeaningMeter() {
    const bar = document.getElementById('meaning-bar');
    const percentEl = document.getElementById('meaning-percent');
    const labelEl = document.getElementById('meaning-label');

    bar.style.width = '100%';
    percentEl.textContent = '100%';
    labelEl.textContent = '"Unfortunately understandable"';

    setTimeout(() => {
        bar.style.width = '0%';
        percentEl.textContent = '0%';
        labelEl.textContent = '"Perfect. Absolutely meaningless."';
    }, 400);
}

// Uselessness Score Button
function initUselessButton() {
    const btn = document.getElementById('btn-more-useless');
    const scoreEl = document.getElementById('uselessness-score');
    let val = 98.7;

    btn.addEventListener('click', () => {
        val = Math.min(99.99, val + 0.3);
        scoreEl.textContent = `${val.toFixed(2)}%`;
        scoreEl.style.color = '#00ff66';
        setTimeout(() => scoreEl.style.color = 'var(--accent-cyan)', 300);
    });
}

// Web Audio API Oscilloscope & VU Visualizer
function initAudioVisualizer() {
    const canvas = document.getElementById('waveform-canvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Initial idle animation loop
    function drawIdleWave() {
        ctx.fillStyle = '#050608';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ff5500';
        ctx.beginPath();

        const sliceWidth = canvas.width / 100;
        let x = 0;
        const time = Date.now() * 0.003;

        for (let i = 0; i < 100; i++) {
            const v = Math.sin(i * 0.1 + time) * 15 + Math.cos(i * 0.05 + time * 1.5) * 10;
            const y = canvas.height / 2 + v;

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);

            x += sliceWidth;
        }

        ctx.stroke();
        animationFrameId = requestAnimationFrame(drawIdleWave);
    }

    drawIdleWave();
}

function setupAudioNode(audioElement) {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        analyserNode = audioCtx.createAnalyser();
        analyserNode.fftSize = 256;
    }

    try {
        const source = audioCtx.createMediaElementSource(audioElement);
        source.connect(analyserNode);
        analyserNode.connect(audioCtx.destination);
    } catch (e) {
        // Element already connected
    }
}
