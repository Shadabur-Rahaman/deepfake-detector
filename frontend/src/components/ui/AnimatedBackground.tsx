import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

// Generate particles in a neural network-like structure
function generatePoints(count = 1500) {
  const points = new Float32Array(count);
  
  for (let i = 0; i < count; i++) {
    // Create layers of neural network
    const layer = Math.floor(i / (count / 5)); // 5 layers
    const x = (Math.random() - 0.5) * 10;
    const y = (Math.random() - 0.5) * 8 + layer * 2 - 4;
    const z = (Math.random() - 0.5) * 6;
    
    points[i * 3] = x;
    points[i * 3 + 1] = y;
    points[i * 3 + 2] = z;
  }
  
  return points;
}

function AnimatedParticles() {
  const pointsRef = useRef<THREE.Points>(null!);
  const positions = generatePoints(1000);

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.05;
      pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
      
      // Animate individual points
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += Math.sin(state.clock.elapsedTime * 0.5 + positions[i]) * 0.002;
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#4f46e5"
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

interface AnimatedBackgroundProps {
  className?: string;
  intensity?: number;
}

export function AnimatedBackground({ className = '', intensity = 0.3 }: AnimatedBackgroundProps) {
  const handleWebGLError = (error: any) => {
    console.warn('WebGL context lost or error occurred:', error)
  }

  return (
    <div className={`absolute inset-0 -z-10 ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 5], fov: 75 }}
        style={{ background: 'transparent' }}
        dpr={[1, 2]}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', handleWebGLError)
          gl.domElement.addEventListener('webglcontextrestored', () => {
            console.log('WebGL context restored')
          })
        }}
        onError={handleWebGLError}
      >
        <ambientLight intensity={intensity} />
        <pointLight position={[10, 10, 10]} intensity={intensity} />
        <Suspense fallback={null}>
          <AnimatedParticles />
        </Suspense>
      </Canvas>
    </div>
  );
}
