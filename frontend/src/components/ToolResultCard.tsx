import React from 'react';
import { Brain, Layers, Compass, GitFork, Calendar, CheckCircle } from 'lucide-react';

interface ToolResultCardProps {
  toolData: any;
}

export const ToolResultCard: React.FC<ToolResultCardProps> = ({ toolData }) => {
  if (!toolData) return null;

  // 1. 8-Puzzle Card
  if (toolData.algorithm && (toolData.initial_state || toolData.moves)) {
    return (
      <div className="my-3 p-4 bg-gradient-to-br from-blue-50/70 to-indigo-50/70 border border-blue-200 rounded-2xl shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-blue-600" />
            <span className="font-bold text-xs text-blue-950 uppercase tracking-wider">
              {toolData.algorithm.toUpperCase()} 8-Puzzle Execution
            </span>
          </div>
          <span className="text-[11px] font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full">
            {toolData.solvable ? (toolData.found ? 'Solved' : 'Unsolved') : 'Unsolvable'}
          </span>
        </div>

        {/* 3x3 initial board preview */}
        {toolData.initial_state && (
          <div className="flex items-center gap-4">
            <div className="grid grid-cols-3 gap-1 bg-white p-1.5 rounded-lg border border-blue-200 w-24 h-24">
              {toolData.initial_state.map((tile: number, idx: number) => (
                <div
                  key={idx}
                  className={`flex items-center justify-center rounded text-xs font-bold ${
                    tile === 0 ? 'bg-transparent text-transparent' : 'bg-blue-600 text-white'
                  }`}
                >
                  {tile !== 0 ? tile : ''}
                </div>
              ))}
            </div>

            <div className="space-y-1 text-xs text-gray-700">
              <div>
                <span className="text-gray-400">Moves: </span>
                <span className="font-bold text-blue-700">{toolData.solution_cost} steps</span>
              </div>
              <div>
                <span className="text-gray-400">Nodes Expanded: </span>
                <span className="font-bold">{toolData.nodes_expanded}</span>
              </div>
              <div>
                <span className="text-gray-400">Runtime: </span>
                <span className="font-bold">{toolData.execution_time_ms} ms</span>
              </div>
            </div>
          </div>
        )}

        {/* Moves sequence pills */}
        {toolData.moves && toolData.moves.length > 0 && (
          <div className="flex flex-wrap gap-1 pt-1">
            {toolData.moves.slice(0, 10).map((m: string, i: number) => (
              <span key={i} className="px-2 py-0.5 bg-white border border-blue-200 text-blue-800 rounded text-[10px] font-bold font-mono">
                {m}
              </span>
            ))}
            {toolData.moves.length > 10 && (
              <span className="text-[10px] text-gray-500 self-center">
                +{toolData.moves.length - 10} more moves
              </span>
            )}
          </div>
        )}
      </div>
    );
  }

  // 2. Towers of Hanoi Card
  if (toolData.num_disks && toolData.min_moves_theoretical) {
    return (
      <div className="my-3 p-4 bg-gradient-to-br from-indigo-50/70 to-purple-50/70 border border-indigo-200 rounded-2xl shadow-xs space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-600" />
          <span className="font-bold text-indigo-950 uppercase tracking-wider">
            Towers of Hanoi ({toolData.num_disks} Disks)
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="p-2 bg-white rounded-lg border border-indigo-100">
            <span className="text-gray-400 block text-[10px]">Optimal Moves</span>
            <span className="font-bold text-indigo-600 text-sm">{toolData.total_moves} moves</span>
          </div>
          <div className="p-2 bg-white rounded-lg border border-indigo-100">
            <span className="text-gray-400 block text-[10px]">Formula 2^n - 1</span>
            <span className="font-bold text-gray-800 text-sm">{toolData.min_moves_theoretical}</span>
          </div>
        </div>
      </div>
    );
  }

  // 3. Graph Search Card
  if (toolData.path && toolData.visited_order) {
    return (
      <div className="my-3 p-4 bg-gray-50 border border-gray-200 rounded-2xl shadow-xs space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <GitFork className="w-4 h-4 text-blue-600" />
          <span className="font-bold text-gray-900 uppercase tracking-wider">
            {toolData.algorithm} Search Result
          </span>
        </div>
        <div className="font-mono text-blue-700 font-bold bg-white p-2 rounded-lg border border-gray-200">
          Path: {toolData.path.join(' → ')}
        </div>
        <div className="flex justify-between text-gray-600 text-[11px]">
          <span>Nodes Expanded: <strong>{toolData.nodes_expanded}</strong></span>
          <span>Time: <strong>{toolData.execution_time_ms} ms</strong></span>
        </div>
      </div>
    );
  }

  // 4. Study Planner Card
  if (toolData.timetable && toolData.quality_score) {
    return (
      <div className="my-3 p-4 bg-gradient-to-br from-blue-50 to-emerald-50 border border-blue-200 rounded-2xl shadow-xs space-y-2 text-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-blue-600" />
            <span className="font-bold text-blue-900 uppercase tracking-wider">
              Simulated Annealing Timetable
            </span>
          </div>
          <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
            {toolData.quality_score}% Quality Score
          </span>
        </div>
        <p className="text-gray-600">
          Plan generated across {toolData.total_days} days ({toolData.daily_capacity} hrs/day max capacity).
        </p>
      </div>
    );
  }

  return null;
};
