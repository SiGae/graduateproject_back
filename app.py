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

app = Flask(__name__)

@app.route('/getCheckMode', methods=['POST'])
def outCheckboard():
	jsondata = request.get_json()
	print(jsondata)

	data = str(jsondata["month"]) + "/" + str(jsondata["day"])
	print(data)

	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	con = pymysql.connect(host = 'localhost', port = 3306, user=pri.uid, db= pri.dbase, charset='utf8')
	cur = con.cursor()
	cur.execute(sql)

	result = cur.fetchall()
	result= result[0][0]
	result = ast.literal_eval(result)
	if data in result.keys():
		return jsonify(result)
	else:
		temp = dict()
		temp1 = dict()
		for i in range(len(result["init"])):
	
			temp[str(i)] = {
				"id" : result["init"][str(i)]["id"],
				"name" : result["init"][str(i)]["name"],
				"status" : 0
			}

		print(result["init"])
		print(temp)

		out = {
			data : temp
		}
		return jsonify(out)

	

@app.route('/check', methods=['GET'])
def alwayTrue():
	return jsonify({
		"userOnline" : "true"
	})



@app.route('/makeclass_text', methods=['POST'])
def createClass():
	f = request.files["file"]
	js = request.form
	tempdic = dict()
	for i in js:
		tempdic[i] = js[i]

	con = pymysql.connect(host = 'localhost', port = 3306, user=pri.uid, db= pri.dbase, charset='utf8')
	cur  = con.cursor()

	print('a')
	sql = "select userId from user where name = \'{}\';".format(tempdic['userId'])
	cur.execute(sql)
	result = cur.fetchone()
	attend = dict()
	attend["init"] = xlsxTojson(f)

	print('b')
	sql = '''insert INTO classInfo(className, classNo, classRoom, attend, userId) values (\'{0}\', \'{1}\',\'{2}\', \"{3}\", {4});'''.format(tempdic['subName'], tempdic['type'], tempdic['roomNumber'], str(attend), result[0])
	print(sql)
	cur.execute(sql)
	con.commit()
	con.close()

	return {"success" : "clear"}

@app.route('/professor', methods=["POST"])
def printlist():
	jsondata = request.get_json()
	print(jsondata)

	con = pymysql.connect(host = 'localhost', port = 3306, user=pri.uid, db= pri.dbase, charset='utf8')
	cur  = con.cursor()

	sql = "select userId from user where name = \'{}\';".format(jsondata['id'])
	cur.execute(sql)
	result = cur.fetchone()

	sql = "select classId, classname from classInfo where userId = {};".format(result[0])
	cur.execute(sql)
	result = cur.fetchall()
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

	con = pymysql.connect(host = 'localhost', port = 3306, user=pri.uid, db= pri.dbase, charset='utf8')
	cur  = con.cursor()

	sql = 'insert INTO user(name, email, password, phone, userType) values("{}", "{}", "{}", "{}", 0);'.format(jsondata['username'], jsondata['e_mail'], jsondata['password'], jsondata['phone'])
	cur.execute(sql)
	con.commit()
	con.close()

	# with open("userdata/userlist.json", "r") as fr:
	# 	userdata = json.loads(fr.read())
	# if jsondata["username"] in userdata["id"]:
	# 	print("flag")
	# 	return jsonify({"auth" : "false"})
	# sql = 'insert '
	# userdata["id"][jsondata['username']] = jsondata['password'] 
	# out = json.dumps(userdata)

	# with open("userdata/userlist.json", "w") as fa:
	# 	fa.write(out)
	
	# with open("userdata/userlist.json", "r") as fb:
	# 	print(json.loads(fb.read()))
	

	
	return jsonify({"auth" : "true"})


@app.route('/logout', methods=['POST'])
def logout():
	return "<script>alert('로그아웃 되었습니다.')</script>"


@app.route('/login', methods=['POST'])
def checklogin():
	jsondata = request.get_json()

	con = pymysql.connect(host = 'localhost', port = 3306, user=pri.uid, db= pri.dbase, charset='utf8')
	cur  = con.cursor()

	print(jsondata['username'])
	print(jsondata['password'])

	sql = "SELECT name, password from user"
	cur.execute(sql)
	result = cur.fetchall()
	con.close()

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



if __name__ == '__main__':
	app.secret_key = os.urandom(24)
	app.run(host='0.0.0.0', debug=True)

