"""AI Study Buddy — CS4680 Prompt Engineering Assignment 3.

Launch: python -m streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from ai_engine import DEFAULT_MODEL, StudyBuddyError, explain_topic, generate_quiz, grade_quiz
from sample_data import PREVIEW_QUIZ, PREVIEW_TOPIC, preview_explanation
from ollama_engine import DEFAULT_OLLAMA_MODEL, OllamaError, explain_local, quiz_local, local_models

load_dotenv()
st.set_page_config(page_title="AI Study Buddy", page_icon="🎓", layout="wide")

st.markdown(
    """<style>
        .block-container {max-width: 1080px; padding-top: 2.0rem;}
        [data-testid="stMetricValue"] {font-weight: 800;}
        .hero {background: linear-gradient(115deg, #173e78, #3867b2);
          color: white; padding: 27px 32px; border-radius: 18px; margin-bottom: 22px;}
        .hero h1 {color: white; margin: 0; font-size: 2.3rem;}
        .hero p {color: #e8f0ff; margin: 8px 0 0 0; font-size: 1.04rem;}
        .section-note {color:#667085; font-size:.88rem; margin-top:-5px;}
    </style>""",
    unsafe_allow_html=True,
)


def get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key and key != "your_openai_api_key_here":
        return key
    try:
        return str(st.secrets.get("OPENAI_API_KEY", "")).strip()
    except Exception:
        return ""


def show_error(exc: Exception) -> None:
    if isinstance(exc, OllamaError):
        st.error(str(exc))
    elif isinstance(exc, AuthenticationError):
        st.error("OpenAI API authentication failed. Check the key in your .env file.")
    elif isinstance(exc, RateLimitError):
        st.error("The API hit a rate or billing limit. Check your API account and retry.")
    elif isinstance(exc, APIConnectionError):
        st.error("Cannot reach the OpenAI API. Check your internet connection.")
    elif isinstance(exc, APIStatusError):
        st.error(f"The API returned an error (HTTP {exc.status_code}). Review model access/billing.")
    elif isinstance(exc, StudyBuddyError):
        st.error(str(exc))
    else:
        st.error(f"Something went wrong ({type(exc).__name__}). Check the terminal for details.")


def init_state() -> None:
    defaults = {
        "explanation": "", "explained_topic": "", "explained_level": "",
        "explained_language": "English", "refinement_count": 0,
        "quiz": [], "quiz_id": 0, "quiz_topic_used": "", "quiz_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()
api_key = get_api_key()
try:
    installed_models = local_models()
    ollama_available = True
except OllamaError:
    installed_models = []
    ollama_available = False

with st.sidebar:
    st.title("⚙️ App Settings")
    mode = st.radio(
        "Run mode", ["Local Ollama (FREE)", "OpenAI API (paid)", "Preview only"],
        index=0 if ollama_available else 2,
        help="Local Ollama uses AI installed on this Mac; OpenAI uses a paid cloud API; Preview shows fixed examples.",
    )
    live = mode != "Preview only"
    local = mode == "Local Ollama (FREE)"
    if local:
        if ollama_available:
            st.success("Local Ollama detected — no API key needed")
        else:
            st.error("Ollama is not running. Open the Ollama app on this Mac.")
        model_options = installed_models or [DEFAULT_OLLAMA_MODEL]
        model = st.selectbox(
            "Installed Ollama model", model_options,
            index=model_options.index(DEFAULT_OLLAMA_MODEL) if DEFAULT_OLLAMA_MODEL in model_options else 0,
        )
        if ollama_available and not installed_models:
            st.warning("No downloaded models found. In Terminal, run: ollama pull qwen3.5:9b")
    elif live:
        model = DEFAULT_MODEL
        if api_key:
            st.success("OpenAI API key found — ready for live requests")
        else:
            st.error("No OpenAI key. Add OPENAI_API_KEY to .env, or choose Local Ollama.")
    else:
        model = "Prewritten example"
        st.info("Preview: fixed examples, not live AI-generated responses.")
    language = st.selectbox("Output language", ["English", "中文"])
    st.caption(f"AI model: `{model}`")
    st.divider()
    with st.expander("🎯 Prompt Engineering Patterns"):
        st.markdown(
            "**1. Persona:** System instructions make the model a careful CS tutor.\n\n"
            "**2. Few-Shot:** Examples demonstrate the expected explanation and quiz style.\n\n"
            "**3. Iterative Refinement:** Learner feedback and a prior answer produce an improved version."
        )
    st.caption("For classroom demonstrations. Verify important facts against course materials.")

# Clear previous output on provider changes, preventing preview text from looking live.
if st.session_state.get("last_mode") != mode:
    st.session_state.explanation = ""
    st.session_state.quiz = []
    st.session_state.quiz_result = None
    st.session_state.last_mode = mode

st.markdown(
    '<div class="hero"><h1>🎓 AI Study Buddy</h1>'
    '<p>Learn complex concepts, practice with quizzes, and improve explanations using AI.</p></div>',
    unsafe_allow_html=True,
)

if not live:
    st.warning(
        "PREVIEW ONLY — this displays a fixed TCP handshake example. "
        "Switch to Local Ollama or OpenAI API for real generative AI."
    )

tab1, tab2, tab3 = st.tabs(["📘 Explain a Concept", "🧠 Practice Quiz", "🔍 How AI Works"])

with tab1:
    st.subheader("Ask the AI Tutor")
    topic = st.text_input("What do you want to learn?", value=PREVIEW_TOPIC, key="explain_topic_input")
    level = st.selectbox("Your learning level", ["Beginner", "Computer Science Student", "Advanced"], index=1)

    if st.button("✨ Explain Topic", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic.")
        elif live and not local and not api_key:
            st.error("Add an OpenAI API key or choose free Local Ollama.")
        elif not live and topic.strip().casefold() != PREVIEW_TOPIC.casefold():
            st.error("Preview only supports the fixed TCP Three-Way Handshake topic. Switch to Live AI for other topics.")
        else:
            with st.spinner("Preparing explanation..."):
                try:
                    answer = (
                        (explain_local(topic, level, language, model=model) if local else
                         explain_topic(api_key, topic, level, language, model=model))
                        if live else preview_explanation(language)
                    )
                    st.session_state.explanation = answer
                    st.session_state.explained_topic = topic
                    st.session_state.explained_level = level
                    st.session_state.explained_language = language
                    st.session_state.refinement_count = 0
                except Exception as error:
                    show_error(error)

    if st.session_state.explanation:
        st.divider()
        st.caption(f"Topic: {st.session_state.explained_topic} · Level: {st.session_state.explained_level}")
        with st.container(border=True):
            st.markdown(st.session_state.explanation)
        st.markdown("**Improve the explanation (Iterative Refinement)**")
        c1, c2, c3 = st.columns(3)
        with c1:
            simpler = st.button("🔎 Make it simpler", use_container_width=True)
        with c2:
            example = st.button("💡 Give another example", use_container_width=True)
        with c3:
            shorter = st.button("📝 Make it shorter", use_container_width=True)
        custom_feedback = st.text_input(
            "Or give custom feedback", placeholder="For example: Focus on the sequence numbers"
        )
        improve = st.button("🔄 Apply my feedback", disabled=not custom_feedback.strip())
        feedback = (
            "Explain more simply for a total beginner." if simpler else
            "Include a fresh, concrete step-by-step example." if example else
            "Rewrite as a concise summary with three key points." if shorter else
            custom_feedback.strip() if improve else ""
        )
        if feedback:
            if live and not local and not api_key:
                st.error("Add an OpenAI API key or choose free Local Ollama.")
            else:
                with st.spinner("Refining the explanation..."):
                    try:
                        revised = (
                            (
                                explain_local(
                                    st.session_state.explained_topic,
                                    st.session_state.explained_level,
                                    st.session_state.explained_language,
                                    model=model, previous=st.session_state.explanation, feedback=feedback,
                                ) if local else explain_topic(
                                    api_key, st.session_state.explained_topic,
                                    st.session_state.explained_level,
                                    st.session_state.explained_language,
                                    previous=st.session_state.explanation, feedback=feedback, model=model,
                                )
                            ) if live else preview_explanation(st.session_state.explained_language, feedback)
                        )
                        st.session_state.explanation = revised
                        st.session_state.refinement_count += 1
                        st.rerun()
                    except Exception as error:
                        show_error(error)
        st.download_button(
            "⬇️ Download study notes", data=st.session_state.explanation,
            file_name="study_buddy_notes.txt", mime="text/plain",
        )

with tab2:
    st.subheader("Generate Your Practice Quiz")
    quiz_topic = st.text_input("Quiz topic", value=PREVIEW_TOPIC, key="quiz_topic_input")
    qc1, qc2 = st.columns(2)
    with qc1:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    with qc2:
        count = st.slider("Number of questions", min_value=3, max_value=5, value=3)

    if st.button("🧠 Generate Quiz", type="primary", use_container_width=True):
        if not quiz_topic.strip():
            st.warning("Please enter a quiz topic.")
        elif live and not local and not api_key:
            st.error("Add an OpenAI API key or choose free Local Ollama.")
        elif not live and quiz_topic.strip().casefold() != PREVIEW_TOPIC.casefold():
            st.error("Preview only supports the fixed TCP Three-Way Handshake quiz. Switch to Live AI for other topics.")
        else:
            with st.spinner("Creating practice questions..."):
                try:
                    quiz_questions = (
                        (quiz_local(quiz_topic, difficulty, language, count, model=model) if local else
                         generate_quiz(api_key, quiz_topic, difficulty, language, count, model=model))
                        if live else [dict(q) for q in PREVIEW_QUIZ]
                    )
                    st.session_state.quiz = quiz_questions
                    st.session_state.quiz_topic_used = quiz_topic if live else PREVIEW_TOPIC
                    st.session_state.quiz_id += 1
                    st.session_state.quiz_result = None
                except Exception as error:
                    show_error(error)

    if st.session_state.quiz:
        st.divider()
        st.caption(f"Quiz topic: {st.session_state.quiz_topic_used}")
        with st.form(key=f"quiz_form_{st.session_state.quiz_id}"):
            answers = []
            for i, q in enumerate(st.session_state.quiz):
                st.markdown(f"**Question {i+1}. {q['question']}**")
                selected = st.radio(
                    f"Choose one answer for Question {i+1}",
                    options=range(4),
                    format_func=lambda value, opts=q["options"]: opts[value],
                    index=None,
                    key=f"question_{st.session_state.quiz_id}_{i}",
                    label_visibility="collapsed",
                )
                answers.append(selected)
                st.markdown("---")
            submitted = st.form_submit_button("✅ Submit Answers", type="primary")
            if submitted:
                if any(answer is None for answer in answers):
                    st.warning("Please answer every question before submitting.")
                else:
                    score, correct = grade_quiz(st.session_state.quiz, answers)
                    st.session_state.quiz_result = {"score": score, "correct": correct, "answers": answers}

        if st.session_state.quiz_result is not None:
            result = st.session_state.quiz_result
            total = len(st.session_state.quiz)
            st.metric("Your Score", f"{result['score']}/{total}")
            st.progress(result["score"] / total)
            for i, q in enumerate(st.session_state.quiz):
                if result["correct"][i]:
                    st.success(f"Q{i+1}: Correct — {q['options'][q['answer_index']]}")
                else:
                    st.error(
                        f"Q{i+1}: Not quite. Correct answer: "
                        f"{q['options'][q['answer_index']]}"
                    )
                st.caption(q["explanation"])

with tab3:
    st.subheader("Prompt Engineering in This App")
    st.markdown(
        "**Persona Pattern** — a system instruction sets a consistent CS-tutor role, "
        "learning tone, and accuracy guidelines.\n\n"
        "**Few-Shot Pattern** — example explanations and questions show the AI the "
        "output structure and difficulty we want.\n\n"
        "**Iterative Refinement Pattern** — a prior explanation and student feedback "
        "are used to request a revised, improved answer."
    )
    st.code("UI input → Prompt templates → Local Ollama / OpenAI API → AI output → UI", language="text")
    st.markdown(
        "**Quiz reliability:** Questions are requested as structured JSON. "
        "The Python app validates all answer keys and scores the quiz locally "
        "(rather than asking the AI to invent a score)."
    )
    st.info("Local Ollama generates real answers on this Mac without cloud API fees. OpenAI mode uses a paid API. Preview contains fixed examples and is not live AI.")

st.caption("CS4680 • AI Assistant Project MVP • Streamlit + Local Ollama (free) / OpenAI API (optional)")
