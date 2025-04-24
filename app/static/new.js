import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 0, 3);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);





const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 1;
controls.maxDistance = 8;
let box;
let model; 


window.addEventListener('DOMContentLoaded', () => {
  window.closeAlert = function () {
    const alertDiv = document.getElementById('cyber-Alert');
    if (alertDiv) {
      alertDiv.style.display = 'none';
    }
  };
  
});

 window.toggleMobileNav = function () {
    const nav = document.getElementById('mobileNav');
    const hamburger = document.getElementById('hamburger');
    const closeIcon = document.getElementById('closeIcon');

    nav.classList.toggle('show');

    const isVisible = nav.classList.contains('show');
    hamburger.style.display = isVisible ? 'none' : 'block';
    closeIcon.style.display = isVisible ? 'block' : 'none';
  };


function updateBoxPosition() {
    if (box && model) {
        
        box.position.copy(model.position);
    }
}




const loader = new GLTFLoader();
const textureLoader = new THREE.TextureLoader();




function scaleModelForScreen() {
    if (!model) return;
  
    const isMobile = window.innerWidth <= 600;
  
    const scaleValue = isMobile ? 1.5 : 3;
    model.scale.set(scaleValue, scaleValue, scaleValue);
  
    if (isMobile) {
      model.position.set(0, 0, 1.3); 
    } else {
      model.position.set(1, 0.2, 0.5); 
    }
  }

loader.load(
  '/models/earth (5).glb',
  (gltf) => {
    model = gltf.scene; 
    scene.add(model);

    scaleModelForScreen(); 

    window.addEventListener('resize', scaleModelForScreen);

    textureLoader.load('/models/', (earthBaseTexture) => {
      textureLoader.load('/models/earthlights1k2.jpg', (earthLightsTexture) => {
        model.traverse((child) => {
          if (child.isMesh) {
            let baseMaterial = new THREE.MeshStandardMaterial({
              map: earthBaseTexture,
            });

            let lightsMaterial = new THREE.MeshStandardMaterial({
              map: null,
              emissiveMap: earthLightsTexture,
              emissive: new THREE.Color(0xffffff),
              emissiveIntensity: 2,
              transparent: true,
              blending: THREE.AdditiveBlending,
              depthWrite: false,
            });

            child.material = [baseMaterial, lightsMaterial];
            child.material.forEach(mat => mat.needsUpdate = true);
          }
        });

        animateBlinking();
      });
    });

    const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
    const boxMaterial = new THREE.MeshBasicMaterial({
      color: 0x000000,
      transparent: true,
      opacity: 0,
    });

    const markerBox = new THREE.Mesh(boxGeometry, boxMaterial);
    markerBox.position.copy(model.position);
    scene.add(markerBox);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    window.addEventListener('click', onMouseClick, false);
    window.addEventListener('mousemove', onMouseMove, false);

    function onMouseClick(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObject(markerBox, true);
    
      if (intersects.length > 0) {
        // ✅ Close the cyber alert
        if (typeof closeAlert === 'function') {
          closeAlert();
        }
    
        const demoWrapper = document.querySelector('.demo-wrapper');
        if (demoWrapper) {
          demoWrapper.classList.add('show');
    
          const screenPos = markerBox.position.clone().project(camera);
          const x = (screenPos.x * 0.5 + 0.5) * window.innerWidth;
          const y = -(screenPos.y * 0.5 - 0.5) * window.innerHeight;
    
          demoWrapper.style.left = `${x}px`;
          demoWrapper.style.top = `${y}px`;
        }
      }
    }
    

    function onMouseMove(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObject(markerBox, true);
      document.body.style.cursor = intersects.length > 0 ? 'pointer' : 'auto';
    }
  }
);


const closeBtn = document.querySelector('.close');
if (closeBtn) {
  closeBtn.addEventListener('click', () => {
    const demoWrapper = document.querySelector('.demo-wrapper');
    if (demoWrapper) {
      demoWrapper.classList.remove('show');
    }
  });
}

  

function animateBlinking() {
    let clock = new THREE.Clock(); 

    function update() {
        requestAnimationFrame(update);
        
        let time = clock.getElapsedTime(); 
        let intensity = Math.abs(Math.sin(time * 3)) * 2 + 1; 

        if (model) {
            model.traverse((child) => {
                if (child.isMesh && child.material.length > 1) {
                    
                    child.material[1].emissiveIntensity = intensity;
                }
            });
        }
    }

    update();
}


const ambientLight = new THREE.AmbientLight(0xffffff, 0.8); 
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 6); 
directionalLight.position.set(-2, 1, 2); 

// ✅ Shadow Fixes
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048; 
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.bias = -0.002; 
directionalLight.shadow.radius = 5; 

directionalLight.shadow.camera.near = 5;
directionalLight.shadow.camera.far = 10;
directionalLight.shadow.camera.left = -2;
directionalLight.shadow.camera.right = 2;
directionalLight.shadow.camera.top = 2;
directionalLight.shadow.camera.bottom = 5;

scene.add(directionalLight);


const hemiLight = new THREE.HemisphereLight(0x87CEEB, 0x404040, 5); 
scene.add(hemiLight);


scene.background = new THREE.Color("#040720");


const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 500;
const positions = new Float32Array(particlesCount * 3);
const colors = new Float32Array(particlesCount * 3); 

for (let i = 0; i < particlesCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 1] = (Math.random() - 0.5) * 20;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 20;

    
    colors[i * 3] = 1;  // R
    colors[i * 3 + 1] = 1;  // G
    colors[i * 3 + 2] = 1;  // B
}

particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 4));
particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

const particlesMaterial = new THREE.PointsMaterial({
    size: 0.03,
    vertexColors: true, 
    transparent: true,
    opacity: 1
});

const particles = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particles);


function animate() {
    requestAnimationFrame(animate);
    updateBoxPosition(); 

    if (model) {
        model.rotation.y += 0.001;
    }

    // Make some particles blink randomly
    const colorAttribute = particlesGeometry.getAttribute('color');
    for (let i = 0; i < particlesCount; i++) {
        if (Math.random() > 0.97) { 
            let intensity = Math.random(); 
            colorAttribute.array[i * 3] = intensity;  
            colorAttribute.array[i * 3 + 1] = intensity;  
            colorAttribute.array[i * 3 + 2] = intensity;  
        }
    }
    colorAttribute.needsUpdate = true;

    controls.update();
    renderer.render(scene, camera);
}

document.querySelectorAll('.nav-link.dropdown-toggle').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
  
      
      this.classList.toggle('active');
  
      
      let submenu = this.nextElementSibling;
      
    
      const icon = this.querySelector('.dropdown-icon');
  
      
      if (this.classList.contains('active')) {
        
        icon.innerHTML = `
          <svg class="dropdown-icon" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff">
            <g id="SVGRepo_iconCarrier">
              <path d="M9 12H15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
            </g>
          </svg>
        `;
      } else {
        
        icon.innerHTML = `
          <svg class="dropdown-icon" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff">
            <g id="SVGRepo_iconCarrier">
              <path d="M9 12H15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
              <path d="M12 9L12 15" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
            </g>
          </svg>
        `;
      }
  
      if (submenu && submenu.classList.contains('submenu')) {
        if (submenu.style.maxHeight) {
          submenu.style.maxHeight = null; 
        } else {
          submenu.style.maxHeight = `${submenu.scrollHeight}px`; 
        }
      }
    });
  });


  
animate();


window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
