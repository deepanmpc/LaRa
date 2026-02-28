import React from 'react';
import { ZoomIn, ZoomOut, Move, Download, Image as ImageIcon } from 'lucide-react';

export const ChartToolbar = ({ title, onZoomIn, onZoomOut, onPanToggle, onExportCSV, onExportPNG, isPanning }) => {
    return (
        <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <div className="flex items-center gap-2 bg-gray-900/50 p-1 rounded-lg border border-gray-700">
                <button 
                    onClick={onZoomIn}
                    className="p-1.5 rounded hover:bg-gray-700 text-slate-400 hover:text-white transition-colors"
                    title="Zoom In"
                >
                    <ZoomIn size={16} />
                </button>
                <button 
                    onClick={onZoomOut}
                    className="p-1.5 rounded hover:bg-gray-700 text-slate-400 hover:text-white transition-colors"
                    title="Zoom Out"
                >
                    <ZoomOut size={16} />
                </button>
                <div className="w-px h-4 bg-gray-700 mx-1"></div>
                <button 
                    onClick={onPanToggle}
                    className={`p-1.5 rounded transition-colors ${isPanning ? 'bg-primary-500/20 text-primary-400' : 'hover:bg-gray-700 text-slate-400 hover:text-white'}`}
                    title="Toggle Pan"
                >
                    <Move size={16} />
                </button>
                <div className="w-px h-4 bg-gray-700 mx-1"></div>
                <button 
                    onClick={onExportCSV}
                    className="p-1.5 rounded hover:bg-gray-700 text-slate-400 hover:text-white transition-colors"
                    title="Export CSV"
                >
                    <Download size={16} />
                </button>
                <button 
                    onClick={onExportPNG}
                    className="p-1.5 rounded hover:bg-gray-700 text-slate-400 hover:text-white transition-colors"
                    title="Export PNG"
                >
                    <ImageIcon size={16} />
                </button>
            </div>
        </div>
    );
};
