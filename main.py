import hashlib
import uuid

from flask import Flask, render_template, request, redirect, url_for, make_response

from models.baza import db
from models.topic import Topic
from models.user import User

app = Flask(__name__)

db.create_all()


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    topics = db.query(Topic).all()

    return render_template("index.html", user=user, topics=topics)


@app.route("/signup", methods=["GET", "POST"])
def singup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        repeat = request.form.get("repeat")

        if password != repeat:
            return "Hasła nie pasują do siebie!"

        print(username)
        print(password)
        print(repeat)
        user = User(username=username, password_hash=hashlib.sha256(password.encode()).hexdigest())
        user.session_token = str(uuid.uuid4())
        print(user.session_token)
        print(hashlib.sha256(password.encode()).hexdigest())
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", user.session_token)

        return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.query(User).filter_by(username=username).first()

        if not user:
            return "Błędne hasło lub nazwa użytkownika"
        else:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user.password_hash:
                user.session_token = str(uuid.uuid4())
                db.add(user)
                db.commit()

                response = make_response(redirect(url_for('index')))
                response.set_cookie("session_token", user.session_token)

                return response
            else:
                return "Błędne hasło lub nazwa użytkownika"


@app.route("/create-topic", methods=["GET", "POST"])
def topic_create():
    if request.method == "GET":
        return render_template("topic_create.html")
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()

        if not user:
            return redirect(url_for('login'))

        topic = Topic.create(title=title, text=text, author=user)
        print(topic)
        return redirect(url_for('index'))


@app.route("/topic/<topic_id>", methods=["GET"])
def topic_details(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    return render_template("topic_details.html", topic=topic, user=user)


@app.route("/topic/<topic_id>/edit", methods=["GET", " POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topic_edit.html", topic=topic)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()
        print("wszystkie jest ok #0")
        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "Nie jesteś autorem posta!!!!"
        else:
            print("wszystkie jest ok #1")
            topic.title = title
            topic.text = text
            print("wszystkie jest ok #2")
            db.add(topic)
            db.commit()
            print("wszystkie jest ok #3")

            return redirect(url_for('topic_details', topic_id=topic_id))


@app.route("/topic/<topic_id>/delete", methods=["GET", "POST"])
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))

    if request.method == "GET":
        return render_template("topic_delete.html", topic=topic)

    elif request.method == "POST":
        session_token = request.cookies.get("session_token")
        user = db.query(User).filter_by(session_token=session_token).first()

        if not user:
            return redirect(url_for('login'))
        elif topic.author.id != user.id:
            return "Nie jestes autorem"
        else:
            db.delete(topic)
            db.commit()
            return redirect(url_for('index'))

@app.route("/test")
def test():
    return render_template("xd.html")

# index.php
# index.jsp

if __name__ == '__main__':
    app.run()
