# app.py
import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from model import rank_resumes

UPLOAD_FOLDER = "resumes"
ALLOWED_EXT = {"pdf"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", tables=None, chart_data=None)

@app.route("/upload", methods=["POST"])
def upload():
    # clear resumes folder before saving new files (optional)
    for f in os.listdir(app.config["UPLOAD_FOLDER"]):
        try:
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], f))
        except:
            pass

    files = request.files.getlist("resumes")
    saved = 0
    for file in files:
        if file and file.filename and file.filename.lower().endswith(".pdf"):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            saved += 1

    if saved == 0:
        return redirect(url_for("index"))

    # run ranking
    df = rank_resumes("job_description.txt", app.config["UPLOAD_FOLDER"])
    csv_path = "ranked_resumes.csv"
    df.to_csv(csv_path, index=False)

    # Prepare chart data
    chart_labels = df["Resume"].tolist()
    chart_scores = (df["Score"] * 100).round(2).tolist()  # convert to 0-100 scale for chart

    # Render template with table and chart data
    return render_template("index.html",
                           tables=[df.to_html(classes="data table table-striped", index=False, justify="center")],
                           chart_data={"labels": chart_labels, "scores": chart_scores},
                           report_file=csv_path)

@app.route("/download")
def download():
    path = "ranked_resumes.csv"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
