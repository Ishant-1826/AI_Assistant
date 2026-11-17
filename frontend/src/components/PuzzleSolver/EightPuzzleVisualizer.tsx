import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, SkipForward, SkipBack, Shuffle, Brain, CheckCircle, AlertTriangle, Cpu } from 'lucide-react';

const DEFAULT_GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0];

export const EightPuzzleVisualizer: React.FC = () => {
  const [board, setBoard] = useState<number[]>([1, 2, 3, 4, 5, 6, 7, 0, 8]);
  const [goal, setGoal] = useState<number[]>(DEFAULT_GOAL);
  const [algorithm, setAlgorithm] = useState<string>('astar');
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [solutionSteps, setSolutionSteps] = useState<number[][]>([]);
  const [solutionMoves, setSolutionMoves] = useState<string[]>([]);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(400); // ms per step
  const [metrics, setMetrics] = useState<any>(null);
  const [customInput, setCustomInput] = useState<string>('1, 2, 3, 4, 5, 6, 7, 0, 8');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const timerRef = useRef<any>(null);

  // Solvability check
  const countInversions = (arr: number[]) => {
    const tiles = arr.filter(x => x !== 0);
    let inv = 0;
    for (let i = 0; i < tiles.length; i++) {
      for (let j = i + 1; j < tiles.length; j++) {
        if (tiles[i] > tiles[j]) inv++;
      }
    }
    return inv;
  };

  const inversions = countInversions(board);
  const isBoardSolvable = (inversions % 2) === (countInversions(goal) % 2);

  // Tile click: if adjacent to blank 0, swap
  const handleTileClick = (idx: number) => {
    if (isPlaying) return;
    const blankIdx = board.indexOf(0);
    const r1 = Math.floor(idx / 3), c1 = idx % 3;
    const r2 = Math.floor(blankIdx / 3), c2 = blankIdx % 3;

    if (Math.abs(r1 - r2) + Math.abs(c1 - c2) === 1) {
      const nextBoard = [...board];
      [nextBoard[idx], nextBoard[blankIdx]] = [nextBoard[blankIdx], nextBoard[idx]];
      setBoard(nextBoard);
      setCustomInput(nextBoard.join(', '));
      // Clear current solution playback
      setSolutionSteps([]);
      setCurrentStepIdx(0);
    }
  };

  const handleShuffle = async () => {
    try {
      const res = await fetch('/api/puzzles/eight_puzzle/random?moves=16');
      const data = await res.json();
      setBoard(data.initial_state);
      setCustomInput(data.initial_state.join(', '));
      setSolutionSteps([]);
      setSolutionMoves([]);
      setCurrentStepIdx(0);
      setMetrics(null);
      setErrorMessage('');
    } catch (e: any) {
      setErrorMessage('Could not shuffle: ' + e.message);
    }
  };

  const handleApplyCustomInput = () => {
    try {
      const parts = customInput.split(/[\s,]+/).filter(Boolean).map(Number);
      if (parts.length !== 9 || new Set(parts).size !== 9 || parts.some(n => n < 0 || n > 8)) {
        setErrorMessage('Input must contain exactly the 9 unique digits: 0 through 8.');
        return;
      }
      setBoard(parts);
      setSolutionSteps([]);
      setCurrentStepIdx(0);
      setMetrics(null);
      setErrorMessage('');
    } catch (e: any) {
      setErrorMessage('Invalid input format');
    }
  };

  const handleSolve = async () => {
    setIsSolving(true);
    setErrorMessage('');
    setIsPlaying(false);

    try {
      const res = await fetch('/api/puzzles/eight_puzzle/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          initial_state: board,
          algorithm: algorithm,
          goal_state: goal,
          depth_limit: 25
        })
      });

      const data = await res.json();
      if (!data.solvable) {
        setErrorMessage('This puzzle state is mathematically unsolvable due to odd inversion parity.');
        setMetrics(data);
        setIsSolving(false);
        return;
      }

      setMetrics(data);
      if (data.path && data.path.length > 0) {
        setSolutionSteps(data.path);
        setSolutionMoves(data.moves || []);
        setCurrentStepIdx(0);
        setIsPlaying(true);
      } else {
        setErrorMessage('No solution path found within search bounds.');
      }
    } catch (e: any) {
      setErrorMessage('Solving failed: ' + e.message);
    } finally {
      setIsSolving(false);
    }
  };

  // Playback timer effect
  useEffect(() => {
    if (isPlaying && solutionSteps.length > 0) {
      timerRef.current = setInterval(() => {
        setCurrentStepIdx(prev => {
          if (prev >= solutionSteps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          const next = prev + 1;
          setBoard(solutionSteps[next]);
          return next;
        });
      }, playbackSpeed);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, solutionSteps, playbackSpeed]);

  const stepForward = () => {
    if (currentStepIdx < solutionSteps.length - 1) {
      const next = currentStepIdx + 1;
      setCurrentStepIdx(next);
      setBoard(solutionSteps[next]);
    }
  };

  const stepBackward = () => {
    if (currentStepIdx > 0) {
      const prev = currentStepIdx - 1;
      setCurrentStepIdx(prev);
      setBoard(solutionSteps[prev]);
    }
  };

  const resetToStart = () => {
    setIsPlaying(false);
    if (solutionSteps.length > 0) {
      setCurrentStepIdx(0);
      setBoard(solutionSteps[0]);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-600" />
            8-Puzzle Sliding Solver
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Test and compare real Python implementations of heuristic search, BFS, DFS, IDS, and local search algorithms.
          </p>
        </div>

        {/* Solvability Badge */}
        <div className="flex items-center gap-2">
          {isBoardSolvable ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle className="w-3.5 h-3.5" /> Solvable (Inversions: {inversions})
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
              <AlertTriangle className="w-3.5 h-3.5" /> Unsolvable (Inversions: {inversions})
            </span>
          )}
        </div>
      </div>

      {/* Main Grid & Controls */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Left: 3x3 Puzzle Board */}
        <div className="md:col-span-6 flex flex-col items-center">
          <div className="bg-gray-100 p-3 rounded-2xl shadow-inner border border-gray-300 w-72 h-72 grid grid-cols-3 gap-2">
            {board.map((tile, idx) => (
              <button
                key={idx}
                onClick={() => handleTileClick(idx)}
                disabled={isPlaying}
                className={`flex items-center justify-center font-bold text-2xl rounded-xl transition-all duration-200 select-none shadow-sm ${
                  tile === 0
                    ? 'bg-transparent border-2 border-dashed border-gray-300 cursor-default'
                    : tile === goal[idx]
                    ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
                    : 'bg-white text-gray-800 hover:bg-gray-50 border border-gray-200 active:scale-95'
                }`}
              >
                {tile !== 0 ? tile : ''}
              </button>
            ))}
          </div>

          <p className="text-xs text-gray-400 mt-2">
            Click adjacent tiles to slide manually into the empty space.
          </p>

          {/* Playback Controls */}
          {solutionSteps.length > 0 && (
            <div className="w-full mt-5 bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-3">
              <div className="flex items-center justify-between text-xs font-medium text-gray-600">
                <span>Step {currentStepIdx} of {solutionSteps.length - 1}</span>
                {solutionMoves[currentStepIdx - 1] && (
                  <span className="font-bold text-blue-600 uppercase">
                    Move: {solutionMoves[currentStepIdx - 1]}
                  </span>
                )}
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-blue-600 h-1.5 transition-all duration-150"
                  style={{ width: `${(currentStepIdx / Math.max(1, solutionSteps.length - 1)) * 100}%` }}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={resetToStart}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition"
                  title="Reset to Start"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
                <button
                  onClick={stepBackward}
                  disabled={currentStepIdx === 0}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 disabled:opacity-40 rounded-lg transition"
                  title="Step Backward"
                >
                  <SkipBack className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition flex items-center gap-1.5 shadow-sm text-sm"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                  onClick={stepForward}
                  disabled={currentStepIdx >= solutionSteps.length - 1}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 disabled:opacity-40 rounded-lg transition"
                  title="Step Forward"
                >
                  <SkipForward className="w-4 h-4" />
                </button>
              </div>

              {/* Speed Slider */}
              <div className="flex items-center justify-between text-xs text-gray-500 pt-1">
                <span>Speed</span>
                <input
                  type="range"
                  min="100"
                  max="1000"
                  step="50"
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                  className="w-32 accent-blue-600 cursor-pointer"
                />
                <span>{playbackSpeed}ms</span>
              </div>
            </div>
          )}
        </div>

        {/* Right: Algorithm & State Configuration */}
        <div className="md:col-span-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1.5">
              Select Solving Algorithm
            </label>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              disabled={isSolving || isPlaying}
              className="w-full px-3.5 py-2.5 bg-gray-50 border border-gray-300 rounded-xl text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            >
              <option value="astar">A* Search (Manhattan Distance Heuristic - Optimal)</option>
              <option value="bfs">Breadth-First Search (BFS - Shortest Move Count)</option>
              <option value="ids">Iterative Deepening Search (IDS - Low Memory)</option>
              <option value="dfs">Depth-First Search (DFS - Depth-limited to 25)</option>
              <option value="hill_climbing">Hill Climbing (Greedy Local Search)</option>
              <option value="simulated_annealing">Simulated Annealing (Stochastic Local Search)</option>
            </select>
          </div>

          {/* Quick Setup Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleShuffle}
              disabled={isSolving || isPlaying}
              className="flex-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-xl transition flex items-center justify-center gap-1.5"
            >
              <Shuffle className="w-3.5 h-3.5" /> Random Solvable
            </button>
            <button
              onClick={() => {
                setBoard([1, 2, 3, 4, 5, 6, 7, 8, 0]);
                setCustomInput('1, 2, 3, 4, 5, 6, 7, 8, 0');
                setSolutionSteps([]);
                setCurrentStepIdx(0);
              }}
              disabled={isSolving || isPlaying}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-semibold rounded-xl transition"
            >
              Solved State
            </button>
          </div>

          {/* Custom State Input */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
              Custom State (0 represents the blank tile)
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customInput}
                onChange={(e) => setCustomInput(e.target.value)}
                placeholder="1, 2, 3, 4, 5, 6, 7, 0, 8"
                className="flex-1 px-3 py-1.5 text-xs bg-gray-50 border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono"
              />
              <button
                onClick={handleApplyCustomInput}
                className="px-3 py-1.5 bg-gray-800 text-white text-xs font-medium rounded-lg hover:bg-gray-900 transition"
              >
                Apply
              </button>
            </div>
          </div>

          {/* Solve Button */}
          <button
            onClick={handleSolve}
            disabled={isSolving}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 active:scale-[0.99] disabled:opacity-50 text-white font-semibold rounded-xl shadow-sm transition flex items-center justify-center gap-2"
          >
            <Cpu className="w-4 h-4" />
            {isSolving ? 'Solving with Python Engine...' : `Run ${algorithm.toUpperCase()} Solver`}
          </button>

          {/* Error Message */}
          {errorMessage && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0 text-red-500" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Execution Metrics */}
          {metrics && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                Execution Metrics
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 bg-white rounded-lg border border-gray-100">
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">Nodes Expanded</span>
                  <span className="font-bold text-gray-800 text-sm">{metrics.nodes_expanded}</span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-gray-100">
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">Solution Moves</span>
                  <span className="font-bold text-blue-600 text-sm">{metrics.solution_cost} moves</span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-gray-100">
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">Execution Time</span>
                  <span className="font-bold text-gray-800 text-sm">{metrics.execution_time_ms} ms</span>
                </div>
                <div className="p-2.5 bg-white rounded-lg border border-gray-100">
                  <span className="text-gray-400 block text-[10px] uppercase font-semibold">Goal Reached</span>
                  <span className={`font-bold text-sm ${metrics.found ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {metrics.found ? 'YES (Optimal)' : 'NO (Local Trap)'}
                  </span>
                </div>
              </div>

              {/* Explanation Note */}
              <div className="text-xs text-gray-600 bg-white p-2.5 rounded-lg border border-gray-100 leading-relaxed">
                {metrics.explanation}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
