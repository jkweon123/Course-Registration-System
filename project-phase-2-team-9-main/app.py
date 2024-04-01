from flask import Flask, session, render_template, redirect, url_for, request, flash
import mysql.connector
from datetime import timedelta, datetime
import random

app = Flask('app')
app.secret_key = "classified"
app.permanent_session_lifetime = timedelta(minutes=5)

mydb = mysql.connector.connect( 
    host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
    user="admin",
    password="groupnine",
    database="university"
)

def _process_time(class_time):
    time_list = class_time.split("-")

    start_time = float(time_list[0][0:2])
    if str(time_list[0][3]) != '0':
        start_time += 0.5

    end_time = float(time_list[1][0:2])
    if str(time_list[1][3]) != '0':
        end_time += 0.5

    return start_time, end_time


def _get_curr_semester():
    seasons = {
            'Fall': ['August','September', 'October', 'November', 'December'],
            'Spring': ['January', 'February', 'March', 'April', 'May', 'June']
            }
    
    current_time = datetime.now()
    current_month = current_time.strftime('%B')
    current_year = current_time.strftime('%Y')

    for season in seasons:
        if current_month in seasons[season]:
            return season, current_year
    return 'Invalid input month'

def _get_next_semester():
    curr_semester = _get_curr_semester()
    if curr_semester == 'Invalid input month':
        return curr_semester
    elif curr_semester[0] == 'Fall':
        return 'Spring',str(int(curr_semester[1])+1)
    else:
        return 'Fall', str(curr_semester[1])
    

def _calc_GPA(courses):
    GPA = {
        'A':4.0,
        'A-':3.7,
        'B+':3.3,
        'B':3.0,
        'B-':2.7,
        'C+':2.3,
        'C':2.0,
        'F':0.0
            }
    
    sumGPA = 0 #sum of GPA
    sumCredit = 0  #Total of credit hours
    finalGPA = 0 #cumalative GPA

    
    
    belowBcounter = 0

    ctr = 0

    for course in courses:
        if course['grade'] != None:
            ctr += 1
            sumGPA+= GPA[course['grade']]
            sumCredit+= course['credits']
            if GPA[course['grade']] < 3:
                belowBcounter += 1

    if ctr < 1:
        return -1
    
    finalGPA = sumGPA / ctr

    return float(finalGPA), sumCredit, belowBcounter



@app.route('/', methods=['GET', 'POST'])
def login():
  # Login and create session variables
    if session and 'type' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        # Connect to database and get form variables
        try: 
            mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
            cursor = mydb.cursor(dictionary=True)
            email = request.form["email"]
            password = request.form.get("password")
            
        except:
            flash("Error while connecting to database. Please try again", "error")
            return render_template('login.html') 
        
        # Check if there's any input:
        # if email == "" or password == "":
        #     flash("Please enter your email and password", "error")
        #     return render_template('login.html') 
        
        try: 
            cursor.execute("SELECT email, password, uid FROM users WHERE email = (%s) AND password = (%s) ", (email, password))
            user = cursor.fetchone()      

            if user:
                session['email'] = email
                session['password'] = password
                session['id'] = user['uid']
                session["registration"] = []
                session['type'] = []

                cursor.execute("SELECT * FROM user_types JOIN users ON users.uid = user_types.uid WHERE users.uid = %s", (user['uid'],))
                user_types = cursor.fetchall()
                for each_type in user_types:
                    session['type'].append(each_type['user_type'])


                flash("Login successful", "success")
                print(session['type'])

                return redirect(url_for('home'))
            
                    
            # #if you are a recommender
            email = request.form["email"]
            cursor.execute("SELECT email FROM recs")
            recs = cursor.fetchall()
            for rec in recs:
                if rec['email'] == email:
                    session['email'] = email
                    #check if already sent email
                    cursor.execute("SELECT message FROM recs WHERE email = (%s)", (session['email'],))
                    msg = cursor.fetchone()
                    if msg:
                        msg = msg['message']
                    #gather applicant info
                    cursor.execute("SELECT uid FROM recs WHERE email = (%s)", (session['email'],))
                    uid = cursor.fetchone()['uid']
                    cursor.execute("SELECT fname, lname FROM users WHERE uid = (%s)", (uid,))
                    name = cursor.fetchone()
                    flash("Login successful", "success")
                    return render_template('writeletter.html', email=email, msg=msg, name=name)

            flash("Invalid email and password. Please input valid login information", "error")
        
        except:
            flash("Error while logging in, please try again", "error")

    return render_template('login.html')



#Create account 
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    user_types = ['Admin', 'Applicant', 'GS', 'CAC', 'Reviewer', 'Advisor', 'Student', 'Instructor'] # add more user types
    #enter into database
    if request.method == 'POST':
        mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
        )
        cur = mydb.cursor(dictionary=True)

    

        email = request.form['email']
        passw = request.form['password']
        fname = request.form['firstname']
        lname = request.form['lastname']
        address = request.form['address']
        ssn = request.form['ssn']
        is_type = None

        if "is_type" in request.form:
            is_type = request.form['is_type']

        if is_type:
            is_type = 'Applicant'

        #dup protection
        cur.execute("SELECT email FROM users")
        e = cur.fetchall()
        for em in e:
            if em['email'] == email:
                return render_template('create_account.html', error='Email in use', user_types=user_types)
        cur.execute("SELECT ssn FROM users")
        s = cur.fetchall()

        cur.execute("SELECT uid FROM users")
        data = cur.fetchall()

        # If we retrieved at least as many data as the number of possible 8 digit numbers, then somehow we have exceeded id limit
        if len(data) >= 9000000000:
            flash("We've reached user limit. Cannot create more", "error")
            return redirect(url_for('account'))
                    
        id_unique = True
        new_id  = random.randint(10000000, 99999999)
        while id_unique:
            new_id  = random.randint(10000000, 99999999)
            if not any(new_id in d.values() for d in data):
                id_unique = False

        # SSN matches valuein table
        for sn in s:
            if sn['ssn'] == ssn:
                return render_template('create_account.html', error='SSN in use', user_types=user_types)
            
        cur.execute("INSERT INTO users (fname, lname, email, password, address, ssn) VALUES (%s,%s,%s,%s,%s,%s)", (fname, lname, email, passw, address, ssn,))
        mydb.commit()
        cur.execute("SELECT uid FROM users WHERE email = (%s)", (email,))
        usr = cur.fetchall()

        # If is type, then that means it's an applicant
        if is_type:
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Applicant'))
            mydb.commit()
            return render_template('login.html')
        
        
        # Additional check to return to login 
        if (not ('type' in session)) or ('type' in session and not ('Admin' in session['type'])):
            return render_template('login.html')
        

        # Applicants can only have that role
        if request.form.get('Applicant'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Applicant'))
            mydb.commit()
            return render_template('create_account.html', user_types=user_types, session=session)
    
        if request.form.get('Admin'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Admin'))
            mydb.commit()
        if request.form.get('GS'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'GS'))
            mydb.commit()
        if request.form.get('CAC'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'CAC'))
            mydb.commit()
        if request.form.get('Reviewer'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Reviewer'))
            mydb.commit()
        if request.form.get('Advisor'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Advisor'))
            mydb.commit()
        if request.form.get('Instructor'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Instructor'))
            mydb.commit()
        if request.form.get('Student'):   
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (usr[0]['uid'], 'Student'))
            cur.execute("INSERT INTO student (uid) VALUES (%s)", (usr[0]['uid']))
            mydb.commit()
            
        dep = request.form['department']


        if request.form.get('GS') or request.form.get('CAC') or request.form.get('Instructor') or request.form.get('Advisor'):
            cur.execute("INSERT INTO faculty (uid, department) VALUES (%s,%s)", (usr[0]['uid'], dep))
            mydb.commit()


        if 'type' in session and 'Admin' in session['type']:
            return render_template('create_account.html', user_types=user_types, session=session)
        return render_template('login.html')
    
    return render_template('create_account.html', user_types=user_types, session=session)




@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session or len(session) == 1:
        return redirect('/')

    if 'type' in session:
        print(session['type'])
        return render_template("landing.html")
    return redirect('/')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not session or len(session) == 1:
        return redirect('/')
    # Log the user out and redirect them to the login page
    session.clear()
    return redirect('/')

@app.route('/query', methods=['GET', 'POST'])
def query():
    mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
    )
    cur = mydb.cursor(dictionary=True)
    data = None
    if request.method == 'POST':
        mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
        )
        cur = mydb.cursor(dictionary=True)
        year = request.form['year']
        degree = request.form['degree']
        semester = request.form['semester']
        if year:
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.year = (%s)", (year,))
            data = cur.fetchall()
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.status = 'admitted' AND applications.year = (%s)", (year,))
            admitted_data = cur.fetchall()
            #cur.execute("SELECT users.lname, users.fname, users.uid, users.email FROM users JOIN user_types ON users.uid = user_types.uid WHERE user_types.type = 'Alumni' AND ")
            cur.execute("SELECT COUNT(applications.uid) AS total_applicants FROM applications WHERE applications.year = (%s)", (year,))
            total_applicants_stat = cur.fetchone()
            # admitted students statistic
            cur.execute("SELECT COUNT(applications.uid) AS admit_total FROM applications WHERE applications.status = 'admitted' AND applications.year = (%s)", (year,))
            admit_total_stat = cur.fetchone()
            # rejected students statistic
            cur.execute("SELECT COUNT(applications.uid) AS reject_total FROM applications WHERE applications.status = 'denied' AND applications.year = (%s)", (year,))
            reject_total_stat = cur.fetchone()
            cur.execute("SELECT AVG(gres.total) AS gre_total FROM applications JOIN gres ON applications.gre = gres.greid WHERE applications.status = 'admitted' AND applications.year = (%s)", (year,))
            gre_stat = cur.fetchone()
            return render_template("query.html", gre_stat=gre_stat, data=data, admitted_data=admitted_data, total_applicants_stat=total_applicants_stat, admit_total_stat=admit_total_stat, reject_total_stat=reject_total_stat, type_of_query=year)
        if degree:
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.degree = (%s)", (degree,))
            data = cur.fetchall()
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.status = 'admitted' AND applications.degree = (%s)", (degree,))
            admitted_data = cur.fetchall()
            cur.execute("SELECT COUNT(applications.uid) AS total_applicants FROM applications WHERE applications.degree = (%s)", (degree,))
            total_applicants_stat = cur.fetchone()
            # admitted students statistic
            cur.execute("SELECT COUNT(applications.uid) AS admit_total FROM applications WHERE applications.status = 'admitted' AND applications.degree = (%s)", (degree,))
            admit_total_stat = cur.fetchone()
            # rejected students statistic
            cur.execute("SELECT COUNT(applications.uid) AS reject_total FROM applications WHERE applications.status = 'denied' AND applications.degree = (%s)", (degree,))
            reject_total_stat = cur.fetchone()
            cur.execute("SELECT AVG(gres.total) AS gre_total FROM applications JOIN gres ON applications.gre = gres.greid WHERE applications.status = 'admitted' AND applications.degree = (%s)", (degree,))
            gre_stat = cur.fetchone()
            return render_template("query.html", gre_stat=gre_stat, data=data, admitted_data=admitted_data, total_applicants_stat=total_applicants_stat, admit_total_stat=admit_total_stat, reject_total_stat=reject_total_stat, type_of_query=degree)
        if semester:
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.semester = (%s)", (semester,))
            data = cur.fetchall()
            cur.execute("SELECT users.lname, users.fname, users.uid FROM users JOIN applications ON users.uid = applications.uid WHERE applications.status = 'admitted' AND applications.semester = (%s)", (semester,))
            admitted_data = cur.fetchall()
            cur.execute("SELECT COUNT(applications.uid) AS total_applicants FROM applications WHERE applications.semester = (%s)", (semester,))
            total_applicants_stat = cur.fetchone()
            # admitted students statistic
            cur.execute("SELECT COUNT(applications.uid) AS admit_total FROM applications WHERE applications.status = 'admitted' AND applications.semester = (%s)", (semester,))
            admit_total_stat = cur.fetchone()
            # rejected students statistic
            cur.execute("SELECT COUNT(applications.uid) AS reject_total FROM applications WHERE applications.status = 'denied' AND applications.semester = (%s)", (semester,))
            reject_total_stat = cur.fetchone()
            cur.execute("SELECT AVG(gres.total) AS gre_total FROM applications JOIN gres ON applications.gre = gres.greid WHERE applications.status = 'admitted' AND applications.semester = (%s)", (semester,))
            gre_stat = cur.fetchone()
            return render_template("query.html", gre_stat=gre_stat, data=data, admitted_data=admitted_data, total_applicants_stat=total_applicants_stat, admit_total_stat=admit_total_stat, reject_total_stat=reject_total_stat, type_of_query=semester)
    return render_template("query.html", data=data)


