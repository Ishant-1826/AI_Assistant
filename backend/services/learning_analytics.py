from typing import Dict, List, Any, Optional
from ..probabilistic.bayesian_network import StudentConceptBayesianNetwork
from ..probabilistic.em_algorithm import run_em_gmm
from ..probabilistic.hmm import run_hmm_analysis

def get_complete_student_analytics(
    quiz_evidence: Optional[Dict[str, int]] = None,
    recent_quiz_results: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Combines Bayesian Concept Mastery, EM Study Habit Clustering,
    and HMM Learning Trajectory into a comprehensive student intelligence report.
    """
    # 1. Bayesian Concept Mastery
    evidence = quiz_evidence if quiz_evidence is not None else {"q_pf": 1, "q_rec": 1, "q_ga": 0}
    bn = StudentConceptBayesianNetwork()
    bayes_results = bn.infer_concept_mastery(evidence)
    
    # 2. EM Student Persona Clustering
    em_results = run_em_gmm(k_clusters=3, max_iters=25)
    
    # 3. HMM Progress Trajectory
    obs_indices = recent_quiz_results if recent_quiz_results is not None else [0, 0, 1, 2, 2, 2]
    hmm_results = run_hmm_analysis(obs_indices)
    
    return {
        "student_profile": {
            "name": "Alex Mercer (Demo Student)",
            "program": "Computer Science & Artificial Intelligence",
            "term": "Semester 4"
        },
        "bayesian_mastery": bayes_results,
        "em_study_persona": {
            "is_synthetic": em_results["is_synthetic_data"],
            "clusters": em_results["clusters"],
            "student_archetype": em_results["clusters"][1]["name"], # Default to Consistent Achievers
            "iterations": em_results["iterations_count"],
            "convergence": em_results["log_likelihood_convergence"]
        },
        "hmm_progress_trajectory": hmm_results
    }
