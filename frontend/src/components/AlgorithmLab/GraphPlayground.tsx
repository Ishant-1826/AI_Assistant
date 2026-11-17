import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, SkipForward, GitFork, BarChart3, Info, CheckCircle2 } from 'lucide-react';

interface GraphNode {
  id: string;
  x: number;
  y: number;
}

interface GraphEdge {
  from: string;
  to: string;
  weight: number;
}

const DEFAULT_NODES: GraphNode[] = [
  { id: 'A', x: 80, y: 150 },
  { id: 'B', x: 220, y: 80 },
  { id: 'C', x: 220, y: 220 },
  { id: 'D', x: 380, y: 60 },
  { id: 'E', x: 380, y: 150 },
  { id: 'F', x: 380, y: 240 },
  { id: 'G', x: 520, y: 150 },
];

const DEFAULT_EDGES: GraphEdge[] = [
  { from: 'A', to: 'B', weight: 3 },
  { from: 'A', to: 'C', weight: 5 },
  { from: 'B', to: 'D', weight: 2 },
  { from: 'B', to: 'E', weight: 4 },
  { from: 'C', to: 'E', weight: 2 },
  { from: 'C', to: 'F', weight: 6 },
  { from: 'D', to: 'G', weight: 5 },
  { from: 'E', to: 'G', weight: 2 },
  { from: 'F', to: 'G', weight: 3 },
];

