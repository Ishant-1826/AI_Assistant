# CampusMind AI – Intelligent College Student Assistant & AI Algorithm Laboratory

CampusMind AI is a comprehensive, production-grade web application tailored for computer science and engineering university students. It combines a modern **ChatGPT-like conversational assistant**, complete **voice interaction (Speech-to-Text and Text-to-Speech)**, genuine **Python implementations of core Artificial Intelligence algorithms**, and interactive visual laboratories.

---

## 🚀 Key Features

### 1. Conversational AI Student Assistant & Real-Time Web Knowledge
- **ChatGPT-Style UI**: Minimal white and light-gray surfaces, rounded message bubbles, markdown formatting, syntax-highlighted code blocks, copy and regenerate buttons.
- **Real-Time Google Search Grounding**:
  - Integrated with **Google Gemini Search Grounding** (`types.GoogleSearch`) and verified educational web search providers.
  - Automatically decides when external web information or verification is required.
  - Displays animated *"Searching the web for: '...' "* status indicator during research.
  - Extracts and renders clickable **Source Cards** (article title, domain, excerpt, verified security badge).
  - Users can also explicitly toggle the **Web Search Globe button** in the chat bar.
- **Intelligent 8-Category Question Routing**:
  1. `GENERAL_KNOWLEDGE`: Direct LLM synthesis.
  2. `EDUCATIONAL_QUESTIONS`: Structured conceptual breakdown (Simple Definition, Intuitive Explanation, Formula, Variable Breakdown, Step-by-Step Solved Example, Real-World Applications, Exam Takeaways).
  3. `CURRENT_INFORMATION`: Live web search for recent events, newest versions, and latest tech.
  4. `MATHEMATICAL_QUESTIONS`: Calculus, Linear Algebra, Laplace/Fourier transformations with KaTeX LaTeX formulas.
  5. `CODING_QUESTIONS`: Code generation, line-by-line debugging in Python, C, C++, and Java.
  6. `ALGORITHM_QUESTIONS`: Direct execution of Python search/pathfinding engines.
  7. `PUZZLE_QUESTIONS`: Genuine execution of 8-Puzzle, Wumpus World, or Hanoi solvers.
  8. `STUDY_RELATED_QUESTIONS`: Exam revision schedules, notes, and quiz generation.
- **Hinglish & Adaptive Pedagogical Modes**:
  - Supports conversational **Hinglish** explanations (e.g. *"Explain Laplace in Hinglish"*), simplified analogies, detailed derivations, exam notes, and practice problems.
- **Voice Interaction (Input & Output)**:
  - **Speech-to-Text (Voice Input)**: Leverages browser Web Speech API (`SpeechRecognition`). Shows live audio feedback, inserts transcript directly into the chat box for review/editing, and never auto-sends without confirmation.
  - **Text-to-Speech (Voice Output)**: Uses browser `SpeechSynthesis` to read AI responses aloud with customizable speech rate and voice selection.
- **SQLite Persistence**: Chat sessions and conversation history are persistently stored and manageable (rename, delete, switch).

---

### 2. AI Puzzle Solver
- **8-Puzzle Sliding Solver**:
  - Interactive 3x3 draggable/clickable tile board.
  - Mathematical solvability validator using inversion count parity check.
  - Algorithms: **A\*** (Manhattan Distance heuristic), **BFS** (optimal move count), **DFS**, **IDS**, **Hill Climbing**, and **Simulated Annealing**.
  - Animated step-by-step playback with forward, backward, pause, and speed controls.
  - Displays nodes expanded, move count, runtime, and diagnostic explanations (e.g. local optimum traps).
- **Wumpus World Cave Exploration**:
  - Interactive 4x4 grid cave with Agent, Wumpus, Pits, Gold, and sensory percepts (Breeze, Stench, Glitter).
  - **Bayesian Network Hazard Estimation**: Computes exact posterior $P(\text{Pit} \mid \text{Breezes})$ and $P(\text{Wumpus} \mid \text{Stenches})$ for every hidden cell.
  - Step-by-step exploration tracking safe, dangerous, and uncertain cells.
- **Towers of Hanoi**:
  - Visualizer with 3 pegs and adjustable disk count (3 to 6 disks).
  - **Recursive Divide-and-Conquer (DFS)** solver showing optimal $2^n - 1$ steps.
  - **BFS State-Space Search** solver demonstrating shortest-path search across configuration space.

---

### 3. Algorithm Laboratory
- **Interactive Graph Search Playground**:
  - Visual SVG graph canvas with nodes and weighted edges.
  - Compare **DFS**, **BFS**, and **Iterative Deepening Search (IDS)** side-by-side.
  - Step-by-step frontier and visited set animation.
  - Detailed comparison table showing time, nodes expanded, path length, optimality, and memory complexity.
- **Grid Pathfinding & Dynamic Replanning**:
  - 15x15 interactive grid: click or drag to draw and erase walls.
  - Random maze generator.
  - **A\* Pathfinding**: Guarantees shortest path using Manhattan heuristic.
  - **D\* Lite Dynamic Replanning**: Introduces obstacles directly on the active path and demonstrates incremental replanning without restarting search from scratch.
  - **Hill Climbing**: Demonstrates greedy steepest ascent and visualizes getting trapped in local minima or plateaus.

