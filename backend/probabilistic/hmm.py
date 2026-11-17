import numpy as np
import time
from typing import Dict, List, Any, Optional, Tuple

class StudentProgressHMM:
    """
    Hidden Markov Model (HMM) for Student Learning Progress.
    Hidden States:
      0: Needs Practice
      1: Learning
      2: Confident
    Observations:
      0: Incorrect
      1: Partially Correct
      2: Correct
    """
    def __init__(self):
        self.state_names = ["Needs Practice", "Learning", "Confident"]
        self.obs_names = ["Incorrect", "Partially Correct", "Correct"]
        
        # Initial state probabilities pi: student usually starts needing practice or learning
        self.pi = np.array([0.60, 0.30, 0.10])
        
        # Transition probability matrix A [from_state, to_state]
        self.A = np.array([
            [0.60, 0.35, 0.05], # From Needs Practice
            [0.10, 0.65, 0.25], # From Learning
            [0.05, 0.15, 0.80]  # From Confident
        ])
        
        # Emission probability matrix B [hidden_state, observation]
        self.B = np.array([
            [0.70, 0.20, 0.10], # Needs Practice emits [Incorrect, Partial, Correct]
            [0.25, 0.45, 0.30], # Learning emits
            [0.05, 0.15, 0.80]  # Confident emits
        ])

    def forward_algorithm(self, observations: List[int]) -> Tuple[float, np.ndarray]:
        """
        Calculates forward trellis alpha_t(i) = P(o_1..o_t, q_t = S_i | model)
        Returns total observation likelihood P(O | model) and normalized posterior state probs.
        """
        T = len(observations)
        N = len(self.state_names)
        alpha = np.zeros((T, N))
        
        # Initialization
        alpha[0, :] = self.pi * self.B[:, observations[0]]
        
        # Induction
        for t in range(1, T):
            for j in range(N):
                alpha[t, j] = np.sum(alpha[t - 1, :] * self.A[:, j]) * self.B[j, observations[t]]
                
        prob_obs = float(np.sum(alpha[T - 1, :]))
        
        # Normalized posterior probabilities at each time step
        posteriors = np.zeros((T, N))
        for t in range(T):
            step_sum = np.sum(alpha[t, :])
            if step_sum > 0:
                posteriors[t, :] = alpha[t, :] / step_sum
            else:
                posteriors[t, :] = 1.0 / N
                
        return prob_obs, posteriors

    def viterbi_algorithm(self, observations: List[int]) -> Tuple[List[int], float]:
        """
        Finds the most likely sequence of hidden states using dynamic programming.
        """
        T = len(observations)
        N = len(self.state_names)
        
        viterbi_matrix = np.zeros((T, N))
        backpointer = np.zeros((T, N), dtype=int)
        
        # Initialization
        viterbi_matrix[0, :] = self.pi * self.B[:, observations[0]]
        
        # Recursion
        for t in range(1, T):
            for j in range(N):
                probs = viterbi_matrix[t - 1, :] * self.A[:, j] * self.B[j, observations[t]]
                best_prev = np.argmax(probs)
                viterbi_matrix[t, j] = probs[best_prev]
                backpointer[t, j] = best_prev
                
        # Termination & Path Reconstruction
        best_last_state = int(np.argmax(viterbi_matrix[T - 1, :]))
        best_prob = float(viterbi_matrix[T - 1, best_last_state])
        
        best_path = [best_last_state]
        for t in range(T - 1, 0, -1):
            prev_state = int(backpointer[t, best_path[-1]])
            best_path.append(prev_state)
            
        best_path.reverse()
        return best_path, best_prob

def run_hmm_analysis(observation_indices: Optional[List[int]] = None) -> Dict[str, Any]:
    """
    Runs Forward and Viterbi analysis for a student's sequence of quiz attempts.
    0: Incorrect, 1: Partially Correct, 2: Correct
    Default: [0, 0, 1, 2, 2, 2] (Progression from struggling to confident)
    """
    start_time = time.perf_counter()
    hmm = StudentProgressHMM()
    
    obs = observation_indices if observation_indices is not None else [0, 0, 1, 2, 2, 2]
    
    # Run Forward Algorithm
    obs_prob, state_posteriors = hmm.forward_algorithm(obs)
    
    # Run Viterbi Algorithm
    viterbi_state_indices, viterbi_prob = hmm.viterbi_algorithm(obs)
    viterbi_states = [hmm.state_names[idx] for idx in viterbi_state_indices]
    
    # Format timeline for visualization
    timeline = []
    for t in range(len(obs)):
        timeline.append({
            "step": t + 1,
            "observation_id": obs[t],
            "observation_name": hmm.obs_names[obs[t]],
            "most_likely_state": hmm.state_names[viterbi_state_indices[t]],
            "probabilities": {
                "NeedsPractice": round(float(state_posteriors[t, 0]), 3),
                "Learning": round(float(state_posteriors[t, 1]), 3),
                "Confident": round(float(state_posteriors[t, 2]), 3)
            }
        })
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    explanation = (
        f"Hidden Markov Model (HMM) evaluated {len(obs)} student quiz observations in {execution_time_ms:.2f} ms. "
        f"The Forward algorithm estimated posterior state probabilities across time, and the Viterbi algorithm "
        f"decoded the globally optimal hidden state sequence: {' -> '.join(viterbi_states)}. "
        f"Important: These model outputs represent probabilistic estimates based on observed quiz answers, "
        f"designed to guide tailored practice recommendations rather than definitive judgments about student capability."
    )
    
    return {
        "algorithm": "Hidden Markov Model (Forward & Viterbi Algorithms)",
        "observations_count": len(obs),
        "observations": [hmm.obs_names[o] for o in obs],
        "viterbi_sequence": viterbi_states,
        "viterbi_path_probability": round(viterbi_prob, 8),
        "total_observation_likelihood": round(obs_prob, 8),
        "timeline": timeline,
        "state_names": hmm.state_names,
        "transition_matrix": hmm.A.tolist(),
        "emission_matrix": hmm.B.tolist(),
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
