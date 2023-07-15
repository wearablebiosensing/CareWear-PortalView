from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, storage, db
import pandas as pd
import io
import tempfile
import csv


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
        'storageBucket': "carewear-77d8e.appspot.com",
        'databaseURL': 'https://carewear-77d8e-default-rtdb.firebaseio.com/'
})
ref = db.reference('/sensors_message')  # Path to your sensor data node in the database


@app.route('/')
def home():
  return render_template("canvas.html")








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
            header_row = ['x', 'y', 'timestamp']
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
            # file_name = temp_file.name.split('/')[-1]
            # print(file_name)
            # blob = bucket.blob('MagneticTiles/' + file_name)  # Use the temp file name as the blob name
            # blob.upload_from_file(temp_file)
            


        # Clear the accumulated data
        accumulated_data.clear()

    response = {'message': 'Data received and processed successfully'}
    return jsonify(response)
