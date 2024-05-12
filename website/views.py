from flask import Blueprint, render_template, flash, request, redirect, url_for
from dotenv import load_dotenv
import requests
import urllib3
import os
import datetime

load_dotenv()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

views = Blueprint('views', __name__)

@views.route('/activity', methods=['GET','POST'])
def activity():
    auth_url = "https://www.strava.com/oauth/token"
    activities_url = "https://www.strava.com/api/v3/activities"

    payload = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'grant_type': "refresh_token",
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)

    access_token = res.json()['access_token']

    header = {"Authorization" : 'Bearer ' + access_token}

    if request.method == 'POST':
        name = request.form.get('name')
        type = request.form.get('type')
        sportType = request.form.get('sporttype')
        date = request.form.get('date')
        time = request.form.get('time')
        descritption = request.form.get('descritption')
        distance = request.form.get('distance')
        trainer = request.form.get('trainer')
        commute = request.form.get('commute')

        if len(request.form.get('name')) < 1:
            flash('Name must be longer than 1', category='error')
        elif len(request.form.get('type')) < 1 :
            flash('Type must be longer than 1', category='error')
        elif len(request.form.get('sporttype')) < 1 :
            flash('Sport type must be longer than 1', category='error')
        elif len(request.form.get('date')) < 1 :
            flash('Date must be longer than 1', category='error')
        elif len(request.form.get('time')) < 1 :
            flash('Time must be longer than 1', category='error')
        elif len(request.form.get('description')) < 1 :
            flash('Description must be longer than 1', category='error')
        elif len(request.form.get('distance')) < 1 :
            flash('Distance must be longer than 1', category='error')
        elif len(request.form.get('trainer')) < 1 :
            flash('Trainer must be longer than 1', category='error')
        elif len(request.form.get('commute')) < 1 :
            flash('Commute must be longer than 1', category='error')
        else:
    
            param = {"name" : request.form.get('name'), 'type': request.form.get('type'), 'sport_type': request.form.get('sporttype'), 'start_date_local': '2024-05-12 00:13:24', 'elapsed_time': request.form.get('time'), 'description': request.form.get('description'), 'distance': request.form.get('distance'), 'trainer': request.form.get('trainer'), 'commute': request.form.get('commute')}
            requests.post(activities_url, headers=header, params=param)
            flash('Activity Added', category='success')
            return redirect(url_for('views.home'))
        
    return render_template("activity.html")

@views.route('/', methods=['GET','POST'])
def home():
    auth_url = "https://www.strava.com/oauth/token"
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    athlete_url = "https://www.strava.com/api/v3/athlete"
    google = os.getenv('GOOGLE_MAPS_API_KEY')

    payload = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'refresh_token': os.getenv('REFRESH_TOKEN'),
        'grant_type': "refresh_token",
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)

    access_token = res.json()['access_token']

    header = {"Authorization" : 'Bearer ' + access_token}
    param = {"per_page" : 200, 'page': 1}
    dataset = requests.get(activities_url, headers=header, params=param).json()
    athleteSet = requests.get(athlete_url, headers=header).json()
    athleteImageURL = f'{athleteSet["profile"]}'
    athleteFirstName = f'{athleteSet["firstname"]}'
    athleteLastName = f'{athleteSet["lastname"]}'
    athleteFollowers = f'{athleteSet["follower_count"]}'
    athleteCity = f'{athleteSet["city"]}'
    recentMap = f'{dataset[0]["map"]["summary_polyline"]}'
    recentMiles = f'{round(dataset[0]["distance"]* 0.000621371, 2)}'
    recentTime = f'{datetime.timedelta(seconds=dataset[0]["moving_time"])}'
    recentKudos = f'{dataset[0]["kudos_count"]}'

    athleteTotal_url = "https://www.strava.com/api/v3/athletes/" + f'{athleteSet["id"]}' + "/stats"
    athleteTotalSet = requests.get(athleteTotal_url, headers=header).json()

    athleteRunTotal = f'{round(athleteTotalSet["all_run_totals"]["distance"] * 0.000621371, 2)}'

    singleActivity = []
    activityList = []

    for activity in dataset:
        singleActivity = []
        singleActivity.append(activity["id"])
        singleActivity.append(activity["name"])
        singleActivity.append(activity["type"])
        singleActivity.append(activity["start_date"])
        activityList.append(singleActivity)
    
    singleWatt = []
    wattList = []

    for watt in dataset:
        singleWatt = []
        if "Run" in activity["type"]:
            singleWatt.append(watt["start_date"])
            singleWatt.append(watt["distance"] * 0.000621371)
            wattList.append(singleWatt)

    labels = [row[0] for row in wattList]
    values = [row[1] for row in wattList]

    return render_template("home.html", activityList=activityList, athlete=athleteImageURL, athleteFirstName=athleteFirstName, athleteLastName=athleteLastName, labels=labels, values=values, recentMap=recentMap, athleteFollowers=athleteFollowers, athleteCity=athleteCity, athleteRunTotal=athleteRunTotal, recentMiles=recentMiles, recentTime=recentTime, recentKudos=recentKudos, google=google)