@app.route('/remove_user/<id>', methods=['GET', 'POST'])
def remove_user(id):
    mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("DELETE FROM applications WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM degrees WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM gres WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM recs WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM reviews WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM user_types WHERE uid = (%s)", (id,))
    cur.execute("DELETE FROM users WHERE uid = (%s)", (id,))
    mydb.commit()
    return redirect('/home')

@app.route('/user_page/<id>', methods=['GET', 'POST'])
def user_page(id):
    if not session or len(session) == 1:
        return redirect('/')
    user_types = ['Admin', 'Applicant', 'GS', 'CAC', 'Reviewer']
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    cur_user = cur.fetchone()
    if request.method == 'POST':
        cur = mydb.cursor(dictionary=True)
        email = request.form['email']
        passw = request.form['password']
        fname = request.form['firstname']
        lname = request.form['lastname']
        address = request.form['address']
        ssn = request.form['ssn']
        is_type = request.form.get('user_type') 
        remove = request.form['remove']
        cur = mydb.cursor(dictionary=True)
        if email != '':
            cur.execute("UPDATE users SET email = (%s) WHERE uid = (%s)", (email, id,))
        elif passw != '':
            cur.execute("UPDATE users SET password = (%s) WHERE uid = (%s)", (passw, id,))
        elif fname != '':
            cur.execute("UPDATE users SET fname = (%s) WHERE uid = (%s)", (fname, id,))
        elif lname != '':
            cur.execute("UPDATE users SET lname = (%s) WHERE uid = (%s)", (lname, id,))
        elif address != '':
            cur.execute("UPDATE users SET address = (%s) WHERE uid = (%s)", (address, id,))
        elif ssn != '':
            cur.execute("UPDATE users SET ssn = (%s) WHERE uid = (%s)", (ssn, id,))
            mydb.commit()
            '''elif is_type != '':
            cur.execute("UPDATE users SET type = (%s) WHERE uid = (%s)", (is_type, id,))'''
        mydb.commit()
        return redirect('/home')

    return render_template("user_page.html", user_types=user_types, cur_user=cur_user, id=id)



'''
Applications
'''

@app.route('/view_apps/<id>', methods=['GET', 'POST'])
def view_apps(id):
    if not session or len(session) == 1:
        return redirect('/')

    mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM applications WHERE uid = (%s)", (id,))
    app = cur.fetchone()
    # if not app:
    #     error = "Applicants application inclomplete"
    #     return render_template('home.html', error=error)
    cur.execute("SELECT * FROM recs WHERE uid = (%s)", (id,))
    rec = cur.fetchall()
    cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (id,))
    deg = cur.fetchall()
    
    past_d1 = None
    past_d2 = None
    if len(deg) > 0:
        past_d1 = deg[0]
    
    if len(deg) > 1:
        past_d2 = deg[1]

        
    status_types = ['admitted', 'denied']
    transcript_types = ['F', 'T']
    if request.method == 'POST':
        is_type = request.form.get('status_type')
        if not is_type:
            is_type = 'incomplete'
        transcript_type = request.form.get('transcript_type')
        cur.execute("UPDATE applications SET status = (%s) WHERE uid= (%s)", (is_type, id,))
        cur.execute("UPDATE applications SET transcript = (%s) WHERE uid = (%s)", (transcript_type, id,))
        mydb.commit()
        cur.execute("SELECT * FROM applications WHERE uid = (%s)", (id,))
        app = cur.fetchall()[0]
        if app['transcript'] == 'T' and rec[0]['message'] and rec[1]['message'] and rec[2]['message'] and app['status'] == 'incomplete':
            print("inside")
            cur.execute("UPDATE applications SET status = 'complete' WHERE uid = (%s)", (id,))
            mydb.commit()
        print("after")
        return redirect('/home')
    return render_template("view_apps.html", past_d1=past_d1, past_d2=past_d2, rec=rec, app=app, status_types=status_types, transcript_types=transcript_types)

    
@app.route('/applicant_decision', methods=['GET', 'POST'])
def applicant_decision():
    if request.method == 'POST':
        mydb = mysql.connector.connect(
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
        )
        cur = mydb.cursor(dictionary=True)
        if request.form['accept_reject'] == 'Accept':
            cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
            cur_uid = cur.fetchone()['uid']
            cur.execute("DELETE FROM user_types WHERE uid = (%s)", (cur_uid,))
            mydb.commit()
            cur.execute("INSERT INTO user_types (uid, user_type) VALUES (%s,%s)", (cur_uid, 'Student'))
            mydb.commit()
            cur.execute("SELECT degree FROM applications WHERE applications.uid = (%s)", (cur_uid,))
            deg = cur.fetchone()['degree']
            cur.execute("INSERT INTO student (uid, program) VALUES (%s,%s)", (cur_uid, deg))
            mydb.commit()
            return redirect(url_for('logout'))
        if request.form['accept_reject'] == 'Reject':
            cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
            cur_uid = cur.fetchone()['uid']
            cur.execute("DELETE FROM applications WHERE applications.uid = (%s)", (cur_uid,))
            mydb.commit()
            return redirect(url_for('home'))

        return redirect(url_for('home'))
    return redirect(url_for('home'))

#application
@app.route('/application', methods=['GET', 'POST'])
def application():
    if not session or len(session) == 1:
        return redirect('/')

    mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
    )
    cur = mydb.cursor(dictionary=True)
    if 'Reviewer' in session['type'] and request.method == 'POST':
        mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
        cur = mydb.cursor(dictionary=True)
        userid = request.form['reviewapp']
        cur.execute("SELECT * FROM users WHERE uid=(%s)", (userid,))
        user = cur.fetchone()

        cur.execute("SELECT * FROM applications WHERE uid=(%s)", (userid, ))
        app = cur.fetchone()

        cur.execute("SELECT * FROM degrees WHERE degid=(%s)", (app['past_d1'], ))
        degrees = []
        degree1 = cur.fetchone()
        degrees.append(degree1)

        if app['past_d2']:
            cur.execute("SELECT * FROM degrees WHERE degid=(%s)", (app['past_d2'],))
            degree2 = cur.fetchone()
            degrees.append(degree2)

        cur.execute("SELECT * FROM gres WHERE greid=(%s)", (app['gre'],))
        gre = cur.fetchone()

        cur.execute("Select * From recs WHERE recid = (%s)", (app['letter'],))
        recs = cur.fetchall()
        cur.execute("Select * From recs WHERE recid = (%s)", (app['letter2'],))
        recs2 = cur.fetchall()
        cur.execute("Select * From recs WHERE recid = (%s)", (app['letter3'],))
        recs3 = cur.fetchall()
    # letterids = []
    # if app['letter_1']:
    #   letterids.append(app['letter_1'])
    # if app['letter_2']:
    #   letterids.append(app['letter_2'])
    # if app['letter_3']:
    #   letterids.append(app['letter_3'])
    # letters = []
    # for letterid in letterids:
    #   cur.execute("SELECT * FROM recs WHERE recid=(%s)", (letterid,))
    #   letters.append(cur.fetchone())
        
        return render_template("application.html", form="review", user=user, app=app, degrees=degrees, gre=gre, recs = recs, recs2=recs2, recs3=recs3 )
    if 'CAC' in session['type'] and request.method == 'POST':
        cur = mydb.cursor(dictionary=True)
        userid = request.form.get('decideapp')
        cur.execute("SELECT * FROM reviews WHERE uid=(%s)", (userid,))
        reviews = cur.fetchall()
        cur.execute("SELECT * FROM applications WHERE uid=(%s)", (userid,))
        app = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE uid=(%s)", (userid,))
        user = cur.fetchone()
        cur.execute("SELECT rating FROM reviews WHERE uid=(%s)", (userid,))
        rating_array = cur.fetchall()
        sum_rating = 0
        for i in range(len(rating_array)):
            sum_rating += int(rating_array[i]['rating'])
        if len(rating_array) == 0:
            review_avg = 0
        else:
            review_avg = sum_rating / len(rating_array)
        return render_template("decide_cac.html", reviews=reviews, app=app, user=user, review_avg=review_avg)
    
    # cur = mydb.cursor(dictionary=True)
    # create = request.form.get('createapp') 
    # view = request.form.get('viewapp') 
    # send = request.form.get('sendrec')
    # cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
    # uid = cur.fetchone()['uid']
    cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
    uid = cur.fetchone()['uid']
    cur.execute("SELECT * FROM applications WHERE uid = (%s)", (uid,))
    app = cur.fetchone()
    cur.execute("SELECT message FROM recs WHERE uid = (%s)", (uid,))
    sent = cur.fetchone()
    if sent:
        sent = sent['message']

    #create application
    if not app:
        mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
        cur = mydb.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = (%s)", (session['email'],))
        data = cur.fetchone()
        return render_template('application.html', form='create', data=data, year=datetime.now().year)

    #view application
    if app:
        mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
        cur = mydb.cursor(dictionary=True)
        # accept_or_reject = request.form['accept_reject']
        # change the applicant to a student: either a MS or PhD user type
        # if accept_or_reject == 'Accept':  
        #     cur.execute("UPDATE user_types SET VALUES user_type = (%s) WHERE uid = (%s)", ('Student', uid,))
        #     mydb.commit()

            # delete user information
        
        accept_reject = ['Accept', 'Reject']
        cur.execute("SELECT * FROM applications WHERE uid = (%s)", (uid,))
        app = cur.fetchone()
        cur.execute("SELECT * FROM gres WHERE uid = (%s)", (uid,))
        gre = cur.fetchone()
        cur.execute("SELECT writer, message FROM recs WHERE uid = (%s)", (uid,))
        rec = cur.fetchall()
        return render_template('application.html', form='view', app=app, gre=gre, rec=rec, accept_rejects=accept_reject)
    
    # if app and sent:
    #     mydb = mysql.connector.connect(
    #         host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
    #         user="admin",
    #         password="groupnine",
    #         database="university"
    #     )
    #     cur = mydb.cursor(dictionary=True)
    #     cur.execute("SELECT writer, email FROM recs WHERE uid = (%s)", (uid,))
    #     rec = cur.fetchone()
    #     print("send")
    #     return render_template('application.html', form='send', rec=rec)

    return render_template('application.html')

