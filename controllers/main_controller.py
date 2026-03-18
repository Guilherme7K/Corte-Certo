from flask import Blueprint, render_template
from config import BARBEIRO_INFO

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html', barbeiro=BARBEIRO_INFO)
