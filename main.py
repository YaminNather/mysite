from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage, db
import pyrebase

from flask import Flask, render_template, request, redirect, session, jsonify, Response, url_for

# import the Firestore client
# import google.cloud
# from google.cloud import firestore

#for plotting
import io
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy
import random

from markupsafe import escape

# for login time
import datetime
from datetime import datetime, timezone
import time

#for email
import smtplib
from datetime import timedelta
from email.mime.text import MIMEText
from flask_mail import Mail, Message

#download report
import csv


cred = credentials.Certificate('D:\CSC681\csc681-72217-firebase-adminsdk-h9y4k-176a39cd5a.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)

config = {
  'apiKey': "AIzaSyAlqmpDorxTkTFPnt8K6GSnBWZSKPC10kU",
  'authDomain': "csc681-72217.firebaseapp.com",
  'databaseURL': "https://csc681-72217-default-rtdb.firebaseio.com",
  'projectId': "csc681-72217",
  'storageBucket': "csc681-72217.appspot.com",
  'messagingSenderId': "991638766609",
  'appId': "1:991638766609:web:6f1126bac2f730a81d1db0",
  'measurementId': "G-RE7FRFEMSQ"
}

#Initialising all variables
firebase = pyrebase.initialize_app(config)  #firebase connection
auth = firebase.auth()  #connection to firebase authentication
db = firestore.client() #connection to firebase client


app.secret_key = 'secret'






@app.route('/')
def home():
    return render_template('index.html')

#SIGN UP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.create_user_with_email_and_password(email, password)
            #auth.verify_password(password, user.password_hash)
            session['user'] = email
            session['uid'] = user['localId']
            t = time.localtime()
            session['current_time'] = time.strftime("%H:%M:%S", t)

            return redirect('/enterinfo')
        
        except:
            return render_template('signup.html', error='Email already exists')

    return render_template('signup.html')

@app.route('/enterinfo')
def enterinfo():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        designation = request.form['designation']
        dob = request.form['dob']
        email = session['user']
        bloodgrp = request.form['bgrp']


        data = {
        'Name': fname+lname,
        'Designation': designation,
        'DOB' : dob,
        'Email' : email,
        'BloodGroup' : bloodgrp,
        }
        # # subcollection_ref.add(data)

        db.collection("users").add(data)

        return render_template('tasks.html')
    
    return render_template('personalinfo.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)  
            #auth.verify_password(password, user.password_hash)
            session['user'] = email
            session['uid'] = user['localId']
            t = time.localtime()
            # current_time = str(time.strftime("%H:%M:%S", t))
            session['current_time'] = time.strftime("%H:%M:%S", t)
            # return redirect('/dashboard')
            return redirect(url_for('dashboard'))
        
        except:
            return render_template('signin.html', error='Invalid email or password')

    return render_template('signin.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        uid = session.get('uid')
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()
        for result in results:
            user_data = result.to_dict()

        # current_time = datetime.datetime.now()
        # t = time.localtime()
        # current_time = time.strftime("%H:%M:%S", t)

        if uid == "Lu6LwMC7lXRTgDxgMYd6vF6XEPM2":
            return render_template('adminpage2.html', user=session['user'], time=session.get('current_time'))
        else:
            return render_template('dashboard.html', user=user_data, time=session.get('current_time'))
    else:
        return redirect('/login')

#LOGOUT    
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

#PROFILE PAGE
@app.route('/profile')
def profile():

    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        try:
            query = users_ref.where('Email', '==', email).limit(1)
            results = query.get()
            for result in results:
                user_data = result.to_dict()
            return render_template('profile_test.html', user=user_data)
        
        except:
            return render_template('profile_test.html', error="USER NOT FOUND")

    else:
        return render_template('profile_test.html')
    
#VIEW OTHER EMPLOYEES
@app.route('/view')
def view():
    collection_ref = db.collection('users')
    docs = collection_ref.get()
    
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())

    # Get search query from URL parameter
    search_query = request.args.get('search')

    # Filter users based on search query
    if search_query:
        filtered_users = []
        for user in users:
            if search_query.lower() in user['Name'].lower():
                filtered_users.append(user)
        users = filtered_users

    return render_template('view_test.html', users=users)


#TASKS
@app.route('/tasks', methods=['POST', 'GET'])
def create_task():
    if 'user' in session:

        uid = session.get('uid')

        

        tasks_1 = db.collection("users").document(uid).collection("tasks").where('Completed', '==', True).stream()
        tasks_2 = db.collection("users").document(uid).collection("tasks").where('Date', '<', datetime.utcnow()).stream()
        tasks = list(tasks_1) + list(tasks_2)

        # Delete queried tasks
        for task in tasks:
            task.reference.delete()

        # Query tasks collection again for remaining tasks
        tasks = db.collection("users").document(uid).collection("tasks").stream()

        if request.method == 'POST':
            task = request.form['Task']
            datetimevar = request.form['Datetime']
            completed = False

            data = {
            'Task': task,
            'Date': datetimevar,
            'Completed': completed
            }
            # # subcollection_ref.add(data)

            db.collection("users").document(uid).collection("tasks").add(data)

            return render_template('tasks.html', tasks=tasks)
        
        else:
            return render_template('tasks.html', tasks=tasks)
        
# DELETING A TASK
@app.route('/tasks/<task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user' in session:
        uid = session.get('uid')

        db.collection("users").document(uid).collection("tasks").document(task_id).delete()

        return redirect(url_for('create_task'))
    
    return redirect(url_for('login'))

# SCHEDULES
@app.route('/schedule')
def schedule():
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()
        for result in results:
            user_data = result.to_dict()

        name = user_data['Name']

        week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday' ]
        
        ans = []
        for day in week:
            docs = (db.collection("schedules").document(name).collection(day)).get()
            for doc in docs:    
                ans.append(doc.to_dict())

        return render_template('schedule.html', ans = ans)

# @app.route('/schedule_update', methods=['GET', 'POST'])
# def schedule_update():
#     if 'user' in session:
#         email = session['user']
#         users_ref = db.collection('users')
#         query = users_ref.where('Email', '==', email).limit(1)
#         results = query.get()
#         for result in results:
#             user_data = result.to_dict()

#         name = user_data['Name']
#         week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday' ]
#         ans = []

#         if request.method == 'POST':
#             day = request.form['day']
#             hour = request.form['hour']
#             new_value = request.form['newinput']

#             # doc_ref = db.collection('schedules').document(name).collection(day).document()
#             # doc_ref.set({hour: new_value}, merge=True)

#             doc_ref = db.collection('schedules').document(name).collection(day).where(hour, '==', hour).limit(1).get()

#             for doc in doc_ref:
#                 doc_id = doc.id
#                 doc_ref =db.collection('schedules').document(name).collection(day).document(doc_id)
#                 doc_ref.update({hour: new_value})

#             # for day in week:
#             #     docs = db.collection('schedules').document(name).collection(day).get()
#             #     day_schedule = {}
#             #     for doc in docs:
#             #         day_schedule.update(doc.to_dict())
#             #     ans.append(day_schedule)

#             return render_template('update_schedule.html', ans=ans)
        
#         return render_template('update_schedule.html')
        
#     return render_template('update_schedule.html')

@app.route('/schedule_update', methods=['GET', 'POST'])
def schedule_update():
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()
        for result in results:
            user_data = result.to_dict()

        name = user_data['Name']
        week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday' ]
        ans = []

        if request.method == 'POST':
            day = request.form['day']
            hour = request.form['hour']
            new_value = request.form['newinput']

            try:
                doc_ref = db.collection('schedules').document(name).collection(day).where('hour', '==', hour).limit(1).get()

                for doc in doc_ref:
                    doc_id = doc.id
                    doc_ref = db.collection('schedules').document(name).collection(day).document(doc_id)
                    doc_ref.update({hour: new_value})

                    #doc_ref.update({hour: new_value})

                return render_template('update_schedule.html', ans=ans)
            
            except Exception as e:

                print(e)
                return "Error updating document"

        
        return render_template('update_schedule.html', ans=ans)
        
    return render_template('update_schedule.html', ans=ans)

# REPORT 
@app.route('/report')
def report():
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()
        for result in results:
            user_data = result.to_dict()
        name = user_data['Name']

        report_data = db.collection("attendance3").get()
        report_val = []
        for data in report_data:    
            data_dict = data.to_dict()
            attendance_dict = data_dict['attendance']
            report_val.append({
                'date' : data_dict['date'],
                'attendance' : attendance_dict[name]
            })
        # print(report_val)
        # field_names = ['date', 'present']
        # with open('/static/styles/' + name + '.csv', 'w') as csvfile:
        #     writer = csv.DictWriter(csvfile, fieldnames = field_names)
        #     writer.writeheader()
        #     writer.writerows(report_val)
            
        return render_template('report.html', report_data=report_val)

#ADMIN

## Admin Page Dashboard
@app.route('/adminpage')
def admin():
    return render_template('adminpage2.html')

## Admin Page to SIGN UP user using email password verification from firebase auth
@app.route('/adminpage_signup', methods=['GET', 'POST'])
def adminpage_signupuser():

    if request.method == 'POST':
        
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.create_user_with_email_and_password(email, password)
            #auth.verify_password(password, user.password_hash)
            session['user'] = email
            session['uid'] = user['localId']
            return redirect('/adminpage_adduser', email=email)
    
        except:
            return render_template('adminpage_signup.html', error='Email already exists')
        
    return render_template('adminpage_signup.html')

## Admin page to ADD USER DETAILS
@app.route('/adminpage_adduser', methods=['GET', 'POST'])
def adminpage_adduser():

    if request.method == 'POST':
        name = request.form.get('name')
        email = session.get['email']
        
        collection_ref = db.collection('users')

        doc_ref = collection_ref.document()
        doc_ref.set({
            'Name': name,
            'Email': email
        })

    return render_template('adminpage_adduser.html')

## Admin Page to view USERS

@app.route('/adminpage_userview')
def adminpage_userview():
    collection_ref = db.collection('users')
    docs = collection_ref.get()
    
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())

    search_query = request.args.get('search')

    # Filter users based on search query
    if search_query:
        return redirect(url_for('.adminpage_personaluserview', search=search_query))

    return render_template('adminpage_userview.html', users = users)

## ADMIN PAGE to view detailed report of a single user
@app.route('/adminpage_personaluserview')
def adminpage_personaluserview():

    user_name = request.args["search"]

    collection_ref = db.collection('users')
    docs = collection_ref.get()

    print(user_name)
    
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())
    
    filtered_users = []
    for user in users:
        
        if user_name in user['Name']:
            filtered_users.append(user)

    users = filtered_users

    return render_template('adminpage_personaluserview.html', user = users[0])

#ADMIN REPORT
@app.route('/admin_report')
def admin_report():

    collection_ref = db.collection('users')
    docs = collection_ref.get()
    
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())

    search_query = request.args.get('search')

    if search_query:
        report_data = db.collection("attendance3").get()
        report_val = []
        for data in report_data:    
            data_dict = data.to_dict()
            attendance_dict = data_dict['attendance']
            report_val.append({
                'date' : data_dict['date'],
                'attendance' : attendance_dict[search_query]
            })

        return render_template('adminreport.html', users=users, report_data=report_val)
    
    else:
        return render_template('adminreport.html', users=users)
    
