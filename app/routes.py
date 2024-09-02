from flask import render_template, url_for, flash, redirect, request, Blueprint
from app import db, bcrypt
from app.models import User, Article
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from app.news_aggregator import fetch_and_store_articles, feeds, keywords
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import Text

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/news_feed", methods=['GET', 'POST'])
@login_required
def news_feed():
    selected_feeds = []
    selected_keywords = []

    if request.method == 'POST':
        # Capture the selected feeds and keywords from the form
        selected_feeds = request.form.getlist('feed')
        selected_keywords = request.form.getlist('keyword')

        # Start filtering the articles
        articles = Article.query

        if selected_feeds:
            articles = articles.filter(Article.feed_url.in_(selected_feeds))

        if selected_keywords:
            # Correctly filter with overlap using Text type casting
            articles = articles.filter(
                Article.keywords.overlap(cast(selected_keywords, ARRAY(Text)))
            )

        articles = articles.order_by(Article.published_at.desc()).all()

    else:
        articles = Article.query.order_by(Article.published_at.desc()).all()

    # Pass selected feeds and keywords back to the template
    return render_template(
        'news_feed.html',
        articles=articles,
        feeds=feeds,
        keywords=keywords,
        selected_feeds=selected_feeds,
        selected_keywords=selected_keywords
    )

@main.route("/fetch_articles")
@login_required
def fetch_articles():
    fetch_and_store_articles()
    flash('Articles have been fetched successfully!', 'success')
    return redirect(url_for('main.news_feed'))
