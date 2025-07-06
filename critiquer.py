import streamlit as st
import pdfplumber
import spacy
import language_tool_python
from fuzzywuzzy import fuzz

# Load models
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

# Expected keywords (customize per job)
expected_keywords = ["Python", "SQL", "Machine Learning", "Data Analysis", "Communication"]

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def analyze_resume(text):
    doc = nlp(text)
    num_words = len([token.text for token in doc if token.is_alpha])
    num_sentences = len(list(doc.sents))

    # Grammar check
    grammar_matches = tool.check(text)
    grammar_issues = len(grammar_matches)

    # Keyword matching
    keyword_scores = {}
    for kw in expected_keywords:
        score = fuzz.partial_ratio(kw.lower(), text.lower())
        keyword_scores[kw] = score

    return num_words, num_sentences, grammar_issues, grammar_matches, keyword_scores

# Streamlit UI
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📝")
st.title("📝 AI Resume Critiquer")
st.write("Upload your resume (PDF) to get instant feedback on grammar, length, and job relevance.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        text = extract_text_from_pdf(uploaded_file)
        num_words, num_sentences, grammar_issues, grammar_matches, keyword_scores = analyze_resume(text)

        st.subheader("📊 Resume Analysis")
        st.write(f"**Word count:** {num_words}")
        st.write(f"**Sentence count:** {num_sentences}")
        st.write(f"**Grammar issues found:** {grammar_issues}")

        if grammar_issues > 0:
            with st.expander("See grammar issues"):
                for issue in grammar_matches[:5]:  # show only first 5
                    st.write(f"- {issue.message} (at position {issue.offset})")

        st.subheader("✅ Keyword Match")
        for kw, score in keyword_scores.items():
            if score > 80:
                st.success(f"{kw}: Good match ({score}%)")
            elif score > 50:
                st.warning(f"{kw}: Partial match ({score}%)")
            else:
                st.error(f"{kw}: Missing or low match ({score}%)")

    except Exception as e:
        st.error(f"Error reading PDF: {e}")