@app.route('/admin_report_personal')
def admin_report_personal():
    name = request.args["user_name"]
    report_data = db.collection("attendance3").get()
    report_val = []
    for data in report_data:    
        data_dict = data.to_dict()
        attendance_dict = data_dict['attendance']
        report_val.append({
            'date' : data_dict['date'],
            'attendance' : attendance_dict[name]
        })
    return render_template('adminreport_personal.html', report_data=report_val)

#ADMIN TASK
@app.route('/admin_task')
def admin_task():
    
    collection_ref = db.collection('users')
    docs = collection_ref.get()
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())

    return render_template('admin_task_test.html', users = users)
    

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'antikaburman02@gmail.com'
app.config['MAIL_PASSWORD'] = 'Anjali$2002'
mail = Mail(app)
@app.route('/admin_task_personal')
def admin_task_email():
    
    name = request.args.get("user_name")

    msg = Message('Hello from Flask-Mail', sender='antikaburman02@gmail.com', recipients=['antika.burman@science.christuniversity.in'])
    msg.body = "This is a test email sent from a Flask application."
    mail.send(msg)
    return 'Email sent!'
    

## ADMIN ATTENDANCE
@app.route('/admin_attendance/')
def admin_attendance():
    
    collection_ref = db.collection('users')
    docs = collection_ref.get()
    
    # Store data in a list of dictionaries
    users = []
    for doc in docs:
        users.append(doc.to_dict())

    return render_template('admin_attendance.html', users = users)
    # return users

