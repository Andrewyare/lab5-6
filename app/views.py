from flask import  render_template, request, redirect, session, url_for, flash 
from app import app, db
from user_agent import generate_user_agent
from datetime import datetime
import os, logging
from app.form import LoginForm
from app.models import Contacts

app.config['SECRET_KEY'] = 'super_secret_key'

user = generate_user_agent()
now = datetime.now()

time = now.strftime("%H:%M")

os = os.name

menu = ["Flask", "Is", "Great"]
text = 'Some quick example text to build on the card title and make up the bulk of the card`s content.'

@app.route('/')
def index():
	return render_template("index.html", title = "Flask",text = text, time = time,os=os) 

@app.route('/home')
def home():
	return render_template("index.html", title = "Flask",text = text, time = time,os=os) 

@app.route('/about')   
def about():
	return render_template('about.html',menu = menu,user = user,time = time,os=os)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = LoginForm()
    main = logging.getLogger('main')
    main.setLevel(logging.DEBUG)
    handler = logging.FileHandler('log')
    format = logging.Formatter('%(asctime)s  %(name)s %(levelname)s: %(message)s')
    handler.setFormatter(format)
    if form.validate_on_submit():
        session['username'] = form.name.data
        session['email'] = form.email.data
        save_to_db(form)
        flash("Data sent successfully: " + session.get('username') + ' ' + session.get('email'), category = 'success')
        return redirect(url_for("contact"))

    elif request.method == 'POST':
        flash("Validation failed", category = 'warning')
        main.addHandler(handler)
        main.error(form.name.data + " " + form.email.data + " " + form.phone.data + " " + form.subject.data + " " + form.message.data)

    if(session.get('username') == None):
        return render_template('contact.html', form=form, username="Guest")
    else :
        form.name.data = session.get('username')
        form.email.data = session.get('email')
        return render_template('contact.html', form=form, username=session.get('username'))


@app.route('/database')
def database() :
    contacts = Contacts.query.all()
    return render_template('database.html', contacts=contacts)

@app.route('/database/delete/<id>')
def delete_by_id(id):
    data = Contacts.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("database"))

@app.context_processor
def inject_user():
    date = time
    return dict(user_info=request.headers.get('User-Agent'), date=date)

def save_to_db(form) :
    contact = Contacts(
        name = form.name.data,
        email = form.email.data,
        phone = form.phone.data,
        subject = form.subject.data,
        message = form.message.data
    )
    try:
        db.session.add(contact)
        db.session.commit()
    except:
        db.session.flush()
        db.session.rollback()