#!/usr/bin/python

# Recognize / using the form input data

import time	   # time
import fnmatch # globbing
import os.path # for checking if a file exist
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "sOmEsTuPiDkEy"

def getFollowing(username):	
	following = []
	start = False
	if os.path.exists("users/" + username):
		with open("users/" + username, "r") as f:
			for line in f:
				if start == True:
					following.append(line.strip("\n"))
				if line.strip() == "following:":
					start = True
	return following

def getPosts(username):
	topPost = ["", "", "", "", "", "", "", "", "", ""]
	postTime = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
	following = getFollowing(username)
	for users in following:
		if os.path.exists("posts/" + users):
			with open("posts/" + users, "r") as f:
				for line in f:
					if "t<>p" in line:
						time = line.split("t<>p")[0]
						post = line.split("t<>p")[1]
						for i in range(0, 10):
							if postTime[i] == -1:
								postTime[i] = float(time)
								topPost[i] = post
								break
							elif time < postTime[i]:
								postTime[i] = float(time)
								topPost[i] = post
								break
	return topPost

@app.route("/", methods=['post', 'get'])
def index():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if os.path.exists("users/" + username):
			file = open("users/" + username, "r")
			pwd = file.readline()
			if pwd.split("password=")[1] == password+"\n":
				session['username'] = username
				session['password'] = password
				return redirect(url_for("home"))
			return render_template("index.html", err="error")
		return render_template("index.html", err="nouser")
	return render_template("index.html")

@app.route("/home", methods=['post','get'])
def home():
	if 'username' in session:
		topPosts = getPosts(session['username'])
		return render_template("home.html", username=session['username'], posts=topPosts)
	return redirect("/")

@app.route('/register', methods=['post', 'get'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		if os.path.exists("users/" + username):
			return render_template("index.html", err="error")
		else:
			file = open("users/"+username, "w")
			pwd = "password=" + password + "\n"
			file.write(pwd)
			file.close()
			return redirect("/")
	return render_template("register.html")

@app.route('/edit', methods=['post', 'get'])
def edit():
	if 'username' in session:
		if request.method == 'POST':
			if request.form['oldpassword'] == session['password']:
				file = open("users/" + session['username'], "r+")
				pwd = "password=" + request.form['newpassword']
				file.write(pwd)
				file.close()
				return redirect("/home")
			return render_template("editprofile.html", errormsg="error")
		following = getFollowing(session['username'])
		return render_template("editprofile.html", following=following)
	return redirect("/")

@app.route('/search', methods=['post', 'get'])
def search():
	if 'username' in session:
		if request.method == 'POST':
			users = []
			for file in os.listdir("users/"):
				# search for any user with the pattern request.form['usernme']
				if fnmatch.fnmatch(file, "*" + request.form['username'] + "*"):
					users.append(file)
			return render_template("searchresults.html", username=users, search=request.form['username'])
		return redirect("/home")
	return redirect("/")

@app.route('/follow', methods=['post','get'])
def follow():
	# the users should already exist if this function is called
	if 'username' in session:
		following = request.form['following']
		with open("users/"+session['username'], "r+") as f:
			foundFollowing = False
			foundFollowingTag = False
			for line in f:
				if line.strip() == "following:":
					foundFollowingTag = True
				if line == following:
					foundFollowing = True
			if not foundFollowingTag:
				f.write("\nfollowing:")
			if not foundFollowing:
				f.write('\n'+following)
		return redirect("/home")
	return redirect("/")

@app.route("/post", methods=['post', 'get'])
def post():
	if 'username' in session:
		if request.method == 'POST':
			ts = time.time();
			msg = request.form['text']
			# t<>P used to separate timestamp and message
			cat = str(ts) + "t<>p" + msg
			if os.path.exists("posts/" + session['username']):
				file = open("posts/" + session['username'], "a")
				file.write("\n#STARTPOST#")
				file.write("\n" + cat)
				file.write("\n#ENDPOST")
				file.close()
				return redirect("/home")
			else:
				# first time user is posting
				file = open("posts/" + session['username'], "w")
				file.write("\n#STARTPOST#")
				file.write("\n" + cat)
				file.write("\n#ENDPOST")
				file.close()
				return redirect("/home")
		return redirect("/home")
	return redirect("/home")

@app.route('/logout', methods=['post','get'])
def logout():
	session.pop('username', None)
	return redirect("/")	

@app.route('/remove', methods=['post', 'get'])
def remove():
	if 'username' in session:
		username = session['username']
		session.pop('username', None)
		os.remove("users/"+username)
	return redirect("/")

app.run("127.0.0.1", 13000, debug=True)