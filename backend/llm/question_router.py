import re
from typing import Dict, Any, Tuple

CATEGORIES = [
    "GENERAL_KNOWLEDGE",
    "EDUCATIONAL_QUESTIONS",
    "CURRENT_INFORMATION",
    "MATHEMATICAL_QUESTIONS",
    "CODING_QUESTIONS",
    "ALGORITHM_QUESTIONS",
    "PUZZLE_QUESTIONS",
    "STUDY_RELATED_QUESTIONS"
]

def classify_question(message: str) -> Tuple[str, bool]:
    """
    Classifies user message into one of the 8 educational categories
    and returns: (category_name, should_search_web)
    """
    msg_lower = message.lower().strip()
    
    # 1. PUZZLE_QUESTIONS
    if any(k in msg_lower for k in ["8 puzzle", "8-puzzle", "wumpus", "towers of hanoi", "tower of hanoi", "sliding puzzle"]):
        return "PUZZLE_QUESTIONS", False
        
    # 2. ALGORITHM_QUESTIONS
    if any(k in msg_lower for k in [
        "bfs", "dfs", "dijkstra", "a* path", "astar", "d* lite", "hill climbing", 
        "iterative deepening", "quicksort", "mergesort", "binary search", "graph traversal"
    ]) and any(w in msg_lower for w in ["run", "solve", "execute", "path", "find", "step", "visualize"]):
        return "ALGORITHM_QUESTIONS", False
        
    # 3. STUDY_RELATED_QUESTIONS
    if any(k in msg_lower for k in [
        "study plan", "study timetable", "revision plan", "schedule my exam", 
        "exam notes", "short notes", "generate practice questions", "quiz me"
    ]):
        return "STUDY_RELATED_QUESTIONS", False
        
    # 4. CURRENT_INFORMATION (News, latest versions, recent AI events)
    if any(k in msg_lower for k in [
        "latest", "recent", "current", "newest", "today", "now", "2025", "2026",
        "released", "latest version of", "what is the latest"
    ]):
        return "CURRENT_INFORMATION", True
        
    # 5. CODING_QUESTIONS
    if any(k in msg_lower for k in [
        "write a program", "write code", "in python", "in c++", "in java", "in c",
        "debug this", "syntax error", "implement a function", "code snippet"
    ]):
        return "CODING_QUESTIONS", False
        
    # 6. MATHEMATICAL_QUESTIONS
    if any(k in msg_lower for k in [
        "laplace", "fourier", "eigenvalue", "eigenvector", "derivative", "integral",
        "matrix", "determinant", "calculate", "solve equation", "bayes theorem", "probability"
    ]):
        # Educational math: web search helps verify complex tables or definitions
        return "MATHEMATICAL_QUESTIONS", True
        
    # 7. EDUCATIONAL_QUESTIONS (General science, engineering, CS theory)
    if any(k in msg_lower for k in [
        "what is", "explain", "how does", "difference between", "define", "principles of",
        "newton's laws", "normalization in dbms", "operating system scheduling", "pca",
        "neural network", "transformer", "in hinglish", "explain simply"
    ]):
        return "EDUCATIONAL_QUESTIONS", True
        
    # 8. GENERAL_KNOWLEDGE
    return "GENERAL_KNOWLEDGE", False
