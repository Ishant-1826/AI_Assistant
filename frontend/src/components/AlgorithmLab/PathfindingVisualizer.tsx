import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, Shuffle, Sparkles, Navigation, AlertCircle, RefreshCw } from 'lucide-react';

const GRID_SIZE = 15;

export const PathfindingVisualizer: React.FC = () => {
  const [grid, setGrid] = useState<number[][]>(() => {
    return Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0));
  });

  const [start, setStart] = useState<[number, number]>([1, 1]);
  const [goal, setGoal] = useState<[number, number]>([13, 13]);
  const [algorithm, setAlgorithm] = useState<'astar' | 'dstar' | 'hill_climbing'>('astar');
  const [isMouseDown, setIsMouseDown] = useState<boolean>(false);
  const [visitedCells, setVisitedCells] = useState<[number, number][]>([]);
  const [pathCells, setPathCells] = useState<[number, number][]>([]);
  const [replannedPathCells, setReplannedPathCells] = useState<[number, number][]>([]);
  const [dynamicObstacles, setDynamicObstacles] = useState<[number, number][]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<any>(null);
  const [statusMessage, setStatusMessage] = useState<string>('');

  const handleCellClick = (r: number, c: number) => {
    if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) return;
    const newGrid = grid.map(row => [...row]);
    newGrid[r][c] = newGrid[r][c] === 1 ? 0 : 1;
    setGrid(newGrid);
  };

  const handleCellMouseEnter = (r: number, c: number) => {
    if (!isMouseDown) return;
    if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) return;
    const newGrid = grid.map(row => [...row]);
    newGrid[r][c] = 1;
    setGrid(newGrid);
  };

  const clearGrid = () => {
    setGrid(Array.from({ length: GRID_SIZE }, () => Array(GRID_SIZE).fill(0)));
    setVisitedCells([]);
    setPathCells([]);
    setReplannedPathCells([]);
    setDynamicObstacles([]);
    setMetrics(null);
    setStatusMessage('');
  };

  const generateRandomMaze = () => {
    clearGrid();
    const newGrid = Array.from({ length: GRID_SIZE }, () =>
      Array.from({ length: GRID_SIZE }, () => (Math.random() < 0.28 ? 1 : 0))
    );
    newGrid[start[0]][start[1]] = 0;
    newGrid[goal[0]][goal[1]] = 0;
    setGrid(newGrid);
  };

  const runPathfinding = async () => {
    setIsSearching(true);
    setVisitedCells([]);
    setPathCells([]);
    setReplannedPathCells([]);
    setDynamicObstacles([]);
    setMetrics(null);

    try {
      if (algorithm === 'astar') {
        const res = await fetch('/api/algorithms/astar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grid: grid,
            start: start,
            goal: goal,
            heuristic: 'manhattan'
          })
        });
        const data = await res.json();
        setMetrics(data);
        if (data.found) {
          setVisitedCells(data.visited_order || []);
          setPathCells(data.path || []);
          setStatusMessage(`A* successfully found optimal path (${data.path_length} steps) in ${data.execution_time_ms} ms!`);
        } else {
          setStatusMessage('A* could not reach the goal: path is completely blocked by obstacles.');
        }
      } else if (algorithm === 'dstar') {
        // D* Lite with dynamic obstacle insertion
        const res = await fetch('/api/algorithms/dstar', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grid: grid,
            start: start,
            goal: goal
          })
        });
        const data = await res.json();
        setMetrics(data);
        setPathCells(data.initial_path || []);
        setReplannedPathCells(data.replanned_path || []);
        setDynamicObstacles(data.dynamic_obstacles_added || []);
        setStatusMessage(
          `D* Lite computed initial path, introduced dynamic obstacles at ${JSON.stringify(data.dynamic_obstacles_added)}, and dynamically replanned in ${data.replan_expansions} expansions!`
        );
      } else if (algorithm === 'hill_climbing') {
        const res = await fetch('/api/algorithms/hill_climbing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            grid: grid,
            start: start,
            goal: goal
          })
        });
        const data = await res.json();
        setMetrics(data);
        setPathCells(data.path || []);
        if (data.found) {
          setStatusMessage(`Hill Climbing greedily reached the goal in ${data.path_length} steps!`);
        } else {
          setStatusMessage(
            'Hill Climbing became trapped in a local optimum! No adjacent free cell had a strictly lower Manhattan distance.'
          );
        }
      }
    } catch (e: any) {
      setStatusMessage('Error: ' + e.message);
    } finally {
      setIsSearching(false);
    }
  };

  const pathSet = new Set(pathCells.map(p => `${p[0]},${p[1]}`));
  const replannedPathSet = new Set(replannedPathCells.map(p => `${p[0]},${p[1]}`));
  const visitedSet = new Set(visitedCells.map(p => `${p[0]},${p[1]}`));
  const dynamicObstacleSet = new Set(dynamicObstacles.map(p => `${p[0]},${p[1]}`));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Navigation className="w-5 h-5 text-emerald-600" />
            Grid Pathfinding & Dynamic Replanning (A*, D* Lite, Hill Climbing)
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Draw obstacles, generate mazes, and observe how A* finds the optimal route, D* Lite dynamically replans around new obstacles, and Hill Climbing encounters local traps.
          </p>
        </div>

        {/* Algorithm & Run Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value as any)}
            className="px-3 py-1.5 text-xs bg-gray-50 border border-gray-300 rounded-lg font-semibold text-gray-800 focus:outline-none"
          >
            <option value="astar">A* Pathfinding (Manhattan)</option>
            <option value="dstar">D* Lite (Dynamic Obstacles & Replanning)</option>
            <option value="hill_climbing">Hill Climbing (Greedy Local Search)</option>
          </select>

          <button
            onClick={generateRandomMaze}
            className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-lg transition flex items-center gap-1"
          >
            <Shuffle className="w-3.5 h-3.5" /> Random Maze
          </button>

          <button
            onClick={clearGrid}
            className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-lg transition"
          >
            Clear Grid
          </button>

          <button
            onClick={runPathfinding}
            disabled={isSearching}
            className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-sm transition flex items-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5" />
            {isSearching ? 'Computing...' : 'Run Pathfinding'}
          </button>
        </div>
      </div>

      {/* Grid and Legend */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        {/* Left: Interactive Grid Canvas */}
        <div
          className="md:col-span-8 flex flex-col items-center bg-gray-50 p-4 rounded-2xl border border-gray-200 select-none"
          onMouseDown={() => setIsMouseDown(true)}
          onMouseUp={() => setIsMouseDown(false)}
          onMouseLeave={() => setIsMouseDown(false)}
        >
          <div
            className="grid gap-1 bg-white p-2 rounded-xl shadow-inner border border-gray-300"
            style={{
              gridTemplateColumns: `repeat(${GRID_SIZE}, minmax(0, 1fr))`,
              width: 'min(100%, 450px)',
              height: 'min(100%, 450px)',
            }}
          >
            {grid.map((row, r) =>
              row.map((cell, c) => {
                const isStart = r === start[0] && c === start[1];
                const isGoal = r === goal[0] && c === goal[1];
                const isObstacle = cell === 1;
                const isDynamicObstacle = dynamicObstacleSet.has(`${r},${c}`);
                const isPath = pathSet.has(`${r},${c}`);
                const isReplannedPath = replannedPathSet.has(`${r},${c}`);
                const isVisited = visitedSet.has(`${r},${c}`);

                let cellColor = 'bg-white hover:bg-gray-100';

                if (isStart) {
                  cellColor = 'bg-emerald-500 text-white font-bold ring-2 ring-emerald-300';
                } else if (isGoal) {
                  cellColor = 'bg-rose-500 text-white font-bold ring-2 ring-rose-300';
                } else if (isDynamicObstacle) {
                  cellColor = 'bg-amber-500 animate-pulse text-white font-bold';
                } else if (isObstacle) {
                  cellColor = 'bg-slate-800';
                } else if (isReplannedPath && algorithm === 'dstar') {
                  cellColor = 'bg-indigo-600 text-white font-bold';
                } else if (isPath) {
                  cellColor = 'bg-blue-500 text-white font-bold';
                } else if (isVisited) {
                  cellColor = 'bg-blue-100/70';
                }

                return (
                  <div
                    key={`${r}-${c}`}
                    onClick={() => handleCellClick(r, c)}
                    onMouseEnter={() => handleCellMouseEnter(r, c)}
                    className={`aspect-square rounded-sm border border-gray-200/60 cursor-pointer flex items-center justify-center text-[10px] transition-colors duration-150 ${cellColor}`}
                  >
                    {isStart ? 'S' : isGoal ? 'G' : isDynamicObstacle ? '⚠' : ''}
                  </div>
                );
              })
            )}
          </div>

          <p className="text-[11px] text-gray-500 mt-3 text-center">
            Click or drag across cells to place/remove wall obstacles.
          </p>
        </div>

        {/* Right: Legend & Diagnostics */}
        <div className="md:col-span-4 space-y-4">
          {/* Legend */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2 text-xs">
            <h4 className="font-bold text-gray-700 uppercase tracking-wider text-[11px]">
              Legend
            </h4>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-emerald-500 inline-block" />
                <span>Start Point</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-rose-500 inline-block" />
                <span>Goal Point</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-slate-800 inline-block" />
                <span>Wall Obstacle</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-blue-500 inline-block" />
                <span>Computed Path</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-indigo-600 inline-block" />
                <span>D* Replanned Path</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3.5 h-3.5 rounded bg-amber-500 inline-block" />
                <span>Dynamic Obstacle</span>
              </div>
            </div>
          </div>

          {/* Status Message */}
          {statusMessage && (
            <div className="bg-blue-50 border border-blue-200 text-blue-900 text-xs p-3.5 rounded-xl leading-relaxed">
              <span className="font-bold block mb-1">Status:</span>
              {statusMessage}
            </div>
          )}

          {/* Explanation Card */}
          {metrics && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2 text-xs leading-relaxed text-gray-600">
              <h4 className="font-bold text-gray-800 uppercase text-[11px] tracking-wider">
                Algorithm Explanation
              </h4>
              <p>{metrics.explanation}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
