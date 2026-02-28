import React, { useRef, useState, useEffect, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import { Network, ZoomIn } from 'lucide-react';

const GraphPage = () => {
    const fgRef = useRef();

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
        return colors[node.group] || "#94a3b8";
    };

    return (
        <div className="flex flex-col h-[calc(100vh-8rem)]">
            <header className="mb-6 flex justify-between items-end shrink-0">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                        <Network className="text-primary-400" /> Interactive Knowledge Graph
                    </h1>
                    <p className="text-slate-400 mt-1">3D Topology of cognitive zones, emotional triggers, and successful interventions.</p>
                </div>
                <button
                    onClick={() => fgRef.current?.cameraPosition({ x: 0, y: 0, z: 250 }, { x: 0, y: 0, z: 0 }, 1000)}
                    className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-slate-300 hover:text-white"
                >
                    <ZoomIn size={16} /> Reset View
                </button>
            </header>

            <div className="flex-1 bg-gray-950 border border-gray-700 rounded-xl overflow-hidden relative shadow-inner">
                {/* Visualizer Container */}
                <div className="absolute inset-0">
                    <ForceGraph3D
                        ref={fgRef}
                        graphData={graphData}
                        nodeLabel="label"
                        nodeColor={getNodeColor}
                        nodeVal="val"
                        linkWidth={(link) => (link.strength ? link.strength * 2 : 1)}
                        linkColor={(link) => link.color || "#475569"}
                        onNodeClick={handleClickNode}
                        backgroundColor="#0f111a"
                        // Advanced settings
                        linkDirectionalParticles={2}
                        linkDirectionalParticleSpeed={d => d.strength * 0.01}
                        nodeOpacity={0.9}
                    />
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
