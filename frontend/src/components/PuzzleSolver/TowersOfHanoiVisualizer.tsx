import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, SkipForward, SkipBack, Layers, CheckCircle } from 'lucide-react';

export const TowersOfHanoiVisualizer: React.FC = () => {
  const [numDisks, setNumDisks] = useState<number>(3);
  const [useBFS, setUseBFS] = useState<boolean>(false);
  const [simulation, setSimulation] = useState<any>(null);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(500);

  const timerRef = useRef<any>(null);

  const fetchSolution = async () => {
    setIsPlaying(false);
    try {
      const res = await fetch('/api/puzzles/towers_of_hanoi/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_disks: numDisks, use_bfs: useBFS })
      });
      const data = await res.json();
      setSimulation(data);
      setCurrentStepIdx(0);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchSolution();
  }, [numDisks, useBFS]);

  useEffect(() => {
    if (isPlaying && simulation?.steps) {
      timerRef.current = setInterval(() => {
        setCurrentStepIdx(prev => {
          if (prev >= simulation.steps.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, playbackSpeed);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, simulation, playbackSpeed]);

  const currentStep = simulation?.steps?.[currentStepIdx] || null;
  const pegs = currentStep?.pegs || { A: [], B: [], C: [] };

  // Colors for disks (1 = smallest, up to 6 = largest)
  const diskColors = [
    'bg-sky-400',
    'bg-blue-500',
    'bg-indigo-500',
    'bg-violet-600',
    'bg-purple-600',
    'bg-fuchsia-600',
  ];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Layers className="w-6 h-6 text-indigo-600" />
            Towers of Hanoi Visualizer
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Explore divide-and-conquer recursion and state-space graph search. Minimal moves: 2^n - 1.
          </p>
        </div>

        {/* Configuration Controls */}
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-semibold text-gray-700 bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-200">
            <span>Disks:</span>
            {[3, 4, 5, 6].map(n => (
              <button
                key={n}
                onClick={() => setNumDisks(n)}
                className={`px-2 py-0.5 rounded text-xs font-bold transition ${
                  numDisks === n
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-gray-600 hover:bg-gray-200'
                }`}
              >
                {n}
              </button>
            ))}
          </div>

          <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-200 cursor-pointer">
            <input
              type="checkbox"
              checked={useBFS}
              disabled={numDisks > 4}
              onChange={(e) => setUseBFS(e.target.checked)}
              className="accent-indigo-600 rounded"
            />
            <span>BFS Graph Search {numDisks > 4 && '(n <= 4)'}</span>
          </label>
        </div>
      </div>

      {/* Main Pegs Visualization Area */}
      <div className="bg-gradient-to-b from-gray-50 to-gray-100 p-8 rounded-2xl border border-gray-200">
        <div className="grid grid-cols-3 gap-6 items-end h-64 relative">
          {(['A', 'B', 'C'] as const).map(pegName => {
            const diskStack = pegs[pegName] || [];
            return (
              <div key={pegName} className="flex flex-col items-center justify-end h-full relative">
                {/* Vertical Pole */}
                <div className="w-3 bg-stone-400 rounded-t-full absolute bottom-4 top-4 z-0 shadow-inner" />

                {/* Base Plate */}
                <div className="w-full max-w-[180px] h-4 bg-stone-600 rounded-lg shadow-md z-10 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-white tracking-widest">
                    PEG {pegName}
                  </span>
                </div>

                {/* Stacked Disks on this Peg */}
                <div className="absolute bottom-4 z-20 flex flex-col-reverse items-center gap-1.5 w-full">
                  {diskStack.map((diskNum: number) => {
                    const widthPercent = 30 + (diskNum / numDisks) * 60;
                    return (
                      <div
                        key={diskNum}
                        style={{ width: `${widthPercent}%` }}
                        className={`h-7 rounded-lg shadow-sm border border-black/10 flex items-center justify-center text-white text-xs font-bold transition-all duration-300 ${
                          diskColors[(diskNum - 1) % diskColors.length]
                        }`}
                      >
                        {diskNum}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Playback Controls & Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* Controls */}
        <div className="md:col-span-7 bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-gray-700">
            <span>Move {currentStepIdx} of {simulation?.steps?.length ? simulation.steps.length - 1 : 0}</span>
            {currentStep?.disk && (
              <span className="text-indigo-600 font-bold">
                Move Disk {currentStep.disk}: {currentStep.from_peg} → {currentStep.to_peg}
              </span>
            )}
          </div>

          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => { setIsPlaying(false); setCurrentStepIdx(0); }}
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-200 transition"
              title="Reset"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentStepIdx(prev => Math.max(0, prev - 1))}
              disabled={currentStepIdx === 0}
              className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-40 rounded-lg hover:bg-gray-200 transition"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-xs font-bold hover:bg-indigo-700 transition flex items-center gap-1.5 shadow-sm"
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              {isPlaying ? 'Pause' : 'Play'}
            </button>
            <button
              onClick={() => setCurrentStepIdx(prev => Math.min((simulation?.steps?.length || 1) - 1, prev + 1))}
              disabled={currentStepIdx >= (simulation?.steps?.length || 1) - 1}
              className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-40 rounded-lg hover:bg-gray-200 transition"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          {/* Speed slider */}
          <div className="flex items-center justify-between text-xs text-gray-500 pt-1">
            <span>Speed:</span>
            <input
              type="range"
              min="150"
              max="900"
              step="50"
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
              className="w-32 accent-indigo-600 cursor-pointer"
            />
            <span>{playbackSpeed}ms</span>
          </div>
        </div>

        {/* Metrics Summary */}
        <div className="md:col-span-5 bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-2 text-xs">
          <div className="flex justify-between py-1 border-b border-gray-200">
            <span className="text-gray-500">Algorithm:</span>
            <span className="font-semibold text-gray-800">{simulation?.algorithm}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-gray-200">
            <span className="text-gray-500">Total Moves Taken:</span>
            <span className="font-bold text-indigo-600">{simulation?.total_moves}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-gray-200">
            <span className="text-gray-500">Theoretical Minimum (2^n - 1):</span>
            <span className="font-bold text-emerald-600">{simulation?.min_moves_theoretical} moves</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-gray-500">Execution Time:</span>
            <span className="font-semibold text-gray-800">{simulation?.execution_time_ms} ms</span>
          </div>
        </div>
      </div>
    </div>
  );
};