@app.route('/admin_attendance_2', methods=['POST', 'GET'])
def admin_attendance_display():
    user_name = request.args.get("user_name")
    print(f"Username = {user_name}")
    return render_template('admin_attendance_personal.html', name=user_name)
    #return 'User %s' % escape(user_name)

@app.route('/adminplot.png')
def admin_plot_png():
    user_name = request.args.get("user_name")
    fig = admin_createfigure(user_name)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def admin_createfigure(user_name):
    docs = (db.collection("attendance").document(user_name).get()).to_dict()
    x = list(docs.values())
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    mylabels = list(docs.keys())
    axis.pie(x, labels=mylabels, shadow = True)
    axis.legend(title="Days", loc="upper left", bbox_to_anchor=(0.95, 1.1))
    return fig

@app.route('/adminplot2.png')
def admin_plot_png2():
    user_name = request.args.get("user_name")
    fig = admin_create_figure2(user_name)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def admin_create_figure2(user_name):
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()

        for result in results:
            user_data = result.to_dict()

    docs = (db.collection("attendance2").document(user_name).get()).to_dict()
    vals = list(docs.values())
    fig = Figure(figsize=(15, 5))
    axis = fig.add_subplot(1, 1, 1)
    axis.grid(True)
    months = list(docs.keys())
    # axis.ylabel('Number of absences')
    axis.bar(months, vals)
    return fig

# ATTENDANCE-SELF

@app.route('/attendance_self')
def attendance_self():
    return render_template('attendance.html')

@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()

        for result in results:
            user_data = result.to_dict()

        name = user_data['Name']
        docs = (db.collection("attendance").document(name).get()).to_dict()
        x = list(docs.values())
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        mylabels = list(docs.keys())
        axis.pie(x, labels=mylabels, shadow = True)
        axis.legend(title="Days", loc="upper left", bbox_to_anchor=(0.95, 1.1))
        return fig
    
@app.route('/plot2.png')
def plot_png2():
    fig = create_figure2()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure2():
    if 'user' in session:
        email = session['user']
        users_ref = db.collection('users')
        query = users_ref.where('Email', '==', email).limit(1)
        results = query.get()

        for result in results:
            user_data = result.to_dict()

        name = user_data['Name']
        docs = (db.collection("attendance2").document(name).get()).to_dict()
        vals = list(docs.values())
        fig = Figure(figsize=(15, 5))
        axis = fig.add_subplot(1, 1, 1)
        axis.grid(True)
        months = list(docs.keys())
        # axis.ylabel('Number of absences')
        axis.bar(months, vals)
        return fig



if __name__ == '__main__':
    app.run(debug=True)