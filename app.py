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
import pandas as pd
import pymysql
import privateInfo as pri
import ast
import datetime



def xlsxTojson(file):
	df = pd.read_excel(file)
	print(df.columns)

	ddf0 = df["Unnamed: 5"]
	ddf1 = df["Unnamed: 6"]
	ad0 = ddf0.values.tolist()
	ad1 = ddf1.values.tolist()
	ad0 = ad0[10:]
	ad1 = ad1[10:]
	print(ad0)
	print(ad1)
	li = dict()
	for i in range(len(ad0)):
		temp = dict()
		temp["id"] = str(ad0[i])
		temp["name"] = str(ad1[i])
		li[str(i)] = temp
	print(li)
	return li

def sql_select(sqltext):
	con = pymysql.connect(host = 'localhost', port=3306, user = pri.uid, db = pri.dbase, charset='utf8')
	cur = con.cursor()
	cur.execute(sqltext)
	result = cur.fetchall()
	con.close()
	return result

def sql_exe(sqltext):
	con = pymysql.connect(host = 'localhost', port=3306, user = pri.uid, db = pri.dbase, charset='utf8')
	cur = con.cursor()
	print(sqltext)
	cur.execute(sqltext)
	con.commit()
	con.close()
	return True

app = Flask(__name__)

@app.route('/getRatio', methods=['POST'])
def getClassRatio():
	jsondata = request.get_json()
	print(jsondata)
	for i in jsondata:
		print(i)
	sql = "select ratio from scoreRatio where classId = {}".format(jsondata["subId"])
	ratio = sql_select(sql)
	print(ratio)
	result = dict()
	if len(ratio) == 0:
		result["ratio"] = False
	else:
		print(ratio[0][0])
		results = ast.literal_eval(ratio[0][0])
		out = []
		for i in results:
			out.append(results[i])

		print(out)

		result["ratio"] = True
		result["parts"] = out
	print(result)

	return jsonify(result)

@app.route('/createRatio', methods=['POST'])
def createRatio():
	jsondata =request.get_json()
	print(jsondata)
	for i in jsondata:
		print(i)
	arr = jsondata['ratioArr']
	print(arr)
	ratio = dict()
	for i in range(len(arr)):
		ratio[str(i)] = arr[i]
	print(ratio)
	sql = '''SELECT classId from scoreRatio where classId = {}'''.format(jsondata['subId'])
	result = sql_select(sql)
	if len(result) == 0:
		sql = '''insert INTO scoreRatio(classId, ratio) values ({}, "{}")'''.format(jsondata['subId'], ratio)
	else:
		sql = '''UPDATE scoreRatio SET ratio = "{0}" where classId = {1}'''.format(ratio, jsondata['subId'])
	sql_exe(sql)
	return jsonify({"success":True})

@app.route('/getCheckDate', methods=['POST'])
def outDate():
	jsondata = request.get_json()
	print(jsondata)
	for i in jsondata:

		print(i)

	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	result= sql_select(sql)
	result = ast.literal_eval(result[0][0])
	dateList = []
	for i in result:
		if i != "init":
			dateList.append(i)
		
	dt = datetime.datetime.now()
	date = "{0}/{1}".format(dt.month, dt.day)
	if not(date in dateList):
		dateList.append("{0}/{1}".format(dt.month, dt.day))

	out = {
		"date" : dateList
	}

	print(out)
	return jsonify(out)


@app.route('/getStudentList', methods=['POST'])
def outCheckboard():
	jsondata = request.get_json()
	print(jsondata)

	data = str(jsondata["month"]) + "/" + str(jsondata["day"])
	print(data)

	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	result= sql_select(sql)
	result = ast.literal_eval(result[0][0])
	dateList = []

	temp = dict()

	if data in result.keys():
		print("기존 출력")
		temp = result[data]
	else:
		print("생성")
		for i in range(len(result["init"])):
	
			temp[str(i)] = {
				"id" : result["init"][str(i)]["id"],
				"name" : result["init"][str(i)]["name"],
				"status" : 0
			}
		result[data] = temp
		print(result)
		sql = '''UPDATE classInfo SET attend = "{0}" where classId = {1}'''.format(result, str(jsondata["subId"]))
		sql_exe(sql)

	out = {
			data : temp
		}
	

	return jsonify(out)

@app.route('/attendData', methods=['POST'])
def updateAttend():
	jsondata = request.get_json()
	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	result= sql_select(sql)


	result = ast.literal_eval(result[0][0])
	date = jsondata['month'] + "/" + jsondata['day']

	constudent = dict()
	for i in range(len(jsondata['studentList'])):
		constudent[str(i)] = jsondata['studentList'][i]
	print(date)
	result[date] = constudent

	sql ='''UPDATE classInfo SET attend = "{0}" where classId = {1}'''.format(result, str(jsondata["subId"]))
	sql_exe(sql)
	out = {
		'success' : 'true'
	}
	return jsonify(out)

@app.route('/check', methods=['GET'])
def alwayTrue():
	return jsonify({
		'success' : "true"
	})



@app.route('/makeclass_text', methods=['POST'])
def createClass():
	f = request.files["file"]
	js = request.form
	tempdic = dict()
	for i in js:
		tempdic[i] = js[i]

	print('a')
	sql = "select userId from user where name = \'{}\';".format(tempdic['userId'])
	attend = dict()
	attend["init"] = xlsxTojson(f)
	result = sql_select(sql)
	print('b')
	sql = '''insert INTO classInfo(className, classNo, classRoom, attend, userId) values (\'{0}\', \'{1}\',\'{2}\', \"{3}\", {4});'''.format(tempdic['subName'], tempdic['type'], tempdic['roomNumber'], str(attend), result[0][0])
	print(sql)
	sql_exe(sql)
	sql = '''select classId from '''

	return {"success" : "clear"}

@app.route('/professor', methods=["POST"])
def printlist():
	jsondata = request.get_json()
	print(jsondata)

	sql = "select userId from user where name = \'{}\';".format(jsondata['id'])
	res = sql_select(sql)
	sql = "select classId, classname from classInfo where userId = {};".format(res[0][0])
	result = sql_select(sql)
	tem = dict()
	t = 0 
	for i in result:
		s = {"id" : i[0], "name" : i[1]}
		tem[str(t)] = s
		t+=1
	out = dict()
	out["subjectList"] = tem
	out["success"] = 'true'
	print(out)
	
	return jsonify(out)



@app.route('/register', methods=['POST'])
def registerw():
	jsondata = request.get_json()
	print(jsondata)

	sql_exe(sql)
	
	return jsonify({"auth" : "true"})


@app.route('/logout', methods=['POST'])
def logout():
	return "<script>alert('로그아웃 되었습니다.')</script>"


@app.route('/login', methods=['POST'])
def checklogin():
	jsondata = request.get_json()

	print(jsondata['username'])
	print(jsondata['password'])

	sql = "SELECT name, password from user"
	result = sql_select(sql)

	dic = dict()

	for i in result:
		print(i[0])
		print("pw = ")
		print(i[1])
		if jsondata["username"] == i[0] and jsondata["password"] == i[1]:
			dic["auth"] = "TRUE"
			break
		else:
			dic["auth"] = "ERROR"
	print(dic)

	return jsonify(dic)



CORS(app)

if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.run(host='0.0.0.0', debug=True)

