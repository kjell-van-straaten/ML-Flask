from flask import Flask, render_template, request,g, redirect, session
from app.functions import *
from app.classes import *
from bson import ObjectId
import datetime
import joblib
from os.path import join, dirname, realpath

#initialize flask app
app= Flask(__name__)
app.secret_key = 'courgette'

#establish connection to db
db = connect_db()
account_table = db.Accounts
machinedata_table = db.MachineData

#unpickle the created model
print(dirname(realpath(__file__)))
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/classifier.pkl')
classifier = joblib.load(UPLOADS_PATH)


@app.before_request
def before_request():
  g.user = None
  if 'user_id' in session:
    current_user = account_table.find_one({"_id": ObjectId(session['user_id'])})
    user = User(current_user['_id'],current_user['name'],current_user['password'], current_user['role'])
    g.user = user

@app.route('/')
def index():
  return render_template('landingpage.html')

@app.route('/input_data', methods=['GET', 'POST'])
def input_data():
  #/input_data?id=sap123&machine=elektromotor&stroom=45
  id = request.args.get('id')
  machine = request.args.get('machine')
  stroom = request.args.get('stroom')
  dateTimeObj = datetime.datetime.now()
  #timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
  
  prediction = bool(classifier.predict([[stroom]])[0])
  
  create_record(machinedata_table, [id, machine, prediction, int(stroom), dateTimeObj])
  return "data entry succesfull for machine {}".format(id)


@app.route('/dashboard')
def dashboard():
  last_error_data = list(machinedata_table.aggregate(
    [
        {"$match":
            {
                'prediction': True
            }
        },
        {
            "$group":
            {
                "_id": '$id',
                'machine': {"$first": "$machine"},
                "last_error": {"$max": "$timestamp"} 
            }
        }
    ]))
  last_error_data = sorted(last_error_data, key=lambda d: d['last_error'], reverse=True) 

  return render_template('dashboard.html', data=last_error_data)  

@app.route('/raw')
def raw():
  historic_data = list(machinedata_table.find({}))

  historic_data = sorted(historic_data, key=lambda d: d['timestamp'], reverse=True) 

  return render_template('raw.html', data=historic_data)  

@app.route('/machinedetail', methods=['GET', 'POST'])
def machine_detail():
  id = request.args.get('id')

  if id == None:
    if request.method == 'POST':
      id = request.form['id']
      historic_data = list(machinedata_table.find({"id": id}))
      historic_data = sorted(historic_data, key=lambda d: d['timestamp'], reverse=True) 

      labels = [i['timestamp'].strftime("%d-%b-%Y (%H:%M:%S.%f)") for i in historic_data]
      values = [i['stroom'] for i in historic_data]

      return render_template('machinedetail.html', data=historic_data, labels=labels, values=values, machine=id)  


    return render_template('machinedetail.html', nodata = True) 
  
  else:
    historic_data = list(machinedata_table.find({"id": id}))
    historic_data = sorted(historic_data, key=lambda d: d['timestamp'], reverse=True) 

    labels = [i['timestamp'].strftime("%d-%b-%Y (%H:%M:%S.%f)") for i in historic_data]
    values = [i['stroom'] for i in historic_data]
    return render_template('machinedetail.html', data=historic_data, labels=labels, values=values, machine=id)

@app.route('/navbar')
def navbar():
  admin = False

  if g.user:
    current_user = g.user

    if g.user.roles['admin']:
      admin = True
      
  else:
    current_user = False

  return render_template('navbar.html', current_user=current_user, admin = admin)

@app.route('/logout')
def logout():
  session.pop('user_id', None)
  return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
   
    session.pop('user_id', None)

    username = request.form['username']
    password = request.form['password']

    #find instance associated to given name, if no instance is found NONE is returned
    login_user = account_table.find_one({"name": username})

    #if we have a user, and the decrypted passwords match then save new user id and redirect to tournaments page;
    if login_user and (login_user["password"] == str(persistent_hash(password))):
      user = User(login_user['_id'],login_user['name'],login_user['password'], login_user['role'])
      session['user_id'] = str(user.id)
      return redirect("/")

    #else, redirect to login page again
    else:
      return render_template('login.html', failed = True)

  else: 
    return render_template('login.html')

#page for creating account, POST account into database, w/ encrypted password
@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    if account_table.find_one({"name": username}):
      return render_template('signup.html', failed = True) 

    else:
      create_record(account_table, [username, email, str(persistent_hash(password)), 'none'])
      return redirect('/login')

  return render_template('signup.html')


