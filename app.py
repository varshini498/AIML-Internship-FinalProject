from flask import Flask, render_template, request
import os
from ranker import process_resumes

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Job roles and descriptions
JOB_DESCRIPTIONS = {
    "Data Scientist": "Analyze data using Python, Pandas, NumPy, and build machine learning models using scikit-learn or TensorFlow. Should understand data visualization, feature engineering, and statistical analysis.",
    "Web Developer": "Design and build responsive web applications using HTML, CSS, JavaScript, and React. Experience with APIs, databases, and Node.js or Flask preferred.",
    "AI Engineer": "Develop and deploy NLP and Deep Learning models using PyTorch or TensorFlow. Should have experience with neural networks, transformers, and optimization.",
    "Backend Developer": "Develop scalable RESTful APIs using Flask or Node.js. Handle databases, authentication, and performance tuning.",
    "Data Analyst": "Perform data cleaning, analysis, and visualization using SQL, Excel, and Power BI. Communicate insights through dashboards."
}

@app.route('/')
def index():
    return render_template('index.html', jobs=JOB_DESCRIPTIONS.keys())

@app.route('/upload', methods=['POST'])
def upload_files():
    job_role = request.form.get("job_role")
    job_description = JOB_DESCRIPTIONS.get(job_role, "")
    uploaded_files = request.files.getlist("resumes")

    if not uploaded_files or not job_description.strip():
        return render_template("index.html", error="Please select a job and upload resumes.", jobs=JOB_DESCRIPTIONS.keys())

    results = process_resumes(uploaded_files, job_description)
    return render_template("results.html", results=results, job_role=job_role)

if __name__ == "__main__":
    app.run(debug=True)
