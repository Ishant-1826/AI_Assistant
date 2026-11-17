import os
import json
import re
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator

from .prompts import CAMPUSMIND_SYSTEM_PROMPT
from .tool_router import route_and_execute_tool
from .question_router import classify_question
from ..services.search_service import perform_educational_web_search, extract_gemini_grounding
from ..config import settings

def format_educational_concept_response(query: str, in_hinglish: bool = False, web_sources: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Generates rich, pedagogical responses adhering to the required structure:
    Definition, Formula, Breakdown, Step-by-Step Example, Applications, Exam Key Points.
    Supports English and Hinglish.
    """
    q_lower = query.lower()
    
    # 1. LAPLACE TRANSFORMATION
    if "laplace" in q_lower:
        if in_hinglish:
            return (
                "### 📘 Laplace Transformation (लाप्लास रूपांतरण) - Complete Guide\n\n"
                "#### 1. Simple Definition (सरल परिभाषा)\n"
                "Laplace Transform ek powerful mathematical tool hai jo time-domain signal $f(t)$ ko frequency-domain ya complex frequency domain ($s$-domain) me convert karta hai. "
                "Iska main purpose complicated differential equations ko simple algebraic equations me badalna hai taaki unhe asani se solve kiya ja sake.\n\n"
                "#### 2. Mathematical Formula (गणितीय सूत्र)\n"
                "One-sided (unilateral) Laplace Transform ka formula:\n"
                "$$\\mathcal{L}\\{f(t)\\} = F(s) = \\int_{0}^{\\infty} f(t) e^{-st} dt$$\n\n"
                "#### 3. Formula Breakdown (सूत्र का विश्लेषण)\n"
                "- **$f(t)$**: Original continuous-time signal (jahan $t \\ge 0$).\n"
                "- **$s = \\sigma + j\\omega$**: Complex frequency parameter ($s$-plane).\n"
                "- **$e^{-st}$**: Kernel of transformation (damping factor $e^{-\\sigma t}$ + oscillation $e^{-j\\omega t}$).\n"
                "- **$\\int_0^\\infty$**: Definite integral across time domain.\n\n"
                "#### 4. Step-by-Step Solved Example (हल किया गया उदाहरण)\n"
                "**Problem:** Find Laplace transform of $f(t) = e^{at}$.\n\n"
                "**Step 1:** Formula me substitute karein:\n"
                "$$F(s) = \\int_0^\\infty e^{at} e^{-st} dt = \\int_0^\\infty e^{-(s - a)t} dt$$\n\n"
                "**Step 2:** Integrate karein:\n"
                "$$F(s) = \\left[ \\frac{e^{-(s - a)t}}{-(s - a)} \\right]_0^\\infty$$\n\n"
                "**Step 3:** Limits put karein ($s > a$ assume karte hue taaki $e^{-\\infty} = 0$ ho):\n"
                "$$F(s) = 0 - \\left( \\frac{1}{-(s - a)} \\right) = \\frac{1}{s - a}$$\n\n"
                "**Result:** $\\mathcal{L}\\{e^{at}\\} = \\frac{1}{s - a}$ (Region of Convergence: $\\text{Re}(s) > a$).\n\n"
                "#### 5. Real-World Applications (वास्तविक अनुप्रयोग)\n"
                "- **Control Systems**: Transfer function $H(s) = \\frac{Y(s)}{X(s)}$ calculate karne aur system stability check karne me.\n"
                "- **Electrical Circuits**: RLC circuits me Kirchhoff's differential equations ko Ohm's law jaise algebraic equations me solve karne me.\n"
                "- **Signal Processing & Mechanical Vibrations**: Spring-mass-damper systems ke dynamic response ko analyze karne me.\n\n"
                "#### 6. Important Points to Remember for Exams (परीक्षा के लिए मुख्य बिंदु)\n"
                "- $\\mathcal{L}\\{1\\} = \\frac{1}{s}$\n"
                "- $\\mathcal{L}\\{t^n\\} = \\frac{n!}{s^{n+1}}$\n"
                "- $\\mathcal{L}\\{\\sin(\\omega t)\\} = \\frac{\\omega}{s^2 + \\omega^2}$\n"
                "- $\\mathcal{L}\\{\\cos(\\omega t)\\} = \\frac{s}{s^2 + \\omega^2}$\n"
                "- Linear property aur First Frequency Shift Property: $\\mathcal{L}\\{e^{at} f(t)\\} = F(s - a)$."
            )
        else:
            return (
                "### 📘 Laplace Transformation: Comprehensive Educational Guide\n\n"
                "#### 1. Simple Definition\n"
                "The **Laplace Transform** is an integral transform that converts a real-variable function of time $f(t)$ into a complex frequency-domain function $F(s)$. "
                "Its primary mathematical utility is converting linear ordinary differential equations into easily solvable algebraic equations.\n\n"
                "#### 2. Mathematical Definition\n"
                "The unilateral Laplace transform of a function $f(t)$ defined for $t \\ge 0$ is:\n"
                "$$\\mathcal{L}\\{f(t)\\} = F(s) = \\int_{0}^{\\infty} f(t) e^{-st} dt$$\n\n"
                "#### 3. Formula Explanation\n"
                "- **$f(t)$**: The input time-domain signal.\n"
                "- **$s = \\sigma + j\\omega$**: Complex frequency variable in the $s$-plane, where $\\sigma$ governs convergence/decay and $\\omega$ represents angular frequency.\n"
                "- **$e^{-st}$**: The kernel function that decomposes the signal into decaying exponentials and sinusoids.\n"
                "- **ROC (Region of Convergence)**: The set of points in the complex $s$-plane for which the integral converges.\n\n"
                "#### 4. Step-by-Step Solved Example\n"
                "**Task:** Compute the Laplace transform of $f(t) = e^{at}$ for $t \\ge 0$.\n\n"
                "1. **Substitute into definition:**\n"
                "   $$F(s) = \\int_0^\\infty e^{at} e^{-st} dt = \\int_0^\\infty e^{-(s - a)t} dt$$\n"
                "2. **Evaluate the improper integral:**\n"
                "   $$F(s) = \\lim_{T \\to \\infty} \\left[ \\frac{e^{-(s - a)t}}{-(s - a)} \\right]_0^T$$\n"
                "3. **Apply limits (for $\\text{Re}(s) > a$ so that $e^{-(s-a)T} \\to 0$):**\n"
                "   $$F(s) = 0 - \\left( -\\frac{1}{s - a} \\right) = \\frac{1}{s - a}$$\n\n"
                "Hence, $\\mathcal{L}\\{e^{at}\\} = \\frac{1}{s - a}$ with $\\text{Re}(s) > a$.\n\n"
                "#### 5. Real-World Engineering Applications\n"
                "- **Control Systems**: Designing PID controllers and determining closed-loop stability using poles and zeros on the $s$-plane.\n"
                "- **Electrical Circuit Analysis**: Converting inductor ($sL$) and capacitor ($\\frac{1}{sC}$) differential equations into algebraic impedance equations.\n"
                "- **Mechanical Engineering**: Analyzing damped harmonic oscillators, suspension systems, and resonance.\n\n"
                "#### 6. Important Points to Remember\n"
                "- **Linearity**: $\\mathcal{L}\\{c_1 f_1(t) + c_2 f_2(t)\\} = c_1 F_1(s) + c_2 F_2(s)$\n"
                "- **Differentiation Property**: $\\mathcal{L}\\{f'(t)\\} = s F(s) - f(0^-)$\n"
                "- **Integration Property**: $\\mathcal{L}\\left\\{\\int_0^t f(\\tau) d\\tau\\right\\} = \\frac{F(s)}{s}$\n"
                "- **Frequency Shifting**: $\\mathcal{L}\\{e^{at} f(t)\\} = F(s - a)$"
            )

    # 2. FOURIER TRANSFORMATION
    if "fourier" in q_lower:
        return (
            "### 🌊 Fourier Transformation: Comprehensive Guide\n\n"
            "#### 1. Simple Definition\n"
            "The **Fourier Transform** is a mathematical technique that decomposes any waveform or time-dependent signal into the individual sinusoidal frequencies that compose it.\n\n"
            "#### 2. Mathematical Formula\n"
            "The continuous-time Fourier transform is given by:\n"
            "$$F(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-j\\omega t} dt$$\n"
            "And its Inverse Fourier Transform is:\n"
            "$$f(t) = \\frac{1}{2\\pi} \\int_{-\\infty}^{\\infty} F(\\omega) e^{j\\omega t} d\\omega$$\n\n"
            "#### 3. Formula Explanation\n"
            "- **$f(t)$**: Signal in the continuous time domain.\n"
            "- **$\\omega = 2\\pi f$**: Angular frequency in radians/second.\n"
            "- **$e^{-j\\omega t} = \\cos(\\omega t) - j \\sin(\\omega t)$**: Euler's identity decomposing the signal into orthogonal harmonic sinusoids.\n\n"
            "#### 4. Step-by-Step Example\n"
            "**Find Fourier Transform of Rectangular Pulse:** $f(t) = 1$ for $|t| \\le \\frac{T}{2}$, and $0$ elsewhere.\n"
            "$$F(\\omega) = \\int_{-T/2}^{T/2} 1 \\cdot e^{-j\\omega t} dt = \\left[ \\frac{e^{-j\\omega t}}{-j\\omega} \\right]_{-T/2}^{T/2} = \\frac{e^{j\\omega T/2} - e^{-j\\omega T/2}}{j\\omega} = T \\cdot \\frac{\\sin(\\omega T / 2)}{\\omega T / 2} = T \\operatorname{sinc}\\left(\\frac{\\omega T}{2}\\right)$$\n\n"
            "#### 5. Real-World Applications\n"
            "- **Audio Processing & Equalization**: Separating bass, mid, and treble frequencies in music streaming.\n"
            "- **Image Compression (JPEG)**: 2D Discrete Cosine / Fourier transforms eliminate high-frequency details imperceptible to human eyes.\n"
            "- **Telecommunications**: Modulating and multiplexing cellular, WiFi, and optical fiber channels (OFDM).\n\n"
            "#### 6. Important Points to Remember\n"
            "- A sharp, narrow pulse in the time domain yields a broad frequency spectrum (Uncertainty Principle).\n"
            "- Duality: Time-domain convolution corresponds to simple multiplication in the frequency domain: $f(t) * g(t) \\iff F(\\omega) \\cdot G(\\omega)$."
        )

    # 3. EIGENVALUES AND EIGENVECTORS
    if "eigenvalue" in q_lower or "eigenvector" in q_lower:
        return (
            "### 📐 Eigenvalues and Eigenvectors: Linear Algebra Guide\n\n"
            "#### 1. Simple Definition\n"
            "An **eigenvector** of a square matrix is a non-zero vector whose direction does not change when that matrix transformation is applied—it only scales. "
            "The factor by which the eigenvector scales is its corresponding **eigenvalue** ($\\lambda$).\n\n"
            "#### 2. Mathematical Equation\n"
            "$$A \\mathbf{v} = \\lambda \\mathbf{v}$$\n"
            "Or in homogeneous form:\n"
            "$$(A - \\lambda I) \\mathbf{v} = \\mathbf{0}$$\n"
            "For non-trivial solutions ($\\mathbf{v} \\ne \\mathbf{0}$), the **characteristic equation** must hold:\n"
            "$$\\det(A - \\lambda I) = 0$$\n\n"
            "#### 3. Step-by-Step Solved Example\n"
            "**Matrix:** $A = \\begin{pmatrix} 4 & 2 \\\\ 1 & 3 \\end{pmatrix}$\n\n"
            "1. **Characteristic Equation:**\n"
            "   $$\\det(A - \\lambda I) = \\det\\begin{pmatrix} 4 - \\lambda & 2 \\\\ 1 & 3 - \\lambda \\end{pmatrix} = 0$$\n"
            "   $$(4 - \\lambda)(3 - \\lambda) - (2)(1) = \\lambda^2 - 7\\lambda + 12 - 2 = \\lambda^2 - 7\\lambda + 10 = 0$$\n"
            "2. **Factor to find Eigenvalues:**\n"
            "   $$(\\lambda - 5)(\\lambda - 2) = 0 \\implies \\lambda_1 = 5, \\quad \\lambda_2 = 2$$\n"
            "3. **Find Eigenvector for $\\lambda = 5$:**\n"
            "   $$(A - 5I) \\mathbf{v} = \\begin{pmatrix} -1 & 2 \\\\ 1 & -2 \\end{pmatrix} \\begin{pmatrix} v_1 \\\\ v_2 \\end{pmatrix} = \\begin{pmatrix} 0 \\\\ 0 \\end{pmatrix} \\implies -v_1 + 2v_2 = 0 \\implies \\mathbf{v}_1 = \\begin{pmatrix} 2 \\\\ 1 \\end{pmatrix}$$\n\n"
            "#### 4. Real-World Applications\n"
            "- **Google PageRank**: The web graph's stationary distribution is the dominant eigenvector of the hyperlink transition matrix.\n"
            "- **Principal Component Analysis (PCA)**: Data axes with maximum variance are eigenvectors of the covariance matrix.\n"
            "- **Vibration Analysis**: Eigenvalues represent natural resonant frequencies in mechanical bridges and buildings.\n\n"
            "#### 5. Key Points for Exams\n"
            "- $\\text{Trace}(A) = \\sum \\lambda_i$ (Sum of diagonal elements equals sum of eigenvalues).\n"
            "- $\\det(A) = \\prod \\lambda_i$ (Determinant equals the product of eigenvalues).\n"
            "- Symmetric matrices always have real eigenvalues and orthogonal eigenvectors."
        )

    # 4. PRINCIPAL COMPONENT ANALYSIS (PCA)
    if "pca" in q_lower or "principal component" in q_lower:
        return (
            "### 📊 Principal Component Analysis (PCA): Machine Learning Guide\n\n"
            "#### 1. Simple Definition\n"
            "**Principal Component Analysis (PCA)** is an unsupervised dimensionality reduction algorithm that projects high-dimensional data onto a lower-dimensional subspace while preserving as much data variance as possible.\n\n"
            "#### 2. Mathematical Procedure\n"
            "1. **Mean Centering**: $\\mathbf{X}_{\\text{centered}} = \\mathbf{X} - \\boldsymbol{\\mu}$\n"
            "2. **Compute Covariance Matrix**: $\\mathbf{\\Sigma} = \\frac{1}{N - 1} \\mathbf{X}_{\\text{centered}}^T \\mathbf{X}_{\\text{centered}}$\n"
            "3. **Eigendecomposition**: $\\mathbf{\\Sigma} \\mathbf{v}_i = \\lambda_i \\mathbf{v}_i$\n"
            "4. **Projection**: Select top $k$ eigenvectors $\\mathbf{W} = [\\mathbf{v}_1, \\dots, \\mathbf{v}_k]$ and project: $\\mathbf{Z} = \\mathbf{X}_{\\text{centered}} \\mathbf{W}$.\n\n"
            "#### 3. Real-World Applications\n"
            "- **Data Visualization**: Compressing 100+ feature datasets down to 2D or 3D scatter plots.\n"
            "- **Facial Recognition (Eigenfaces)**: Compressing pixel vectors into a compact linear combination of basis face patterns.\n"
            "- **Noise Reduction & Collinearity Elimination**: Eliminating correlated redundant features before training classifiers."
        )

    # 5. DBMS NORMALIZATION
    if "normalization" in q_lower or "dbms" in q_lower:
        return (
            "### 🗄️ Database Normalization: 1NF to BCNF Guide\n\n"
            "#### 1. Simple Definition\n"
            "Database Normalization is the systematic process of organizing relational database tables to minimize data redundancy and prevent insertion, update, and deletion anomalies.\n\n"
            "#### 2. Normal Forms Explained Step-by-Step\n"
            "- **1NF (First Normal Form)**: Each column must contain atomic (indivisible) values. No repeating groups or arrays.\n"
            "- **2NF (Second Normal Form)**: Must be in 1NF AND have **No Partial Functional Dependencies** (every non-prime attribute must depend on the whole candidate key, not just a part of a composite key).\n"
            "- **3NF (Third Normal Form)**: Must be in 2NF AND have **No Transitive Dependencies** ($X \\to Y$ and $Y \\to Z$ where $Z$ is non-prime is not allowed; non-prime attributes must depend only on the superkey).\n"
            "- **BCNF (Boyce-Codd Normal Form)**: For every functional dependency $X \\to Y$, $X$ must be a superkey.\n\n"
            "#### 3. Practical Example\n"
            "Consider table: `StudentCourse(StudentID, CourseID, StudentName, Instructor, Room)`\n"
            "- Candidate Key: `(StudentID, CourseID)`\n"
            "- `StudentID -> StudentName` is a partial dependency violating 2NF.\n"
            "- **Solution**: Decompose into `Student(StudentID, StudentName)` and `CourseEnrollment(StudentID, CourseID, Instructor, Room)`."
        )

    # 6. OPERATING SYSTEM SCHEDULING
    if "scheduling" in q_lower or "operating system" in q_lower or "os schedule" in q_lower:
        return (
            "### ⚙️ Operating System CPU Scheduling Algorithms\n\n"
            "#### 1. Simple Definition\n"
            "CPU Scheduling is the process by which the OS kernel's scheduler allocates CPU execution time to ready processes to maximize throughput, minimize latency, and ensure fairness.\n\n"
            "#### 2. Major Scheduling Algorithms\n"
            "1. **FCFS (First-Come, First-Served)**: Non-preemptive, simple queue. Suffers from the *Convoy Effect* where short jobs get stuck behind long I/O or compute jobs.\n"
            "2. **SJF (Shortest Job First)**: Provably optimal for minimizing average waiting time. Difficult to implement in practice because future CPU burst time is unknown.\n"
            "3. **Round Robin (RR)**: Preemptive scheduling designed for time-sharing systems. Each process receives a fixed time slice (*quantum*). If quantum is too small, context-switch overhead degrades performance.\n"
            "4. **Priority Scheduling**: Processes run based on assigned priorities. Subject to *starvation*, resolved through *aging* (gradually increasing priority of waiting processes).\n"
            "5. **Multi-Level Feedback Queue (MLFQ)**: Adaptive scheduler with multiple priority queues that dynamically adjusts priorities based on process CPU burst history."
        )

    # 7. NEWTON'S LAWS
    if "newton" in q_lower:
        return (
            "### 🍎 Newton's Three Laws of Motion: Physics Guide\n\n"
            "#### 1. First Law (Law of Inertia)\n"
            "An object remains at rest, or in uniform motion in a straight line, unless acted upon by an external net force:\n"
            "$$\\sum \\mathbf{F} = \\mathbf{0} \\implies \\frac{d\\mathbf{v}}{dt} = \\mathbf{0}$$\n\n"
            "#### 2. Second Law (Fundamental Law of Dynamics)\n"
            "The net external force on an object equals the time rate of change of its linear momentum $\\mathbf{p} = m\\mathbf{v}$:\n"
            "$$\\mathbf{F}_{\\text{net}} = \\frac{d\\mathbf{p}}{dt} = m\\mathbf{a} \\quad \\text{(for constant mass)}$$\n\n"
            "#### 3. Third Law (Action and Reaction)\n"
            "For every action force exerted by body A on body B, body B exerts an equal in magnitude and opposite in direction reaction force on body A:\n"
            "$$\\mathbf{F}_{AB} = -\\mathbf{F}_{BA}$$\n\n"
            "#### Real-World Example:\n"
            "Rocket Propulsion: High-speed exhaust gas is forced downwards (action), propelling the rocket upwards with equal momentum (reaction)."
        )

    # 8. GENERAL EDUCATIONAL / WEB ANSWER
    # If search sources were retrieved, incorporate them smoothly
    sources_text = ""
    if web_sources and len(web_sources) > 0:
        sources_text = "\n\n#### Verified Search Information:\n"
        for s in web_sources[:3]:
            sources_text += f"- **{s['title']}**: {s.get('snippet', '')}\n"

    return (
        f"### 🎓 CampusMind Educational Tutor\n\n"
        f"**Topic Inquiry:** *\"{query}\"*\n\n"
        f"#### Conceptual Overview:\n"
        f"Here is a student-friendly explanation of **{query}** designed for university coursework.\n\n"
        f"{sources_text}\n"
        f"#### Core Principles & Structure:\n"
        f"- **Primary Concept**: Examines foundational principles, definitions, and underlying mechanisms.\n"
        f"- **Analytical Representation**: Can be modeled formally using standard domain equations and logical constraints.\n"
        f"- **Practical Application**: Extensively implemented across contemporary engineering, software systems, and data science.\n\n"
        f"Feel free to ask for a specific perspective: *\"Explain simply\"*, *\"Explain in Hinglish\"*, *\"Give exam notes\"*, or *\"Provide code examples\"*!"
    )

async def stream_chat_response(
    messages: List[Dict[str, str]],
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    web_search_enabled: bool = False
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Streams assistant response chunks, performs intelligent question routing,
    executes Google Search or educational search grounding, and runs genuine Python algorithms.
    """
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "").strip()
            break
            
    if not last_user_msg:
        yield {"type": "chunk", "text": "Hello! How can I assist you with your college studies today?"}
        yield {"type": "done"}
        return
        
    # Check for Hinglish request
    in_hinglish = "hinglish" in last_user_msg.lower()
    
    # 1. Intelligent Question Classification
    category, auto_search = classify_question(last_user_msg)
    should_search = web_search_enabled or auto_search
    
    # 2. Check for Algorithm or Puzzle Execution first
    tool_name, tool_result, tool_summary = route_and_execute_tool(last_user_msg)
    if tool_name and tool_result:
        yield {
            "type": "tool",
            "tool_name": tool_name,
            "tool_data": tool_result
        }
        
    # Determine Provider & Keys
    selected_provider = provider or settings.default_llm_provider
    key_gemini = api_key if (provider == "gemini" and api_key) else (settings.gemini_api_key or os.getenv("GEMINI_API_KEY"))
    key_openai = api_key if (provider == "openai" and api_key) else (settings.openai_api_key or os.getenv("OPENAI_API_KEY"))
    
    # 3. Google Gemini with Built-in Google Search Grounding
    if (selected_provider in ("gemini", "auto")) and key_gemini:
        try:
            from google import genai
            from google.genai import types
            
            # Emit searching status if web search is active
            if should_search:
                yield {
                    "type": "search_status",
                    "status": "searching",
                    "query": last_user_msg[:60]
                }
                
            client = genai.Client(api_key=key_gemini)
            
            # Configure tools with Google Search grounding
            tools_list = []
            if should_search:
                tools_list.append(types.Tool(google_search=types.GoogleSearch()))
                
            gen_config = types.GenerateContentConfig(
                system_instruction=CAMPUSMIND_SYSTEM_PROMPT,
                tools=tools_list if tools_list else None
            )
            
            prompt_content = last_user_msg
            if tool_summary:
                prompt_content += f"\n\n[CONTEXT: Real Python Tool Execution Result]:\n{tool_summary}\nPlease explain this real result clearly."
            if in_hinglish:
                prompt_content += "\n\n[IMPORTANT: Explain in conversational, student-friendly Hinglish with technical English terms and clear LaTeX equations]."
                
            # Stream response
            response_stream = client.models.generate_content_stream(
                model=settings.model_name_gemini,
                contents=prompt_content,
                config=gen_config
            )
            
            accumulated_grounding_sources = []
            accumulated_queries = []
            
            for chunk in response_stream:
                # Check for grounding metadata in candidates
                if hasattr(chunk, 'candidates') and chunk.candidates:
                    cand = chunk.candidates[0]
                    queries, sources = extract_gemini_grounding(cand)
                    if queries and not accumulated_queries:
                        accumulated_queries = queries
                    if sources:
                        for s in sources:
                            if s not in accumulated_grounding_sources:
                                accumulated_grounding_sources.append(s)
                                
                if hasattr(chunk, 'text') and chunk.text:
                    yield {"type": "chunk", "text": chunk.text}
                    
            # Emit sources if found
            if accumulated_grounding_sources:
                yield {
                    "type": "sources",
                    "sources": accumulated_grounding_sources,
                    "queries": accumulated_queries or [last_user_msg[:60]]
                }
                
            yield {"type": "done"}
            return
        except Exception as e:
            yield {"type": "info", "text": f"(Gemini note: {str(e)[:75]}. Falling back to educational knowledge engine...)\n\n"}
            
    # 4. OpenAI or Fallback Web Search Integration
    web_sources = []
    if should_search:
        yield {
            "type": "search_status",
            "status": "searching",
            "query": last_user_msg[:60]
        }
        # Run educational web search asynchronously
        loop = asyncio.get_event_loop()
        web_sources = await loop.run_in_executor(None, perform_educational_web_search, last_user_msg, 4)
        if web_sources:
            yield {
                "type": "sources",
                "sources": web_sources,
                "queries": [last_user_msg[:60]]
            }
            
    # Try OpenAI if configured
    if (selected_provider in ("openai", "auto")) and key_openai:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=key_openai)
            
            formatted_messages = [{"role": "system", "content": CAMPUSMIND_SYSTEM_PROMPT}]
            for m in messages:
                formatted_messages.append({"role": m["role"], "content": m["content"]})
                
            context_additions = []
            if tool_summary:
                context_additions.append(f"[Real Algorithm Execution Data]:\n{tool_summary}")
            if web_sources:
                sources_str = "\n".join([f"- {s['title']} ({s['url']}): {s.get('snippet', '')}" for s in web_sources])
                context_additions.append(f"[Verified Web Search Context]:\n{sources_str}")
            if in_hinglish:
                context_additions.append("[Instruction: Explain in conversational, student-friendly Hinglish].")
                
            if context_additions:
                formatted_messages.append({
                    "role": "system",
                    "content": "\n\n".join(context_additions)
                })
                
            stream = await client.chat.completions.create(
                model=settings.model_name_openai,
                messages=formatted_messages,
                stream=True
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield {"type": "chunk", "text": delta.content}
            yield {"type": "done"}
            return
        except Exception as e:
            yield {"type": "info", "text": f"(OpenAI note: {str(e)[:75]}. Falling back to educational knowledge engine...)\n\n"}
            
    # 5. Standalone Educational Tutor Engine
    if tool_summary:
        fallback_text = (
            f"### CampusMind AI Algorithm Laboratory Result\n\n"
            f"Here are the genuine execution results from the Python engine:\n\n"
            f"```text\n{tool_summary}\n```\n\n"
            f"#### Pedagogical Breakdown:\n"
            f"- **Algorithm Mechanism**: Notice the transition order and pruning sequence determined by the search strategy.\n"
            f"- **Computational Complexity**: Observe the number of nodes expanded versus the lower bound.\n"
            f"- **Next Step**: Open the **Algorithm Laboratory** or **AI Puzzle Solver** tab to inspect the interactive step-by-step visualization!"
        )
    else:
        fallback_text = format_educational_concept_response(
            last_user_msg,
            in_hinglish=in_hinglish,
            web_sources=web_sources
        )
        
    # Append Sources and References section if sources exist and not already in text
    if web_sources and "### Sources & References" not in fallback_text:
        fallback_text += "\n\n### 🔗 Sources & References\n"
        for s in web_sources:
            fallback_text += f"- [{s['title']}]({s['url']}) *({s.get('source_name', 'web')})*\n"
            
    # Stream in natural chunk sizes
    chunk_size = 25
    for i in range(0, len(fallback_text), chunk_size):
        yield {"type": "chunk", "text": fallback_text[i:i+chunk_size]}
        await asyncio.sleep(0.01)
        
    yield {"type": "done"}
