import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.llm.question_router import classify_question
from backend.services.search_service import perform_educational_web_search, extract_gemini_grounding
from backend.llm.assistant import format_educational_concept_response

class TestQuestionRouterAndSearch(unittest.TestCase):
    def test_question_routing_categories(self):
        # 1. Educational Questions
        cat1, search1 = classify_question("Explain Newton's laws of motion")
        self.assertEqual(cat1, "EDUCATIONAL_QUESTIONS")
        self.assertTrue(search1)

        # 2. Math Questions
        cat2, search2 = classify_question("What is Laplace Transformation?")
        self.assertEqual(cat2, "MATHEMATICAL_QUESTIONS")
        self.assertTrue(search2)

        # 3. Current Info
        cat3, search3 = classify_question("What is the latest version of Python in 2026?")
        self.assertEqual(cat3, "CURRENT_INFORMATION")
        self.assertTrue(search3)

        # 4. Puzzle Questions
        cat4, search4 = classify_question("Solve this 8 puzzle with A*")
        self.assertEqual(cat4, "PUZZLE_QUESTIONS")
        self.assertFalse(search4)

        # 5. Algorithm Questions
        cat5, search5 = classify_question("Find shortest path using BFS on graph")
        self.assertEqual(cat5, "ALGORITHM_QUESTIONS")
        self.assertFalse(search5)

        # 6. Coding Questions
        cat6, search6 = classify_question("Write a program in Python for quicksort")
        self.assertEqual(cat6, "CODING_QUESTIONS")
        self.assertFalse(search6)

        # 7. Study Related
        cat7, search7 = classify_question("Create a study timetable for my revision")
        self.assertEqual(cat7, "STUDY_RELATED_QUESTIONS")
        self.assertFalse(search7)

    def test_educational_response_structure(self):
        res = format_educational_concept_response("What is Laplace Transformation?")
        self.assertIn("Simple Definition", res)
        self.assertIn("Mathematical Definition", res)
        self.assertIn("Step-by-Step Solved Example", res)
        self.assertIn("Real-World Engineering Applications", res)
        self.assertIn("Important Points to Remember", res)

    def test_hinglish_response(self):
        res = format_educational_concept_response("What is Laplace Transformation?", in_hinglish=True)
        self.assertIn("लाप्लास रूपांतरण", res)
        self.assertIn("सरल परिभाषा", res)
        self.assertIn("differential equations", res)

    def test_math_eigenvalues_response(self):
        res = format_educational_concept_response("Explain eigenvalues and eigenvectors")
        self.assertIn("A \\mathbf{v} = \\lambda \\mathbf{v}", res)
        self.assertIn("Characteristic Equation", res)

    def test_web_search_execution(self):
        sources = perform_educational_web_search("Laplace transformation", max_results=3)
        self.assertIsInstance(sources, list)
        if len(sources) > 0:
            s = sources[0]
            self.assertIn("title", s)
            self.assertIn("url", s)
            self.assertIn("source_name", s)

if __name__ == "__main__":
    unittest.main(verbosity=2)
