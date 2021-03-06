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
import hashlib
from operator import itemgetter


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
	try:
		cur.execute(sqltext)
	except Exception as e:
		print(e)

	con.commit()
	con.close()
	return True

def callFinalscore(subId):
	sql = "select ratio from scoreRatio where classId = {}".format(subId)
	result = sql_select(sql)
	try:
		ratio = ast.literal_eval(result[0][0])
		print(ratio)
		sql = "select perfect, list from scoreData where classId = {}".format(subId)
		result = sql_select(sql)
		perfect = ast.literal_eval(result[0][0])
		score = ast.literal_eval(result[0][1])
	except:
		return True

	ratios = []
	raname = []

	print(ratio)

	for i in ratio:
		raname.append(ratio[i]['name'])
		i = ast.literal_eval(ratio[i]['ratio'])
		ratios.append(i)
	print(raname)
	perfect = perfect['perfectScore']
	score = score['scorelist']

	li = []

	for i in range(len(score)):
		result = dict()
		sc = []
		target = score[i]
		data = 0
		for j in range(len(ratios)):
			if not(j in target['label']):
				target['label'].append('0')
			if target['label'][j] == "" :
				target['label'][j] = '0'
			try:
				print(raname[j])
				print(target['label'][j])
				sc.append({'coname' : raname[j], 'score' : target['label'][j]})
				data += (eval(target['label'][j]) / eval(perfect[j]) * ratios[j])
			except:
				return True
		result['id'] = target['id']
		result['name'] = target['name']
		result['score'] = data
		result['component'] = sc
		result['grade'] = 'E'
		li.append(result)
	return li

def sortStudent(li):
	data = sorted(li, key = itemgetter('score'), reverse=True)
	return data

def duplicateId(id):
	sql = 'SELECT name from user where name = "{}"'.format(id)
	result = sql_select(sql)
	if len(result) == 0:
		return True
	else:
		return False



app = Flask(__name__)

@app.route('/manageGrade', methods=['POST'])
def manage():
	jsondata = request.get_json()
	print(jsondata)
	print(jsondata['gradeRatioArr'])
	for i in jsondata:
		print(i)
	sql = '''UPDATE GradeInfo SET grade = "{0}", ratio = "{2}" where classId = {1}'''.format(jsondata['studentList'], jsondata['subId'], jsondata['gradeRatioArr'])
	print("ping")
	sql_exe(sql)
	return jsonify({'success' : True})	


@app.route('/getAttendScore', methods=['POST'])
def get_final_attend():
	jsondata = request.get_json()
	for i in jsondata:
		print(i)
	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	result = sql_select(sql)
	result = ast.literal_eval(result[0][0])
	li = []
	print(result)
	for i in range(len(result["init"])):
		a = {
			"id": result["init"][str(i)]["id"],
			"name": result["init"][str(i)]["name"],
			"출석": 0,
			"결석": 0,
			"지각": 0
		}
		for j in result:
			print(result)
			print(j)

			if j != "init":
				print(j)
				if result[j][str(i)]["status"] == 0:
					a['출석'] += 1
				elif result[j][str(i)]["status"] == 1:
					a['결석'] += 1
				else:
					a['지각'] += 1
		li.append(a)
	result = {
    	'success': True,
		'data': li
		}
	return result

@app.route('/getlist', methods=['POST'])
def getstulist():
	jsondata = request.get_json()
	classId = jsondata['subId']
	
	sql = "select attend from classInfo where classId = {}".format(jsondata['subId'])
	result= sql_select(sql)
	result = ast.literal_eval(result[0][0])
	result = result['init']
	datalist = []

	for i in result:
		asp = {
			"id" : result[i]['id'],
			"name" : result[i]['name']
		}
		datalist.append(asp)

	temp = {
		'success' : True,
		'data' : datalist
	}
	return jsonify(temp)


