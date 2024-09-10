import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { FBXLoader } from 'three/examples/jsm/loaders/FBXLoader';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import sample from '../assets/3dModels/sample/scene.gltf';

interface Params {
  object: string
}

const Showcase3dModel: React.FC<Params> = (props) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // scene
    const scene = new THREE.Scene();

    // camera
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    
    // window size
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth/1.5, window.innerHeight/1.5);

    // set background
    renderer.setClearColor(0xffffff, 1); 
    
    // mounting element
    if (mountRef.current) {
      mountRef.current.appendChild(renderer.domElement);
    }
    
    // orbit control
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controls.enablePan = false;

    // ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 1);
    scene.add(ambientLight);

    // directonal light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 10, 7.5);
    scene.add(directionalLight);
    
    // load model
    const loader = new GLTFLoader();
    loader.load(sample,
      (object) => {
        // FBX
        //console.log('FBX model loaded:', object);
        //object.scale.set(0.03, 0.03, 0.03);
        //scene.add(object);

        // GLTF
        console.log('GLTF model loaded:', object.scene);
        const model = object.scene;
        scene.add(model);
      },
      undefined,
      (error) => {
        console.error('An error occurred while loading the model:', error);
      }
    );

    camera.position.z = 5;

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };

    animate();

    return () => {
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div ref={mountRef}></div>
  );
};

export default Showcase3dModel;
