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
	with open("userdata/userlist.json", 'r') as fr:
		userdata = json.loads(fr.read())
		dic = dict()
		if jsondata["username"] in userdata["id"] and jsondata["password"]==userdata["id"][jsondata["username"]]:
			dic["user"] = "TRUE"
		else :
			dic["user"] = "ERROR"
		out = json.dumps(dic)
		

	return jsonify(out)

@app.route("/makeclass", methods=["POST"])
def register():
	#files = request.files['file']
	jsondata = request.get_json
	print(jsondata)
	
	#filename = secure_filename(files.filename)

	#files = request.files['file']
	#files.save("./file/{}".format(filename))
	return ""



if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.run(host='0.0.0.0', debug=True)

