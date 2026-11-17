import React, { useState, useEffect } from 'react';
import { Network, Activity, GitCommit, CheckCircle2, XCircle, Info, Sparkles, TrendingUp } from 'lucide-react';

export const LearningAnalyticsView: React.FC = () => {
  // Bayesian state
  const [evidence, setEvidence] = useState<{ q_pf: number; q_rec: number; q_ga: number }>({
    q_pf: 1,
    q_rec: 1,
    q_ga: 0
  });
  const [bayesResult, setBayesResult] = useState<any>(null);

  // EM state
  const [emResult, setEmResult] = useState<any>(null);

  // HMM state
  const [hmmObservations, setHmmObservations] = useState<number[]>([0, 0, 1, 2, 2, 2]);
  const [hmmResult, setHmmResult] = useState<any>(null);

  // Fetch Bayesian calculation
  const fetchBayesian = async (ev = evidence) => {
    try {
      const res = await fetch('/api/probabilistic/bayesian_mastery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ evidence: ev })
      });
      const data = await res.json();
      setBayesResult(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Fetch EM GMM
  const fetchEM = async () => {
    try {
      const res = await fetch('/api/probabilistic/em_gmm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ k_clusters: 3, max_iters: 25 })
      });
      const data = await res.json();
      setEmResult(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Fetch HMM
  const fetchHMM = async (obs = hmmObservations) => {
    try {
      const res = await fetch('/api/probabilistic/hmm_tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observations: obs })
      });
      const data = await res.json();
      setHmmResult(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchBayesian();
    fetchEM();
    fetchHMM();
  }, []);

  const toggleEvidence = (key: 'q_pf' | 'q_rec' | 'q_ga') => {
    const nextVal = evidence[key] === 1 ? 0 : 1;
    const nextEv = { ...evidence, [key]: nextVal };
    setEvidence(nextEv);
    fetchBayesian(nextEv);
  };

  const handleAddObservation = (obsVal: number) => {
    if (hmmObservations.length >= 10) return;
    const nextObs = [...hmmObservations, obsVal];
    setHmmObservations(nextObs);
    fetchHMM(nextObs);
  };

  const handleResetObservations = () => {
    const defaultObs = [0, 0, 1, 2, 2, 2];
    setHmmObservations(defaultObs);
    fetchHMM(defaultObs);
  };

  return (
    <div className="p-4 sm:p-6 max-w-6xl mx-auto space-y-8">
      {/* Title */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Activity className="w-6 h-6 text-purple-600" />
            Probabilistic Intelligence & Learning Analytics
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Exact Bayesian Network inference, Expectation Maximization (Gaussian Mixture Models), and Hidden Markov Model progress tracking.
          </p>
        </div>
      </div>

      {/* SECTION A: Bayesian Network for Student Concept Mastery */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-gray-100">
          <div>
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Network className="w-5 h-5 text-blue-600" />
              A. Bayesian Network: Concept Mastery Inference
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Propagates quiz evidence backward and forward through Conditional Probability Tables (CPT) using Bayes&apos; Rule.
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full">
            Exact Variable Elimination
          </span>
        </div>

        {/* Evidence Toggles and Posterior Probability Gauges */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
          {/* Evidence Input Controls */}
          <div className="md:col-span-5 bg-gray-50 p-4 rounded-xl border border-gray-200 space-y-3">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Enter Quiz Evidence (Observations)
            </h4>

            <div className="space-y-2.5">
              {[
                { key: 'q_pf', label: 'Quiz 1: Programming Fundamentals', parent: 'Programming Fundamentals' },
                { key: 'q_rec', label: 'Quiz 2: Recursion & Induction', parent: 'Recursion' },
                { key: 'q_ga', label: 'Quiz 3: Graph Algorithms', parent: 'Graph Algorithms' },
              ].map(item => {
                const passed = evidence[item.key as keyof typeof evidence] === 1;
                return (
                  <div
                    key={item.key}
                    onClick={() => toggleEvidence(item.key as any)}
                    className="p-3 bg-white border border-gray-200 rounded-xl flex items-center justify-between cursor-pointer hover:border-gray-300 transition shadow-xs"
                  >
                    <div>
                      <span className="font-semibold text-xs text-gray-900 block">{item.label}</span>
                      <span className="text-[10px] text-gray-400">Prerequisite: {item.parent}</span>
                    </div>

                    <button
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                        passed
                          ? 'bg-emerald-500 text-white shadow-xs'
                          : 'bg-rose-100 text-rose-700'
                      }`}
                    >
                      {passed ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                      {passed ? 'Passed' : 'Failed'}
                    </button>
                  </div>
                );
              })}
            </div>

            <p className="text-[11px] text-gray-500 italic pt-1">
              Click any quiz above to toggle evidence and observe live posterior updates.
            </p>
          </div>

          {/* Posterior Probabilities Bars */}
          <div className="md:col-span-7 space-y-4">
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Calculated Posterior Concept Mastery P(Concept | Quizzes)
            </h4>

            {bayesResult && (
              <div className="space-y-3.5">
                {[
                  { id: 'ProgrammingFundamentals', name: 'Programming Fundamentals', prob: bayesResult.posterior_probabilities?.ProgrammingFundamentals || 0.6 },
                  { id: 'Recursion', name: 'Recursion & Dynamic Thinking', prob: bayesResult.posterior_probabilities?.Recursion || 0.5 },
                  { id: 'GraphAlgorithms', name: 'Graph Algorithms (Search & Trees)', prob: bayesResult.posterior_probabilities?.GraphAlgorithms || 0.4 },
                ].map(concept => {
                  const pct = (concept.prob * 100).toFixed(1);
                  return (
                    <div key={concept.id} className="p-3.5 bg-gray-50 border border-gray-200 rounded-xl space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-gray-800">{concept.name}</span>
                        <span className="font-bold text-blue-600">{pct}% Mastery</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {bayesResult?.explanation && (
              <div className="text-xs text-gray-600 bg-blue-50 border border-blue-200 p-3.5 rounded-xl leading-relaxed">
                {bayesResult.explanation}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SECTION B: Expectation Maximization (EM) - Gaussian Mixture Model */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-gray-100">
          <div>
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              B. Expectation Maximization (EM): Gaussian Mixture Clustering
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Unsupervised clustering of student study habits (Study Hours vs Quiz Accuracy) with full E-Step & M-Step convergence.
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-full">
            Synthetic Demo Data
          </span>
        </div>

        {emResult && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
            {/* Cluster Cards */}
            <div className="md:col-span-5 space-y-3">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                Discovered Student Archetypes (K = 3)
              </h4>

              {emResult.clusters?.map((c: any) => (
                <div key={c.cluster_id} className="p-3.5 bg-gray-50 border border-gray-200 rounded-xl space-y-1.5 text-xs">
                  <div className="flex justify-between font-bold text-gray-900">
                    <span>{c.name}</span>
                    <span className="text-emerald-600 font-mono">{(c.weight * 100).toFixed(0)}% Pop</span>
                  </div>
                  <div className="flex justify-between text-gray-500 text-[11px]">
                    <span>Mean Study: <strong>{c.mean_study_hours} hrs/wk</strong></span>
                    <span>Mean Accuracy: <strong>{c.mean_quiz_accuracy}%</strong></span>
                  </div>
                  <div className="text-[10px] text-gray-400">
                    Assigned: {c.student_count} sample students
                  </div>
                </div>
              ))}
            </div>

            {/* Convergence Chart & Visualization */}
            <div className="md:col-span-7 space-y-4">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                Log-Likelihood Convergence History ({emResult.iterations_count} iterations)
              </h4>

              {/* Convergence Bar Visualizer */}
              <div className="bg-gray-50 p-4 rounded-xl border border-gray-200 flex items-end gap-1.5 h-36">
                {emResult.log_likelihood_convergence?.map((ll: number, idx: number) => {
                  const minLL = emResult.log_likelihood_convergence[0];
                  const maxLL = emResult.log_likelihood_convergence[emResult.log_likelihood_convergence.length - 1];
                  const range = Math.max(1, maxLL - minLL);
                  const normalizedH = Math.max(15, Math.min(100, ((ll - minLL) / range) * 100));

                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                      <div
                        style={{ height: `${normalizedH}%` }}
                        className="w-full bg-emerald-500 rounded-t transition-all duration-300"
                        title={`Iter ${idx + 1}: LL = ${ll}`}
                      />
                      <span className="text-[9px] text-gray-400">{idx + 1}</span>
                    </div>
                  );
                })}
              </div>

              <div className="text-xs text-gray-600 bg-emerald-50 border border-emerald-200 p-3.5 rounded-xl leading-relaxed">
                {emResult.explanation}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION C: Hidden Markov Model (HMM) Learning Progress Tracker */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-gray-100">
          <div>
            <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <GitCommit className="w-5 h-5 text-indigo-600" />
              C. Hidden Markov Model: Learning State Trajectory (Forward & Viterbi)
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Decodes hidden student competency states (Needs Practice, Learning, Confident) across a sequence of quiz answers.
            </p>
          </div>
          <button
            onClick={handleResetObservations}
            className="text-xs font-semibold px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
          >
            Reset Sequence
          </button>
        </div>

        {/* Observation Sequence Timeline */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-700 uppercase tracking-wider">
              Quiz Observation Sequence ({hmmObservations.length})
            </span>
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-gray-500 mr-1">Add Attempt:</span>
              <button
                onClick={() => handleAddObservation(0)}
                className="px-2.5 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-semibold rounded-lg border border-rose-200"
              >
                + Incorrect
              </button>
              <button
                onClick={() => handleAddObservation(1)}
                className="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-700 text-xs font-semibold rounded-lg border border-amber-200"
              >
                + Partial
              </button>
              <button
                onClick={() => handleAddObservation(2)}
                className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-lg border border-emerald-200"
              >
                + Correct
              </button>
            </div>
          </div>

          {/* Timeline Pills */}
          {hmmResult && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2.5">
              {hmmResult.timeline?.map((step: any) => (
                <div
                  key={step.step}
                  className="p-3 bg-gray-50 border border-gray-200 rounded-xl space-y-1.5 text-xs text-center"
                >
                  <span className="text-[10px] text-gray-400 block font-mono">Attempt #{step.step}</span>
                  <span className={`inline-block px-2 py-0.5 rounded font-bold text-[11px] ${
                    step.observation_id === 2 ? 'bg-emerald-100 text-emerald-800' :
                    step.observation_id === 1 ? 'bg-amber-100 text-amber-800' :
                    'bg-rose-100 text-rose-800'
                  }`}>
                    {step.observation_name}
                  </span>
                  <div className="pt-1 border-t border-gray-200">
                    <span className="text-[10px] text-gray-400 block">Viterbi State:</span>
                    <span className="font-bold text-indigo-700 text-[11px]">
                      {step.most_likely_state}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Viterbi Summary & Caution */}
        {hmmResult && (
          <div className="space-y-3">
            <div className="p-4 bg-indigo-50/70 border border-indigo-200 rounded-xl text-xs text-indigo-950 space-y-1 leading-relaxed">
              <span className="font-bold block text-indigo-900">Optimal Hidden Sequence (Viterbi Decoding):</span>
              <div className="font-semibold text-indigo-800 flex flex-wrap items-center gap-1.5 pt-1">
                {hmmResult.viterbi_sequence?.map((state: string, idx: number) => (
                  <React.Fragment key={idx}>
                    <span className="px-2 py-0.5 bg-white rounded-md shadow-xs border border-indigo-200">
                      {state}
                    </span>
                    {idx < hmmResult.viterbi_sequence.length - 1 && <span>→</span>}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Disclaimer */}
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-xl text-[11px] text-gray-500 flex items-start gap-2">
              <Info className="w-4 h-4 text-gray-400 mt-0.5 shrink-0" />
              <span>
                <strong>Pedagogical Note:</strong> Hidden Markov Model classifications represent probabilistic likelihoods based on quiz history, intended to guide targeted practice recommendations rather than make definitive judgements about a student.
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
