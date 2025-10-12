import { Suspense, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial, Text, Line } from '@react-three/drei'
import * as THREE from 'three'

// Face detection grid visualization
function FaceDetectionGrid() {
  const gridRef = useRef(null!)
  const scanLineRef = useRef(null!)
  
  useFrame((state) => {
    if (gridRef.current) {
      gridRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
    }
    
    if (scanLineRef.current) {
      scanLineRef.current.position.y = Math.sin(state.clock.elapsedTime * 2) * 3
    }
  })
  
  // Generate face detection points
  const facePoints = useMemo(() => {
    const points = new Float32Array(68 * 3) // 68 facial landmarks
    const faceModel = [
      // Jaw line
      ...Array.from({ length: 17 }, (_, i) => {
        const angle = (i / 16) * Math.PI - Math.PI/2
        return [Math.cos(angle) * 1.5, Math.sin(angle) * 0.8 - 0.5, 0]
      }).flat(),
      // Eyes
      ...Array.from({ length: 12 }, (_, i) => {
        const isLeft = i < 6
        const angle = (i % 6) / 5 * Math.PI * 2
        const eyeX = isLeft ? -0.6 : 0.6
        return [eyeX + Math.cos(angle) * 0.3, 0.2 + Math.sin(angle) * 0.2, 0]
      }).flat(),
      // Nose
      ...[
        [0, 0.1, 0], [0, -0.1, 0], [0, -0.3, 0],
        [-0.2, -0.2, 0], [0.2, -0.2, 0]
      ].flat(),
      // Mouth
      ...Array.from({ length: 12 }, (_, i) => {
        const angle = (i / 11) * Math.PI
        return [Math.cos(angle) * 0.4, -0.7 + Math.sin(angle) * 0.2, 0]
      }).flat(),
    ]
    
    faceModel.forEach((coord, i) => {
      points[i] = coord * 2 // Scale up
    })
    
    return points
  }, [])
  
  return (
    <group ref={gridRef} position={[0, 0, 0]}>
      {/* Face landmark points */}
      <Points positions={facePoints} stride={3}>
        <PointMaterial
          transparent
          color="#ff6b6b"
          size={0.1}
          sizeAttenuation={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </Points>
      
      {/* Scanning line effect */}
      <mesh ref={scanLineRef} position={[0, 0, 0.1]}>
        <planeGeometry args={[4, 0.05]} />
        <meshBasicMaterial 
          color="#00ff88" 
          transparent 
          opacity={0.8}
          blending={THREE.AdditiveBlending}
        />
      </mesh>
      
      {/* Detection box */}
      <lineSegments>
        <edgesGeometry attach="geometry" args={[new THREE.BoxGeometry(3, 4, 0.1)]} />
        <lineBasicMaterial color="#00ff88" />
      </lineSegments>
    </group>
  )
}

// Authenticity Analysis Visualization
function AuthenticityAnalysis() {
  const particlesRef = useRef(null!)
  
  const analysisPoints = useMemo(() => {
    const positions = new Float32Array(1000 * 3)
    const colors = new Float32Array(1000 * 3)
    
    for (let i = 0; i < 1000; i++) {
      // Create analysis data points
      positions[i * 3] = (Math.random() - 0.5) * 10
      positions[i * 3 + 1] = (Math.random() - 0.5) * 8
      positions[i * 3 + 2] = (Math.random() - 0.5) * 5
      
      // Color based on authenticity (green = real, red = fake)
      const authenticity = Math.random()
      colors[i * 3] = authenticity < 0.7 ? 1 : authenticity // Red
      colors[i * 3 + 1] = authenticity > 0.3 ? 1 : 0.2       // Green
      colors[i * 3 + 2] = 0.3                                // Blue
    }
    
    return { positions, colors }
  }, [])
  
  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.1
      
      // Animate analysis particles
      const positions = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += Math.sin(state.clock.elapsedTime + i * 0.01) * 0.005
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })
  
  return (
    <Points 
      ref={particlesRef} 
      positions={analysisPoints.positions} 
      colors={analysisPoints.colors}
      stride={3}
    >
      <PointMaterial
        transparent
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        vertexColors={true}
      />
    </Points>
  )
}

// MesoNet CNN Visualization
function MesoNetVisualization() {
  const networkRef = useRef(null!)
  
  useFrame((state) => {
    if (networkRef.current) {
      networkRef.current.rotation.z = state.clock.elapsedTime * 0.2
    }
  })
  
  return (
    <group ref={networkRef} position={[0, 0, -8]}>
      {/* CNN Layer visualization */}
      {Array.from({ length: 5 }, (_, layerIndex) => (
        <group key={layerIndex} position={[0, 0, layerIndex * 1.5]}>
          {Array.from({ length: 16 }, (_, nodeIndex) => {
            const angle = (nodeIndex / 16) * Math.PI * 2
            const radius = 1 + layerIndex * 0.2
            return (
              <mesh 
                key={nodeIndex}
                position={[
                  Math.cos(angle) * radius,
                  Math.sin(angle) * radius,
                  0
                ]}
              >
                <sphereGeometry args={[0.05, 8, 8]} />
                <meshBasicMaterial 
                  color={layerIndex === 4 ? "#ff4757" : "#3742fa"} 
                  transparent
                  opacity={0.8}
                />
              </mesh>
            )
          })}
        </group>
      ))}
    </group>
  )
}

interface DeepfakeCanvasProps {
  className?: string
  variant?: 'detection' | 'analysis' | 'neural'
}

export function DeepfakeCanvas({ className, variant = 'detection' }: DeepfakeCanvasProps) {
  const handleWebGLError = (error: any) => {
    console.warn('WebGL context lost or error occurred:', error)
  }

  return (
    <div className={className}>
      <Canvas
        camera={{ position: [0, 0, 8], fov: 75 }}
        gl={{ alpha: true, antialias: true }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', handleWebGLError)
          gl.domElement.addEventListener('webglcontextrestored', () => {
            console.log('WebGL context restored')
          })
        }}
        onError={handleWebGLError}
      >
        <Suspense fallback={null}>
          {variant === 'detection' && <FaceDetectionGrid />}
          {variant === 'analysis' && <AuthenticityAnalysis />}
          {variant === 'neural' && <MesoNetVisualization />}
          
          <ambientLight intensity={0.3} />
          <pointLight position={[5, 5, 5]} intensity={0.5} color="#00ff88" />
        </Suspense>
      </Canvas>
    </div>
  )
}
