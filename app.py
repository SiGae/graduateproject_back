from flask import Flask, redirect, url_for
from flask import render_template
from flask import jsonify, flash, request, redirect, session
import json
import os
from flask import request
from flask import make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import logging

app = Flask(__name__)

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/login', methods=['POST'])
def checklogin():
	jsondata = request.get_json()
	print(jsondata)
	return ""

@app.route("/register", methods=["POST"])
def register():
	files = request.files['file']
	# jsondata = request.get_json()
	filename = secure_filename(files.filename)

	files = request.files['file']
	files.save("./jsonfile")
	return



@app.route("/fileupload", methods=["POST"])
def fileup():
	# target='api'
	# if not os.path.isdir(target):
	# 	os.mkdir(target)

	# files = request.files['file']
	# filename = secure_filename(files.filename)
	# destination="/fileout".join([target, filename])
	# files.save(destination)
	files = request.files['file']
	# jsondata = request.get_json()
	filename = secure_filename(files.filename)

	files = request.files['file']
	files.save("./jsonfile")
	return ""


if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.run(host='0.0.0.0', debug=True)

