import os
import re
import streamlit as st
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types

# Keep the Windows console free from Hugging Face symlink notices
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "true"


# === 1. Build the Professor Vector application interface ===
st.set_page_config(
    page_title="Professor Vector | Knowledge Assistant",
    page_icon="🔎"
)

st.title("🔎 Professor Vector — Smart Study Assistant")
st.subheader("Day 1 Workshop Project")

# Let users provide their Gemini credentials without displaying the key
st.sidebar.header("AI Configuration")
gemini_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    help="Enter your API key to enable AI-generated answers."
)


# === 2. Create and initialize the academic document collection ===
@st.cache_resource
def initialize_document_store():
    # Sample notes covering database systems, computer architecture, and campus rules
    knowledge_items = [
        "Advanced DBMS: ACID properties guarantee that database transactions are processed reliably.",
        "Advanced DBMS: A Vector Database stores high-dimensional embeddings for semantic search mapping.",
        "Computer Organization (COA): Amdahl's law computes the theoretical speedup in latency of execution.",
        "Computer Organization (COA): Cache memory minimizes the average time to access data from the Main Memory.",
        "Campus Policy: The official daily student leave policy requires applying 24 hours in advance via the portal.",
        "Campus Policy: The institutional code of conduct mandates carrying physical ID cards at all times."
    ]

    # Load the sentence encoder and precompute vectors to avoid repeated work
    encoder = SentenceTransformer("all-MiniLM-L6-v2")
    knowledge_vectors = encoder.encode(knowledge_items)

    return knowledge_items, encoder, knowledge_vectors


# Reuse the initialized document collection throughout the application
knowledge_items, sentence_encoder, knowledge_vectors = (
    initialize_document_store()
)


# === 3. Retrieve relevant notes and generate a grounded response ===
def answer_from_knowledge(question, api_key):
    # Represent the incoming question in the same vector space as the notes
    question_vector = sentence_encoder.encode([question])

    # Measure how closely each stored note matches the user's question
    similarity_scores = sentence_encoder.similarity(
        question_vector,
        knowledge_vectors
    )[0].tolist()

    # Sort matching notes from most relevant to least relevant
    ranked_items = sorted(
        zip(knowledge_items, similarity_scores),
        key=lambda pair: pair[1],
        reverse=True
    )

    # Supply the two highest-ranked notes as supporting evidence
    selected_notes = [note for note, score in ranked_items[:2]]
    reference_material = "\n".join(selected_notes)

    # Define boundaries that keep the response grounded in retrieved information
    assistant_rules = (
        "You are Professor Vector, a helpful academic study assistant. "
        "Answer using ONLY the supplied reference material. "
        "If the requested information is missing, reply exactly: "
        "'I do not have the relevant information in the provided document context.'"
    )

    # Assemble the evidence and question into a single prompt
    combined_prompt = (
        f"Reference Material:\n{reference_material}\n\n"
        f"Student Question: {question}"
    )

    try:
        # Connect to Google's Gemini API with the user's credentials
        gemini_client = genai.Client(api_key=api_key)

        # Inspect the models available to the current API key
        model_catalog = list(gemini_client.models.list())
        usable_models = []

        # Ignore models intended for media, audio, or other specialized tasks
        unsupported_categories = (
            "embedding", "image", "tts", "live",
            "audio", "robotics", "computer-use"
        )

        # Select Flash models that support text content generation
        for model_info in model_catalog:
            full_name = getattr(model_info, "name", "") or ""
            supported_actions = (
                getattr(model_info, "supported_actions", []) or []
            )
            clean_name = full_name.removeprefix("models/")

            if (
                "generateContent" in supported_actions
                and "flash" in clean_name.lower()
                and not any(
                    category in clean_name.lower()
                    for category in unsupported_categories
                )
            ):
                usable_models.append(clean_name)

        # Explain the issue if no suitable model is available
        if not usable_models:
            return (
                "No compatible text-generation Flash model is available "
                "for this API key. Verify your Gemini API access and "
                "the models enabled for your account.",
                selected_notes
            )

        # Prefer the highest numbered model version discovered
        def extract_version(model_name):
            version_match = re.search(
                r"gemini-(\d+(?:\.\d+)*)",
                model_name
            )

            if version_match:
                return tuple(
                    int(part)
                    for part in version_match.group(1).split(".")
                )

            return (0,)

        usable_models.sort(key=extract_version, reverse=True)

        # Attempt generation with each compatible model until one succeeds
        generation_errors = []

        for selected_model in usable_models:
            try:
                result = gemini_client.models.generate_content(
                    model=selected_model,
                    contents=combined_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=assistant_rules,
                        temperature=0.2
                    )
                )

                # Return the generated answer alongside its supporting notes
                if result.text:
                    return result.text, selected_notes

                generation_errors.append(
                    f"{selected_model}: no text was returned"
                )

            except Exception as model_exception:
                generation_errors.append(
                    f"{selected_model}: {model_exception}"
                )

        # Report model failures when every available option has been tried
        return (
            "Unable to generate an answer with the available models. "
            "Check API permissions, quota, and the following errors:\n"
            + "\n".join(generation_errors),
            selected_notes
        )

    except Exception as api_exception:
        # Handle API initialization and model-discovery failures gracefully
        return f"❌ Gemini connection error: {api_exception}", []


# === 4. Accept questions and present the study results ===
student_question = st.text_input(
    "Enter a question about DBMS, COA, or campus policies:"
)

if st.button("Find Answer", type="primary"):
    # Validate the required inputs before starting the RAG workflow
    if not gemini_key:
        st.warning(
            "⚠️ Add your Gemini API key in the sidebar to continue."
        )

    elif not student_question.strip():
        st.warning("⚠️ Please enter a question before submitting.")

    else:
        # Display progress while relevant notes and an AI response are prepared
        with st.spinner("Searching study notes and preparing your answer..."):
            final_answer, supporting_notes = answer_from_knowledge(
                student_question,
                gemini_key
            )

        # Show the result and expose the evidence used to produce it
        if "❌ Gemini connection error" in final_answer:
            st.error(final_answer)

        else:
            st.success("### Answer")
            st.write(final_answer)

            # Allow students to inspect the notes used by the retrieval stage
            if supporting_notes:
                with st.expander("📚 Inspect Supporting Study Notes"):
                    for note_number, note_text in enumerate(
                        supporting_notes, start=1
                    ):
                        st.info(f"**Reference {note_number}:** {note_text}")