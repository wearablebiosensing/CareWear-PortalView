from flask import Flask, render_template, request, jsonify, redirect,url_for
import firebase_admin
from firebase_admin import credentials, storage, db
import pandas as pd
import io
import tempfile
import csv
import re
import os
import scipy.signal as signal
import numpy as np



app = Flask(__name__)
root = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/Project_Carehub/CareWear-PortalView/CareWear-MagneticTilesActivity/"

cred = credentials.Certificate('./carewear-77d8e-b0c3a74e907c.json') 

firebaseConfig = {
  "apiKey": "AIzaSyDyjHLuokjuGEPr3HOSsX8FP16qxyS62W8",
  "authDomain": "carewear-77d8e.firebaseapp.com",
  "databaseURL": "https://carewear-77d8e-default-rtdb.firebaseio.com",
  "projectId": "carewear-77d8e",
  "storageBucket": "carewear-77d8e.appspot.com",
  "messagingSenderId": "683558385369",
  "appId": "1:683558385369:web:1d729eff041a05d547b0c8"
}
firebase_admin.initialize_app(cred, {
        'storageBucket': 'carewear-77d8e.appspot.com',
        'databaseURL': 'https://carewear-77d8e-default-rtdb.firebaseio.com/'
})
ref = db.reference('/sensors_message')  # Path to your sensor data node in the database
## For each individual file within the Watch folder Eg: 638116435299306610_30hz.csv
## Quality check for each file get the parameters and write to a results file.
# per_watch - is a list of CSV files in a folder.
def local_file_read(per_watch,root):
    df_acc_list = []
    for file in per_watch: # Get the CSV files for the given watch ID.
        if re.search('acc', file):
            print("All Acc files: ",file)
            df_acc = pd.read_csv(root + "/"+file)
            df_acc_list.append(df_acc)
    df_20 = pd.concat(df_acc_list)
    print(df_20.head())
    print("Start and End Timestamp: ",df_20.iloc[0]["DateTime"],df_20.iloc[df_20.shape[0]-1]["DateTime"])
    # Convert the Timestamp column to datetime objects
    df_20['Timestamp'] = pd.to_datetime(df_20['DateTime'], format='%H:%M:%S:%f')
    # Sort the DataFrame by the Timestamp column
    df_20_sorted = df_20.sort_values('Timestamp')
    print("Sorted Start and End Timestamp: ",df_20_sorted.iloc[0]["DateTime"],df_20_sorted.iloc[df_20_sorted.shape[0]-1]["DateTime"])
    print("New sorted df",df_20_sorted.columns)
    accel_data_x = np.array(df_20_sorted[' x'])
    accel_data_y = np.array(df_20_sorted['y'])
    accel_data_z = np.array(df_20_sorted['z'])
    zcr_x = calculate_zero_crossing_rate(accel_data_x)
    zcr_y = calculate_zero_crossing_rate(accel_data_y)
    zcr_z = calculate_zero_crossing_rate(accel_data_z)
    print("ZCR X:", zcr_x)
    print("ZCR Y:", zcr_y)
    print("ZCR Z:", zcr_z)
    
# Takes in a numpy array of values from the accelerometer data
def calculate_zero_crossing_rate(accel_data):
    accel_data = (accel_data - np.mean(accel_data)) / np.std(accel_data)
        # Calculate Zerocrossing rate.
    zero_crossings = np.nonzero(np.diff(np.signbit(accel_data)))[0]
    zcr = len(zero_crossings) / (2.0 * len(accel_data))
    return zcr

# Read data form cloud. 
def read_csv_from_firebase():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    print("blobs: ",blobs)
    main_list = []
    acc_df_list = []
    for blob in blobs:
        if blob.name.endswith('.csv') and blob.name.split("/")[0]=="fff6be8bb6243e97" and blob.name.split("/")[1]=="11-07-2023":  
            print("blob.name.split: ",blob.name.split("/"))
            main_list.append(blob.name.split("/"))
        if blob.name.endswith('.csv') and 'acc' in blob.name and blob.name.split("/")[0]=="fff6be8bb6243e97" and blob.name.split("/")[1]=="11-07-2023":
              print("blob.name. ACC data === ",blob.name)
              csv_data = blob.download_as_text()
              df_acc = pd.read_csv(io.StringIO(csv_data))
              acc_df_list.append(df_acc)
    acc_df = pd.concat(acc_df_list, ignore_index=True)
    # Convert the Timestamp column to datetime objects
    acc_df['Timestamp'] = pd.to_datetime(acc_df['DateTime'], format='%H:%M:%S:%f')
    # Sort the DataFrame by the Timestamp column
    acc_df_sorted = acc_df.sort_values('Timestamp')
    print("Sorted Start and End Timestamp: ",acc_df_sorted.iloc[0]["DateTime"],acc_df_sorted.iloc[acc_df_sorted.shape[0]-1]["DateTime"])
    print("New sorted df",acc_df_sorted.columns)  
    print(acc_df.columns,acc_df.shape)
    # This is a list of all files in the folder. 
    files_list_df = pd.DataFrame(main_list,columns=["deviceID","date","file_name"])
    return files_list_df

