import React, { useState, useEffect } from 'react';
import { Calendar, Plus, Trash2, Zap, Clock, CheckCircle, BarChart, Bookmark, Sparkles } from 'lucide-react';

interface TopicItem {
  id: string;
  subject: string;
  title: string;
  estimated_hours: number;
  difficulty: number;
  priority: number;
  exam_day: number;
}

const DEFAULT_TOPICS: TopicItem[] = [
  { id: '1', subject: 'Artificial Intelligence', title: 'A* & Heuristic Search', estimated_hours: 3.0, difficulty: 4, priority: 5, exam_day: 4 },
  { id: '2', subject: 'Artificial Intelligence', title: 'Bayesian Networks & HMMs', estimated_hours: 3.5, difficulty: 5, priority: 5, exam_day: 4 },
  { id: '3', subject: 'Mathematics', title: 'Linear Algebra & Matrices', estimated_hours: 2.5, difficulty: 3, priority: 4, exam_day: 6 },
  { id: '4', subject: 'Computer Systems', title: 'Virtual Memory & Paging', estimated_hours: 2.0, difficulty: 3, priority: 3, exam_day: 7 },
  { id: '5', subject: 'Databases', title: 'B-Trees & Indexing', estimated_hours: 2.0, difficulty: 3, priority: 3, exam_day: 7 },
  { id: '6', subject: 'Algorithms', title: 'Dynamic Programming Patterns', estimated_hours: 3.0, difficulty: 4, priority: 4, exam_day: 5 },
];