---

### 4. Study Planner (Simulated Annealing Engine)
- Personalized timetable generator based on student topics, difficulties, priorities, and exam deadlines.
- **Simulated Annealing Optimization**:
  - Quadratic penalty on daily capacity overload.
  - Strict deadlines preventing topics from being scheduled post-exam.
  - Workload variance smoothing to prevent student burnout.
- Displays cooling cycles, energy reduction curve, quality score, and day-by-day timetable blocks.
- Persistent saving to SQLite.

---

### 5. Probabilistic Intelligence & Learning Analytics
- **Bayesian Network for Concept Mastery**:
  - Models dependencies between Programming Fundamentals, Recursion, Graph Algorithms, and Quizzes.
  - Exact variable elimination inference updating concept mastery probabilities in real time as quiz evidence is toggled.
- **Expectation Maximization (Gaussian Mixture Models)**:
  - Unsupervised clustering of student study patterns (Study Hours vs Quiz Accuracy).
  - E-Step responsibility calculation and M-Step parameter updates.
  - Log-likelihood convergence chart.
- **Hidden Markov Model (HMM) Learning Progress Tracker**:
  - Hidden states: *Needs Practice*, *Learning*, *Confident*.
  - Observations: *Incorrect*, *Partially Correct*, *Correct*.
  - Forward Algorithm for posterior state distributions.
  - Viterbi Algorithm for decoding the most likely hidden competency sequence.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide React, Framer Motion, React Markdown |
| **Backend** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2, NumPy, SciPy |
| **Database** | SQLite3 |
| **LLM Integration** | Google Gemini API (`google-generativeai`), OpenAI API (`openai`), Custom Fallback Engine |
| **Audio APIs** | Web Speech API (`SpeechRecognition` & `SpeechSynthesis`) |

---

## 📦 Quick Start (One-Click Launch)

### 🪟 Windows (Double-Click)
Simply **double-click** `START.bat` in the project root folder.
- Automatically verifies Python 3, Node.js, and npm.
- Creates and activates the Python virtual environment (`venv`).
- Installs backend (`requirements.txt`) and frontend (`npm install`) dependencies if needed.
- Checks `.env` configuration (creates from `.env.example` if missing).
- Starts FastAPI backend (port 8000) and Vite frontend (port 5173) in separate labeled windows with live logs.
- Automatically launches your default web browser to `http://localhost:5173`.
- Pressing any key in the main launcher window cleanly terminates both servers and releases all ports.

### 🐧 Linux / macOS
```bash
chmod +x START.sh
./START.sh
```
Or use `./run.sh`.

---

## 🛠️ Manual Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. (Optional) Configure LLM Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY` or `OPENAI_API_KEY`. If left empty, CampusMind AI automatically runs using its built-in educational tutor mode.

### 4. Start the Application
Run the FastAPI backend (which serves both the API and the compiled React frontend):
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
```
http://127.0.0.1:8000
```

### 5. (Alternative) Frontend Development Mode with Hot Reloading
If actively developing frontend components:
- In Terminal 1: `uvicorn backend.main:app --port 8000`
- In Terminal 2: `cd frontend && npm run dev` (runs Vite dev server on `http://localhost:5173` with proxy to backend)

---

## 🧪 Running Unit Tests

To run the automated test suites verifying all algorithms, puzzles, probabilistic models, and API endpoints:

```bash
# Core Algorithm and Puzzle Unit Tests (11 test suites)
python backend/tests/run_tests.py

# Full FastAPI REST Endpoints & Lifecycle Integration Tests
python backend/tests/test_api.py
```

---

## 📂 Project Structure

```
project/
├── backend/
│   ├── algorithms/          # DFS, BFS, IDS, A*, D* Lite, Hill Climbing, Simulated Annealing
│   ├── puzzles/             # 8-Puzzle, Towers of Hanoi, Wumpus World
│   ├── probabilistic/       # Bayesian Network, EM GMM, Hidden Markov Model
│   ├── services/            # Study Planner (SA), Learning Analytics
│   ├── llm/                 # Tool Router, Assistant, System Prompts
│   ├── routes/              # Chat, Algorithms, Puzzles, Probabilistic, Planner APIs
│   ├── tests/               # Unit tests & API integration tests
│   ├── config.py
│   ├── database.py          # SQLite database schema & CRUD
│   └── main.py              # FastAPI application entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/      # Chat, Sidebar, Visualizers, Settings, MessageItem
│   │   ├── utils/           # Web Speech API helpers (voice.ts)
│   │   ├── App.tsx          # Root application layout
│   │   ├── main.tsx
│   │   └── types.ts
│   ├── dist/                # Production build
│   ├── package.json
│   ├── tailwind.config.js / @tailwindcss/vite
│   └── vite.config.ts
├── requirements.txt
├── .env.example
└── README.md
```

---

## 📄 License
MIT License. Built for university computer science education and intelligent student assistance.
