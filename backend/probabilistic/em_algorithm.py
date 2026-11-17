import numpy as np
import time
from typing import Dict, List, Any, Optional

def generate_synthetic_student_data(num_samples: int = 150) -> np.ndarray:
    """
    Generates synthetic 2D student learning pattern data:
    Feature 1: Weekly Study Hours (range: 2 to 25 hours)
    Feature 2: Quiz Accuracy Percentage (range: 40% to 100%)
    Generates 3 synthetic student archetypes.
    """
    np.random.seed(42)
    # Cluster 1: Light Study / Developing Students
    c1 = np.random.multivariate_normal(
        mean=[5.0, 52.0],
        cov=[[3.0, 1.2], [1.2, 18.0]],
        size=int(num_samples * 0.3)
    )
    
    # Cluster 2: Moderate Study / Consistent Achievers
    c2 = np.random.multivariate_normal(
        mean=[12.0, 76.0],
        cov=[[4.0, 3.5], [3.5, 22.0]],
        size=int(num_samples * 0.4)
    )
    
    # Cluster 3: Intensive Study / Mastery Students
    c3 = np.random.multivariate_normal(
        mean=[20.0, 92.0],
        cov=[[3.5, 2.0], [2.0, 12.0]],
        size=int(num_samples * 0.3)
    )
    
    data = np.vstack([c1, c2, c3])
    # Clip to realistic ranges
    data[:, 0] = np.clip(data[:, 0], 1.0, 30.0)
    data[:, 1] = np.clip(data[:, 1], 30.0, 100.0)
    return data

def gaussian_pdf_multivariate(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """Computes multivariate Gaussian density for array of points."""
    d = len(mean)
    det = np.linalg.det(cov)
    # Add regularizer if singular
    if det <= 1e-9:
        cov = cov + np.eye(d) * 1e-4
        det = np.linalg.det(cov)
        
    inv = np.linalg.inv(cov)
    diff = x - mean
    exponent = -0.5 * np.sum(diff @ inv * diff, axis=1)
    norm_const = 1.0 / np.sqrt(((2 * np.pi) ** d) * det)
    return np.maximum(norm_const * np.exp(exponent), 1e-12)

def run_em_gmm(
    k_clusters: int = 3,
    max_iters: int = 35,
    tolerance: float = 1e-4,
    custom_data: Optional[List[List[float]]] = None
) -> Dict[str, Any]:
    """
    Runs the Expectation-Maximization algorithm for Gaussian Mixture Models on student data.
    """
    start_time = time.perf_counter()
    
    if custom_data and len(custom_data) > 5:
        data = np.array(custom_data, dtype=float)
        is_synthetic = False
    else:
        data = generate_synthetic_student_data(150)
        is_synthetic = True
        
    n_samples, n_features = data.shape
    
    # Initialize parameters
    np.random.seed(42)
    # Choose random points as initial means
    random_idx = np.random.choice(n_samples, k_clusters, replace=False)
    means = data[random_idx].copy()
    covariances = [np.cov(data, rowvar=False) for _ in range(k_clusters)]
    weights = np.ones(k_clusters) / k_clusters
    
    log_likelihood_history = []
    iteration_history = []
    
    for it in range(max_iters):
        # --- E-STEP: Compute Responsibilities ---
        # gamma matrix shape: (n_samples, k_clusters)
        pdf_matrix = np.zeros((n_samples, k_clusters))
        for k in range(k_clusters):
            pdf_matrix[:, k] = weights[k] * gaussian_pdf_multivariate(data, means[k], covariances[k])
            
        sum_pdf = np.sum(pdf_matrix, axis=1, keepdims=True)
        # Avoid division by zero
        sum_pdf = np.maximum(sum_pdf, 1e-12)
        gamma = pdf_matrix / sum_pdf
        
        # Calculate log-likelihood
        current_ll = float(np.sum(np.log(sum_pdf)))
        log_likelihood_history.append(round(current_ll, 3))
        
        iteration_history.append({
            "iteration": it + 1,
            "log_likelihood": round(current_ll, 3),
            "means": [[round(m[0], 2), round(m[1], 2)] for m in means],
            "weights": [round(float(w), 3) for w in weights]
        })
        
        # Check convergence
        if it > 0 and abs(log_likelihood_history[-1] - log_likelihood_history[-2]) < tolerance:
            break
            
        # --- M-STEP: Update Parameters ---
        n_k = np.sum(gamma, axis=0) # Effective count per cluster
        weights = n_k / n_samples
        
        for k in range(k_clusters):
            # Update mean
            means[k] = np.sum(gamma[:, k:k+1] * data, axis=0) / max(n_k[k], 1e-9)
            # Update covariance
            diff = data - means[k]
            cov = (gamma[:, k:k+1] * diff).T @ diff / max(n_k[k], 1e-9)
            # Regularize to guarantee positive definiteness
            cov += np.eye(n_features) * 1e-3
            covariances[k] = cov
            
    # Final cluster assignments
    cluster_assignments = int_labels = np.argmax(gamma, axis=1)
    
    archetype_names = ["Needs Practice & Support", "Consistent Achievers", "High-Mastery Grinders"]
    
    clusters_info = []
    for k in range(k_clusters):
        count = int(np.sum(int_labels == k))
        name = archetype_names[k % len(archetype_names)]
        clusters_info.append({
            "cluster_id": k,
            "name": name,
            "weight": round(float(weights[k]), 3),
            "mean_study_hours": round(float(means[k][0]), 2),
            "mean_quiz_accuracy": round(float(means[k][1]), 2),
            "std_study_hours": round(float(np.sqrt(covariances[k][0, 0])), 2),
            "std_quiz_accuracy": round(float(np.sqrt(covariances[k][1, 1])), 2),
            "student_count": count
        })
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    # Format sample data points for visualization
    data_points = []
    for i in range(min(n_samples, 120)):
        data_points.append({
            "study_hours": round(float(data[i, 0]), 2),
            "quiz_accuracy": round(float(data[i, 1]), 2),
            "cluster": int(int_labels[i]),
            "responsibility": [round(float(gamma[i, k]), 2) for k in range(k_clusters)]
        })
        
    explanation = (
        f"Expectation Maximization (EM) converged in {len(log_likelihood_history)} iterations ({execution_time_ms:.2f} ms). "
        f"The algorithm fitted a {k_clusters}-component Gaussian Mixture Model (GMM) to student learning patterns without supervision. "
        f"In the E-step, soft responsibilities (posterior membership probabilities) were estimated. "
        f"In the M-step, cluster weights, means, and covariances were re-estimated to maximize the expected log-likelihood."
    )
    
    return {
        "algorithm": "Expectation-Maximization (Gaussian Mixture Model)",
        "is_synthetic_data": is_synthetic,
        "k_clusters": k_clusters,
        "iterations_count": len(log_likelihood_history),
        "log_likelihood_convergence": log_likelihood_history,
        "clusters": clusters_info,
        "points": data_points,
        "execution_time_ms": round(execution_time_ms, 3),
        "explanation": explanation
    }
