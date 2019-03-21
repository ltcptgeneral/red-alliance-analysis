#Titan Robotics Team 2022: Super Script
#Written by Arthur Lu & Jacob Levine
#Notes:
#setup:

__version__ = "1.0.6.000"

__changelog__ = """changelog:
1.0.6.000:
    - added pulldata function
    - service now pulls in, computes data, and outputs data as planned
1.0.5.003:
    - hotfix: actually pushes data correctly now
1.0.5.002:
    - more information given
    - performance improvements
1.0.5.001:
    - grammar
1.0.5.000:
    - service now iterates forever
    - ready for production other than pulling json data
1.0.4.001:
    - grammar fixes
1.0.4.000:
    - actually pushes to firebase
1.0.3.001:
    - processes data more efficiently
1.0.3.000:
    - actually processes data
1.0.2.000:
    - added data reading from folder
    - nearly crashed computer reading from 20 GiB of data
1.0.1.000:
    - added data reading from file
    - added superstructure to code
1.0.0.000:
    - added import statements (revolutionary)
""" 

__author__ = (
    "Arthur Lu <arthurlu@ttic.edu>, "
    "Jacob Levine <jlevine@ttic.edu>,"
    )

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import analysis
#import titanlearn
import visualization
import os
import sys
import warnings
import glob
import numpy as np
import time
import tbarequest as tba
import csv

def titanservice():
    
    print("[OK] loading data")

    start = time.time()
    
    source_dir = 'data'
    file_list = glob.glob(source_dir + '/*.csv') #supposedly sorts by alphabetical order, skips reading teams.csv because of redundancy
    data = []
    files = [fn for fn in glob.glob('data/*.csv') 
             if not (os.path.basename(fn).startswith('teams'))] #scores will be handled sperately

    for i in files:
            data.append(analysis.load_csv(i))

    stats = []
    measure_stats = []
    teams = analysis.load_csv("data/teams.csv")
    scores = analysis.load_csv("data/scores.csv")

    end = time.time()

    print("[OK] loaded data in " + str(end - start) + " seconds")

    #assumes that team number is in the first column, and that the order of teams is the same across all files
    #unhelpful comment
    for measure in data: #unpacks 3d array into 2ds

        measure_stats = []

        for i in range(len(measure)): #unpacks into specific teams

                    ofbest_curve = [None]
                    r2best_curve = [None]

                    line = measure[i]

                    #print(line)

                    x = list(range(len(line)))
                    eqs, rmss, r2s, overfit = analysis.optimize_regression(x, line, 10, 1)

                    beqs, brmss, br2s, boverfit = analysis.select_best_regression(eqs, rmss, r2s, overfit, "min_overfit")

                    #print(eqs, rmss, r2s, overfit)
                    
                    ofbest_curve.append(beqs)
                    ofbest_curve.append(brmss)
                    ofbest_curve.append(br2s)
                    ofbest_curve.append(boverfit)
                    ofbest_curve.pop(0)

                    #print(ofbest_curve)

                    beqs, brmss, br2s, boverfit = analysis.select_best_regression(eqs, rmss, r2s, overfit, "max_r2s")

                    r2best_curve.append(beqs)
                    r2best_curve.append(brmss)
                    r2best_curve.append(br2s)
                    r2best_curve.append(boverfit)
                    r2best_curve.pop(0)

                    #print(r2best_curve)

                    
                    measure_stats.append(teams[i] + list(analysis.basic_stats(line, 0, 0)) + list(analysis.histo_analysis(line, 1, -3, 3)) + ofbest_curve + r2best_curve)

        stats.append(list(measure_stats))
        nishant = []
            
        for i in range(len(scores)):

                    ofbest_curve = [None]
                    r2best_curve = [None]

                    line = measure[i]

                    #print(line)

                    x = list(range(len(line)))
                    eqs, rmss, r2s, overfit = analysis.optimize_regression(x, line, 10, 1)

                    beqs, brmss, br2s, boverfit = analysis.select_best_regression(eqs, rmss, r2s, overfit, "min_overfit")

                    #print(eqs, rmss, r2s, overfit)
                    
                    ofbest_curve.append(beqs)
                    ofbest_curve.append(brmss)
                    ofbest_curve.append(br2s)
                    ofbest_curve.append(boverfit)
                    ofbest_curve.pop(0)

                    #print(ofbest_curve)

                    beqs, brmss, br2s, boverfit = analysis.select_best_regression(eqs, rmss, r2s, overfit, "max_r2s")

                    r2best_curve.append(beqs)
                    r2best_curve.append(brmss)
                    r2best_curve.append(br2s)
                    r2best_curve.append(boverfit)
                    r2best_curve.pop(0)

                    #print(r2best_curve)
                    
                    z = len(scores[0]) + 1
                    nis_num = []

                    nis_num.append(eval(str(ofbest_curve[0])))
                    nis_num.append(eval(str(r2best_curve[0])))

                    nis_num.append((eval(ofbest_curve[0]) + eval(r2best_curve[0])) / 2)

                    nishant.append(teams[i] + nis_num)
                
    json_out = {}
    score_out = {}

    for i in range(len(teams)):
            score_out[str(teams[i][0])] = (nishant[i])

    location = db.collection(u'stats').document(u'stats-noNN')
    for i in range(len(teams)):
        general_general_stats = location.collection(teams[i][0])
        
        for j in range(len(files)):
            json_out[str(teams[i][0])] = (stats[j][i])
            name = os.path.basename(files[j])
            general_general_stats.document(name).set({'stats':json_out.get(teams[i][0])})

    for i in range(len(teams)):
        nnum = location.collection(teams[i][0]).document(u'nishant_number').set({'nishant':score_out.get(teams[i][0])})

