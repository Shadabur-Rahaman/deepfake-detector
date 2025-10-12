import { Suspense, useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import * as THREE from 'three'

// Generate particles in an elegant neural network structure
function generateNeuralPoints() {
  const points = new Float32Array(1200)
  
  for (let i = 0; i < 400; i++) {
    // Create elegant layered structure
    const layer = Math.floor(i / 80)
    const angle = (i % 80) * (Math.PI * 2 / 80)
    const radius = 2.5 + layer * 1.0
    
    // Smooth, organic distribution
    const x = Math.cos(angle) * radius + (Math.random() - 0.5) * 0.8
    const y = (Math.random() - 0.5) * 3 + layer * 1.2 - 2
    const z = Math.sin(angle) * radius + (Math.random() - 0.5) * 0.8
    
    points[i * 3] = x
    points[i * 3 + 1] = y 
    points[i * 3 + 2] = z
  }
  
  return points
}

function NeuralNetwork() {
  const pointsRef = useRef<THREE.Points>(null!)
  const positions = generateNeuralPoints()

  useFrame((state) => {
    if (pointsRef.current) {
      // Elegant, slow rotation
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.04
      pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.03) * 0.05
      
      // Subtle breathing effect
      const positions = pointsRef.current.geometry.attributes.position.array as Float32Array
      for (let i = 0; i < positions.length; i += 3) {
        const time = state.clock.elapsedTime
        positions[i + 1] += Math.sin(time * 0.8 + positions[i] * 0.2) * 0.0008
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#6366f1"
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        opacity={0.8}
      />
    </Points>
  )
}

function ConnectingLines() {
  const lineRef = useRef<THREE.Group>(null!)
  
  useFrame((state) => {
    if (lineRef.current) {
      // Gentle rotation
      lineRef.current.rotation.y = state.clock.elapsedTime * 0.02
    }
  })

  const lines = []
  // Create elegant, subtle connections
  for (let i = 0; i < 12; i++) {
    const points = []
    const angle1 = (i / 12) * Math.PI * 2
    const angle2 = ((i + 3) / 12) * Math.PI * 2
    
    points.push(new THREE.Vector3(
      Math.cos(angle1) * 3,
      Math.sin(i * 0.5) * 1,
      Math.sin(angle1) * 3
    ))
    points.push(new THREE.Vector3(
      Math.cos(angle2) * 4,
      Math.cos(i * 0.3) * 1,
      Math.sin(angle2) * 4
    ))
    
    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    
    lines.push(
      <primitive key={i} object={new THREE.Line(geometry, new THREE.LineBasicMaterial({ 
        color: "#8b5cf6", 
        transparent: true, 
        opacity: 0.4
      }))} />
    )
  }

  return <group ref={lineRef}>{lines}</group>
}


function LoadingFallback() {
  return (
    <div className="absolute inset-0 flex items-center justify-center">
      <div className="w-32 h-32 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

interface HeroCanvasProps {
  className?: string
}

export function HeroCanvas({ className }: HeroCanvasProps) {
  const handleWebGLError = (error: any) => {
    // WebGL context lost is usually recoverable, so we don't need to show error to user
    // Only log in development mode to avoid console spam
    if (import.meta.env.DEV) {
      console.warn('WebGL context lost or error occurred:', error)
    }
  }

  const handleWebGLContextLost = (event: Event) => {
    event.preventDefault(); // Prevent default context loss behavior
    handleWebGLError(event);
  }

  const handleWebGLContextRestored = () => {
    // Only log in development mode
    if (import.meta.env.DEV) {
      console.log('WebGL context restored')
    }
  }

  return (
    <div className={className}>
      <Suspense fallback={<LoadingFallback />}>
        <Canvas
          camera={{ position: [0, 0, 5], fov: 75 }}
          style={{ background: 'transparent' }}
          dpr={[1, 2]}
          performance={{ min: 0.5 }}
          onCreated={({ gl }) => {
            // Add WebGL context lost event listener
            gl.domElement.addEventListener('webglcontextlost', handleWebGLContextLost)
            gl.domElement.addEventListener('webglcontextrestored', handleWebGLContextRestored)
          }}
          onError={handleWebGLError}
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1.0} />
          <pointLight position={[-10, -10, -10]} intensity={0.8} />
          <NeuralNetwork />
          <ConnectingLines />
        </Canvas>
      </Suspense>
    </div>
  )
}

export default HeroCanvas