export const GraphPlayground: React.FC = () => {
  const [nodes, setNodes] = useState<GraphNode[]>(DEFAULT_NODES);
  const [edges, setEdges] = useState<GraphEdge[]>(DEFAULT_EDGES);
  const [startNode, setStartNode] = useState<string>('A');
  const [goalNode, setGoalNode] = useState<string>('G');
  const [algorithm, setAlgorithm] = useState<'bfs' | 'dfs' | 'ids'>('bfs');

  const [searchResult, setSearchResult] = useState<any>(null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(600);

  const timerRef = useRef<any>(null);

  // Build adjacency list for API
  const buildGraphPayload = () => {
    const graphDict: Record<string, Array<{ target: string; weight: number }>> = {};
    nodes.forEach(n => { graphDict[n.id] = []; });
    edges.forEach(e => {
      if (!graphDict[e.from]) graphDict[e.from] = [];
      graphDict[e.from].push({ target: e.to, weight: e.weight });
    });
    return graphDict;
  };

  const handleRunSearch = async () => {
    setIsPlaying(false);
    setComparisonResult(null);
    try {
      const graphDict = buildGraphPayload();
      const endpoint = `/api/algorithms/${algorithm}`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph: graphDict, start: startNode, goal: goalNode, max_depth: 8 })
      });
      const data = await res.json();
      setSearchResult(data);
      setCurrentStepIdx(0);
      setIsPlaying(true);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCompareAll = async () => {
    setIsPlaying(false);
    try {
      const graphDict = buildGraphPayload();
      const res = await fetch('/api/algorithms/compare_search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph: graphDict, start: startNode, goal: goalNode, max_depth: 8 })
      });
      const data = await res.json();
      setComparisonResult(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (isPlaying && searchResult?.steps) {
      timerRef.current = setInterval(() => {
        setCurrentStepIdx(prev => {
          if (prev >= searchResult.steps.length - 1) {
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
  }, [isPlaying, searchResult, playbackSpeed]);

  const currentStep = searchResult?.steps?.[currentStepIdx] || null;
  const visitedSet = new Set(currentStep?.visited || []);
  const frontierSet = new Set(currentStep?.frontier || []);
  const finalPath = searchResult?.path || [];
  const finalPathEdges = new Set<string>();

  for (let i = 0; i < finalPath.length - 1; i++) {
    finalPathEdges.add(`${finalPath[i]}->${finalPath[i + 1]}`);
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100">
        <div>
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <GitFork className="w-5 h-5 text-blue-600" />
            Graph Search Playground
          </h3>
          <p className="text-xs text-gray-500 mt-1">
            Interactively explore state space search with BFS (FIFO queue), DFS (LIFO stack), and Iterative Deepening.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Start and Goal selectors */}
          <div className="flex items-center gap-1.5 text-xs bg-gray-50 px-2.5 py-1.5 rounded-lg border border-gray-200">
            <span className="text-gray-500 font-semibold">Start:</span>
            <select
              value={startNode}
              onChange={(e) => setStartNode(e.target.value)}
              className="bg-transparent font-bold text-gray-800 focus:outline-none"
            >
              {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
            </select>
          </div>

          <div className="flex items-center gap-1.5 text-xs bg-gray-50 px-2.5 py-1.5 rounded-lg border border-gray-200">
            <span className="text-gray-500 font-semibold">Goal:</span>
            <select
              value={goalNode}
              onChange={(e) => setGoalNode(e.target.value)}
              className="bg-transparent font-bold text-gray-800 focus:outline-none"
            >
              {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
            </select>
          </div>

          {/* Algorithm selector */}
          <select
            value={algorithm}
            onChange={(e) => setAlgorithm(e.target.value as any)}
            className="px-3 py-1.5 text-xs bg-gray-50 border border-gray-300 rounded-lg font-semibold text-gray-800 focus:outline-none"
          >
            <option value="bfs">BFS (Breadth-First)</option>
            <option value="dfs">DFS (Depth-First)</option>
            <option value="ids">IDS (Iterative Deepening)</option>
          </select>

          <button
            onClick={handleRunSearch}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition"
          >
            Run Search
          </button>

          <button
            onClick={handleCompareAll}
            className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-semibold rounded-lg transition flex items-center gap-1"
          >
            <BarChart3 className="w-3.5 h-3.5" /> Compare All
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
        <div className="md:col-span-8 bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col items-center justify-center relative overflow-hidden">
          <svg className="w-full h-80 max-w-xl" viewBox="0 0 600 300">
            {/* Draw Edges */}
            {edges.map((e, idx) => {
              const fromN = nodes.find(n => n.id === e.from);
              const toN = nodes.find(n => n.id === e.to);
              if (!fromN || !toN) return null;

              const isPathEdge = finalPathEdges.has(`${e.from}->${e.to}`);
              const midX = (fromN.x + toN.x) / 2;
              const midY = (fromN.y + toN.y) / 2;

              return (
                <g key={idx}>
                  <line
                    x1={fromN.x}
                    y1={fromN.y}
                    x2={toN.x}
                    y2={toN.y}
                    stroke={isPathEdge ? '#2563eb' : '#cbd5e1'}
                    strokeWidth={isPathEdge ? 4 : 2}
                    className="transition-colors duration-300"
                  />
                  {/* Arrow marker indicator */}
                  <circle
                    cx={toN.x - (toN.x - fromN.x) * 0.15}
                    cy={toN.y - (toN.y - fromN.y) * 0.15}
                    r={3}
                    fill={isPathEdge ? '#2563eb' : '#94a3b8'}
                  />
                  {/* Weight label */}
                  <rect
                    x={midX - 10}
                    y={midY - 8}
                    width={20}
                    height={16}
                    fill="#f8fafc"
                    rx={3}
                  />
                  <text
                    x={midX}
                    y={midY + 4}
                    textAnchor="middle"
                    className="text-[10px] font-bold fill-slate-500 font-mono"
                  >
                    {e.weight}
                  </text>
                </g>
              );
            })}

            {/* Draw Nodes */}
            {nodes.map(n => {
              const isStart = n.id === startNode;
              const isGoal = n.id === goalNode;
              const isCurrent = currentStep?.current === n.id;
              const isVisited = visitedSet.has(n.id);
              const isFrontier = frontierSet.has(n.id);
              const isInPath = finalPath.includes(n.id);

              let fillColor = '#ffffff';
              let strokeColor = '#94a3b8';

              if (isCurrent) {
                fillColor = '#3b82f6'; // Bright blue for active
                strokeColor = '#1d4ed8';
              } else if (isInPath && currentStep?.action === 'goal_reached') {
                fillColor = '#10b981'; // Green for final path
                strokeColor = '#059669';
              } else if (isVisited) {
                fillColor = '#e2e8f0'; // Visited gray
                strokeColor = '#64748b';
              } else if (isFrontier) {
                fillColor = '#fef3c7'; // Amber for frontier
                strokeColor = '#f59e0b';
              }

              return (
                <g key={n.id} className="transition-all duration-300 cursor-pointer">
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={isCurrent ? 24 : 20}
                    fill={fillColor}
                    stroke={strokeColor}
                    strokeWidth={isCurrent ? 3 : 2}
                    className="shadow-sm"
                  />
                  <text
                    x={n.x}
                    y={n.y + 5}
                    textAnchor="middle"
                    className={`text-sm font-bold select-none ${
                      isCurrent || (isInPath && currentStep?.action === 'goal_reached')
                        ? 'fill-white'
                        : 'fill-slate-800'
                    }`}
                  >
                    {n.id}
                  </text>
                  {isStart && (
                    <text x={n.x} y={n.y - 26} textAnchor="middle" className="text-[9px] font-bold fill-emerald-600">
                      START
                    </text>
                  )}
                  {isGoal && (
                    <text x={n.x} y={n.y + 34} textAnchor="middle" className="text-[9px] font-bold fill-rose-600">
                      GOAL
                    </text>
                  )}
                </g>
              );
            })}
          </svg>

          {/* Step playback bar */}
          {searchResult?.steps && (
            <div className="w-full mt-3 bg-white p-3 rounded-xl border border-gray-200 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => { setIsPlaying(false); setCurrentStepIdx(0); }}
                  className="p-1.5 hover:bg-gray-100 rounded text-gray-600"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="px-3 py-1 bg-blue-600 text-white rounded font-medium flex items-center gap-1"
                >
                  {isPlaying ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                  {isPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                  onClick={() => setCurrentStepIdx(prev => Math.min(searchResult.steps.length - 1, prev + 1))}
                  disabled={currentStepIdx >= searchResult.steps.length - 1}
                  className="p-1.5 hover:bg-gray-100 rounded text-gray-600 disabled:opacity-40"
                >
                  <SkipForward className="w-3.5 h-3.5" />
                </button>
              </div>

              <span className="text-gray-500 font-mono">
                Step {currentStepIdx} / {searchResult.steps.length - 1}
              </span>
            </div>
          )}
        </div>

        {/* Right: Step Description & State Details */}
        <div className="md:col-span-4 space-y-4">
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 space-y-2.5">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Step Information
            </h4>
            {currentStep ? (
              <div className="text-xs text-gray-700 space-y-2 leading-relaxed">
                <p className="bg-white p-2.5 rounded-lg border border-gray-200 font-medium text-blue-900">
                  {currentStep.description}
                </p>
                <div className="flex justify-between py-1 border-b border-gray-200">
                  <span className="text-gray-500">Current Node:</span>
                  <span className="font-bold text-blue-600">{currentStep.current}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-200">
                  <span className="text-gray-500">Frontier:</span>
                  <span className="font-mono text-gray-800">{JSON.stringify(currentStep.frontier || [])}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-500">Visited Nodes:</span>
                  <span className="font-mono text-gray-800">{JSON.stringify(currentStep.visited || [])}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-gray-400">Click &ldquo;Run Search&rdquo; to start algorithm execution.</p>
            )}
          </div>

          {searchResult && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-xs space-y-1.5">
              <span className="font-bold text-emerald-800 block">Final Result:</span>
              <p className="text-emerald-900 font-semibold">
                Path: {searchResult.path?.join(' → ')}
              </p>
              <div className="flex justify-between text-emerald-800 pt-1">
                <span>Expanded: <strong>{searchResult.nodes_expanded}</strong></span>
                <span>Time: <strong>{searchResult.execution_time_ms} ms</strong></span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Comparison Matrix Table */}
      {comparisonResult && (
        <div className="bg-gradient-to-r from-blue-50/50 to-indigo-50/50 border border-blue-200 rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-700" />
            <h4 className="text-sm font-bold text-blue-900">
              Algorithm Comparison: DFS vs BFS vs IDS (Start: {comparisonResult.start} → Goal: {comparisonResult.goal})
            </h4>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left bg-white rounded-xl shadow-sm border border-gray-200">
              <thead className="bg-gray-50 text-gray-600 uppercase font-semibold text-[10px]">
                <tr>
                  <th className="px-4 py-3">Algorithm</th>
                  <th className="px-4 py-3">Path Found</th>
                  <th className="px-4 py-3">Path Length</th>
                  <th className="px-4 py-3">Nodes Expanded</th>
                  <th className="px-4 py-3">Execution Time</th>
                  <th className="px-4 py-3">Optimality</th>
                  <th className="px-4 py-3">Space Complexity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 font-medium">
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 font-bold text-blue-700">BFS</td>
                  <td className="px-4 py-2.5 font-mono">{comparisonResult.bfs.path?.join(' → ')}</td>
                  <td className="px-4 py-2.5 font-bold text-emerald-600">{comparisonResult.bfs.path_length}</td>
                  <td className="px-4 py-2.5">{comparisonResult.bfs.nodes_expanded}</td>
                  <td className="px-4 py-2.5">{comparisonResult.bfs.time_ms} ms</td>
                  <td className="px-4 py-2.5 text-emerald-600 font-bold">Guaranteed (Unweighted)</td>
                  <td className="px-4 py-2.5 font-mono text-gray-500">O(b^d)</td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 font-bold text-purple-700">DFS</td>
                  <td className="px-4 py-2.5 font-mono">{comparisonResult.dfs.path?.join(' → ')}</td>
                  <td className="px-4 py-2.5">{comparisonResult.dfs.path_length}</td>
                  <td className="px-4 py-2.5">{comparisonResult.dfs.nodes_expanded}</td>
                  <td className="px-4 py-2.5">{comparisonResult.dfs.time_ms} ms</td>
                  <td className="px-4 py-2.5 text-amber-600">Not Guaranteed</td>
                  <td className="px-4 py-2.5 font-mono text-emerald-600 font-bold">O(bm)</td>
                </tr>
                <tr className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 font-bold text-indigo-700">IDS</td>
                  <td className="px-4 py-2.5 font-mono">{comparisonResult.ids.path?.join(' → ')}</td>
                  <td className="px-4 py-2.5 font-bold text-emerald-600">{comparisonResult.ids.path_length}</td>
                  <td className="px-4 py-2.5">{comparisonResult.ids.nodes_expanded}</td>
                  <td className="px-4 py-2.5">{comparisonResult.ids.time_ms} ms</td>
                  <td className="px-4 py-2.5 text-emerald-600 font-bold">Guaranteed (Unweighted)</td>
                  <td className="px-4 py-2.5 font-mono text-emerald-600 font-bold">O(bd)</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p className="text-xs text-blue-900 bg-white/80 p-3 rounded-xl border border-blue-100">
            {comparisonResult.comparison_summary}
          </p>
        </div>
      )}
    </div>
  );
};
