import itertools
from typing import Dict, List, Any, Optional

class StudentConceptBayesianNetwork:
    """
    Exact Bayesian Network inference for Student Concept Mastery.
    Nodes:
      - PF: ProgrammingFundamentals (values: 0=Not Mastered, 1=Mastered)
      - REC: Recursion (values: 0, 1)
      - GA: GraphAlgorithms (values: 0, 1)
      - Q_PF: Quiz on Programming Fundamentals (values: 0=Fail, 1=Pass)
      - Q_REC: Quiz on Recursion (values: 0=Fail, 1=Pass)
      - Q_GA: Quiz on Graph Algorithms (values: 0=Fail, 1=Pass)
    """
    def __init__(self):
        # 1. Prior for Programming Fundamentals P(PF=1)
        self.p_pf = 0.60
        
        # 2. CPT for Recursion: P(REC=1 | PF)
        self.cpt_rec = {
            0: 0.15, # P(REC=1 | PF=0)
            1: 0.80  # P(REC=1 | PF=1)
        }
        
        # 3. CPT for Graph Algorithms: P(GA=1 | PF, REC)
        self.cpt_ga = {
            (0, 0): 0.05,
            (0, 1): 0.30,
            (1, 0): 0.40,
            (1, 1): 0.85
        }
        
        # 4. Sensor/Quiz Models:
        # P(Q_PF=Pass | PF)
        self.cpt_q_pf = {
            0: 0.15, # False positive (guessed right)
            1: 0.90  # True positive
        }
        
        # P(Q_REC=Pass | REC)
        self.cpt_q_rec = {
            0: 0.10,
            1: 0.85
        }
        
        # P(Q_GA=Pass | GA)
        self.cpt_q_ga = {
            0: 0.12,
            1: 0.88
        }

    def joint_probability(self, pf: int, rec: int, ga: int, q_pf: int, q_rec: int, q_ga: int) -> float:
        # P(PF)
        prob = self.p_pf if pf == 1 else (1.0 - self.p_pf)
        
        # P(REC | PF)
        p_rec_given_pf = self.cpt_rec[pf] if rec == 1 else (1.0 - self.cpt_rec[pf])
        prob *= p_rec_given_pf
        
        # P(GA | PF, REC)
        p_ga_given_pf_rec = self.cpt_ga[(pf, rec)] if ga == 1 else (1.0 - self.cpt_ga[(pf, rec)])
        prob *= p_ga_given_pf_rec
        
        # P(Q_PF | PF)
        p_q_pf = self.cpt_q_pf[pf] if q_pf == 1 else (1.0 - self.cpt_q_pf[pf])
        prob *= p_q_pf
        
        # P(Q_REC | REC)
        p_q_rec = self.cpt_q_rec[rec] if q_rec == 1 else (1.0 - self.cpt_q_rec[rec])
        prob *= p_q_rec
        
        # P(Q_GA | GA)
        p_q_ga = self.cpt_q_ga[ga] if q_ga == 1 else (1.0 - self.cpt_q_ga[ga])
        prob *= p_q_ga
        
        return prob

    def infer_concept_mastery(self, evidence: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculates exact posterior marginals:
        P(PF=1 | evidence), P(REC=1 | evidence), P(GA=1 | evidence)
        evidence format: {"q_pf": 1, "q_rec": 0, "q_ga": 1}
        where 1=Pass, 0=Fail.
        """
        all_vars = ["pf", "rec", "ga", "q_pf", "q_rec", "q_ga"]
        
        # Sum over all 2^6 = 64 combinations
        total_evidence_weight = 0.0
        numerator_pf = 0.0
        numerator_rec = 0.0
        numerator_ga = 0.0
        
        for pf, rec, ga, q_pf, q_rec, q_ga in itertools.product([0, 1], repeat=6):
            state = {
                "pf": pf,
                "rec": rec,
                "ga": ga,
                "q_pf": q_pf,
                "q_rec": q_rec,
                "q_ga": q_ga
            }
            
            # Check if this state matches observed evidence
            matches = True
            for k, val in evidence.items():
                if state.get(k) != val:
                    matches = False
                    break
                    
            if not matches:
                continue
                
            joint_p = self.joint_probability(pf, rec, ga, q_pf, q_rec, q_ga)
            total_evidence_weight += joint_p
            
            if pf == 1:
                numerator_pf += joint_p
            if rec == 1:
                numerator_rec += joint_p
            if ga == 1:
                numerator_ga += joint_p
                
        if total_evidence_weight == 0.0:
            posterior_pf = self.p_pf
            posterior_rec = 0.50
            posterior_ga = 0.40
        else:
            posterior_pf = numerator_pf / total_evidence_weight
            posterior_rec = numerator_rec / total_evidence_weight
            posterior_ga = numerator_ga / total_evidence_weight
            
        nodes = [
            {
                "id": "pf",
                "name": "Programming Fundamentals",
                "type": "concept",
                "prior": self.p_pf,
                "posterior": round(posterior_pf, 4),
                "parents": []
            },
            {
                "id": "rec",
                "name": "Recursion",
                "type": "concept",
                "prior": 0.54, # Marginal prior
                "posterior": round(posterior_rec, 4),
                "parents": ["pf"]
            },
            {
                "id": "ga",
                "name": "Graph Algorithms",
                "type": "concept",
                "prior": 0.47, # Marginal prior
                "posterior": round(posterior_ga, 4),
                "parents": ["pf", "rec"]
            },
            {
                "id": "q_pf",
                "name": "Quiz: Programming",
                "type": "evidence",
                "observed": evidence.get("q_pf"),
                "parents": ["pf"]
            },
            {
                "id": "q_rec",
                "name": "Quiz: Recursion",
                "type": "evidence",
                "observed": evidence.get("q_rec"),
                "parents": ["rec"]
            },
            {
                "id": "q_ga",
                "name": "Quiz: Graph Algorithms",
                "type": "evidence",
                "observed": evidence.get("q_ga"),
                "parents": ["ga"]
            }
        ]
        
        edges = [
            {"from": "pf", "to": "rec"},
            {"from": "pf", "to": "ga"},
            {"from": "rec", "to": "ga"},
            {"from": "pf", "to": "q_pf"},
            {"from": "rec", "to": "q_rec"},
            {"from": "ga", "to": "q_ga"},
        ]
        
        explanation = (
            f"Bayesian Network exact inference computed the posterior mastery probabilities given observed evidence: "
            f"Programming Fundamentals: {posterior_pf * 100:.1f}%, "
            f"Recursion: {posterior_rec * 100:.1f}%, "
            f"Graph Algorithms: {posterior_ga * 100:.1f}%. "
            f"Because parent concept mastery directly influences prerequisite understanding in the Conditional Probability Tables (CPT), "
            f"evidence propagates both forward (predictive inference) and backward (diagnostic inference) through Bayes' Theorem."
        )
        
        return {
            "evidence_provided": evidence,
            "evidence_likelihood": round(total_evidence_weight, 6),
            "posterior_probabilities": {
                "ProgrammingFundamentals": round(posterior_pf, 4),
                "Recursion": round(posterior_rec, 4),
                "GraphAlgorithms": round(posterior_ga, 4)
            },
            "nodes": nodes,
            "edges": edges,
            "explanation": explanation
        }

def run_bayesian_mastery_demo(evidence: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Default runner for the Bayesian Concept Mastery network.
    Evidence default: {"q_pf": 1, "q_rec": 0, "q_ga": 1}
    """
    bn = StudentConceptBayesianNetwork()
    ev = evidence if evidence is not None else {"q_pf": 1, "q_rec": 1, "q_ga": 0}
    return bn.infer_concept_mastery(ev)