@app.route('/review_application', methods=['POST'])
def review_application():
    if not session or ('type' in session and 'Reviewer' not in session['type']):
        return redirect('/')
    uid = request.form.get("user_id")
    rating = request.form.get("review_rating")
    deficiency = request.form.get("review_deficiency")
    reason = request.form.get("review_reason")
    advisor = request.form.get("review_advisor")
    comments = request.form.get("review_comments")

    mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT email FROM users")
    e = cur.fetchall()

    x = None
    for a in e:
        if a['email'] == advisor:
            x = 'yes'
    if not x:
        return render_template("application.html", error='incorrect advisor email')

    cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
    review_id = cur.fetchone()['uid']
    insertId = cur.lastrowid
    # cur.execute("SELECT review FROM applications WHERE uid = (%s)", (str(uid), ))
    # reiview_cnt = cur.fetchone()['review']
    # if not reiview_cnt:
    #   reiview_cnt = 1
    # else:
    #   reiview_cnt += 1
    print("***********")
    print(str(insertId))
    print(uid)

    # cur.execute("update applications set review = " + str(insertId) + " where uid = (%s)", (str(uid), ))

    # mydb.commit()
    #add recs table
    appid = request.form.get("app_id")
    letterid1 = request.form['letterid']
    letterid2 = request.form['letter2id']
    letterid3 = request.form['letter3id']
    cur.execute("SELECT uid From recs where uid = (%s)", (str(uid), ))
    curApp = cur.fetchall()[0]['uid']
    rec_r = request.form.get("rec_rating_1")
    rec_g = request.form.get("rec_generic_1")
    rec_c = request.form.get("rec_credible_1")
    #2
    rec_r2 = request.form.get("rec_rating_2")
    rec_g2 = request.form.get("rec_generic_2")
    rec_c2 = request.form.get("rec_credible_2")
    #3
    rec_r3 = request.form.get("rec_rating_3")
    rec_g3 = request.form.get("rec_generic_3")
    rec_c3 = request.form.get("rec_credible_3")
    print("letter id = ")
    print(letterid1)
    print("rating = ")
    print(rec_r)
    print("generic = ")
    print(rec_g)
    print("credible = ")
    print(rec_c)
    cur.execute('''INSERT INTO reviews (uid, rating, deficiency, reason, advisor, comments, reviewer_id,
     rating1, generic1, credible1, rating2, generic2, credible2, rating3, generic3, credible3) 
     VALUES ((%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s))''',
                (uid, rating, deficiency, reason, advisor, comments, review_id, rec_r,rec_g,rec_c,rec_r2,rec_g2,rec_c2,rec_r3,rec_g3,rec_c3,))
    # cur.execute("update reviews set rating1=(%s), generic1=(%s),credible1=(%s) where uid = (%s)", (rec_r,rec_g,rec_c,uid,))
    # mydb.commit()
    # cur.execute("update reviews set rating2=(%s), generic2=(%s),credible2=(%s) where uid = (%s)", (rec_r2,rec_g2,rec_c2,uid,))
    # mydb.commit()
    # cur.execute("update reviews set rating3=(%s), generic3=(%s),credible3=(%s) where uid = (%s)", (rec_r3,rec_g3,rec_c3,uid,))
    mydb.commit()
    return redirect(url_for('home'))

@app.route('/cac', methods=['GET', 'POST'])
def cac():
    if not session or len(session) == 1:
        return redirect('/')
    mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM applications JOIN users on applications.uid = users.uid WHERE status='complete'")
    review_apps = cur.fetchall()
    cur.execute("SELECT * FROM applications JOIN users on applications.uid = users.uid")
    apps = cur.fetchall()
    return render_template("cac.html", review_apps=review_apps, apps=apps)
    
    
@app.route('/decide_application', methods=['POST'])
def decide_final():
    if not session or len(session) == 1:
        return redirect('/')
    status = request.form.get("decide_final")
    appid = request.form.get("app_id")
    mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("update applications set status = (%s) where appid = (%s)", (status, appid,))
    mydb.commit()
    return redirect(url_for('home'))

@app.route('/reviewer', methods=['GET', 'POST'])
def reviewer():
    mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
    )
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM applications left join users on users.uid = applications.uid WHERE applications.status = 'complete' ORDER BY users.ssn")
    apps = cur.fetchall()
    print(apps)
    validapp = []
    
    cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
    uid = cur.fetchone()['uid']
    #print(uid)
    # for app in apps:
    #   cur.execute("Select * from reviews where reviewer_id=(%s) and uid=(%s)", (str(uid), str(app["uid"])))
    #   row = cur.fetchone()
    #   if row:
    #     continue
    #   validapp.append(app)
    # print(validapp)
    return render_template("reviewer.html", app=apps)

