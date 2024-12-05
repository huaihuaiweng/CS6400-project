from flask import Blueprint, render_template, request, redirect, url_for
from .Reading_List import fetch_reading_list, remove_from_reading_list, add_to_reading_list
from .Recommendations import fetch_paper_details, reccPaper

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect(url_for("main.reading_list"))

@main_bp.route("/reading-list", methods=["GET", "POST"])
def reading_list():
    reading_list = fetch_reading_list()

    if request.method == "POST":
        selected_papers = request.form.getlist("selected_papers")
        remove_from_reading_list(selected_papers)
        return redirect(url_for("main.reading_list"))

    return render_template("reading_list.html", reading_list=reading_list)

@main_bp.route("/recommendations")
def recommendations():
    recommended_paper_ids = reccPaper()
    recommended_papers = fetch_paper_details(recommended_paper_ids)
    return render_template("recommendations.html", recommended_papers=recommended_papers)