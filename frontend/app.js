import * as THREE from 'three';

let scene, camera, renderer, cube;
let audioListener, audioSource;

init();
animate();

function init() {
  // Scene & camera
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x202020);
  camera = new THREE.PerspectiveCamera(70, window.innerWidth/window.innerHeight, 0.1, 1000);
  camera.position.set(0, 1.6, 3);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.xr.enabled = true;
  document.body.appendChild(renderer.domElement);
  document.body.appendChild(THREE.WEBXR.createButton(renderer));

  // Audio
  audioListener = new THREE.AudioListener();
  camera.add(audioListener);
  audioSource = new THREE.Audio(audioListener);

  // Simple cube
  const geometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
  const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
  cube = new THREE.Mesh(geometry, material);
  cube.position.set(0, 1.5, -1);
  scene.add(cube);

  // Light
  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(1, 3, 2);
  scene.add(light);

  // Button
  document.getElementById('ask-btn').onclick = () => sendQuestion("How would you solve a binary tree problem?");
}

function animate() {
  renderer.setAnimationLoop(() => {
    // Pulse cube while talking
    if (audioSource.isPlaying) {
      const scale = 1 + Math.sin(Date.now() * 0.01) * 0.1;
      cube.scale.set(scale, scale, scale);
    }
    renderer.render(scene, camera);
  });
}

async function sendQuestion(text) {
  try {
    const res = await fetch('http://localhost:3000/api/interview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    console.log("AI Response:", data.text);

    // Convert base64 to AudioBuffer
    const audioData = Uint8Array.from(atob(data.audio), c => c.charCodeAt(0)).buffer;
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const decoded = await audioCtx.decodeAudioData(audioData);

    audioSource.setBuffer(decoded);
    audioSource.play();

  } catch (err) {
    console.error("Error:", err);
  }
}
