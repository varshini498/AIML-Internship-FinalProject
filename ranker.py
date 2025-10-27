import os
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF."""
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def calculate_skill_match(resume_text, job_description):
    """Calculate the skill match percentage."""
    resume_words = set(resume_text.lower().split())
    jd_words = set(job_description.lower().split())

    if not jd_words:  # avoid division by zero
        return 0.0

    common = resume_words.intersection(jd_words)
    return round(len(common) / len(jd_words) * 100, 2)

def process_resumes(uploaded_files, job_description):
    """Process resumes and return ranked results."""
    results = []
    os.makedirs("uploads", exist_ok=True)

    for file in uploaded_files:
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        text = extract_text_from_pdf(file_path)
        if not text.strip():
            results.append({
                "name": "Unknown",
                "filename": file.filename,
                "filepath": file_path,
                "score": 0.0
            })
            continue

        score = calculate_skill_match(text, job_description)

        # Extract name from the first line of resume text if possible
        lines = text.split("\n")
        name = "Unknown"
        for line in lines:
            if "name" in line.lower():
                name = line.split(":")[-1].strip()
                break

        results.append({
            "name": name or "Unknown",
            "filename": file.filename,
            "filepath": file_path,
            "score": score
        })

    # Sort results by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