@app.route('/getGrade', methods=['POST'])
def get_grade():
	jsondata = request.get_json()
	classId = jsondata['subId']
	sql = "select grade, ratio from GradeInfo where classId = {}".format(classId)
	dt = sql_select(sql)
	sclist = False
	sclist = callFinalscore(classId)
	if sclist == True:
		return jsonify({'success' : False})
	li = sortStudent(sclist)
	if len(dt) == 0:
		print("ping")
		sql = 'insert INTO GradeInfo(classId, grade) values ({}, "{}")'.format(classId, li)
		sql_exe(sql)
		temp = li
		li = {
			'studentList' : temp,
			'gradeRatioArr' : ["", "", "", ""],
			'Fcount' : 0
		}
	else:
		

		# sql = "select list from scoreData where classId = " + str(classId)
		# res = sql_select(sql)
		# res = ast.literal_eval(res[0][0])
		# res = res['scorelist']
		# print("aaa")
		# print(res)
		# print("bbb")
		li = dt[0][0]
		li = li[1:]
		li = li[:-1]
		# li = li.replace("}, {", "}}, {{")
		# li = li.split("}, {")
		li = ast.literal_eval(li)
		fi = []
		cnt = 0
		for i in li:
			fi.append(i)
		for i in fi:
			if i['grade'] == 'F':
				cnt += 1
		li = fi
		temp = li
		print("asdf")
		print(temp)
		print("bf")

		# for i in range(len(res)):
		# 	for j in temp:
		# 		if res[i]['id'] == j['id']:
		# 			for k in range(len(j['component'])):
						
		# 				j['component'][k]['score'] = res[i]['label'][k]
		# 			break

		# sql = "select ratio from scoreRatio where classId = " + str(classId)
		# res = sql_select(sql)
		# res = ast.literal_eval(res[0][0])
		# scolist = []
		# for i in range(len(res)):
		# 	scolist.append(int(res[str(i)]["ratio"]))
		# print(scolist)
		# sql = "select perfect from scoreData where classId = " + str(classId)
		# persclist = sql_select(sql)
		# persclist = ast.literal_eval(persclist[0][0])
		# print()
		# persclist = persclist['perfectScore']

		# for i in temp:
		# 	sco = 0
		# 	for j in range(len(scolist)):
		# 		ta = 0
		# 		try:

		# 			if i['component'][j]['score'] != '' and persclist[j] != '' and scolist[j] != '':
		# 				ta = int(i['component'][j]['score']) / int(persclist[j]) * scolist[j]
		# 		except:
		# 			i['component'].append({
		# 				'coname' : '',
		# 				'score' : ''
		# 			})
		# 		sco += ta
		# 	i['score'] = sco
		
		# temp = sortStudent(temp)

			
	
		li = {
			'studentList' : temp,
			'gradeRatioArr' : ["", "", "", ""],
			'Fcount' : cnt
		}
		di = dt[0][1]
		if di != None:
			di = di.replace("[", "")
			di =di.replace("]", "")
			di = di.replace("}, {", "}}, {{")
			di = di.split("}, {")
			a = ast.literal_eval(di[0])
			print(a)
			li['gradeRatioArr'] = a


	result = {
		'success' : True,
		'data' : li
	}

	return result

@app.route('/getTranscript', methods=['POST'])
def getScore():
	jsondata = request.get_json()
	sql = "select perfect, list from scoreData where classId = {}".format(jsondata["subId"])
	data = sql_select(sql)
	result = dict()
	if len(data) == 0:
		result["score"] = False
	else:
		perfect = ast.literal_eval(data[0][0])
		listt = ast.literal_eval(data[0][1])
		sql = "select ratio from scoreRatio where classId = {}".format(jsondata["subId"])
		result = sql_select(sql)
		result = ast.literal_eval(result[0][0])

		perfect = perfect['perfectScore']
		listt = listt["scorelist"]

		if len(result) != len(perfect):
			while (len(result) != len(perfect)):
				perfect.append("")
				for i in listt:
					i['label'].append("")

		result['score'] = True
		a = dict()
		a['perfectScore'] = perfect
		a['studentList'] = listt
		result['data'] = a
		



	return jsonify(result)

@app.route('/sendScore', methods=['POST'])
def sendScore():
	jsondata = request.get_json()
	# print(jsondata)
	info0 = dict()
	info1 = dict()
	info0['scorelist'] = jsondata['studentList']
	info1['perfectScore'] = jsondata['perfectScore']

	sql = '''SELECT classId from scoreData where classId = {}'''.format(jsondata['subId'])
	result = sql_select(sql)
	if len(result) == 0:
		sql = '''insert INTO scoreData(classId, list, perfect) values ({}, "{}", "{}")'''.format(jsondata['subId'], info0, info1)
	else:
		sql = '''UPDATE scoreData SET list = "{0}", perfect = "{1}" where classId = {2}'''.format(info0, info1, jsondata['subId'])
	sql_exe(sql)

	return jsonify({"success":True})



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
	flag =  False
	if len(result) == 0:
		sql = '''insert INTO scoreRatio(classId, ratio) values ({}, "{}")'''.format(jsondata['subId'], ratio)
	else:
		sql = '''UPDATE scoreRatio SET ratio = "{0}" where classId = {1}'''.format(ratio, jsondata['subId'])
		flag = True
	sql_exe(sql)
	if flag:
		sql = '''SELECT classId from GradeInfo where classId = {}'''.format(jsondata['subId'])
		result = sql_select(sql)
		if len(result) != 0:
			sql = '''delete from GradeInfo where classId = {}'''.format(jsondata['subId'])
			sql_exe(sql)
		sql = '''SELECT classId from scoreData where classId = {}'''.format(jsondata['subId'])
		result = sql_select(sql)
		if len(result) != 0:
			sql = '''delete from scoreData where classId = {}'''.format(jsondata['subId'])
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
		if data != None and data != "/":
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
	if duplicateId(jsondata['username']):
		sql = 'insert INTO user(name, email, password, phone, userType) values("{}", "{}", "{}", "{}", 0);'.format(jsondata['username'], jsondata['e_mail'], jsondata['password'], jsondata['phone'])
		sql_exe(sql)
	
		return jsonify({"auth" : "true"})
	else:
		return jsonify({"auth" : "false"})



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

