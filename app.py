from flask import Flask, redirect, url_for
from flask import render_template
from flask import jsonify
import json
from flask import request
from flask import make_response
app = Flask(__name__)

@app.route('/')
def hello_world():
	return render_template('index.html')

@app.route('/login')
def checklogin():
	print("AS")
	return render_template('index.html')


if __name__ == '__main__':
	app.run(host='0.0.0.0')

