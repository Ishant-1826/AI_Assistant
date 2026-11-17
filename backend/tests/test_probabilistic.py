import pytest
from backend.probabilistic.bayesian_network import StudentConceptBayesianNetwork
from backend.probabilistic.em_algorithm import run_em_gmm
from backend.probabilistic.hmm import run_hmm_analysis
from backend.services.study_planner import generate_study_schedule_sa

def test_bayesian_network():
    bn = StudentConceptBayesianNetwork()
    res = bn.infer_concept_mastery({"q_pf": 1, "q_rec": 1, "q_ga": 1})
    probs = res["posterior_probabilities"]
    # With all quizzes passed, mastery probabilities should be high
    assert probs["ProgrammingFundamentals"] > 0.8
    assert probs["Recursion"] > 0.7
    assert probs["GraphAlgorithms"] > 0.6

def test_em_algorithm_gmm():
    res = run_em_gmm(k_clusters=3, max_iters=20)
    assert res["iterations_count"] > 1
    assert len(res["clusters"]) == 3
    # Check log likelihood is increasing/converging
    ll = res["log_likelihood_convergence"]
    assert ll[-1] >= ll[0]

def test_hmm_viterbi():
    obs = [0, 0, 1, 2, 2] # Incorrect, Incorrect, Partial, Correct, Correct
    res = run_hmm_analysis(obs)
    assert len(res["viterbi_sequence"]) == 5
    assert res["viterbi_sequence"][0] == "Needs Practice"
    assert res["viterbi_sequence"][-1] == "Confident"

def test_study_planner_sa():
    topics = [
        {"id": "1", "subject": "CS", "title": "Algorithms", "estimated_hours": 3.0, "difficulty": 4, "priority": 5, "exam_day": 3},
        {"id": "2", "subject": "Math", "title": "Calculus", "estimated_hours": 2.0, "difficulty": 3, "priority": 4, "exam_day": 5}
    ]
    res = generate_study_schedule_sa(topics, daily_available_hours=4.0, total_days=5)
    assert res["status"] == "success"
    assert len(res["timetable"]) == 5