@app.route('/thankyou', methods=['GET', 'POST'])
def thankyou():
    if not session or len(session) == 1:
        return redirect('/')
    if request.method == 'POST':
        mydb = mysql.connector.connect(
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
        cur = mydb.cursor(dictionary=True)
        cur.execute("SELECT uid FROM users WHERE email = (%s)", (session['email'],))
        uid = cur.fetchone()['uid']
        #gre 
        gre = None
        total = request.form.get('total')
        score = request.form.get('score')
        toefl = request.form.get('toefl')
        if total: 
            verbal = int(request.form['verbal'])
            quant = int(request.form['quant'])
            total = int(request.form['total'])
            year = int(request.form['yearexam'])
            cur.execute("SELECT greid FROM gres WHERE uid = (%s)", (uid,))
            gre = cur.fetchone()
            if gre:
                cur.execute("UPDATE gres SET total=(%s), verbal=(%s), quant=(%s), year=(%s) WHERE uid = (%s)", (total, verbal, quant, year, uid,))
                mydb.commit()
            else:
                cur.execute("INSERT INTO gres (uid, total, verbal, quant, year) VALUES (%s,%s,%s,%s,%s)", (uid, total, verbal, quant, year,))
                mydb.commit()
        if score:
            score = int(request.form['score'])
            subject = request.form['subject']
            cur.execute("SELECT greid FROM gres WHERE uid = (%s)", (uid,))
            gre = cur.fetchone()
            if gre:
                cur.execute("UPDATE gres SET score=(%s), subject=(%s) WHERE uid = (%s)", (score, subject, uid)) 
                mydb.commit()
            else:
                cur.execute("INSERT INTO gres (uid, score, subject) VALUES (%s,%s,%s)", (uid, score, subject,))
                mydb.commit()
        if toefl: 
            toefl = int(request.form['toefl'])
            date = int(request.form['dateexam'])
            cur.execute("SELECT greid FROM gres WHERE uid = (%s)", (uid,))
            gre = cur.fetchone()
            if gre:
                cur.execute("UPDATE gres SET toefl=(%s), date=(%s) WHERE uid = (%s)", (score, date, uid)) 
                mydb.commit()
            else:
                cur.execute("INSERT INTO gres (uid, toefl, date) VALUES (%s,%s,%s)", (uid, score, date,))
                mydb.commit()
        cur.execute("SELECT greid FROM gres WHERE uid = (%s)", (uid,))
        gre = cur.fetchone()
        if gre:
            gre = gre['greid']
        #past degrees
        d_type = request.form.get('ms')
        if d_type:
            gpa = float(request.form['gpa'])
            major = request.form['major']
            college = request.form['university']
            year = int(request.form['pdyear'])
            cur.execute("SELECT greid FROM gres WHERE uid = (%s)", (uid,))
            gre = cur.fetchone()['greid']
            cur.execute("INSERT INTO degrees (uid, type, gpa, major, college, year) VALUES (%s,%s,%s,%s,%s,%s)", (uid, d_type, gpa, major, college, year))
            mydb.commit()
        d_type = request.form['bsba']
        gpa = float(request.form['gpa2'])
        major = request.form['major2']
        college = request.form['university2']
        year = int(request.form['pdyear2'])
        cur.execute("INSERT INTO degrees (uid, type, gpa, major, college, year) VALUES (%s,%s,%s,%s,%s,%s)", (uid, d_type, gpa, major, college, year))
        mydb.commit()
        #letter
        writer = request.form['writer']
        email = request.form['email']
        title = request.form['title']
        affiliation = request.form['affiliation']
        #letter 2
        writer2 = request.form['writer2']
        email2 = request.form['email2']
        title2 = request.form['title2']
        affiliation2 = request.form['affiliation2']
        # letter 3
        writer3 = request.form['writer3']
        email3 = request.form['email3']
        title3 = request.form['title3']
        affiliation3 = request.form['affiliation3']
        #dup protection
        cur.execute("SELECT email FROM recs")
        e = cur.fetchall()
        for em in e:
            if em['email'] == email:
                return render_template('application.html', error='Recommender email in use')
        cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (uid, writer, email, title, affiliation))
        cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (uid, writer2, email2, title2, affiliation2))
        cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (uid, writer3, email3, title3, affiliation3))
        mydb.commit()
        #app
        status = 'incomplete'
        transcript = 'F'
        degree = request.form.get('degree')
        semester = request.form.get('semester')
        year = int(request.form.get('year'))
        experience = request.form['exp']
        aoi = request.form['aoi']
        cur.execute("SELECT degid FROM degrees WHERE uid = (%s)", (uid,))
        pdegrees = cur.fetchall()
        past_d1 = pdegrees[0]['degid']
        past_d2 = None
        if len(pdegrees) > 1:
            past_d2 = pdegrees[1]['degid']
        cur.execute("SELECT recid FROM recs WHERE uid = (%s)", (uid,))
        letter = cur.fetchall()
        print(letter)
        cur.execute("INSERT INTO applications (uid, status, transcript, degree, past_d1, past_d2, semester, year, experience, aoi, letter, letter2, letter3, gre) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (uid, status, transcript, degree, past_d1, past_d2, semester, year, experience, aoi, letter[0]['recid'], letter[1]['recid'], letter[2]['recid'], gre))
        mydb.commit()
        return render_template('thankyou.html')
    
    return redirect('/')

#Recommender write to applicant
@app.route('/letterwriter', methods=['GET', 'POST'])
def letterwriter():
    if not session or len(session) == 1:
        return redirect('/')
    if request.method == 'POST':
        send = 'sent'
        email = request.form['lettermail']
        message = request.form['lettermessage']
        return render_template('application.html', form=send, msg=message, email=email)

    return redirect('/home')

#Write to recommender
@app.route('/writeletter', methods=['GET', 'POST'])
def writeletter():
    if not session:
        return redirect('/')
    if request.method == 'POST':
        #add into database
        message = request.form['lettermsg']
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
        )
        cur = mydb.cursor(dictionary=True)
        cur.execute("SELECT uid FROM recs WHERE email = (%s)", (session['email'],))
        uid = cur.fetchall()[0]['uid']
        cur.execute("SELECT recid FROM recs WHERE uid = (%s)", (uid,))
        recid = cur.fetchall()[0]['recid']
        cur.execute("UPDATE recs SET message = (%s) WHERE email = (%s)", (message, session['email']))
        mydb.commit()
        cur.execute("SELECT * FROM applications WHERE uid = (%s)", (uid,))
        app = cur.fetchone()
        cur.execute("SELECT * FROM recs WHERE uid = (%s)", (uid,))
        rec = cur.fetchall()
        if app['transcript'] == 'T' and rec[0]['message'] and rec[1]['message'] and rec[2]['message'] and app['status'] == 'incomplete':
            cur.execute("UPDATE applications SET status = 'complete' WHERE uid = (%s)", (uid,))
            mydb.commit()
        return render_template('writeletter.html', msg=message)
    
    return render_template('writeletter.html', email=None)
  

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    cur = mydb.cursor(dictionary=True)
    cur.execute("DROP TABLE IF EXISTS applications")
    cur.execute("DROP TABLE IF EXISTS degrees")
    cur.execute("DROP TABLE IF EXISTS reviews")
    cur.execute("DROP TABLE IF EXISTS recs")
    cur.execute("DROP TABLE IF EXISTS gres")
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (uid int(8) AUTO_INCREMENT NOT NULL UNIQUE, fname varchar(50) NOT NULL, lname varchar(50) NOT NULL, email varchar(50) NOT NULL UNIQUE, password varchar(50) NOT NULL, address varchar(100) NOT NULL, ssn char(9) NOT NULL UNIQUE,  type enum('Admin', 'Applicant', 'GS', 'CAC', 'Reviewer') NOT NULL, PRIMARY KEY (uid))")
    cur.execute("CREATE TABLE degrees (degid int(5) AUTO_INCREMENT NOT NULL UNIQUE, uid int(8) NOT NULL, type enum('BS/BA', 'MS') NOT NULL, gpa decimal(3,2) NOT NULL, major varchar(50) NOT NULL, college varchar(50) NOT NULL, year int(4) NOT NULL, PRIMARY KEY (degid), FOREIGN KEY (uid) REFERENCES users(uid))")
    cur.execute("CREATE TABLE reviews (revid int(5) AUTO_INCREMENT NOT NULL UNIQUE, uid int(8) NOT NULL, rating ENUM('0','1','2','3') NOT NULL, deficiency varchar(100), reason char(1) NOT NULL, advisor varchar(30), comments varchar(40), reviewer_id int(8) NOT NULL, PRIMARY KEY (revid), FOREIGN KEY (uid) REFERENCES users(uid), FOREIGN KEY (reviewer_id) REFERENCES users(uid))")
    cur.execute("CREATE TABLE recs (recid int(5) AUTO_INCREMENT NOT NULL UNIQUE, uid int(8) NOT NULL, rating ENUM('1','2','3','4','5'), generic ENUM('y','n'), credible ENUM('y','n'), writer varchar(30) NOT NULL, email varchar(50) NOT NULL UNIQUE, title varchar(30) NOT NULL, affiliation varchar(30) NOT NULL, message varchar(200) DEFAULT NULL, PRIMARY KEY (recid), FOREIGN KEY(uid) REFERENCES users(uid))")
    cur.execute("CREATE TABLE gres (greid int(5) AUTO_INCREMENT NOT NULL UNIQUE, uid int(8) NOT NULL UNIQUE, total int(3) DEFAULT NULL, verbal int(3) DEFAULT NULL, quant int(3) DEFAULT NULL, year int(4) DEFAULT NULL, toefl int(3) DEFAULT NULL, score int(3) DEFAULT NULL, subject varchar(30) DEFAULT NULL, date int(4) DEFAULT NULL, PRIMARY KEY (greid), FOREIGN KEY (uid) REFERENCES users(uid))")
    cur.execute("CREATE TABLE applications (appid int(5) AUTO_INCREMENT NOT NULL UNIQUE, uid int(8) NOT NULL UNIQUE, status enum('incomplete', 'complete', 'admitted', 'denied') NOT NULL, transcript  enum('T', 'F') NOT NULL, degree enum('MS', 'PhD') NOT NULL, past_d1 int(5) NOT NULL, past_d2 int(5) DEFAULT NULL, semester enum('Fall', 'Spring') NOT NULL, year int(4) NOT NULL, experience  varchar(300) NOT NULL, aoi varchar(300) NOT NULL, letter int(5) DEFAULT NULL, review int(5) DEFAULT NULL, gre int(5) DEFAULT NULL, PRIMARY KEY (appid), FOREIGN KEY (past_d1) REFERENCES degrees(degid), FOREIGN KEY (past_d2) REFERENCES degrees(degid), FOREIGN KEY (letter) REFERENCES recs(recid), FOREIGN KEY (review) REFERENCES reviews(revid), FOREIGN KEY (gre) REFERENCES gres(greid), FOREIGN KEY (uid) REFERENCES users(uid))")
    cur.execute("INSERT INTO users VALUES (1,'admin', 'admminlname', 'admin@gmail.com', 'password', '123 abc st', '123456789', 'Admin')")
    cur.execute("INSERT INTO users VALUES (2,'gs', 'gslname', 'gs@gmail.com', 'password', '123 abc st', '123456788', 'GS')")
    cur.execute("INSERT INTO users VALUES (3,'cac', 'caclname', 'cac@gmail.com', 'password', '123 abc st', '123456780', 'CAC')")
    cur.execute("INSERT INTO users VALUES (4,'narahari', 'naraharilname', 'narahari@gmail.com', 'password', '123 abc st', '123456799', 'Reviewer')")
    cur.execute("INSERT INTO users VALUES (5,'wood', 'woodlname', 'wood@gmail.com', 'password', '123 abc st', '123426799', 'Reviewer')")
    cur.execute("INSERT INTO users VALUES (6,'heller', 'hellerlname', 'heller@gmail.com', 'password', '123 abc st', '123856799', 'Reviewer')")
    cur.execute("INSERT INTO users VALUES (12312312,'John', 'Lennon', 'john@gmail.com', 'password', '123 abc st', '111111111', 'Applicant')")
    cur.execute("INSERT INTO users VALUES (66666666,'Ringo', 'Starr', 'ringo@gmail.com', 'password', '123 abc st', '222111111', 'Applicant')")
    cur.execute("INSERT INTO degrees VALUES (1, 12312312, 'BS/BA', 3.00, 'CS', 'GWU', '2023')")
    cur.execute("INSERT INTO recs VALUES (1, 12312312, NULL, NULL, NULL, 'JT', 'jt@gmail.com', 'professor', 'GWU', 'Great student')")
    cur.execute("INSERT INTO applications VALUES (1, 12312312, 'complete', 'T', 'MS', 1, NULL, 'FALL', 2023, 'CS TA for Python', 'I love snakes', 1, NULL, NULL)")
    cur.execute("INSERT INTO degrees VALUES (2, 66666666, 'BS/BA', 2.50, 'CS', 'GWU', '2023')")
    cur.execute("INSERT INTO recs VALUES (2, 66666666, NULL, NULL, NULL, 'BC', 'bc@gmail.com', 'professor', 'GWU', NULL)")
    cur.execute("INSERT INTO applications VALUES (2, 66666666, 'incomplete', 'F', 'MS', 2, NULL, 'Spring', 2024, 'I have all the experience', 'I have zero interests', NULL, NULL, NULL)")

    mydb.commit()
    session.clear()
    return redirect('/')




''''
Class Registration
'''

# Remove from registration 
@app.route('/<id>/remove', methods=['GET', 'POST'])
def remove(id):
    if request.method == 'POST':
        session["registration"].remove(request.form["cid"])
        session.modified = True

    return redirect(url_for("register", id=id))


