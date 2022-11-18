import pandas as pd
import numpy as np
import pickle
import os
import ibm
from flask import Flask,request, render_template,session,redirect,flash
import requests
import ibm_db

app=Flask(__name__,template_folder="templates")
app.secret_key = "super secret key"


#for db connection 
dsn_hostname = "ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud" # e.g.: "54a2f15b-5c0f-46df-8954-7e38e612c2bd.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud"
dsn_uid = "ljx83321"        # e.g. "abc12345"
dsn_pwd = "u7Mi2uux6vXQaKhT"      # e.g. "7dBZ3wWt9XN6$o0J"
dsn_driver = "{IBMDB2CL1}"
dsn_database = "bludb"            # e.g. "BLUDB"
dsn_port = "31321"                # e.g. "32733"
dsn_protocol = "TCPIP"            # i.e. "TCPIP"
dsn_security = "SSL"              #i.e. "SSL
dsn_cert="DigiCertGlobalRootCA.crt"
dsn = (
    "DRIVER={0};"
    "DATABASE={1};"
    "HOSTNAME={2};"
    "PORT={3};"
    "PROTOCOL={4};"
    "UID={5};"
    "PWD={6};"
    "SECURITY={7};"
    "SSLServerCertificate={8};").format(dsn_driver, dsn_database, dsn_hostname, dsn_port, dsn_protocol, dsn_uid, dsn_pwd,dsn_security,dsn_cert)
conn = 0
try:
    conn =ibm_db.connect(dsn, "", "")
    print("Connected to database: ", dsn_database, "as user: ", dsn_uid, "on host: ", dsn_hostname)
except:
    print("Unable to connect: ", ibm_db.conn_errormsg())
print(dsn)

#ibm cloud api 
API_KEY = "RQRG9kMruxQGPGPQmzRtxPBBK_6hO91hjt6lDcahLizz"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token',
                               data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}



#for login db table
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        qry="select * from  CUSTOMER where email=? AND password=?"
        stmt=ibm_db.prepare(conn,qry)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        resp=ibm_db.fetch_assoc(stmt)
        print("resp - ",resp)
        if resp:
            return render_template("page.html")
        else:
            return render_template('index.html')

    return render_template('index.html')



#for reg db table
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        user=request.form['name']
        password=request.form['password']
        email=request.form['email']
        shopid=request.form['shopid']
        phone=request.form['phone']
        cityid=request.form['cityid']
        qry="insert into CUSTOMER(user,password,email,shop_id,phone,city_id)values(?,?,?,?,?,?)"
        stmt=ibm_db.prepare(conn,qry)
        ibm_db.bind_param(stmt,1,user)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,email)
        ibm_db.bind_param(stmt,4,shopid)
        ibm_db.bind_param(stmt,5,phone)
        ibm_db.bind_param(stmt,6,cityid)
        resp=ibm_db.execute(stmt)
        print(resp)
        return render_template('index.html')
    return render_template('register.html')


#routings 

@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/payment',methods=['GET','POST'])
def payment():
    return render_template('payment.html')

@app.route('/cities',methods=['GET','POST'])
def cities():
    return render_template('cities.html')

@app.route('/prem',methods=['GET','POST'])
def prem():
    return render_template('prem.html')

@app.route('/page',methods=['GET','POST'])
def page():
    return render_template('page.html')

@app.route('/pricing',methods=['GET','POST'])
def pricing():
    return render_template('pricing.html')

@app.route('/todo',methods=['GET','POST'])
def todo():
    return render_template('todo.html')

@app.route('/offer',methods=['GET','POST'])
def offer ():
    return render_template('offer.html')

@app.route('/contact',methods=['GET','POST'])
def contact ():
    return render_template('contact.html')

@app.route('/pay',methods=['GET','POST'])
def pay ():
    return render_template('payment.html')



def page():
    return render_template('predict.html')


@app.route('/predict', methods=['GET', 'POST'])


def predict():
    if request.method=='GET':
        return render_template('predict.html')
    print("[INFO] loading model...")
    model = pickle.load(open('fdemand.pkl', 'rb'))
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]
    print(features_value)
    
    features_name = ['homepage_featured', 'emailer_for_promotion', 'op_area', 'cuisine',
       'city_code', 'region_code', 'category']
    prediction = model.predict(features_value)
    output=(prediction[0])//2 
    print(output)
    return render_template('predict.html', prediction_text=output)




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=False)