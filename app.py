#!/usr/bin/python3
import json
import os
import subprocess
import mysql.connector 
import sqlite3
from flask import Flask, jsonify, request, abort, render_template, url_for, session, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from subprocess import call
from os import listdir
from os.path import isfile, join
import cert_issuer.config
from cert_issuer.blockchain_handlers import bitcoin
import cert_issuer.issue_certificates
from werkzeug.utils import secure_filename
from pymongo import MongoClient
# IMPORT ETHEREUM FOR GETTING THE BALANCE
# from Cert_Issuer.cert_issuer.blockchain_handlers.ethereum import connectors  

app = Flask(__name__)
config = None
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = '<replace with a secret key>'

#toolbar = DebugToolbarExtension(app)

client = MongoClient('mongodb://localhost:27017')

def get_config():
    global config
    if config == None:
        config = cert_issuer.config.get_config()
    return config



@app.route('/cert_issuer/api/v1.0/issue', methods=['POST'])
def issue():
    config = get_config()
    certificate_batch_handler, transaction_handler, connector = \
            bitcoin.instantiate_blockchain_handlers(config, False)
    certificate_batch_handler.set_certificates_in_batch(request.json)
    cert_issuer.issue_certificates.issue(config, certificate_batch_handler, transaction_handler)
    return json.dumps(certificate_batch_handler.proof)



@app.route("/")
def index():
   
        return render_template('login.html')
@app.route("/index")
def index_n():
 if 'ThirdID' in  session:           
        return render_template('index.html',error=None)
 else:
    return redirect(url_for('index'))
