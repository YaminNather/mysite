import firebase_admin
from firebase_admin import credentials, auth, firestore
import pyrebase # for authentication

from flask import Flask, render_template, request, redirect, session, jsonify

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

#PROFILE PAGE
@app.route('/profile')
def profile():
    # Get the current user's authentication ID
    user_id = request.cookies.get('user_id')

    # Get the user's profile data from the Cloud Firestore collection
    user_doc = db.collection('users').document(user_id).get()
    user_data = user_doc.to_dict()

    # Render the profile page with the user's data
    return render_template('profile.html', user=user_data)

if __name__ == '__main__':
    app.run(debug=True)