def count_files(files_list_df):
    file_count_json = {}
    for i in files_list_df["deviceID"].unique():
        if i == "fff6be8bb6243e97":
          # first subset the pandas df by unique device ID.
          files_list_df_device = files_list_df[files_list_df["deviceID"]==i] 
          # then subet by files: scc,gry,hr, and battery changed.
          files_list_df_acc = files_list_df_device[files_list_df_device["file_name"].str.contains('acc')]
          files_list_df_gry = files_list_df_device[files_list_df_device["file_name"].str.contains('gry')]
          files_list_df_hr = files_list_df_device[files_list_df_device["file_name"].str.contains('hr')]
          files_list_df_battery = files_list_df_device[files_list_df_device["file_name"].str.contains('on')]
          # print("files_list_df_acc:::: ",files_list_df_acc)
          # for acc_file in files_list_df_acc:
          #     csv_data = acc_file.download_as_text()
          #     df_acc = pd.read_csv(io.StringIO(csv_data))
          #     acc_df_list.append(df_acc)
          len_acc_files = files_list_df_acc.shape
          len_gry_files = files_list_df_gry.shape
          len_hr_files =files_list_df_hr.shape
          len_battery_files = files_list_df_battery.shape
          print("FILE ACC INFO ",i,len_acc_files[0])
          file_count_json[i] =[len_acc_files[0],len_gry_files[0],len_hr_files[0],len_battery_files[0]]
    return file_count_json


@app.route('/')
@app.route('/landing')
def home():
  return render_template("landing_page.html")


@app.route('/tiles-game')
def tiles_game():
  return render_template("tiles.html")

@app.route('/scoring-page', methods=['GET','POST'])
def scoring_page():
  return render_template("scoring_module.html")

@app.route('/scoring', methods=['GET','POST'])
def level_complete():
    return redirect(url_for("scoring_page"))


 






# Number of data points to accumulate before writing to the CSV file and uploading
THRESHOLD = 100

# Keep track of accumulated data
accumulated_data = []

# Specify the directory for the temporary file
TEMP_FILE_DIRECTORY = './'

@app.route('/process-mouse-data', methods=['POST'])
def processMouseMovementData():
    res = request.get_json()
    data = res["data"]

    # Accumulate the data
    accumulated_data.extend(data)

    

    # Check if the threshold is reached
    if len(accumulated_data) >= THRESHOLD:
        print("UPLOADING")
        # Create a named temporary file in memory
        with tempfile.NamedTemporaryFile(mode="w+b", delete=False, suffix=".csv", dir=TEMP_FILE_DIRECTORY) as temp_file:

            
            # Create the header row
            header_row = ['x', 'y', 'timestamp', 'shape', 'x(px/s^2)', 'y(px/s^2)']
            csv_data = [header_row] + accumulated_data

            # Convert the accumulated data to a CSV string
            csv_data = '\n'.join([','.join(map(str, row)) for row in csv_data])
            csv_data = csv_data.encode('utf-8')

            # Write the CSV data to the temporary file
            temp_file.write(csv_data)

            # Reset the file position back to the beginning
            temp_file.seek(0)

            # Upload the CSV file to Firebase Storage
            #UNCOMMENT BELOW TO UPLOAD TO FIREBASE
            # bucket = storage.bucket()
            # file_name = temp_file.name.split('\\')[-1]
            # print(file_name)
            # blob = bucket.blob('MagneticTiles/' + file_name)  # Use the temp file name as the blob name
            # blob.upload_from_file(temp_file)
            


        # Clear the accumulated data
        accumulated_data.clear()

    response = {'message': 'Data received and processed successfully'}
    return jsonify(response)

#root = "/Users/shehjarsadhu/Desktop/11-07-2023"
#file_list = os.listdir(root)
#print("file_list: ",file_list)
# local_file_read(file_list,root)
#read_csv_from_firebase()
# file_count_json = read_csv_from_firebase()