# Route to add a class
@app.route('/<id>/add', methods=['GET', 'POST'])
def add(id):
    if request.method == 'POST':
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True)

        # Retrieve form data
        print("Retrieving form")
        cid = request.form["cid"]
        print("Done form")

         # 1. Check if class already in currently registered class
        if cid in session["registration"]:
            flash("You've already registered for that class", "error")
            return redirect(url_for("register", id=id))


        # Check if already enrolled previously
        cursor.execute("SELECT * FROM transcript WHERE cid = %s AND stud_id = %s", (cid, id))
        data = cursor.fetchone()
        if data:
            flash("You already taken that class", "error")
            return redirect(url_for("register", id=id)) 

        
        # Check if there's an advising hold
        cursor.execute("SELECT * FROM form1 WHERE uid = %s", (id,))
        form1 = cursor.fetchall()
        if not form1:
            flash("You can't register without submitting a form1", "error")
            return redirect(url_for("register", id=id)) 

        for i in range(len(form1)):
            if form1[i]['hold'] != 0:
                flash("You have an advising hold", "error")
                return redirect(url_for("register", id=id))             

        for i in range(int(request.form["total_prereq"])):
            curr = "prereq" + str(i+1)
            prereq_info = request.form[curr].split()
            cursor.execute("SELECT * FROM transcript e JOIN course_to_class cc ON e.cid = cc.cid \
                            WHERE stud_id = %s AND dname = %s AND cnum = %s", (id, prereq_info[0], prereq_info[1]))    
        
            prereq = cursor.fetchall()
            
            if not prereq:
                flash("You do not fulfill the prerequisites for this class", "error")
                return redirect(url_for("register", id=id)) 


        # Get current class time
        cursor.execute("SELECT class_time FROM class_section WHERE cid = %s AND csem = %s AND cyear = %s", (cid, request.form["csem"], request.form["cyear"]))  
        curr_class_time = cursor.fetchone()['class_time']
        my_class_time = _process_time(curr_class_time)
        
         # Retrieve all class times for currently registering year and semester for each class and check
        for class_id in session["registration"]:
            cursor.execute("SELECT class_time FROM class_section WHERE cid = %s AND csem = %s \
                           AND cyear = %s", (class_id, request.form["csem"], request.form["cyear"]))
            other_time = cursor.fetchone()['class_time']
            each_class_time =  _process_time(other_time)

            if (my_class_time[0] > each_class_time[0] - 0.5 and my_class_time[0] < each_class_time[1] + 0.5) or (my_class_time[1] > each_class_time[0] - 0.5 and my_class_time[1] < each_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "error")
                return redirect(url_for("register", id=id)) 
          

        # Now we have to check for the classes that already got checked out but for current semester/year
        cursor.execute("SELECT class_time FROM class_section cs JOIN transcript e ON cs.cid = e.cid AND cs.csem = e.cid AND cs.cyear = e.cyear \
                       WHERE cs.csem = %s AND cs.cyear = %s AND stud_id = %s", (request.form["csem"], request.form["cyear"], id))
        time_list = cursor.fetchall()
        for each_class in time_list:
            each_class_time = _process_time(each_class['class_time'])
            if (my_class_time[0] > each_class_time[0] - 0.5 and my_class_time[0] < each_class_time[1] + 0.5) or (my_class_time[1] > each_class_time[0] - 0.5 and my_class_time[1] < each_class_time[1] + 0.5):
                flash("Schedule conflict, oops", "error")
                return redirect(url_for("register", id=id)) 
            

        # If no issue, then add to registered class
        session["registration"].append(cid)
        session.modified = True

    return redirect(url_for("register", id=id))


@app.route('/<id>/checkout', methods=['GET', 'POST'])
def checkout(id):
    # Commit data to transcript table
    if request.method == 'POST':
        mydb = mysql.connector.connect( 
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
        cursor = mydb.cursor(dictionary=True)
        semester = _get_next_semester()
        
        for cid in session["registration"]:
            print(id, cid, semester[0], semester[1])
            cursor.execute("INSERT INTO transcript (stud_id, cid, csem, cyear) VALUES (%s, %s, %s, %s)", (id, cid, semester[0], semester[1]))
            mydb.commit()

        session["registration"] = []
        session.modified = True

        flash("You've successfully registered", "success")

    return redirect(url_for("register", id=id)) 


# Class registration page
@app.route('/<id>/register', methods=['GET', 'POST'])
def register(id):
    if 'type' in session and (id == None or id=="register" or (id.isdigit() and int(id) != session['id'])):
        return redirect(url_for("register", id=session['id']))
    elif 'id' not in session:
        return redirect(url_for('home'))
    
    
    # Connect to database
    mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
    cursor = mydb.cursor(dictionary=True)
    semester = _get_next_semester()
    query = "SELECT * FROM class_section cs JOIN course_to_class cc ON cs.cid = cc.cid \
            JOIN course_info ci ON cc.dname = ci.dname AND cc.cnum = ci.cnum WHERE \
            cs.csem = %s AND cs.cyear = %s"
    params = [semester[0], semester[1]]

    # If request = POST, query based on form data (i.e search function)
    if request.method == 'POST':   
        dname = request.form["dname"]
        cnum = request.form["cnum"]
        cid = request.form["cid"]
        title = request.form["title"]  

        if dname != "":
            query += " AND ci.dname LIKE  %s"
            params.append(f"%{dname}%")
        
        if cnum != "":
            query += " AND ci.cnum = %s"
            params.append(cnum)

        if cid != "":
            query += " AND cs.cid = %s"
            params.append(cid)

        if title != "":
            query += " AND ci.title LIKE %s"
            params.append(f"%{title}%")
       
    cursor.execute(query, params)
    classes = cursor.fetchall()

    instructor_list = {}
    for each_class in classes:
        cursor.execute("SELECT fname, lname FROM users WHERE uid = %s", (each_class['fid'],))
        instructor_list[each_class['fid']] = cursor.fetchone()

    cursor.execute("SELECT * FROM prerequisite p JOIN course_info c ON p.prereq_dname = c.dname AND p.cnum = c.cnum ORDER BY p.cnum")    
    prereqs = cursor.fetchall()

    renderer = {
        "cid": "Class ID",
        "csem": "Semester",
        "cyear": "Year",
        "day_of_week": "Day of week",
        "class_time": "Class Time",
        "fid": "Instructor",
        "dname": "Department",
        "cnum": "Course Number",
        "class_section": "Class Section",
        "title": "Title",
        "credits": "Credits",
    }
    cursor.execute("SELECT * FROM transcript e JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear \
                   JOIN course_to_class j ON c.cid = j.cid JOIN course_info i ON j.dname = i.dname AND j.cnum = i.cnum WHERE \
                   e.stud_id = %s AND e.csem = %s AND e.cyear = %s", (session['id'],semester[0], semester[1]))        
    schedule = cursor.fetchall()

    return render_template('registration.html', schedule=schedule, renderer=renderer, instructor_list=instructor_list, classes=classes, prereqs=prereqs, session=session, semester=semester)


# Course catalog page
@app.route('/catalog')
def catalog():
    mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT dname FROM course_info GROUP BY dname ORDER BY dname ASC")
    dept = cursor.fetchall()
    course = {}
    for row in dept:
        cursor.execute("SELECT * FROM course_info WHERE dname = %s", (row["dname"],))
        course[row["dname"]] = cursor.fetchall()

    cursor.execute("SELECT * FROM prerequisite p JOIN course_info c ON p.dname = c.dname AND p.cnum = c.cnum ORDER BY p.cnum")    
    prereq = cursor.fetchall()
    logged = False

    if 'type' in session:
        logged = True

    return render_template('catalog.html', dept=dept, course=course, prereq=prereq, logged=logged)


@app.route('/form', methods = ['GET', 'POST'])
def form(): 
    error = False
    message = " "

    cursor = mydb.cursor(dictionary=True)

    if "Student" not in session["type"]:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        univId = request.form["field_Id"]
        fname = request.form["field_fname"]
        lname = request.form["field_lname"]
        
        i = 1 
        cs_count = 0 

        for i in range(1, 13):
            currentDept = "class" + str(i) + "dept"
            courseDept = request.form[currentDept]
            currentNum = "class" + str(i) + "num"
            courseNum = request.form[currentNum]

            if courseNum == '':
                error = True
                print("Not valid")
                continue

            if courseDept == "CSCI":
                cs_count += 1
            
            cursor.execute('SELECT dname, cnum FROM course_info WHERE dname = (%s) AND cnum = (%s)', (courseDept, courseNum))
            print(cs_count)
            column_names = [i[0] for i in cursor.description]
            result = [dict(zip(column_names, row)) for row in cursor.fetchall()]

            if len(result) == 0:
                error = True
                message = "You have selected one or more invalid courses"
                return render_template('form.html', error = error, message = message)
            
            cursor.execute("INSERT INTO form1 (uid, courseDept, courseNum, hold) VALUES ((%s),(%s),(%s),(%s))", (univId, courseDept, courseNum, True))
            message = "Form 1 Submitted"
            mydb.commit()

        return render_template('form.html', error = error, message = message)
    return render_template('form.html', error = error, message = message)


# Assign new advisor to student
@app.route('/assign', methods = ['GET', 'POST'])
def assign():
    if "GS" not in session["type"]:
        return redirect(url_for('login'))

    mydb = mysql.connector.connect( 
            host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
            user="admin",
            password="groupnine",
            database="university"
        )
    
    cursor = mydb.cursor(dictionary=True)
    
    if request.method == 'POST':
        advisorId = request.form['field_advId']
        studentId = request.form['field_stuId']
        
        # Check if the input ID is a valid advisor
        cursor.execute("SELECT * FROM users u JOIN user_types t ON u.uid = t.uid WHERE u.uid = %s AND t.user_type = 'Advisor'", (advisorId,))
        data = cursor.fetchall()

        if not data:
            flash("Invalid ID, please choose a valid Advisor", "error")
            return redirect(url_for('grad_secretary'))

        try:
            cursor.execute('UPDATE student SET advisorid = (%s) WHERE uid = (%s)', (advisorId, studentId,))
            mydb.commit()
            flash("Succesfully Assigned", "success")
        except:
            flash("Unsuccessful assignment. Please try again", "error")
        
    return redirect(url_for('grad_secretary'))

# Drop courses
@app.route('/drop', methods=['GET', 'POST'])
def drop():
    if request.method == 'POST':
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True)
        stud_id = request.form['stud_id']
        cid = request.form["cid"]
        csem = request.form["csem"]
        cyear = request.form["cyear"]

        cursor.execute("DELETE FROM transcript WHERE stud_id = %s AND cid = %s AND csem = %s AND cyear = %s", (stud_id, cid, csem, cyear))
        mydb.commit()

        # Update GPA
        cursor.execute(''' SELECT tr.cid, grade, credits FROM transcript tr 
                    JOIN course_to_class cc ON tr.cid = cc.cid 
                    JOIN course_info ci ON cc.dname = ci.dname AND ci.cnum = cc.cnum 
                    WHERE stud_id = %s''', (stud_id,))
        courses = cursor.fetchall()

        newGPA = _calc_GPA(courses)
        if not isinstance(newGPA, int):
            cursor.execute("UPDATE student SET GPA = %s WHERE uid = %s", (newGPA[0], stud_id))
            mydb.commit()
        

        if request.form['origin'] != 'registration':
            return redirect(url_for('student'))

    return redirect(url_for('register', id=session['id']))