@app.route("/home")
def home():
  if 'ThirdID' in  session:        
        cnx = mysql.connector.connect(user='oumaima', password='oumaima1996', host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com', database='oumaima')
        cursor = cnx.cursor()
        sql_select_Query = "SELECT * from verifier,Certificat_non_sign,Etudiant where verifier.id_certificate=Certificat_non_sign.id and verifier.id_tiers_partie=%s and Certificat_non_sign.id_Etudiant=Etudiant.id ORDER BY verifier.verification_date DESC limit 0, 9;  "
        cursor.execute(sql_select_Query,(session['ThirdID'],))
        records = cursor.fetchall()
        print("------------------------- Listing Last Verified Certificates -------------------------------------- ")
        
        for row in records:
        
           print("Certificate id = ", row[5] )
           print("Major = ", row[7] )
           print("Degree = ", row[8] )
           print("Student First name = ",row[15])
           print("Student Last name = ",row[16])
        print(" ---------------------- Stats for Number of certificates by Major ------------------------------")
        first_query=("SELECT COUNT(Certificat_non_sign.id),Certificat_non_sign.Major  FROM verifier,Certificat_non_sign where verifier.id_certificate=Certificat_non_sign.id and verifier.id_tiers_partie=%s GROUP BY Certificat_non_sign.Major  ") 
        cursor_r = cnx.cursor()
        cursor_r.execute(first_query,(session['ThirdID'],))
        myresult1=cursor_r.fetchall()
        dataa1=[]
        dd=[]
        for test in myresult1 :
           dd=[]
           print(test[0])
           print(test[1])
           b = test[0]
           dd.append(b)
           dd.append(test[1])
           dataa1.append(dd)
        print(dataa1)


        print(" ---------------------- Stats for Number of certificates by Institution ------------------------------")
        second_query=("SELECT COUNT(Certificat_non_sign.id),AdminOrganisme.name_organisme FROM verifier,Certificat_non_sign,AdminOrganisme where verifier.id_certificate=Certificat_non_sign.id and Certificat_non_sign.id_AdminOrganisme=AdminOrganisme.id and verifier.id_tiers_partie=%s GROUP BY AdminOrganisme.name_organisme ")
        cursor_rr = cnx.cursor()
        cursor_rr.execute(second_query,(session['ThirdID'],))
        myresult2=cursor_rr.fetchall()
        dataa2=[]
        dd=[]
        for test1 in myresult2 :
           dd=[]
           print(test1[0])
           print(test1[1])
           b = test1[0]
           dd.append(b)
           dd.append(test1[1])
           dataa2.append(dd)
        print(" --------------------------- Listing verifiers ----------------------------------------------------")
        
        third_query=("SELECT * from tiers_partie where NatID=%s ")
        cursor_rrr = cnx.cursor()
        cursor_rrr.execute(third_query,(session['ThirdID'],))
        myresult3=cursor_rrr.fetchall()
        dataa3=myresult3

        return render_template('employerhome.html',certificates=records,chaine1=dataa1,chaine2=dataa2,chaine3=dataa3)
  else:
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
        session.clear()
        return redirect(url_for('index'))

@app.route("/registration")
def registration():
    data=["","","","","","","",""]
    return render_template('registration.html',data=data)
   
@app.route("/registration",methods=['POST'])
def newRegistration():
           ID = request.form['NatID']   
           NatID = request.form['NatID']
           name = request.form['name']
           Lname = request.form['Lname']
           address = request.form['address']
           email = request.form['email']
           sexe = request.form['sexe']
           password=request.form['password']
           password1=request.form['password1']
           cnx = mysql.connector.connect(user='oumaima', password='oumaima1996', host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com', database='oumaima')
           cursor = cnx.cursor()
           verify = ("SELECT name FROM tiers_partie  WHERE  ID = %s OR  NatID = %s ")
           adr = (ID,NatID)
           cursor.execute(verify, adr)
           myresult = cursor.fetchone()

           cursorTest = cnx.cursor()
           verify1 = ("SELECT email FROM personne WHERE  email = %s ")
           cursorTest.execute(verify1,(email, ) )
           myresult1 = cursorTest.fetchone()
           print("test1 :",myresult1)

           myData = (ID,NatID, name,Lname, address ,email,password,sexe)
           if myresult == None :
            if myresult1 == None :
              if password == password1 :
                add_tierPartie = ("INSERT INTO tiers_partie(ID,NatID, name,Lname,address,email,password,sexe) VALUES(%s,%s, %s, %s, %s ,%s, %s, %s)")
                cursor.execute(add_tierPartie, myData)
                emp_no = cursor.lastrowid
                cnx.commit()
                cursor.close()
                cnx.close()
                session['ThirdID']=ID 
                session['first_name']=name
                session['last_name']=Lname

                return redirect(url_for('home'))
              else :
                error=" Password not Valid . Please check your data. "
                return render_template('registration.html',error1=error,data=myData)
            else:
                 error=" Email is already exist"
                 return render_template('registration.html',error1=error,data=myData)

           else :
              error="ID or National ID really exist . Please check your data. "
              return render_template('registration.html',error=error,data=myData)

@app.route("/profile")
def profile_me():


  if 'ThirdID' in  session:   
  #----------------------------------- Checking if the user exists in DB ------------------------------------------$
         import mysql.connector
         from mysql.connector import Error
         data=["","","","","","","","","","","","","","","","","",""]
         print("hheelloo")
         try:
            mySQLconnection = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
            port=3306,
            database='oumaima',
            user='oumaima',
            password='oumaima1996')
            sql_select_Query = "select * from tiers_partie where tiers_partie.id= %s"
            cursor = mySQLconnection .cursor()
            test=(session['ThirdID'],)
            cursor.execute(sql_select_Query,test)
            row = cursor.fetchone()
            if row:
                  data=row
                  print("hiii I'm the third party")
         except Error as e :
                  print ("Error while connecting to MySQL", e)
         finally:
                 cursor.close() 
                            #closing database connection.
                 if(mySQLconnection .is_connected()):
                                           mySQLconnection.close()
                                           print("MySQL connection is closed")
     # return redirect(url_for('modif_profile'))
         return render_template('profile.html',data=data)
  else:
       return redirect(url_for('index'))


              
@app.route("/profile",methods=['POST'])
def modif_profilAdminS():
       
  if 'ThirdID' in session: 
         error=""
         

         address=request.form['address']
    
         id=session['ThirdID']
         print("-------------------------------------------------------------")
         print(id)
         password=request.form['password']
         password1=request.form['password1']
        

  #----------------------------------- Checking if the user exists in DB ------------------------------------------$
         import mysql.connector
         from mysql.connector import Error
      #try:
         mySQLconnection = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
         port=3306,
         database='oumaima',
         user='oumaima',
         password='oumaima1996')
         if password == password1 :
            sql_select_Query = "UPDATE tiers_partie SET  tiers_partie.password =%s , tiers_partie.address =%s  WHERE tiers_partie.id=%s"
            cursor_or = mySQLconnection.cursor(buffered=True)
            cursor_or.execute(sql_select_Query,(password,address,id,))
            print(address)
            print(password)
            mySQLconnection.commit()
            cursor_or.close()
            if(mySQLconnection.is_connected()):
                                           mySQLconnection.close()
                                           print("MySQL connection is closed")


            return redirect(url_for('index_n'))
         else:
            error=" Password not Valid . Please check your data."
            return render_template('profile.html')
  else:
       return redirect(url_for('index'))


