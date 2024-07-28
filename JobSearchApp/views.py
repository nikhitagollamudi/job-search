from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import requests
import urllib.parse
from math import sin, cos, sqrt, atan2, radians
import sys, json

global userid, pnameValue, pdateValue

from geopy.geocoders import Nominatim

def get_latitude_longitude(address):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(address)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return latitude, longitude
    else:
        return None, None

def getLocation(area):
    latitude, longitude = get_latitude_longitude(area)
    if latitude and longitude:
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print("Location not found.")
    return float(latitude), float(longitude)

def getDistance(lat1, lon1, lat2, lon2):
    R = 6373.0  # Earth's radius in kilometers
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) * 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) * 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def SearchJobAction(request):
    if request.method == 'POST':
        area = request.POST.get('t1', False)
        print('area is::', area)
        distance = request.POST.get('t2', False)
        shift = request.POST.get('t3', False)
        weekly = request.POST.get('t4', False)
        salary = request.POST.get('t5', False)
        lat1, lon1 = getLocation(area)
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        output = ""
        with con:
            cur = con.cursor()
            cur.execute("select * FROM jobpost")
            rows = cur.fetchall()
            for row in rows:
                job_id = row[0]
                company = row[1]
                position = row[2]
                responsibility = row[3]
                qualification = row[4]
                experience = row[5]
                skills = row[6]
                location = row[7]
                posted_shift = row[8]
                working_days = row[9]
                tot_salary = row[10]
                environment = row[11]
                post_date = row[12]
                status = row[13]
                print(location, '876543456')
                lat2, lon2 = getLocation(location)
                dist = getDistance(lat1, lon1, lat2, lon2)
                print(dist, 'distdist', shift, posted_shift, weekly, working_days, tot_salary, salary)
                if dist <= float(distance) and shift == posted_shift and working_days == weekly and float(tot_salary) >= float(salary):
                    output += '<tr><td><font size="" color="black">' + str(job_id) + '</td>'
                    output += '<td><font size="" color="black">' + str(company) + '</td>'
                    output += '<td><font size="" color="black">' + str(position) + '</td>'
                    output += '<td><font size="" color="black">' + str(responsibility) + '</td>'
                    output += '<td><font size="" color="black">' + str(qualification) + '</td>'
                    output += '<td><font size="" color="black">' + str(experience) + '</td>'
                    output += '<td><font size="" color="black">' + str(skills) + '</td>'
                    output += '<td><font size="" color="black">' + str(location) + '</td>'
                    output += '<td><font size="" color="black">' + str(posted_shift) + '</td>'
                    output += '<td><font size="" color="black">' + str(working_days) + '</td>'
                    output += '<td><font size="" color="black">' + str(tot_salary) + '</td>'
                    output += '<td><font size="" color="black">' + str(environment) + '</td>'
                    output += '<td><font size="" color="black">' + str(post_date) + '</td>'
                    output += '<td><font size="" color="black">' + str(status) + '</td>'
        context = {'data': output}
        return render(request, 'SearchResult.html', context)

def SearchJob(request):
    if request.method == 'GET':
        return render(request, 'SearchJob.html', {})

def Activate(request):
    if request.method == 'GET':
        job_id = request.GET['jid']
        status = request.GET['status']
        result = None
        if status == "Active":
            result = "Deactivated"
        elif status == "Deactivated":
            result = "Active"
        db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update jobpost set status='" + result + "' where job_id='" + job_id + "'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        context = {'data': 'Job status changed to : ' + result}
        return render(request, 'EmployerScreen.html', context)

def ActivateJob(request):
    if request.method == 'GET':
        global userid
        output = ""
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM jobpost where username='" + userid + "'")
            rows = cur.fetchall()
            for row in rows:
                output += '<tr><td><font size="" color="black">' + str(row[0]) + '</td>'
                output += '<td><font size="" color="black">' + str(row[1]) + '</td>'
                output += '<td><font size="" color="black">' + str(row[2]) + '</td>'
                output += '<td><font size="" color="black">' + str(row[3]) + '</td>'
                output += '<td><font size="" color="black">' + str(row[6]) + '</td>'
                output += '<td><font size="" color="black">' + str(row[13]) + '</td>'
                output += '<td><a href=\'Activate?jid=' + str(row[0]) + '&status=' + row[13] + '\'><font size=3 color=black>Click Here</font></a></td></tr>'
        context = {'data': output}
        return render(request, 'ActivateJob.html', context)

def PostJobAction(request):
    if request.method == 'POST':
        global userid
        position = request.POST.get('t1', False)
        responsibility = request.POST.get('t2', False)
        qualification = request.POST.get('t3', False)
        experience = request.POST.get('t4', False)
        skills = request.POST.getlist('t5')
        location = request.POST.get('t6', False)
        shift = request.POST.get('t7', False)
        working = request.POST.get('t8', False)
        salary = request.POST.get('t9', False)
        environment = request.POST.get('t10', False)
        skills = ''.join(skills)
        print(skills)
        job_count = 0
        output = 'none'
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select count(*) FROM jobpost")
            rows = cur.fetchall()
            for row in rows:
                job_count = row[0]
        job_count = job_count + 1
        today = date.today()
        db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO jobpost(job_id,username,position,responsibility,qualification,experience,skills,location,shift,working_days,salary,work_environment,post_date,status) VALUES('" + str(job_count) + "','" + userid + "','" + position + "','" + responsibility + "','" + qualification + "','" + experience + "','" + skills + "','" + location + "','" + shift + "','" + working + "','" + salary + "','" + environment + "','" + str(today) + "','Active')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            context = {'data': 'Job details added with job ID : ' + str(job_count)}
            return render(request, 'PostJob.html', context)
        else:
            context = {'data': 'Error in adding job details'}
            return render(request, 'PostJob.html', context)

def PostJob(request):
    if request.method == 'GET':
        return render(request, 'PostJob.html', {})

def index(request):
    if request.method == 'GET':
        return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
        return render(request, 'Login.html', {})

def Signup(request):
    if request.method == 'GET':
        return render(request, 'Signup.html', {})

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        email = request.POST.get('t3', False)
        contact = request.POST.get('t4', False)
        qualification = request.POST.get('t5', False)
        address = request.POST.get('t6', False)
        usertype = request.POST.get('t7', False)
        output = 'none'
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = username + " Username already exists"
        if output == "none":
            db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(username,password,emailid,contact_no,qualification,address,usertype) VALUES('" + username + "','" + password + "','" + email + "','" + contact + "','" + qualification + "','" + address + "','" + usertype + "')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                context = {'data': 'Signup process completed'}
                return render(request, 'Signup.html', context)
            else:
                context = {'data': 'Error in adding user details'}
                return render(request, 'Signup.html', context)
        else:
            context = {'data': output}
            return render(request, 'Signup.html', context)

def LoginAction(request):
    if request.method == 'POST':
        global userid
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        usertype = request.POST.get('t3', False)
        status = 'none'
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='jobsearch', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username,password FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    userid = username
                    status = 'success'
                    break
        if status == 'success' and usertype == 'Employer':
            output = 'Welcome ' + username
            context = {'data': output}
            return render(request, 'EmployerScreen.html', context)
        elif status == 'success' and usertype == 'Job Search Agent':
            output = 'Welcome ' + username
            context = {'data': output}
            return render(request, 'ApplicantScreen.html', context)
        else:
            context = {'data': 'Invalid username'}
            return render(request, 'Login.html', context)
