import os
import secrets
import requests
import hashlib
import time
import dialogflow, json, pusher, requests, csv
from flask import request
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask import Flask, session, render_template, url_for, flash, redirect, request, send_from_directory, jsonify
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from project import app, db
from project.forms import UserForm, LoginForm, UpdateDetails
from project.models import User
from PIL import Image

### ESSENTIAL ROUTES ###

@app.route("/")
@app.route("/home", methods = ['GET', 'POST'])
def home():
	return render_template('home.html', title='Home')

@app.route("/userRegister", methods = ['GET', 'POST'])
def userRegister():
	global ID_COUNT
	form = UserForm()
	if form.validate_on_submit():
		
		pw = (form.password.data)
		s = 0
		for char in pw:
			a = ord(char) #ASCII
			s = s+a #sum of ASCIIs acts as the salt
		hashed_password = (str)((hashlib.sha512((str(s).encode('utf-8'))+((form.password.data).encode('utf-8')))).hexdigest())
		user = User(email=form.email.data, name=form.name.data, password = hashed_password)
		
		print("before pic")
		print(user.id)

		if form.photo.data:
			photo_file = save_photo(form.photo1.data)
			user.photo = photo_file
			photo = url_for('static', filename='user/' + user.photo)

		db.session.add(user)
		db.session.commit()

		user = User(id=user.id)
		db.session.commit()
		print(user)

		return redirect(url_for('login'))
	else:
		print('form not validated')
		print(form.errors)
	return render_template('userRegister.html', title='Register', form=form)

def save_photo(form_photo):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_photo.filename)
	photo_fn = random_hex + f_ext
	## Don't use static\user, pass them as separate arguments
	photo_path = os.path.join(app.root_path, 'static','user', photo_fn)
	print('PHOTO TO BE SAVED:: ', photo_path)
	output_size = (125, 125)
	i = Image.open(form_photo)
	i.thumbnail(output_size)
	#this will fail if static/user folder doesn't exist
	i.save(photo_path)
	return photo_fn


@app.route("/login", methods = ['GET','POST'])
def login():
	form = LoginForm(request.form)

	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		pw = (form.password.data)
		s = 0
		for char in pw:
			a = ord(char) #ASCII
			s = s+a #sum of ASCIIs acts as the salt
		now_hash = (str)((hashlib.sha512((str(s).encode('utf-8'))+((form.password.data).encode('utf-8')))).hexdigest())

		if (user and (user.password==now_hash)):
			login_user(user)
			print("hash correct")
			return redirect(url_for('account'))

		else:
			print('Nahin hua')
			flash('Login Unsuccessful. Please check email and password', 'danger')

	return render_template('login.html', title='Login', form=form)


@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
	updateForm = UpdateDetails()
	user = User.query.filter_by(id=current_user.id).first()
	print(user)
	if updateForm.validate_on_submit():

		user = User(email=updateForm.email.data, name=updateForm.name.data, password=updateForm.password.data)
		user.type = 'user'

		# IF ANY PHOTOS ARE UPDATED (Current)
		if updateForm.photo.data:
			photo_file = save_photo(updateForm.photo.data)
			user.photo = photo_file

		db.session.commit()
		print(user)
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))

	elif request.method == 'GET':
		updateForm.email.data = user.email
		updateForm.name.data = user.name
		updateForm.password.data = user.password
		print('Previous content loaded')
	# OLD PHOTO (registration ke waqt ka)
	photo = url_for('static', filename='user/' + user.photo)

	return render_template("account.html", title='Account', form=updateForm, user=user, photo=photo)


@app.route("/viewuser/<user_id>", methods = ['GET', 'POST'])
def user2_account(org_id):

	user = User.query.filter_by(id = org_id).first()
	return render_template('viewUserAccount.html', title='ViewUser', user=user)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))
	flash('You have been logged out', 'success')