@app.route("/", methods=['POST'])
def Login():
 error=""
 if request.form['password'] and request.form['email']:
  #----------------------------------- Checking if the user exists in DB ------$
      import mysql.connector
      from mysql.connector import Error
      try:
         mySQLconnection = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
         port=3306,
         database='oumaima',
         user='oumaima',
         password='oumaima1996')
         sql_select_Query = "select * from tiers_partie  where email= %s and password =%s "
         cursor = mySQLconnection .cursor()
         cursor.execute(sql_select_Query,(request.form['email'],request.form['password']))
         row = cursor.fetchone()
         if row :
           session['ThirdID']=row[0]
           session['first_name']=row[2]
           session['last_name']=row[6]
           return redirect(url_for('home'))
         else:
             error=" Login or password not correct. Please check your data." 
             return render_template('login.html',error=error)
             # return redirect(url_for('index'))

      except Error as e :

           print ("Error while connecting to MySQL", e)
      finally:
                                     #closing database connection.
          if(mySQLconnection .is_connected()):
                                           mySQLconnection.close()
                                           print("MySQL connection is closed")
      
         

 else:
        return redirect(url_for('index'))


@app.route("/index",methods=['POST'])
def show_certificates():
 if 'ThirdID' in session:
  if request.form['certificate']:
   mySQLconnection = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
   port=3306, 
   database='oumaima',
   user='oumaima',
   password='oumaima1996')
   sql_select_Query_or = "select * from blackList where id_certificate=%s"
   cursor = mySQLconnection .cursor()
   cursor.execute(sql_select_Query_or,(request.form['certificate'],))

   row = cursor.fetchone()
   print(row)
   if row== None:
  
    call("sudo rm data/*.json",shell=True)
 
    client = MongoClient('mongodb://salma:salma@35.153.100.231:27017/test')
    #call("sudo rm  /home/ubuntu/Desktop/Cert/Cert-Viewer/cert-viewer/cert_data/*.json",shell=True)
    db = client['doccerts']
    certificates=db.testcerts
    certificate_uid=request.form['certificate']
    print(certificate_uid)
    cc=certificates.find({ '$or':[{'certificateid': request.form['certificate']},{'ID': request.form['certificate']},{'NatID': request.form['certificate']}]}, {'_id': 0})
    #cc=certificates.find()
    data=''
    #print(cc)
    d=[]
    print("-------------------------------------- Listing Certificates ----------------------------------------")
    for c in cc:
     # print(c)
     # if c["certificateid"]==certificate_uid :
       data=c
       print(data)
       d.append(data)
       print(d)
       pat="data/"+data['certificateid']+".json"
       with open(pat, 'w') as file:
            json.dump(data,file)

    
    return render_template('listingcertificates.html',certificates=d)    
   else:
            error="This certificate was deleted for the reason of :"+row[2] +","+row[3]
            print(error)
            return render_template('index.html',error=None,error1=error)
  else:
     
     return redirect(url_for('index_n'))   
 else:
        return redirect(url_for('index'))

@app.route("/uploadCertificate")
def upload_certificate():

  return render_template('uploadJsonFile.html')


@app.route("/uploadCertificate",methods=['POST'])
def upload_certificate_post():
 if 'ThirdID' in session:
  print("----------------------------- Verifying the Uploaded certificate -------------------------------- ")
  if len(request.files) != 0:
            obj=None
            file = request.files['certificatefile']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename)) 
            call("python cert_verifier/verifier.py data/" + filename,shell=True)
            textt = open('verifying_debug.txt', 'r+')
            content = textt.readlines()
            textt.close()
            with open("data/" + filename, 'r') as myfile:
               dat=myfile.read()

            obj = json.loads(dat)
            print("--------------------------- Inserting data into MySql ------------------------------------")
            resultat=1
            for line in content:
               if line.find('passed')==-1:
                  resultat=0 
            print("result of verification ==== ",resultat)
            import mysql.connector
            from mysql.connector import Error
            try:
                 cnx = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
                 port=3306,
                 database='oumaima',
                 user='oumaima',
                 password='oumaima1996')
                 import datetime
                 now=datetime.datetime.now().date()
                 if 'certificateid' in obj:

                   checking_query="SELECT * from verifier where id_tiers_partie=%s and id_certificate=%s"
                   cursor_o = cnx.cursor()
                   cursor_o.execute(checking_query,(session['ThirdID'],obj['certificateid']))
                   ress=cursor_o.fetchone()
                   if ress==None:
                       sql_select_Query = ("INSERT INTO verifier(id_tiers_partie,resultat,id_certificate,verification_date) VALUES(%s,%s,%s,%s) ")
                       cursor = cnx.cursor()
                       print("Inserting data .......................")
                       cursor.execute(sql_select_Query,(session['ThirdID'],resultat,obj['certificateid'],now))
                       cnx.commit()
                       cursor.close()
                       cnx.close() 
                   else: 
                        print("The certificate already verified by this employer ")
                 else:
                    error="The certificate you have uploaded doesn't match the required certificate format."
                    return render_template('index.html',obj=obj,error=filename,text=content)
            except Error as e :
                    print ("Error while connecting to MySQL", e)
            finally:
                                     #closing database connection.
                     if(cnx .is_connected()):
                                           cnx.close()
                                           print("MySQL connection is closed")
            call("rm data/*.json",shell=True)
            return render_template('index.html',obj=obj,error=filename,text=content)

  else:
       return render_template('uploadJsonFile.html')


 else:
        return redirect(url_for('index'))  

  
