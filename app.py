"""Flask web UI for the job search tool.

Gated by a single shared password (WEB_UI_PASSWORD) since this is meant
to be deployed at a public URL -- without it, anyone with the link could
add companies or trigger outbound scrape requests.
"""

import functools
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for

import bulk_search
import store
import targeted_search
from config import ATS_TYPES
from db import init_db

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-me")

WEB_UI_PASSWORD = os.environ.get("WEB_UI_PASSWORD", "")

init_db()


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if WEB_UI_PASSWORD and not session.get("authed"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if not WEB_UI_PASSWORD:
        return redirect(url_for("companies"))
    if request.method == "POST":
        if request.form.get("password") == WEB_UI_PASSWORD:
            session["authed"] = True
            return redirect(request.args.get("next") or url_for("companies"))
        flash("Wrong password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("authed", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    return redirect(url_for("companies"))


@app.route("/companies", methods=["GET", "POST"])
@login_required
def companies():
    if request.method == "POST":
        ok, message = store.add_company(
            request.form.get("name", ""),
            request.form.get("career_url", ""),
            request.form.get("ats_type", "unknown"),
        )
        flash(message)
        return redirect(url_for("companies"))

    return render_template("companies.html", companies=store.list_companies(), ats_types=ATS_TYPES)


@app.route("/companies/<int:company_id>/delete", methods=["POST"])
@login_required
def delete_company(company_id):
    store.delete_company(company_id)
    flash("Company removed")
    return redirect(url_for("companies"))


@app.route("/companies/<int:company_id>/toggle", methods=["POST"])
@login_required
def toggle_company(company_id):
    company = next((c for c in store.list_companies() if c["id"] == company_id), None)
    if company:
        store.set_active(company_id, not company["active"])
    return redirect(url_for("companies"))


@app.route("/bulk", methods=["GET", "POST"])
@login_required
def bulk():
    results = None
    if request.method == "POST":
        results = bulk_search.build_links(
            request.form.get("title", ""),
            request.form.get("location", ""),
            request.form.get("recency", "all"),
        )
    return render_template("bulk.html", results=results, form=request.form)


@app.route("/targeted", methods=["GET", "POST"])
@login_required
def targeted():
    results = None
    if request.method == "POST":
        recency_days_raw = request.form.get("recency_days", "").strip()
        recency_days = int(recency_days_raw) if recency_days_raw else None
        results = targeted_search.run(
            request.form.get("title", ""),
            request.form.get("location", ""),
            recency_days,
        )
    return render_template("targeted.html", results=results, form=request.form)


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5050)))
