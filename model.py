# model.py
import os
import re
import spacy
import PyPDF2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

# Basic PDF text extractor
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for p in reader.pages:
                page_text = p.extract_text()
                if page_text:
                    text += page_text + " "
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text.strip()

# Preprocess text: lower, remove non-alpha except +/#, lemmatize, remove stopwords
def preprocess_text(text):
    if not text:
        return ""
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

# Extract keywords from job description (top nouns/PROPN + important tokens)
def extract_keywords(text, top_n=25):
    doc = nlp(text.lower())
    # Candidate tokens: proper nouns, nouns, and relevant words
    candidates = [token.lemma_ for token in doc if (token.pos_ in ("NOUN", "PROPN", "ADJ") and not token.is_stop and token.is_alpha)]
    freq = {}
    for w in candidates:
        freq[w] = freq.get(w, 0) + 1
    sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in sorted_kw[:top_n]]

# Get top matched skills (intersection of resume tokens vs job keywords)
def top_skills_matched(job_keywords, resume_text, top_k=5):
    resume_tokens = set(preprocess_text(resume_text).split())
    matched = [kw for kw in job_keywords if kw in resume_tokens]
    return matched[:top_k]

# Build summary line: strengths and missing top skills
def build_summary(job_keywords, resume_text):
    matched = top_skills_matched(job_keywords, resume_text, top_k=10)
    if not matched:
        return "Weak keyword overlap with the job description; resume may not match well."
    # strengths: top matched tokens
    strengths = ", ".join(matched[:5])
    # missing: keywords not matched (take top 3)
    missing = [k for k in job_keywords if k not in set(preprocess_text(resume_text).split())]
    missing = missing[:3]
    if missing:
        return f"Strengths: {strengths}. Missing keywords: {', '.join(missing)}."
    else:
        return f"Strong match on keywords: {strengths}."

# Main ranking function
def rank_resumes(job_desc_path, resume_folder):
    # read job description
    with open(job_desc_path, "r", encoding="utf-8") as f:
        job_desc = f.read()

    job_desc_clean = preprocess_text(job_desc)
    job_keywords = extract_keywords(job_desc, top_n=30)

    resume_files = []
    resume_texts = []
    for fname in os.listdir(resume_folder):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(resume_folder, fname)
            txt = extract_text_from_pdf(path)
            resume_files.append(fname)
            resume_texts.append(txt if txt else "")

    # If no resumes found, return empty DataFrame
    if not resume_files:
        return pd.DataFrame(columns=["Resume", "Score", "MatchPercent", "TopSkills", "Summary"])

    # Preprocess all text
    corpus = [job_desc_clean] + [preprocess_text(t) for t in resume_texts]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    vectors = vectorizer.fit_transform(corpus)

    # Cosine similarity: job (index 0) vs resumes (1..n)
    scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    rows = []
    for fname, raw_text, score in zip(resume_files, resume_texts, scores):
        # compute match percent roughly by number of matched keywords / job keywords
        matched = top_skills_matched(job_keywords, raw_text, top_k=len(job_keywords))
        match_percent = round((len(matched) / max(1, len(job_keywords))) * 100, 1)
        top_skills = top_skills_matched(job_keywords, raw_text, top_k=5)
        summary = build_summary(job_keywords, raw_text)
        rows.append({
            "Resume": fname,
            "Score": float(round(score, 4)),
            "MatchPercent": match_percent,
            "TopSkills": ", ".join(top_skills) if top_skills else "None",
            "Summary": summary
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["Score", "MatchPercent"], ascending=False).reset_index(drop=True)
    return df
