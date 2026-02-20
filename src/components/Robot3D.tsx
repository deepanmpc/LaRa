import { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float } from '@react-three/drei';
import * as THREE from 'three';

interface RobotProps {
  mousePosition: { x: number; y: number };
}

const RobotModel = ({ mousePosition }: RobotProps) => {
  const headRef = useRef<THREE.Group>(null);
  const leftEyeRef = useRef<THREE.Mesh>(null);
  const rightEyeRef = useRef<THREE.Mesh>(null);
  const leftPupilRef = useRef<THREE.Mesh>(null);
  const rightPupilRef = useRef<THREE.Mesh>(null);

  useFrame(() => {
    if (leftPupilRef.current && rightPupilRef.current) {
      // Map mouse position to pupil movement (-0.08 to 0.08)
      const targetX = mousePosition.x * 0.08;
      const targetY = mousePosition.y * 0.06;

      // Smoothly interpolate pupil positions
      leftPupilRef.current.position.x = THREE.MathUtils.lerp(
        leftPupilRef.current.position.x,
        -0.25 + targetX,
        0.1
      );
      leftPupilRef.current.position.y = THREE.MathUtils.lerp(
        leftPupilRef.current.position.y,
        0.15 + targetY,
        0.1
      );

      rightPupilRef.current.position.x = THREE.MathUtils.lerp(
        rightPupilRef.current.position.x,
        0.25 + targetX,
        0.1
      );
      rightPupilRef.current.position.y = THREE.MathUtils.lerp(
        rightPupilRef.current.position.y,
        0.15 + targetY,
        0.1
      );
    }

    // Subtle head movement following cursor
    if (headRef.current) {
      headRef.current.rotation.y = THREE.MathUtils.lerp(
        headRef.current.rotation.y,
        mousePosition.x * 0.15,
        0.05
      );
      headRef.current.rotation.x = THREE.MathUtils.lerp(
        headRef.current.rotation.x,
        -mousePosition.y * 0.1,
        0.05
      );
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
      <group scale={1.2}>
        {/* Body */}
        <mesh position={[0, -1.2, 0]}>
          <capsuleGeometry args={[0.4, 0.8, 16, 32]} />
          <meshStandardMaterial color="#f0f4f8" metalness={0.3} roughness={0.4} />
        </mesh>

        {/* Chest plate */}
        <mesh position={[0, -0.9, 0.35]}>
          <boxGeometry args={[0.5, 0.4, 0.1]} />
          <meshStandardMaterial color="#0891b2" metalness={0.5} roughness={0.3} />
        </mesh>

        {/* Neck */}
        <mesh position={[0, -0.4, 0]}>
          <cylinderGeometry args={[0.15, 0.2, 0.3, 32]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.4} roughness={0.3} />
        </mesh>

        {/* Head */}
        <group ref={headRef} position={[0, 0.2, 0]}>
          {/* Main head */}
          <mesh>
            <sphereGeometry args={[0.55, 32, 32]} />
            <meshStandardMaterial color="#f8fafc" metalness={0.2} roughness={0.3} />
          </mesh>

          {/* Face plate */}
          <mesh position={[0, 0, 0.35]}>
            <sphereGeometry args={[0.45, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2]} />
            <meshStandardMaterial color="#f1f5f9" metalness={0.3} roughness={0.2} />
          </mesh>

          {/* Left eye socket */}
          <mesh ref={leftEyeRef} position={[-0.25, 0.15, 0.4]}>
            <sphereGeometry args={[0.12, 32, 32]} />
            <meshStandardMaterial color="#ffffff" metalness={0.1} roughness={0.2} />
          </mesh>

          {/* Right eye socket */}
          <mesh ref={rightEyeRef} position={[0.25, 0.15, 0.4]}>
            <sphereGeometry args={[0.12, 32, 32]} />
            <meshStandardMaterial color="#ffffff" metalness={0.1} roughness={0.2} />
          </mesh>

          {/* Left pupil */}
          <mesh ref={leftPupilRef} position={[-0.25, 0.15, 0.5]}>
            <sphereGeometry args={[0.06, 32, 32]} />
            <meshStandardMaterial color="#0891b2" metalness={0.5} roughness={0.2} />
          </mesh>

          {/* Right pupil */}
          <mesh ref={rightPupilRef} position={[0.25, 0.15, 0.5]}>
            <sphereGeometry args={[0.06, 32, 32]} />
            <meshStandardMaterial color="#0891b2" metalness={0.5} roughness={0.2} />
          </mesh>

          {/* Inner pupil glow - left */}
          <mesh position={[-0.25, 0.15, 0.52]}>
            <sphereGeometry args={[0.025, 16, 16]} />
            <meshStandardMaterial color="#67e8f9" emissive="#67e8f9" emissiveIntensity={0.5} />
          </mesh>

          {/* Inner pupil glow - right */}
          <mesh position={[0.25, 0.15, 0.52]}>
            <sphereGeometry args={[0.025, 16, 16]} />
            <meshStandardMaterial color="#67e8f9" emissive="#67e8f9" emissiveIntensity={0.5} />
          </mesh>

          {/* Mouth/speaker */}
          <mesh position={[0, -0.15, 0.45]}>
            <boxGeometry args={[0.25, 0.06, 0.05]} />
            <meshStandardMaterial color="#94a3b8" metalness={0.6} roughness={0.3} />
          </mesh>

          {/* Ear sensors */}
          <mesh position={[-0.5, 0.1, 0]}>
            <cylinderGeometry args={[0.06, 0.06, 0.15, 16]} />
            <meshStandardMaterial color="#0891b2" metalness={0.5} roughness={0.3} />
          </mesh>
          <mesh position={[0.5, 0.1, 0]}>
            <cylinderGeometry args={[0.06, 0.06, 0.15, 16]} />
            <meshStandardMaterial color="#0891b2" metalness={0.5} roughness={0.3} />
          </mesh>

          {/* Head top sensor */}
          <mesh position={[0, 0.5, 0]}>
            <sphereGeometry args={[0.08, 16, 16]} />
            <meshStandardMaterial color="#0891b2" emissive="#0891b2" emissiveIntensity={0.3} metalness={0.5} roughness={0.3} />
          </mesh>
        </group>

        {/* Shoulders */}
        <mesh position={[-0.55, -0.7, 0]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.4} roughness={0.3} />
        </mesh>
        <mesh position={[0.55, -0.7, 0]}>
          <sphereGeometry args={[0.12, 16, 16]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.4} roughness={0.3} />
        </mesh>

        {/* Arms */}
        <mesh position={[-0.7, -1.1, 0]} rotation={[0, 0, 0.3]}>
          <capsuleGeometry args={[0.08, 0.5, 8, 16]} />
          <meshStandardMaterial color="#f0f4f8" metalness={0.3} roughness={0.4} />
        </mesh>
        <mesh position={[0.7, -1.1, 0]} rotation={[0, 0, -0.3]}>
          <capsuleGeometry args={[0.08, 0.5, 8, 16]} />
          <meshStandardMaterial color="#f0f4f8" metalness={0.3} roughness={0.4} />
        </mesh>

        {/* Hands */}
        <mesh position={[-0.85, -1.5, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.4} roughness={0.3} />
        </mesh>
        <mesh position={[0.85, -1.5, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color="#e2e8f0" metalness={0.4} roughness={0.3} />
        </mesh>
      </group>
    </Float>
  );
};

const Robot3D = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Normalize to -1 to 1
        const x = (event.clientX - centerX) / (window.innerWidth / 2);
        const y = -(event.clientY - centerY) / (window.innerHeight / 2);
        
        setMousePosition({ x: Math.max(-1, Math.min(1, x)), y: Math.max(-1, Math.min(1, y)) });
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div ref={containerRef} className="w-full h-[400px] lg:h-[500px]">
      <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 5, 5]} intensity={0.8} />
        <directionalLight position={[-5, 3, -5]} intensity={0.4} />
        <pointLight position={[0, 2, 3]} intensity={0.5} color="#0891b2" />
        <RobotModel mousePosition={mousePosition} />
      </Canvas>
    </div>
  );
};

export default Robot3D;