def pulldata():
    teams = analysis.load_csv('data/teams.csv')
    scores = []
    for i in range(len(teams)):
        team_scores = []
        #print(teams[i][0])
        request_data_object = tba.req_team_matches(teams[i][0], 2019, "UDvKmPjPRfwwUdDX1JxbmkyecYBJhCtXeyVk9vmO2i7K0Zn4wqQPMfzuEINXJ7e5")
        json_data = request_data_object.json()
        for match in range(len(json_data) - 1, -1, -1):
            if json_data[match].get('winning_alliance') == "":
                print(json_data[match])
                json_data.remove(json_data[match])

            
        json_data = sorted(json_data, key=lambda k: k.get('actual_time', 0), reverse=False)
        for j in range(len(json_data)):
            if "frc" + teams[i][0] in json_data[j].get('alliances').get('blue').get('team_keys'):
                team_scores.append(json_data[j].get('alliances').get('blue').get('score'))
            elif "frc" + teams[i][0] in json_data[j].get('alliances').get('red').get('team_keys'):
                team_scores.append(json_data[j].get('alliances').get('red').get('score'))
        scores.append(team_scores)

    with open("data/scores.csv", "w+", newline = '') as file:
        writer = csv.writer(file, delimiter = ',')
        writer.writerows(scores)
            
def service():

    while True:

        pulldata()

        start = time.time()

        print("[OK] starting calculations")

        fucked = False
        
        for i in range(0, 5):
            try:
                titanservice()
                break
            except:
                if (i != 4):
                    print("[WARNING] failed, trying " + str(5 - i - 1) + " more times")
                else:
                    print("[ERROR] failed to compute data, skipping")
                    fucked = True

        end = time.time()
        if (fucked == True):

            break

        else:
            
            print("[OK] finished calculations")

        print("[OK] waiting: " + str(300 - (end - start)) + " seconds" + "\n")

        time.sleep(300 - (end - start)) #executes once every 5 minutes

warnings.simplefilter("ignore")
#Use a service account
try:
    cred = credentials.Certificate('keys/firebasekey.json')
except:
    cred = credentials.Certificate('keys/keytemp.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

service() #finally we write something that isn't a function definition
#titanservice()