@app.route("/index/<certificateid>",methods=['GET'])
def verifying(certificateid):
 if 'ThirdID' in session: 
  error=""
  print("------------------------------------ Verifying certificate ---------------------------")
  if request.method == 'GET':
       try:
          if len(request.files) != 0:
            file = request.files['certificatefile']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename)) 
            call("python cert_verifier/verifier.py data/" + filename,shell=True)
            textt = open('verifying_debug.txt', 'r+')
            content = textt.readlines()
            textt.close()
            call("rm data/*.json",shell=True)
            return render_template('index.html',error=filename,text=content)

          elif certificateid and os.path.isdir("data/") and os.path.isfile(os.path.join("data/", certificateid+".json")):
             certificateFile=certificateid+".json"
             client = MongoClient('mongodb://salma:salma@35.153.100.231:27017/test')
             #call("sudo rm  /home/ubuntu/Desktop/Cert/Cert-Viewer/cert-viewer/cert_data/*.json",shell=True)
             db = client['doccerts']
             certificates=db.testcerts
             cc=certificates.find({ 'certificateid': certificateid}, {'_id': 0})
             data=[]
             
             
             for c in cc:
                 data.append(c)
                 break    

             call("python cert_verifier/verifier.py  data/" + certificateFile,shell=True)
             text = open('verifying_debug.txt', 'r+')
             content = text.readlines()
             text.close()
             print("Third Party ID ==================",session['ThirdID'])
             print("Certificate ID ==================",certificateid)
             # --------------------------- Inserting Data into MySQL ---------------------------------------
             resultat=1
             for line in content:
               if line.find('passed')==-1:
                  resultat=0 
             import mysql.connector
             from mysql.connector import Error
             try:
                 cnx = mysql.connector.connect(host='doccert.cpt7ef0q6mfq.us-east-1.rds.amazonaws.com',
                 port=3306,
                 database='oumaima',
                 user='oumaima',
                 password='oumaima1996')
                 import datetime
                 now=datetime.datetime.now().date()
                 checking_query="SELECT * from verifier where id_tiers_partie=%s and id_certificate=%s"
                 cursor_o = cnx.cursor()
                 cursor_o.execute(checking_query,(session['ThirdID'],certificateid))
                 ress=cursor_o.fetchone()
                 if ress==None:
                     sql_select_Query = ("INSERT INTO verifier(id_tiers_partie,resultat,id_certificate,verification_date) VALUES(%s,%s,%s,%s) ")
                     cursor = cnx.cursor()
                     print("Inserting data .......................")
                     cursor.execute(sql_select_Query,(session['ThirdID'],resultat,certificateid,now))
                     cnx.commit()
                     cursor.close()
                     cnx.close() 
                 else: 
                      print("The certificate already verified by this employer ")

             except Error as e :
                    print ("Error while connecting to MySQL", e)
             finally:
                                     #closing database connection.
                     if(cnx .is_connected()):
                                           cnx.close()
                                           print("MySQL connection is closed")
          #--------------------------------- End Of Insertion -------------------------------------
                        
             #import csv
             #with open('/home/ubuntu/Desktop/Cert/Cert-Tools/cert-tools/sample_data/rosters/roster_testnet.csv', 'r') as inFile:
              #        reader = csv.reader(inFile, delimiter=',', quoting=csv.QUOTE_NONE)
               #       data=[]
                #      for line in reader:
                 #        if line[1]==request.form['certificate']:
                  #            data=line 
                   #           break 
             return render_template('index.html',data=data,error=certificateFile,text=content)

          else:
             error="This ID doesn't match any certificate, please tape a correct ID"
             return render_template('index.html',error=error)


           #return render_template('index.html',error=certificateFile,text=content,data=data)
       except NameError:
            print("error ...........")
            return render_template('index.html',error=None)

 else:
        return redirect(url_for('index')) 

 
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80)
