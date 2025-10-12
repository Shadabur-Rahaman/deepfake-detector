import { Suspense, useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial, Line } from '@react-three/drei'
import * as THREE from 'three'

// Enhanced neural network with more sophisticated patterns
function EnhancedNeuralNetwork() {
  const pointsRef = useRef(null!)
  const linesRef = useRef(null!)
  
  // Generate neural network structure
  const { positions, connections } = useMemo(() => {
    const positions = new Float32Array(2000 * 3) // 2000 nodes
    const connections = []
    const nodes = []
    
    // Create layered neural structure
    for (let i = 0; i < 2000; i++) {
      const layer = Math.floor(i / 200)
      const angleStep = (Math.PI * 2) / 200
      const angle = (i % 200) * angleStep
      
      const radius = 3 + layer * 0.8
      const height = (Math.random() - 0.5) * 2
      
      const x = Math.cos(angle) * radius + (Math.random() - 0.5) * 2
      const y = height + layer * 1.5 - 7
      const z = Math.sin(angle) * radius + (Math.random() - 0.5) * 2
      
      positions[i * 3] = x
      positions[i * 3 + 1] = y  
      positions[i * 3 + 2] = z
      
      nodes.push(new THREE.Vector3(x, y, z))
    }
    
    // Create connections between nearby nodes
    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i]
      const nearbyNodes = nodes
        .map((n, idx) => ({ node: n, index: idx, distance: node.distanceTo(n) }))
        .filter(n => n.distance > 0 && n.distance < 2.5)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 5) // Connect to 5 nearest nodes
      
      nearbyNodes.forEach(nearby => {
        connections.push([node, nearby.node])
      })
    }
    
    return { positions, connections }
  }, [])

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.05
      pointsRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.15
      
      // Animate individual points with wave effect
      const positions = pointsRef.current.geometry.attributes.position.array
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += Math.sin(state.clock.elapsedTime * 2 + positions[i] * 0.5) * 0.002
      }
      pointsRef.current.geometry.attributes.position.needsUpdate = true
    }
    
    if (linesRef.current) {
      linesRef.current.rotation.y = state.clock.elapsedTime * 0.05
      linesRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.15
    }
  })

  return (
    <group>
      {/* Neural nodes */}
      <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#60a5fa"
          size={0.08}
          sizeAttenuation={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
        />
      </Points>
      
      {/* Neural connections */}
      <group ref={linesRef}>
        {connections.slice(0, 500).map((connection, i) => (
          <Line
            key={i}
            points={connection}
            color="#3b82f6"
            lineWidth={0.5}
            transparent
            opacity={0.3}
          />
        ))}
      </group>
      
      {/* Floating data particles */}
      <DataParticles />
    </group>
  )
}

// Floating data particles for enhanced effect
function DataParticles() {
  const particlesRef = useRef(null!)
  
  const particlePositions = useMemo(() => {
    const positions = new Float32Array(500 * 3)
    for (let i = 0; i < 500; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20
      positions[i * 3 + 1] = (Math.random() - 0.5) * 20
      positions[i * 3 + 2] = (Math.random() - 0.5) * 20
    }
    return positions
  }, [])
  
  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array
      for (let i = 0; i < positions.length; i += 3) {
        positions[i] += Math.sin(state.clock.elapsedTime + i) * 0.001
        positions[i + 2] += Math.cos(state.clock.elapsedTime + i) * 0.001
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })
  
  return (
    <Points ref={particlesRef} positions={particlePositions} stride={3}>
      <PointMaterial
        transparent
        color="#10b981"
        size={0.03}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        opacity={0.6}
      />
    </Points>
  )
}

function LoadingFallback() {
  return (
    <div className="w-full h-full bg-gradient-to-br from-primary/10 to-accent/10 animate-pulse" />
  )
}

interface EnhancedNeuralCanvasProps {
  className?: string
}

export function EnhancedNeuralCanvas({ className }: EnhancedNeuralCanvasProps) {
  const handleWebGLError = (error: any) => {
    console.warn('WebGL context lost or error occurred:', error)
  }

  return (
    <div className={className}>
      <Canvas
        camera={{ position: [0, 0, 12], fov: 75 }}
        gl={{ alpha: true, antialias: true }}
        dpr={[1, 2]}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener('webglcontextlost', handleWebGLError)
          gl.domElement.addEventListener('webglcontextrestored', () => {
            console.log('WebGL context restored')
          })
        }}
        onError={handleWebGLError}
      >
        <Suspense fallback={null}>
          <EnhancedNeuralNetwork />
          
          {/* Ambient lighting */}
          <ambientLight intensity={0.2} />
          <pointLight position={[10, 10, 10]} intensity={0.5} color="#60a5fa" />
          <pointLight position={[-10, -10, -10]} intensity={0.3} color="#3b82f6" />
        </Suspense>
      </Canvas>
    </div>
  )
}