# Personal information page
# Should display current schedule + transcript, past schedules, and transcript
@app.route('/student', methods=['GET', 'POST'])
def student():
    if 'type' in session and 'Student' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM transcript e JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear JOIN course_to_class j ON c.cid = j.cid JOIN course_info i ON j.dname = i.dname AND j.cnum = i.cnum WHERE e.stud_id = %s", (session['id'],))        
        schedule = cursor.fetchall()

        cursor.execute("SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE u.uid = %s ", (session['id'],))
        student = cursor.fetchone()

        cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (session['id'],))
        user_types = cursor.fetchall()

        cursor.execute('''SELECT csem, cyear FROM transcript e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                            ORDER BY e.cyear DESC, e.csem''', (session['id'],))
        semesters = cursor.fetchall()

        curr_sem = _get_curr_semester()
        next_sem = _get_next_semester()

        cursor.execute("SELECT * FROM users WHERE uid = %s", (student['advisorid'],))
        advisor = cursor.fetchone()
       
        cursor.execute('''SELECT t.stud_id, t.grade, ci.dname, ci.cnum, ci.title, ci.credits, cs.csem, cs.cyear, cs.day, cs.class_time FROM transcript t 
                            JOIN class_section cs ON t.cid = cs.cid AND t.csem = cs.csem AND t.cyear = cs.cyear JOIN course_to_class ctc ON cs.cid = ctc.cid 
                            JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum WHERE t.stud_id = (%s)''', (session["id"],))
        courses = cursor.fetchall()


        # Update GPA
        cursor.execute(''' SELECT tr.cid, grade, credits FROM transcript tr 
                    JOIN course_to_class cc ON tr.cid = cc.cid 
                    JOIN course_info ci ON cc.dname = ci.dname AND ci.cnum = cc.cnum 
                    WHERE stud_id = %s''', (student['uid'],))
        classes = cursor.fetchall()
        newGPA = _calc_GPA(classes)
        if not isinstance(newGPA, int):
            cursor.execute("UPDATE student SET GPA = %s WHERE uid = %s", (newGPA[0], student['uid']))
            mydb.commit()

        return render_template('student.html', schedule=schedule, student=student, semesters=semesters, curr_sem=curr_sem, next_sem=next_sem, advisor=advisor, courses=courses, user_types=user_types)
    return redirect('/')


# Alumbus page for past transcript
@app.route('/alumni', methods=['GET', 'POST'])
def alumni():
    if 'type' in session and 'Alumni' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 
        cursor.execute("SELECT * FROM transcript e JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear JOIN course_to_class j ON c.cid = j.cid JOIN course_info i ON j.dname = i.dname AND j.cnum = i.cnum WHERE e.stud_id = %s", (session['id'],))        
        schedule = cursor.fetchall()

        cursor.execute("SELECT * FROM users u JOIN alumni s ON u.uid = s.uid WHERE u.uid = %s ", (session['id'],))
        student = cursor.fetchone()

        cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (session['id'],))
        user_types = cursor.fetchall()

        cursor.execute('''SELECT csem, cyear FROM transcript e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                            ORDER BY e.cyear DESC, e.csem''', (session['id'],))
        semesters = cursor.fetchall()

        cursor.execute('''SELECT t.stud_id, t.grade, ci.dname, ci.cnum, ci.title, ci.credits, cs.csem, cs.cyear, cs.day, cs.class_time 
                        FROM transcript t JOIN class_section cs ON t.cid = cs.cid AND t.csem = cs.csem AND t.cyear = cs.cyear 
                        JOIN course_to_class ctc ON cs.cid = ctc.cid 
                        JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum WHERE t.stud_id = (%s)''', (session["id"],))
        
        courses = cursor.fetchall()

        # Update GPA to make sure it's correct
        cursor.execute(''' SELECT tr.cid, grade, credits FROM transcript tr JOIN course_to_class cc ON tr.cid = cc.cid 
                            JOIN course_info ci ON cc.dname = ci.dname AND ci.cnum = cc.cnum WHERE stud_id = %s''', (session['id'], ))
        courses = cursor.fetchall()
        newGPA = _calc_GPA(courses)
        if not isinstance(newGPA, int):
            cursor.execute("UPDATE alumni SET GPA = %s WHERE uid = %s", (newGPA[0], session['id']))
            mydb.commit()

        return render_template('alumni.html', schedule=schedule, student=student, semesters=semesters, courses=courses, user_types=user_types)
    return redirect('/')


# Instructor page
@app.route('/instructor', methods=['GET', 'POST'])
def instructor():
    if 'type' in session and 'Instructor' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 

        cursor.execute('''SELECT * FROM users u JOIN faculty f ON u.uid = f.uid JOIN class_section c 
                              ON f.uid = c.fid WHERE u.uid = %s ''', (session['id'],))
        faculty = cursor.fetchall()[0]

        cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (session['id'],))
        user_types = cursor.fetchall()


        course_query = "SELECT * FROM class_section c JOIN course_to_class i ON c.cid = i.cid JOIN course_info o ON i.dname = o.dname AND i.cnum = o.cnum WHERE fid = %s"
        params = [session['id']]

        # Search functionality
        if request.method == 'POST':
            print("hey")
            dname = request.form['dname']
            cnum = request.form['cnum']
            cid = request.form['cid']
            title = request.form['title']
            
            if title != "":
                course_query += " AND o.title LIKE %s"
                params.append(f"%{title}%")

            if dname != "":
                course_query += " AND o.dname LIKE %s"
                params.append(f"%{dname}%")

            if cnum != "":
                course_query += " AND o.cnum LIKE %s"
                params.append(cnum)

            if cid != "":
                course_query += " AND c.cid = %s"
                params.append(cid)

        
        cursor.execute(course_query, params)
        course = cursor.fetchall()

        cursor.execute('''SELECT csem, cyear, fid FROM class_section c WHERE c.fid = %s GROUP BY c.csem, c.cyear 
                            ORDER BY c.cyear DESC, c.csem''', (session['id'],))
        semesters = cursor.fetchall()   

        student = {}
        for row in course:
            cursor.execute("SELECT * FROM transcript e JOIN student s ON e.stud_id = s.uid JOIN users u ON s.uid = u.uid WHERE e.cid = %s", (row["cid"],))
            student[row["cid"]] = cursor.fetchall()

        return render_template('instructor.html', faculty=faculty, course=course, student=student, semesters=semesters, user_types=user_types)
    return redirect('/')

# Grad secretary page
@app.route('/grad_secretary', methods=['GET', 'POST'])
def grad_secretary():
    if 'type' in session and 'GS' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 

        semesters = {}
        classes = {}
        user_types = {}
        advisors = {}

        # Get the secretary information
        cursor.execute("SELECT * FROM users WHERE uid = %s", (session['id'],))
        secretary_info = cursor.fetchone()
        
        cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (session['id'],))
        user_types[session['id']] = cursor.fetchall()

        student_query = "SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE 1=1"
        alumni_query = "SELECT * FROM users u JOIN alumni a ON u.uid = a.uid WHERE 1=1"
        stud_list_query = "SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE 1=1"
        grad_list_query = "SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE s.rdygrad != 0"
        applicant_query = "SELECT * FROM users u JOIN user_types t on u.uid = t.uid WHERE t.user_type = 'Applicant'"

        queries_list = {'student': [student_query, []], 'alumni': [alumni_query, []], 'stud_list': [stud_list_query, []], 'grad_list': [grad_list_query, []], 'applicants': [applicant_query, []]}

        # Search function 
        if request.method == 'POST':
            origin = request.form['origin']

            if origin == 'applicant-tab':
                fname = request.form['fname']
                lname = request.form['lname']
                uid = request.form['uid']
                if fname != "":
                    queries_list['applicants'][0] += " AND u.fname LIKE %s"
                    queries_list['applicants'][1].append(f"%{fname}%")

                if lname != "":
                    queries_list['applicants'][0] += " AND u.lname LIKE %s"
                    queries_list['applicants'][1].append(f"%{lname}%")

                if uid != "":
                    queries_list['applicants'][0] += " AND u.uid = %s"
                    queries_list['applicants'][1].append(uid)


            if origin == 'graduating-tab':
                admit_year = request.form['admit_year']
                program = request.form['degree']
                if admit_year != "":
                    queries_list['grad_list'][0] += " AND s.year LIKE %s"
                    queries_list['grad_list'][1].append(f"%{admit_year}%")
                
                if program != "":
                    queries_list['grad_list'][0] += " AND s.program LIKE %s"
                    queries_list['grad_list'][1].append(f"%{program}%")

            
            if origin == 'current-tab':
                admit_year = request.form['admit_year']
                program = request.form['degree']
                if admit_year != "":
                    queries_list['stud_list'][0] += " AND s.year LIKE %s"
                    queries_list['stud_list'][1].append(f"%{admit_year}%")
                
                if program != "":
                    queries_list['stud_list'][0] += " AND s.program LIKE %s"
                    queries_list['stud_list'][1].append(f"%{program}%")


            if origin == 'student-tab':
                fname = request.form['fname']
                lname = request.form['lname']
                uid = request.form['uid']
                if fname != "":
                    queries_list['student'][0] += " AND u.fname LIKE %s"
                    queries_list['student'][1].append(f"%{fname}%")

                if lname != "":
                    queries_list['student'][0] += " AND u.lname LIKE %s"
                    queries_list['student'][1].append(f"%{lname}%")

                if uid != "":
                    queries_list['student'][0] += " AND u.uid = %s"
                    queries_list['student'][1].append(uid)
            

            if origin == 'alumni-tab':
                grad_sem = request.form['grad_sem']
                grad_year = request.form['grad_year']
                program = request.form['degree']

                if grad_sem != "":
                    queries_list['alumni'][0] += " AND a.grad_sem LIKE %s"
                    queries_list['alumni'][1].append(f"%{grad_sem}%")

                if grad_year != "":
                    queries_list['alumni'][0] += " AND a.grad_year LIKE %s"
                    queries_list['alumni'][1].append(f"%{grad_year}%")

                if program != "":
                    queries_list['alumni'][0] += " AND a.program LIKE %s"
                    queries_list['alumni'][1].append(f"%{program}%")

            
        # Get all students from user tables with their course information
     
        for key, query in queries_list.items():
            cursor.execute(query[0], query[1])
            queries_list[key] = cursor.fetchall()
        
        for row in queries_list['student']: 
            cursor.execute('''SELECT csem, cyear FROM transcript e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                            ORDER BY e.cyear DESC, e.csem''', (row['uid'],))
            semesters[row['uid']] = cursor.fetchall()

        
            cursor.execute('''SELECT * FROM transcript e 
                            JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear
                            JOIN course_to_class ctc ON c.cid=ctc.cid
                            JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                            WHERE e.stud_id = %s''', (row['uid'],))
            classes[row['uid']] = cursor.fetchall()

            cursor.execute("SELECT * FROM users WHERE uid = %s", (row['advisorid'],))
            advisors[row['uid']] = cursor.fetchone()

            cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (row['uid'],))
            user_types[row['uid']] = cursor.fetchall()
        
        print(queries_list['student'])

        return render_template('secretary.html', secretary_info=secretary_info, classes=classes, semesters=semesters, advisors=advisors, user_types=user_types, queries_list=queries_list)

    return redirect('/')


# Admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'type' in session and 'Admin' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 

        semesters = {}
        classes = {}
        taught = {}
        advisors = {}
        user_types = {}
        user_dict = {}
        sections = []
     
        # Personal (own) info
        cursor.execute("SELECT * FROM users u JOIN user_types t ON u.uid = t.uid WHERE t.user_type = 'Admin' AND u.uid = %s", (session['id'],))
        admin_info = cursor.fetchone()

  
        # All user info queries should go heres
        student_query = "SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE 1=1"
        instructor_query = "SELECT * FROM users u JOIN faculty f ON u.uid = f.uid WHERE 1=1"
        admin_query = "SELECT * FROM users u JOIN user_types t ON u.uid = t.uid WHERE t.user_type = 'Admin'"
        gs_query = "SELECT * FROM users u JOIN user_types t ON u.uid = t.uid WHERE t.user_type = 'GS'"

        # Add user additional queries here

        # Add query to dictionary for easy looping
        queries = {"Student": student_query, 
                   "Instructor": instructor_query, 
                   "Admin": admin_query,
                   "GS": gs_query}

        params = []

        # Search function
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uid = request.form['uid']

            for key, query in queries.items():
                if fname != "":
                    queries[key] += " AND u.fname LIKE %s"

                if lname != "":
                    queries[key]  += " AND u.lname LIKE %s"
        
                if uid != "":
                    queries[key]  += " AND u.uid = %s"


            if fname != "":
                params.append(f"%{fname}%")

            if lname != "": 
                params.append(f"%{lname}%")

            if uid != "":
                params.append(uid)


        # Execute the query for each info
        for key,val in queries.items():
            cursor.execute(val, params)
            user_dict[key] = cursor.fetchall()


        # Get all the user types of each user
        for key,val in user_dict.items():
            for user in val:
                cursor.execute("SELECT * FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (user['uid'],))
                user_types[user['uid']] = cursor.fetchall()



        # Get the classes taught by the instructors
        for row in user_dict["Instructor"]:
            cursor.execute('''SELECT * FROM class_section c
                            JOIN course_to_class ctc ON c.cid=ctc.cid
                            JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                            WHERE c.fid = %s''', (row['uid'],))
            taught[row['uid']] = cursor.fetchall()



        # Get each class information
        for row in user_dict['Student']:
            cursor.execute('''SELECT csem, cyear FROM transcript e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                                ORDER BY e.cyear DESC, e.csem''', (row['uid'],))
            semesters[row['uid']] = cursor.fetchall()

        
            cursor.execute('''SELECT * FROM transcript e 
                                JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear
                                JOIN course_to_class ctc ON c.cid=ctc.cid
                                JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                                WHERE e.stud_id = %s''', (row['uid'],))
            classes[row['uid']] = cursor.fetchall()

            cursor.execute("SELECT * FROM users WHERE uid = %s", (row['advisorid'],))
            advisors[row['uid']] = cursor.fetchone()

        cursor.execute("SELECT csem, cyear FROM class_section GROUP BY csem, cyear ORDER BY cyear DESC, csem")
        sections = cursor.fetchall()

        return render_template('admin.html', admin_info=admin_info, user_dict=user_dict, taught=taught, sections=sections, semesters=semesters,classes=classes, advisors=advisors, user_types=user_types)
          
    return redirect('/')



@app.route("/update_grade", methods=['GET', 'POST'])
def update_grade():
    if request.method == 'POST':
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True)

        grade = request.form['grade']
        stud_id = request.form['stud_id'] 
        class_id = request.form['class']
        csem = request.form['csem']
        cyear = request.form['cyear']
        origin = request.form['origin']

        # Update grade
        cursor.execute("UPDATE transcript SET grade = %s WHERE stud_id = %s AND cid = %s AND csem = %s AND cyear= %s", (grade, stud_id, class_id, csem, cyear))
        mydb.commit()

        # Update GPA
        cursor.execute(''' SELECT tr.cid, grade, credits FROM transcript tr 
                    JOIN course_to_class cc ON tr.cid = cc.cid 
                    JOIN course_info ci ON cc.dname = ci.dname AND ci.cnum = cc.cnum 
                    WHERE stud_id = %s''', (stud_id,))
        courses = cursor.fetchall()
        newGPA = _calc_GPA(courses)
        if not isinstance(newGPA, int):
            print(newGPA)
            cursor.execute("UPDATE student SET GPA = %s WHERE uid = %s", (newGPA[0], stud_id))
            mydb.commit()
        
        return redirect(url_for(origin))
    

@app.route('/advisor', methods=['GET', 'POST'])
def advisor():
    if 'type' in session and 'Advisor' in session["type"]:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
    
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users u JOIN user_types t ON u.uid = t.uid WHERE t.user_type = 'Advisor' AND u.uid = %s", (session['id'],))
        advisor_info = cursor.fetchall()[0]

        cursor.execute("SELECT user_type FROM user_types JOIN users ON user_types.uid = users.uid WHERE users.uid = %s" , (session['id'],))
        user_types = cursor.fetchall()


        # Get students information
        semesters = {}
        classes = {}
        params = [session['id']]
        student_query = "SELECT * FROM users u JOIN student s ON u.uid = s.uid WHERE s.advisorid = %s"
        

        # Search function 
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            uid = request.form['uid']

            if fname != "":
                student_query += " AND u.fname LIKE %s"
                params.append(f"%{fname}%")

            if lname != "":
                student_query += " AND u.lname LIKE %s"
                params.append(f"%{lname}%")

            if uid != "":
                student_query += " AND u.uid = %s"
                params.append(uid)


        # Get all students from user tables with their course information
        cursor.execute(student_query, params)
        student_list = cursor.fetchall()
        
        for student in student_list: 
            cursor.execute('''SELECT csem, cyear FROM transcript e WHERE e.stud_id = %s GROUP BY e.csem, e.cyear
                            ORDER BY e.cyear DESC, e.csem''', (student['uid'],))
            semesters[student['uid']] = cursor.fetchall()

        
            cursor.execute('''SELECT * FROM transcript e 
                            JOIN class_section c ON e.cid = c.cid AND e.csem = c.csem AND e.cyear = c.cyear
                            JOIN course_to_class ctc ON c.cid=ctc.cid
                            JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum
                            WHERE e.stud_id = %s''', (student['uid'],))
            classes[student['uid']] = cursor.fetchall()


        return render_template('advisor.html', advisor_info=advisor_info, user_types=user_types, semesters=semesters, student_list=student_list, classes=classes)

    return redirect(url_for('login'))

@app.route('/graduating')
def graduating():
    cursor = mydb.cursor(dictionary=True)
    if "Student" not in session["type"]:
        return redirect(url_for('login'))
    
    #Create course list before they submit
    cursor.execute("SELECT t.stud_id, t.grade, ci.dname, ci.cnum, ci.title, ci.credits, cs.csem, cs.cyear, cs.day, cs.class_time FROM transcript t JOIN class_section cs ON t.cid = cs.cid AND t.csem = cs.csem AND t.cyear = cs.cyear JOIN course_to_class ctc ON cs.cid = ctc.cid JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum WHERE t.stud_id = (%s)", (session["id"],))
    courses = cursor.fetchall()
    print(courses)
    return render_template('graduating.html', courses = courses)


@app.route('/apply2grad')
def apply2grad():  
    #Get all courses
    if 'type' in session:
        print(session['type'])
    if 'type' in session and 'Student' in session['type']:
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 

        cursor.execute('''SELECT t.stud_id, t.grade, ci.dname, ci.cnum, ci.title, ci.credits, cs.csem, cs.cyear, cs.day, cs.class_time FROM transcript t 
                            JOIN class_section cs ON t.cid = cs.cid AND t.csem = cs.csem AND t.cyear = cs.cyear JOIN course_to_class ctc ON cs.cid = ctc.cid 
                            JOIN course_info ci ON ctc.dname = ci.dname AND ctc.cnum = ci.cnum WHERE t.stud_id = (%s)''', (session["id"],))
        courses = cursor.fetchall()
        mydb.commit()
        #see if they are masters or phd
        cursor.execute("SELECT * FROM student WHERE uid=(%s)",(session['id'],))
        user = cursor.fetchone()
        programName = user['program']
        

        gpaResult = _calc_GPA(courses)
       
        
        if isinstance(gpaResult, int)and gpaResult == -1:
            flash("You have not completed any courses yet!", "error")
            return redirect(url_for('student'))

        totalGPA = gpaResult[0]
        sumCredit = gpaResult[1]
        belowBcounter = gpaResult[2]
       

        canthisgraduatestudentgraduate = False
        OutsideCS = 0

        if programName == 'MS':
            print("this passed")
            print(belowBcounter)
            #If Total GPA is above or equal to 3 and total credits is more than 30 
            #no more than two grades below a B, then see if they completed all the req class
            if belowBcounter >= 3:
                flash("You are currently under academic suspension", "error")
                return redirect(url_for('student'))

            
            if totalGPA >= 3.0 and sumCredit >= 30 and belowBcounter<=2:
                CSCI6212 = False
                CSCI6221 = False
                CSCI6461 = False
                
                for course in courses:
                    if course['cnum'] == 6212:
                        print("1 pass")
                        CSCI6212 = True
                    if course['cnum'] == 6221:
                        print("2 pass")
                        CSCI6221 = True
                    if course['cnum'] == 6461:
                        print("3 pass")
                        CSCI6461 = True                    
                    if course['dname'] != 'CSCI':
                        OutsideCS += 1
                #If they have taken all the courses needed and at most 2 out of CSCI
                if CSCI6461 and CSCI6221 and CSCI6461 and OutsideCS<=2:
                #    print(OutsideCS)
                    canthisgraduatestudentgraduate = True
        

        if programName == 'PhD':
            if belowBcounter >= 3:
                flash("You are currently under academic suspension", 'error')
                return redirect(url_for('student'))

            #Total GPA 3.5 or higher, 36 credit hours
            if totalGPA >= 3.5 and sumCredit == 36 and belowBcounter <= 1:
                cursor.execute("SELECT decision FROM thesis WHERE uid = (%s)", (session["id"],))
                decision = cursor.fetchall()
                if decision: 
                    for course in courses:
                        if course['dname'] == 'CSCI':
                            #OutsideCS in this case is actually courses in CS but im lazy
                            OutsideCS += course['credits']
                    if OutsideCS >= 30:
                        canthisgraduatestudentgraduate = True
        
        if canthisgraduatestudentgraduate == True:
            cursor.execute("UPDATE student SET rdygrad = TRUE WHERE uid = (%s)",(session['id'],))
            mydb.commit()
            flash("You have applied for graduation.", "success")
        else:
            flash('You are not eligible to graduate, contact your advisor', 'error')
        
        
        return redirect(url_for('student'))

    return redirect(url_for('login'))


