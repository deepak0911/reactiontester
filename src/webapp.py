"""Flask web application for Competitor Feature Comparison."""

import json
import logging
import threading
import uuid

from anthropic import Anthropic
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

from .competitor_finder import find_competitors
from .feature_extractor import extract_features
from .feature_comparator import compare_features
from .output_formatter import save_results

load_dotenv()

logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory store for analysis jobs (job_id -> status/results)
_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _run_analysis(job_id: str, company: str, company_url: str, top_n: int) -> None:
    """Run the full analysis pipeline in a background thread."""
    client = Anthropic()

    def _update(status: str, step: str, **kwargs):
        with _jobs_lock:
            _jobs[job_id].update({"status": status, "step": step, **kwargs})

    try:
        # Step 1: Find competitors
        _update("running", "Discovering competitors...")
        competitors_data = find_competitors(company, client)
        competitors = competitors_data.get("competitors", [])[:top_n]
        competitors_data["competitors"] = competitors
        _update("running", "Competitors found", competitors=competitors_data)

        # Step 2: Extract features
        all_companies = [{"name": company, "url": company_url}] + [
            {"name": c["name"], "url": c["url"]} for c in competitors
        ]

        all_features = []
        for i, comp in enumerate(all_companies):
            _update(
                "running",
                f"Extracting features ({i + 1}/{len(all_companies)}): {comp['name']}...",
            )
            try:
                features = extract_features(comp["name"], comp["url"], client)
            except Exception as exc:
                logger.error("Failed for %s: %s", comp["name"], exc)
                features = {"company": comp["name"], "categories": [], "error": str(exc)}
            all_features.append(features)
            _update("running", f"Extracted features for {comp['name']}", features=all_features)

        # Step 3: Compare
        _update("running", "Comparing features across all competitors...")
        comparison = compare_features(company, all_features, client)

        # Step 4: Save
        save_results(competitors_data, all_features, comparison)

        _update(
            "complete",
            "Analysis complete",
            competitors=competitors_data,
            features=all_features,
            comparison=comparison,
        )
    except Exception as exc:
        logger.error("Analysis failed: %s", exc, exc_info=True)
        _update("error", f"Error: {exc}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    company_url = data.get("company_url", "").strip()
    company_name = data.get("company_name", "").strip()
    top_n = int(data.get("top_n", 5))

    if not company_url:
        return jsonify({"error": "Company URL is required"}), 400
    if not company_name:
        return jsonify({"error": "Company name is required"}), 400

    # Normalize URL
    if not company_url.startswith(("http://", "https://")):
        company_url = "https://" + company_url

    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {"status": "queued", "step": "Starting analysis..."}

    thread = threading.Thread(
        target=_run_analysis,
        args=(job_id, company_name, company_url, top_n),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/results/<job_id>")
def results(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return render_template("index.html", error="Job not found")
    if job["status"] != "complete":
        return render_template("index.html", error="Analysis still in progress")
    return render_template(
        "results.html",
        competitors=job.get("competitors", {}),
        features=job.get("features", []),
        comparison=job.get("comparison", {}),
    )


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
