import React, { useState } from 'react';
import { GraphPlayground } from './GraphPlayground';
import { PathfindingVisualizer } from './PathfindingVisualizer';
import { GitFork, Navigation } from 'lucide-react';

export const AlgorithmLabView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'graph' | 'pathfinding'>('graph');

  return (
    <div className="p-4 sm:p-6 max-w-6xl mx-auto space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-3">
        <button
          onClick={() => setActiveSubTab('graph')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition ${
            activeSubTab === 'graph'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <GitFork className="w-4 h-4" />
          Graph Search Playground (DFS, BFS, IDS)
        </button>

        <button
          onClick={() => setActiveSubTab('pathfinding')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition ${
            activeSubTab === 'pathfinding'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Navigation className="w-4 h-4" />
          Pathfinding & Dynamic Replanning (A*, D* Lite, Hill Climbing)
        </button>
      </div>

      {/* Render active subtab */}
      {activeSubTab === 'graph' && <GraphPlayground />}
      {activeSubTab === 'pathfinding' && <PathfindingVisualizer />}
    </div>
  );
};