export const StudyPlannerView: React.FC = () => {
  const [topics, setTopics] = useState<TopicItem[]>(DEFAULT_TOPICS);
  const [dailyHours, setDailyHours] = useState<number>(4.0);
  const [totalDays, setTotalDays] = useState<number>(7);
  const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
  const [planResult, setPlanResult] = useState<any>(null);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  // New topic form state
  const [newSubject, setNewSubject] = useState<string>('AI');
  const [newTitle, setNewTitle] = useState<string>('');
  const [newHours, setNewHours] = useState<number>(2.0);
  const [newDifficulty, setNewDifficulty] = useState<number>(3);
  const [newPriority, setNewPriority] = useState<number>(4);
  const [newExamDay, setNewExamDay] = useState<number>(5);

  const handleAddTopic = () => {
    if (!newTitle.trim()) return;
    const newTopic: TopicItem = {
      id: String(Date.now()),
      subject: newSubject,
      title: newTitle.trim(),
      estimated_hours: Number(newHours),
      difficulty: Number(newDifficulty),
      priority: Number(newPriority),
      exam_day: Number(newExamDay)
    };
    setTopics([...topics, newTopic]);
    setNewTitle('');
  };

  const handleRemoveTopic = (id: string) => {
    setTopics(topics.filter(t => t.id !== id));
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setSaveSuccess(false);
    try {
      const res = await fetch('/api/planner/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topics: topics,
          daily_available_hours: dailyHours,
          total_days: totalDays
        })
      });
      const data = await res.json();
      setPlanResult(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleSavePlan = async () => {
    if (!planResult) return;
    try {
      await fetch('/api/planner/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `Study Plan (${totalDays} Days, ${dailyHours} hrs/day)`,
          plan_data: planResult
        })
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    handleOptimize();
  }, []);

  return (
    <div className="p-4 sm:p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-blue-600" />
            AI Study Planner & Simulated Annealing Scheduler
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Balancing exam deadlines, cognitive fatigue, and topic difficulty using Simulated Annealing optimization.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleOptimize}
            disabled={isOptimizing}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-xl shadow-sm transition flex items-center gap-2"
          >
            <Zap className="w-4 h-4" />
            {isOptimizing ? 'Annealing Schedule...' : 'Optimize Schedule'}
          </button>

          {planResult && (
            <button
              onClick={handleSavePlan}
              className="px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-semibold rounded-xl transition flex items-center gap-1.5"
            >
              <Bookmark className="w-4 h-4" />
              {saveSuccess ? 'Saved to DB!' : 'Save Plan'}
            </button>
          )}
        </div>
      </div>

      {/* Configuration & Topic Management */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Topics List & Form */}
        <div className="lg:col-span-5 bg-white rounded-2xl shadow-sm border border-gray-200 p-5 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-gray-100">
            <h3 className="text-sm font-bold text-gray-800">
              Exam Topics ({topics.length})
            </h3>
            <span className="text-xs text-gray-500">
              Total: {topics.reduce((sum, t) => sum + t.estimated_hours, 0)} hours
            </span>
          </div>

          {/* Add New Topic Row */}
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-200 space-y-2.5 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                placeholder="Subject (e.g. AI, Math)"
                value={newSubject}
                onChange={(e) => setNewSubject(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none"
              />
              <input
                type="text"
                placeholder="Topic Title"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-gray-300 rounded-lg text-gray-800 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-4 gap-2">
              <div>
                <label className="text-[10px] text-gray-500 block">Hours</label>
                <input
                  type="number"
                  step="0.5"
                  min="0.5"
                  max="10"
                  value={newHours}
                  onChange={(e) => setNewHours(Number(e.target.value))}
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded-lg text-center"
                />
              </div>

              <div>
                <label className="text-[10px] text-gray-500 block">Diff (1-5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={newDifficulty}
                  onChange={(e) => setNewDifficulty(Number(e.target.value))}
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded-lg text-center"
                />
              </div>

              <div>
                <label className="text-[10px] text-gray-500 block">Prio (1-5)</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={newPriority}
                  onChange={(e) => setNewPriority(Number(e.target.value))}
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded-lg text-center"
                />
              </div>

              <div>
                <label className="text-[10px] text-gray-500 block">Exam Day</label>
                <input
                  type="number"
                  min="1"
                  max={totalDays}
                  value={newExamDay}
                  onChange={(e) => setNewExamDay(Number(e.target.value))}
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded-lg text-center font-bold text-rose-600"
                />
              </div>
            </div>

            <button
              onClick={handleAddTopic}
              className="w-full py-1.5 bg-gray-900 hover:bg-black text-white rounded-lg font-medium transition flex items-center justify-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add Topic
            </button>
          </div>

          {/* Topic Cards List */}
          <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
            {topics.map(t => (
              <div
                key={t.id}
                className="p-3 bg-white border border-gray-200 rounded-xl flex items-center justify-between text-xs hover:border-gray-300 transition shadow-xs"
              >
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-gray-900">{t.title}</span>
                    <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-bold">
                      {t.subject}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500 text-[11px] mt-1">
                    <span>{t.estimated_hours} hrs</span>
                    <span>•</span>
                    <span>Diff: {t.difficulty}/5</span>
                    <span>•</span>
                    <span className="text-rose-600 font-semibold">Exam: Day {t.exam_day}</span>
                  </div>
                </div>

                <button
                  onClick={() => handleRemoveTopic(t.id)}
                  className="p-1.5 text-gray-400 hover:text-red-600 transition"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>

          {/* Daily Capacity Slider */}
          <div className="pt-2 border-t border-gray-100 space-y-1.5 text-xs">
            <div className="flex justify-between font-semibold text-gray-700">
              <span>Max Daily Study Hours:</span>
              <span className="text-blue-600 font-bold">{dailyHours} hrs / day</span>
            </div>
            <input
              type="range"
              min="2"
              max="8"
              step="0.5"
              value={dailyHours}
              onChange={(e) => setDailyHours(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
            />
          </div>
        </div>

        {/* Right: Simulated Annealing Optimized Timetable */}
        <div className="lg:col-span-7 space-y-5">
          {planResult && (
            <>
              {/* SA Optimization Metrics Badge */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-4 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
                    Simulated Annealing Score
                  </span>
                  <div className="text-2xl font-black text-blue-900">
                    {planResult.quality_score}% Quality
                  </div>
                  <p className="text-xs text-blue-700 mt-0.5">
                    Energy reduced from {planResult.initial_energy} to {planResult.final_energy} ({planResult.iterations} cycles)
                  </p>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-white shadow-sm border border-blue-200 flex items-center justify-center text-blue-600">
                  <Sparkles className="w-6 h-6" />
                </div>
              </div>

              {/* Day-by-Day Timetable Grid */}
              <div className="space-y-3">
                {planResult.timetable?.map((day: any) => (
                  <div
                    key={day.day}
                    className="bg-white rounded-xl border border-gray-200 p-3.5 shadow-xs space-y-2.5"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-900">{day.label}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          day.utilization_pct > 100
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-emerald-50 text-emerald-700'
                        }`}>
                          {day.total_hours} / {day.capacity_hours} hrs ({day.utilization_pct}%)
                        </span>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className={`h-1.5 rounded-full transition-all duration-300 ${
                          day.utilization_pct > 100 ? 'bg-rose-500' : 'bg-blue-600'
                        }`}
                        style={{ width: `${Math.min(100, day.utilization_pct)}%` }}
                      />
                    </div>

                    {/* Sessions inside this day */}
                    <div className="flex flex-wrap gap-2 pt-1">
                      {day.sessions.length > 0 ? (
                        day.sessions.map((sess: any, sIdx: number) => (
                          <div
                            key={sIdx}
                            className="bg-gray-50 border border-gray-200 px-2.5 py-1.5 rounded-lg text-xs flex items-center gap-2"
                          >
                            <span className="font-semibold text-gray-800">{sess.title}</span>
                            <span className="text-[10px] text-gray-500">({sess.duration_hours}h)</span>
                            <span className="text-[10px] px-1 bg-white border border-gray-200 rounded text-gray-600">
                              D:{sess.difficulty}
                            </span>
                          </div>
                        ))
                      ) : (
                        <span className="text-xs text-gray-400 italic">Rest / Buffer Day</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* SA Optimization Explanation */}
              <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-xs text-gray-600 leading-relaxed">
                <span className="font-bold text-gray-800 block mb-1">Why this schedule was chosen:</span>
                {planResult.explanation}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