@app.route('/update_info', methods = ['GET', 'POST'])
def update_info():
    if request.method == 'POST' and 'id' in session:
        uid = request.form['uid']
        origin = request.form["origin"]
        
        if "type_list" in request.form:
            type_to_remove = request.form["type_list"]

        print("Why")
        mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
        cursor = mydb.cursor(dictionary=True) 
        
    
        for key, val in request.form.items():
            if val != "" and key != "origin" and key != "uid" and key != "type_list":
                if key == "remove_type" and val == "remove":
                    cursor.execute("DELETE FROM user_types WHERE uid = %s AND user_type = %s", (uid, type_to_remove))

                elif key == "add_type":
                    cursor.execute("INSERT INTO user_types(uid, user_type) VALUE (%s, %s)", (uid, val))

                elif key == "department":
                    query = "UPDATE faculty SET " + key + " = %s WHERE uid = %s "
                    params = (key, uid)
                    cursor.execute(query, params)

                else:
                    query = "UPDATE users SET " + key + " = %s WHERE uid = %s "
                    params = (val, uid)
                    print(query, params)
                    cursor.execute(query, params)
                
                mydb.commit()
            
        return redirect(url_for(origin))
    
    return redirect(url_for("home"))

@app.route('/gsViewAdvisee', methods = ['GET','POST'])
def gsViewAdvisee():
    mydb = mysql.connector.connect( 
                host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                user="admin",
                password="groupnine",
                database="university"
            )
    cursor = mydb.cursor(dictionary=True)
    if "GS" not in session["type"]:
        return redirect(url_for('login'))
    if 'type' in session:
        if request.method == 'POST':
            advisorId = request.form['field_advId']
            cursor.execute("SELECT fname, lname FROM users WHERE uid = (%s)", (advisorId,))
            advisor = cursor.fetchall()
            cursor.execute("SELECT fname, lname FROM users u JOIN student s ON u.uid = s.uid WHERE s.advisorid = (%s)", (advisorId,))
            students = cursor.fetchall()

            return render_template('gsViewAdvisee.html', students = students, advisor = advisor)

        return render_template('gsViewAdvisee.html')

@app.route('/writeThesis', methods = ['GET', 'POST'])
def writeThesis(): 
    message = " " 
    cursor = mydb.cursor(dictionary=True)
    if "Student" not in session["type"]:
        return redirect(url_for('login'))
    if request.method == 'POST':
        thesis = request.form['field_thesis']
        if thesis:
            cursor.execute("INSERT INTO thesis (thesis, uid, decision) VALUES ((%s), (%s), (%s))", (thesis, session["id"], False))
            mydb.commit()
            message = "Thesis has been submitted"
            return render_template('writeThesis.html', message=message)
        message = "You have not written a thesis"

    return render_template('writeThesis.html', message = message)

#adv
@app.route('/thesis', methods = ['GET', 'POST'])
def thesis():
    if 'type' in session:
        if 'Advisor' not in session['type']:
            return redirect(url_for('home'))
        
        mydb = mysql.connector.connect( 
                    host="phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com",
                    user="admin",
                    password="groupnine",
                    database="university"
                )
        cursor = mydb.cursor(dictionary=True)
        
        #For the  select
        cursor.execute("SELECT * FROM thesis JOIN student ON thesis.uid = student.uid JOIN users ON student.uid = users.uid WHERE advisorid =(%s)",(session['id'],))
        students = cursor.fetchall()

        #If post select specific student and display
        if request.method == 'POST':
            cursor.execute("SELECT * FROM thesis JOIN student ON thesis.uid = student.uid WHERE thesis.uid=(%s)",(request.form["field_id"],))
            
            thesis = cursor.fetchall()

            print(thesis[0]['thesis'])
            return render_template('thesis.html', students = students, thesis=thesis)
        return render_template('thesis.html', students=students)
    return redirect(url_for('login'))

#adv
@app.route('/thesis_approve', methods = ['GET', 'POST'])
def thesis_approve():
    cursor = mydb.cursor(dictionary=True)

    if "Advisor" not in session["type"]:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form['y/n'] == "yes":
            cursor.execute("UPDATE thesis SET decision = TRUE WHERE uid=(%s)",(request.form['uid'],))
            mydb.commit()
            print("Accepted")
        else:
            print("Rejected")
            cursor.execute("UPDATE thesis SET decision = FALSE WHERE uid=(%s)",(request.form['uid'],))
            mydb.commit()
    return redirect(url_for('thesis'))

@app.route('/gsecgradbtn/<int:uid>', methods=['POST'])
def gsecgradbtn(uid):
    if "GS" not in session["type"]:
        return redirect(url_for('login'))
    
    if 'type' in session: 
        cursor = mydb.cursor(dictionary=True)

        # Get the student's information from the students table
        cursor.execute("SELECT * FROM users JOIN student ON users.uid = student.uid WHERE users.uid = (%s)", (uid,))
        student = cursor.fetchone() #Potential error
        print(student)

        if student:
            curr_semester = _get_curr_semester()

            print(student['fname'])
            # Insert the student's information into the alumni table
            cursor.execute("INSERT INTO alumni (u(id, GPA, grad_sem, grad_year, program) VALUES (%s, %s, %s, %s, %s)", (student['uid'], student['GPA'], curr_semester[0], curr_semester[1], student['program']))
        
            # Delete the student's information from the students table
            cursor.execute("DELETE FROM student WHERE uid = (%s)", (uid,))
            cursor.execute("DELETE FROM user_types WHERE uid = (%s) AND user_type = (%s)", (uid, "Student", ) )

            cursor.execute("INSERT INTO user_types (uid, user_type) VALUES (%s, %s)", (student['uid'], "Alumni",))

            mydb.commit()

    return redirect(url_for('grad_secretary')) 


@app.route('/viewForm', methods = ['GET','POST'])
def viewForm():
    message = " "
    error = False 
    cursor = mydb.cursor(dictionary=True)
    holdCheck = False 

    if "Advisor" not in session["type"]:
        return redirect(url_for('login'))
    
    if 'id' in session:
        cursor.execute("SELECT * FROM users LEFT JOIN student ON users.uid = student.uid WHERE advisorid = (%s)", (session['id'],))
        students = cursor.fetchall() 

        if request.method == 'POST':
            studentId = request.form['field_id']
            print(studentId)
            cursor.execute("SELECT fname, lname, advisorid FROM student JOIN users ON users.uid = student.uid WHERE student.uid = (%s) ", (studentId,))
            row = cursor.fetchone()
            print(row)
            if row: 
                studentName = row['fname']
                advisorId = row['advisorid']

                print(studentName)
                print(advisorId)

                if advisorId == session['id']:
                    cursor = mydb.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM form1 WHERE uid = (%s) ", (studentId,)) 
                    results = cursor.fetchall()
                    studentId = results[0]['uid']
                    mydb.commit()

                    if results[0]['hold'] == True:
                        holdCheck = True 

                    return render_template('viewForm.html', results = results, name = studentName, students = students, studentId = studentId, holdCheck = holdCheck)
                else:
                    error = True
                    return render_template('viewForm.html', error = error, students = students)
            else: 
                message = "You do not advise this student"
                return render_template('viewForm.html', message = message, students = students)
    return render_template('viewForm.html', students = students) 

@app.route('/studentViewForm', methods = ['GET','POST'])
def studentViewForm():
    message = " "
    cursor = mydb.cursor(dictionary=True)

    if "Student" not in session["type"]:
        return redirect(url_for('login'))
    
    if 'id' in session:
        cursor.execute("SELECT * FROM users WHERE uid = (%s)", (session['id'],))
        students = cursor.fetchall() 

        cursor.execute("SELECT fname, lname FROM student JOIN users ON users.uid = student.uid WHERE student.uid = (%s) ", (session['id'],))
        row = cursor.fetchone()

        if row: 
            studentName = row['fname']
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM form1 WHERE uid = (%s) ", (session["id"],)) 
            results = cursor.fetchall()
            mydb.commit()

            if results[0]['hold'] == True:
                message = "Your form 1 will be reviewed and is currently under an advising hold"
            else:
                message = "Your hold has been removed"

            return render_template('studentViewForm.html', results = results, name = studentName, students = students, message = message)
    return render_template('studentViewForm.html', students = students) 

@app.route('/removeHold/<int:uid>', methods = ['GET','POST'])
def removeHold(uid):
    cursor = mydb.cursor(dictionary=True)

    if "Advisor" not in session["type"]:
        return redirect(url_for('login'))
    if 'id' in session: 
        cursor.execute("SELECT hold FROM form1 WHERE uid = (%s)", (uid,))
        hold = cursor.fetchall()

        if hold[0]['hold'] == True:
            cursor.execute("UPDATE form1 SET hold = FALSE") 
            mydb.commit()
        
    return redirect(url_for('viewForm')) 

@app.route('/adminGSViewForm', methods = ['GET','POST'])
def adminGSViewForm():
    print(session["type"])
    cursor = mydb.cursor(dictionary=True)
    if "GS" not in session["type"] and "Admin" not in session["type"]:
        return redirect(url_for('login'))
    if 'id' in session:
        cursor.execute("SELECT fname, lname, users.uid FROM student JOIN users ON users.uid = student.uid")
        students = cursor.fetchall()

        if request.method == 'POST':
            studentId = request.form['field_id']
            print(studentId)
            cursor.execute("SELECT fname, lname FROM student JOIN users ON users.uid = student.uid WHERE student.uid = (%s) ", (studentId,))
            row = cursor.fetchall()
            print(row)
            studentName = row[0]['fname']

            cursor = mydb.cursor(dictionary=True)

            cursor.execute("SELECT * FROM form1 WHERE uid = (%s) ", (studentId,))
            results = cursor.fetchall()
            mydb.commit()

            return render_template('adminGSViewForm.html', results = results, name = studentName, students = students)
    return render_template('adminGSViewForm.html', students = students)
    
