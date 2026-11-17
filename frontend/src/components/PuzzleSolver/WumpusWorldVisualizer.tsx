import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, SkipForward, SkipBack, Shield, Wind, Skull, Sparkles, AlertCircle, Compass } from 'lucide-react';

export const WumpusWorldVisualizer: React.FC = () => {
  const [simulation, setSimulation] = useState<any>(null);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [showBayesianOverlay, setShowBayesianOverlay] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(700);

  const timerRef = useRef<any>(null);

  const runSimulation = async () => {
    setIsLoading(true);
    setIsPlaying(false);
    try {
      const res = await fetch('/api/puzzles/wumpus_world/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid_size: 4, max_steps: 25 })
      });
      const data = await res.json();
      setSimulation(data);
      setCurrentStepIdx(0);
      setIsPlaying(true);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  useEffect(() => {
    if (isPlaying && simulation && simulation.steps) {
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

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Compass className="w-6 h-6 text-amber-600" />
            Wumpus World & Bayesian Hazard Estimation
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            An intelligent agent explores a partially observable cave, using Bayesian inference to calculate Pit and Wumpus probabilities on unvisited tiles.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs font-semibold text-gray-700 cursor-pointer bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200">
            <input
              type="checkbox"
              checked={showBayesianOverlay}
              onChange={(e) => setShowBayesianOverlay(e.target.checked)}
              className="accent-blue-600 rounded"
            />
            Show Bayesian P(Hazard)
          </label>
          <button
            onClick={runSimulation}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl transition shadow-sm"
          >
            {isLoading ? 'Simulating...' : 'New Simulation'}
          </button>
        </div>
      </div>

      {/* Grid and Details */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        {/* Left: 4x4 Cave Grid */}
        <div className="md:col-span-7 flex flex-col items-center">
          <div className="bg-stone-900 p-3 rounded-2xl shadow-md border-2 border-stone-800 w-80 h-80 sm:w-96 sm:h-96 grid grid-cols-4 gap-2">
            {Array.from({ length: 4 }).map((_, r) =>
              Array.from({ length: 4 }).map((_, c) => {
                const cellKey = `${r},${c}`;
                const isAgentHere = currentStep && currentStep.agent_pos[0] === r && currentStep.agent_pos[1] === c;
                const isVisited = currentStep && currentStep.visited.some((p: any) => p[0] === r && p[1] === c);
                const hasPit = simulation && simulation.pits.some((p: any) => p[0] === r && p[1] === c);
                const hasWumpus = simulation && simulation.wumpus[0] === r && simulation.wumpus[1] === c;
                const hasGold = simulation && simulation.gold[0] === r && simulation.gold[1] === c;

                const bayes = currentStep?.hazard_probabilities?.[cellKey];

                return (
                  <div
                    key={cellKey}
                    className={`relative rounded-xl border flex flex-col items-center justify-center p-1 transition-all duration-300 text-center select-none overflow-hidden ${
                      isAgentHere
                        ? 'bg-blue-600/30 border-blue-500 shadow-lg ring-2 ring-blue-400'
                        : isVisited
                        ? 'bg-stone-800/80 border-stone-700'
                        : bayes?.status === 'danger' && showBayesianOverlay
                        ? 'bg-red-950/40 border-red-800/60'
                        : bayes?.status === 'safe' && showBayesianOverlay
                        ? 'bg-emerald-950/30 border-emerald-800/40'
                        : 'bg-stone-950 border-stone-800'
                    }`}
                  >
                    {/* Coordinate indicator */}
                    <span className="absolute top-1 left-1.5 text-[9px] text-stone-500 font-mono">
                      {r},{c}
                    </span>

                    {/* Entities */}
                    {isAgentHere && (
                      <div className="z-10 flex flex-col items-center animate-bounce">
                        <span className="text-xl">🤖</span>
                        <span className="text-[9px] font-bold text-blue-300 uppercase tracking-tighter">
                          Agent
                        </span>
                      </div>
                    )}

                    {!isAgentHere && isVisited && (
                      <div className="flex flex-col items-center gap-0.5 opacity-90">
                        {hasGold && <Sparkles className="w-5 h-5 text-amber-400 animate-pulse" />}
                        <span className="text-[10px] text-stone-400 font-medium">Safe</span>
                      </div>
                    )}

                    {/* Unvisited cells with Bayesian probability */}
                    {!isVisited && showBayesianOverlay && bayes && (
                      <div className="flex flex-col items-center gap-0.5 z-0">
                        <span className="text-[10px] font-semibold text-rose-400">
                          P(Pit): {(bayes.pit * 100).toFixed(0)}%
                        </span>
                        <span className="text-[10px] font-semibold text-amber-300">
                          P(Wump): {(bayes.wumpus * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}

                    {!isVisited && !showBayesianOverlay && (
                      <span className="text-stone-600 text-xs font-mono">?</span>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* Playback Controls */}
          {simulation && simulation.steps && (
            <div className="w-full mt-4 bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-3">
              <div className="flex items-center justify-between text-xs text-gray-600 font-medium">
                <span>Step {currentStepIdx} of {simulation.steps.length - 1}</span>
                <span className="font-bold text-blue-600">
                  Action: {currentStep?.action}
                </span>
              </div>

              {/* Slider */}
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
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-semibold hover:bg-blue-700 transition flex items-center gap-1.5"
                >
                  {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                  onClick={() => setCurrentStepIdx(prev => Math.min(simulation.steps.length - 1, prev + 1))}
                  disabled={currentStepIdx >= simulation.steps.length - 1}
                  className="p-2 text-gray-600 hover:text-gray-900 disabled:opacity-40 rounded-lg hover:bg-gray-200 transition"
                >
                  <SkipForward className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right: Percepts & Live Bayesian Knowledge Base */}
        <div className="md:col-span-5 space-y-4">
          {/* Current Percepts Card */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Current Sensory Percepts
            </h4>
            <div className="grid grid-cols-3 gap-2 text-center text-xs">
              <div className={`p-2.5 rounded-lg border flex flex-col items-center gap-1 ${
                currentStep?.percepts?.breeze
                  ? 'bg-blue-100 text-blue-800 border-blue-300 font-bold'
                  : 'bg-white text-gray-400 border-gray-200'
              }`}>
                <Wind className="w-4 h-4" />
                <span>Breeze</span>
              </div>

              <div className={`p-2.5 rounded-lg border flex flex-col items-center gap-1 ${
                currentStep?.percepts?.stench
                  ? 'bg-emerald-100 text-emerald-800 border-emerald-300 font-bold'
                  : 'bg-white text-gray-400 border-gray-200'
              }`}>
                <Skull className="w-4 h-4" />
                <span>Stench</span>
              </div>

              <div className={`p-2.5 rounded-lg border flex flex-col items-center gap-1 ${
                currentStep?.percepts?.glitter
                  ? 'bg-amber-100 text-amber-800 border-amber-300 font-bold animate-pulse'
                  : 'bg-white text-gray-400 border-gray-200'
              }`}>
                <Sparkles className="w-4 h-4" />
                <span>Glitter</span>
              </div>
            </div>
          </div>

          {/* Step Description */}
          {currentStep && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 leading-relaxed">
              <span className="font-bold block text-blue-800 mb-1">Agent Step Narration:</span>
              {currentStep.description}
            </div>
          )}

          {/* Bayesian Explanation Box */}
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-xs text-gray-600 space-y-2 leading-relaxed">
            <h4 className="font-bold text-gray-800 uppercase text-[11px] tracking-wider">
              How the Bayesian Network Works Here:
            </h4>
            <p>
              When the agent senses <strong>no breeze</strong>, neighboring cells have their Pit probability updated to exactly <strong>0%</strong> (guaranteed safe).
            </p>
            <p>
              When a breeze is felt, Bayes' rule computes posterior $P(Pit \mid Breeze)$, updating frontier risk. The agent always chooses the frontier cell with minimum total risk!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
