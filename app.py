from flask import Flask, render_template, flash, session, request, redirect
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
from flask_ckeditor import CKEditor
import os


app = Flask(__name__)
Bootstrap(app)


# DB Setup
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='anuj'
app.config['MYSQL_PASSWORD']='mydbs'
app.config['MYSQL_DB']='epiphaniDB'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql = MySQL(app)

# generate random secret key
app.config['SECRET_KEY'] = os.urandom(24)

CKEditor(app)

# home route
@app.route('/')
def index():
	cur= mysql.connection.cursor()
	result_value = cur.execute("SELECT * from thoughts")
	if result_value > 0:
		thoughts = cur.fetchall()
		cur.close()
		return render_template('index.html',thoughts=thoughts)
	cur.close()
	return render_template('index.html',thoughts =None)



# about page route
@app.route('/about')
def about():
	return render_template('about.html')



# list of all thoughts
@app.route('/thoughts/<int:id>')
def thoughts(id):
	cur= mysql.connection.cursor()
	result_value = cur.execute("SELECT * FROM thoughts WHERE thought_id={}".format(id))
	if result_value > 0:
		thought = cur.fetchone()
		cur.close()
		return render_template('thoughts.html',thoughts=thought)
	return "No thought found Lets start a thought"



# register route
@app.route('/register',methods =['GET','POST'])
def register():
	if request.method == 'POST':
		userDetails = request.form
		if userDetails['password'] != userDetails['confirm_password']:
			flash('Passwords do not match! Try again.', 'danger')
			return render_template('register.html')
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO user(first_name, last_name, username, email, password) VALUES(%s,%s,%s,%s,%s)",(userDetails['first_name'], userDetails['last_name'], userDetails['username'], userDetails['email'], userDetails['password']))
		mysql.connection.commit()
		cur.close()
		flash('Registration successful! Please login.', 'success')
		return redirect('/login')
	return render_template('register.html')



# login route
@app.route('/login',methods =['GET','POST'])
def login():
	if request.method=='POST':
		userDetails =request.form
		username= userDetails['username']
		cur = mysql.connection.cursor()
		result_value = cur.execute("SELECT * FROM user WHERE username = %s",([username]))
		if result_value > 0:
			user = cur.fetchone()
			if userDetails['password'] == user['password']:
				session['login'] = True
				session['firstName'] = user['first_name']
				session['lastName'] = user['last_name']
				flash('Welcome ' + session['firstName'] +'! You have been successfully logged in', 'success')
			else:
				cur.close()
				flash('Password does not match', 'danger')
				return render_template('login.html')
		else:
			cur.close()
			flash('User not found', 'danger')
			return render_template('login.html')
			cur.close()
		return redirect('/')
	return render_template('login.html')




# write thoughts route
@app.route('/write-thought',methods=['GET','POST'])
def write_thought():
	if request.method=='POST':
		thoughtpost = request.form
		title = thoughtpost['title']
		body = thoughtpost['body']
		mastermind = session['firstName']+' '+session['lastName']
		cur=mysql.connection.cursor()
		cur.execute("INSERT INTO thoughts(title,body,mastermind) VALUES (%s, %s, %s)",(title,body,mastermind))
		mysql.connection.commit()
		cur.close()
		flash("Successful moved from brain to database",'success')
		return redirect('/')
	return render_template('write-thought.html')


# my thoughts display
@app.route('/my-thoughts')
def my_thoughts():
	mastermind = session['firstName']+' '+session['lastName']
	cur = mysql.connection.cursor()
	result_value = cur.execute("SELECT * FROM thoughts WHERE mastermind = %s",[mastermind])
	if result_value > 0:
		my_thoughts = cur.fetchall()
		return render_template('my-thoughts.html',my_thoughts = my_thoughts)
	else:
		return render_template('my-thoughts.html',my_thoughts=None)


# edit thought route
@app.route('/edit-thought/<int:id>',methods=['GET','POST'])
def edit_thought(id):
	if request.method=='POST':
		cur = mysql.connection.cursor()
		title = request.form['title']
		body = request.form['body']
		cur.execute("UPDATE thoughts SET title = %s, body = %s WHERE thought_id =%s",(title,body,id))
		mysql.connection.commit()
		cur.close()
		flash('Thought updated','success')
		return redirect('/thoughts/{}'.format(id))
	cur =  mysql.connection.cursor()
	result_value = cur.execute("SELECT * FROM thoughts WHERE thought_id = {}".format(id))
	if result_value > 0:
		thought = cur.fetchone()
		thought_form = {}
		thought_form['title'] = thought['title']
		thought_form['body'] = thought['body']
		return render_template('edit-thought.html',thought_form = thought_form)


# delete thought route
@app.route('/delete-thought/<int:id>')
def delete_thought(id):
	cur = mysql.connection.cursor()
	cur.execute("DELETE FROM thoughts WHERE thought_id = {}".format(id))
	mysql.connection.commit()
	flash("Your thought has been deleted from database",'success')
	return redirect('/my-thoughts')
	

# logout route
@app.route('/logout')
def logout():
	session.clear()
	flash("You have been logged out",'info')
	return redirect('/')


if __name__ =='__main__':
	app.run(debug=True)