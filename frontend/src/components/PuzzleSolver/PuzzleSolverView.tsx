import React, { useState } from 'react';
import { EightPuzzleVisualizer } from './EightPuzzleVisualizer';
import { WumpusWorldVisualizer } from './WumpusWorldVisualizer';
import { TowersOfHanoiVisualizer } from './TowersOfHanoiVisualizer';
import { Brain, Compass, Layers } from 'lucide-react';

export const PuzzleSolverView: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'8puzzle' | 'wumpus' | 'hanoi'>('8puzzle');

  return (
    <div className="p-4 sm:p-6 max-w-6xl mx-auto space-y-6">
      {/* Sub-tab navigation */}
      <div className="flex items-center gap-2 border-b border-gray-200 pb-3">
        <button
          onClick={() => setActiveSubTab('8puzzle')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition ${
            activeSubTab === '8puzzle'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Brain className="w-4 h-4" />
          8-Puzzle Solver
        </button>

        <button
          onClick={() => setActiveSubTab('wumpus')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition ${
            activeSubTab === 'wumpus'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Compass className="w-4 h-4" />
          Wumpus World (Bayesian)
        </button>

        <button
          onClick={() => setActiveSubTab('hanoi')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition ${
            activeSubTab === 'hanoi'
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          }`}
        >
          <Layers className="w-4 h-4" />
          Towers of Hanoi
        </button>
      </div>

      {/* Render selected view */}
      {activeSubTab === '8puzzle' && <EightPuzzleVisualizer />}
      {activeSubTab === 'wumpus' && <WumpusWorldVisualizer />}
      {activeSubTab === 'hanoi' && <TowersOfHanoiVisualizer />}
    </div>
  );
};
