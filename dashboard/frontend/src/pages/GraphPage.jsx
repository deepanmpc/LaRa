import React, { useRef, useState, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { Network, ZoomIn, Play, Pause, Camera } from 'lucide-react';
import * as THREE from 'three';
import SpriteText from 'three-spritetext';

const GraphPage = () => {
    const fgRef = useRef();
    const [isPlaying, setIsPlaying] = useState(false);
    const [temporalSlider, setTemporalSlider] = useState(14); // e.g., Day 14 recorded

    // Mocking the node/edge payload from Spring Boot GraphController
    const [graphData] = useState({
        nodes: [
            { id: "Child_Hash123", group: 1, label: "Child Matrix", val: 50 },
            { id: "Concept_Math", group: 2, label: "Fractions ZPD", val: 20 },
            { id: "Emotion_Frustrated", group: 3, label: "Frustration Peak", val: 30 },
            { id: "Tool_Breathing", group: 4, label: "Deep Breathing", val: 25 },
        ],
        links: [
            { source: "Concept_Math", target: "Emotion_Frustrated", strength: 0.8, type: "TRIGGERED_BY", color: "#ef4444" },
            { source: "Emotion_Frustrated", target: "Tool_Breathing", strength: 0.9, type: "MITIGATED", color: "#3b82f6" },
            { source: "Child_Hash123", target: "Concept_Math", strength: 0.5, type: "ENGAGED", color: "#818cf8" },
        ]
    });

    const handleClickNode = useCallback(
        (node) => {
            // Zoom in on the clicked node
            const distance = 80;
            const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);
            if (fgRef.current) {
                fgRef.current.cameraPosition(
                    { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio },
                    node, // look at point
                    2000  // ms transition duration
                );
            }
        },
        [fgRef]
    );

    const getNodeColor = (node) => {
        const colors = {
            1: "#6366f1", // Child (Primary)
            2: "#ec4899", // Concept (Pink)
            3: "#f59e0b", // Emotion (Orange)
            4: "#10b981", // Tool (Emerald)
        };
        // Fading implementation for older temporal epochs
        if (node.val < temporalSlider) return "#334155";
        return colors[node.group] || "#94a3b8";
    };

    const handleScreenshot = () => {
        // Hooks into the internal THREE.js WebGL rendering context
        if (fgRef.current) {
            const dataUrl = fgRef.current.renderer().domElement.toDataURL("image/png");
            const link = document.createElement("a");
            link.download = `lara-knowledge-graph-day${temporalSlider}.png`;
            link.href = dataUrl;
            link.click();
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            <header className="mb-6 flex justify-between items-end shrink-0">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                        <Network className="text-primary-400" /> Interactive Knowledge Graph (v2)
                    </h1>
                    <p className="text-slate-400 mt-1">Simulated graph evolution showing node centrality and clustered communities.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={handleScreenshot}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-slate-300 hover:text-white"
                    >
                        <Camera size={16} /> Export PNG
                    </button>
                    <button
                        onClick={() => fgRef.current?.cameraPosition({ x: 0, y: 0, z: 250 }, { x: 0, y: 0, z: 0 }, 1000)}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-slate-300 hover:text-white"
                    >
                        <ZoomIn size={16} /> Reset View
                    </button>
                </div>
            </header>

            <div className="flex-1 bg-gray-950 border border-gray-700 rounded-xl overflow-hidden relative shadow-inner">
                {/* Visualizer Container */}
                <div className="absolute inset-0">
                    <ForceGraph3D
                        ref={fgRef}
                        graphData={graphData}
                        backgroundColor="#090a0f" // Deeper cyber-business palette
                        nodeLabel="label"
                        nodeThreeObject={node => {
                            const isFaded = node.val < temporalSlider;
                            const color = getNodeColor(node);
                            const size = Math.max(10, node.val * 0.45); // Scale up balls to fit text like user's image

                            const group = new THREE.Group();

                            // Glowing Glass Sphere (Elegant UI)
                            const geometry = new THREE.SphereGeometry(size, 32, 32);
                            const material = new THREE.MeshPhysicalMaterial({
                                color: color,
                                transparent: true,
                                opacity: isFaded ? 0.2 : 0.85,
                                transmission: 0.6,
                                roughness: 0.1,
                                thickness: 2.5,
                                emissive: color,
                                emissiveIntensity: isFaded ? 0.05 : 0.6
                            });
                            const sphere = new THREE.Mesh(geometry, material);
                            group.add(sphere);

                            // Inner Text Label
                            if (!isFaded) {
                                // Formatting text to wrap or fit gracefully
                                const textLabel = node.label.replace(' ', '\n');
                                const sprite = new SpriteText(textLabel);
                                sprite.color = '#ffffff';
                                sprite.textHeight = size * 0.3; // Proportionally scale text inside node
                                sprite.fontWeight = '700';
                                sprite.fontFace = 'Inter, sans-serif';
                                group.add(sprite);
                            }

                            return group;
                        }}
                        nodeThreeObjectExtend={false}
                        linkWidth={(link) => (link.strength ? link.strength * 2.5 : 1.5)}
                        linkColor={(link) => link.color || "#334155"}
                        onNodeClick={handleClickNode}
                        // Advanced particle highway styling
                        linkDirectionalParticles={4}
                        linkDirectionalParticleWidth={2}
                        linkDirectionalParticleColor={() => "#ffffff"}
                        linkDirectionalParticleSpeed={d => (d.strength || 0.5) * 0.015}
                        linkResolution={16}
                    />
                </div>

                <div className="absolute top-6 right-6 bg-gray-900/90 backdrop-blur border border-gray-700 p-4 rounded-lg pointer-events-auto w-64">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4">Temporal Evolution</h4>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setIsPlaying(!isPlaying)}
                            className="p-2 rounded-full bg-primary-500/20 text-primary-400 hover:bg-primary-500 hover:text-white transition-colors"
                        >
                            {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                        </button>
                        <input
                            type="range"
                            min="1" max="50"
                            value={temporalSlider}
                            onChange={(e) => setTemporalSlider(e.target.value)}
                            className="flex-1 accent-primary-500"
                        />
                    </div>
                    <div className="flex justify-between text-xs text-slate-500 mt-2">
                        <span>Session 1</span>
                        <span>Session {temporalSlider}</span>
                    </div>
                </div>

                {/* Legend Overlay */}
                <div className="absolute bottom-6 right-6 bg-gray-900/80 backdrop-blur border border-gray-700 p-4 rounded-lg pointer-events-none">
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Node Typology</h4>
                    <div className="space-y-2 text-sm text-slate-400">
                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-primary-500"></div> Child Matrix</div>
                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-pink-500"></div> ZPD Concept</div>
                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-amber-500"></div> Emotional State</div>
                        <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-emerald-500"></div> Clinical Tool</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GraphPage;
