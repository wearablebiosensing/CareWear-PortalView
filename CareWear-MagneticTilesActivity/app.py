import io
import tempfile
import csv
import re
import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify, redirect,url_for, Response
import firebase_admin
from firebase_admin import credentials, storage, db
import pandas as pd
import numpy as np
import scipy.signal as signal
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
# pip3 install -r flask firebase-admin pandas scipy numpy matplotlib
import threading
csv_lock = threading.Lock()

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
socketio = SocketIO(app)
# Subscribe to multiple topics
# topics = [("M5StackcPlus/acceleration", 0), ("M5StackcPlus/hello", 0)]  # Replace with your desired topics and QoS level

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    # for topic, qos in topics:
    client.subscribe("M5StackcPlus/acceleration",0)  # Subscribe to the MQTT topic

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    print(f"Received message on topic '{topic}': {payload}")
    # if topic.split("/") == "hello":
    #     data = message.payload.decode()
    #     print(f"Received message Hello Topic: {topic}")
    #     print(f"Received message: {data}")
    #     socketio.emit('mqtt_message2', {'data': data})
    data = message.payload.decode()
    print(f"Received message acceleration: {topic}")
    print(f"Received message: {data}")
    socketio.emit('mqtt_message', {'data': data})



mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883)

@app.route('/mqtt_connect_page')
def mqtt_connect():
    return render_template('mqtt_template.html')

@socketio.on('connect')
def handle_connect():
    print('WebSocket connected')

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


@app.route('/tiles_game', methods=['GET','POST'])
def tiles_game():
  return render_template("tiles.html")


# ----------- Routes for the scoring Page -----------------

#Shows renders the scoring page with some parameters
@app.route('/scoring_page', methods=['GET','POST'])
def scoring_page():
    userID = request.args.get('userID')
    level = int(request.args.get('level'))
    return render_template("scoring_module.html", userID=userID, level=level)


#The scoring page calls to this route when loading to get the graph based on input
@app.route('/mouse_movement_graph/<userID>/<level>')
def scoring_graph(userID, level):
    csv_file = f"Level_{level} - user{userID}.csv"  # Adjust the file naming pattern as needed
    with csv_lock:
        image_data = plot_mouse_movement(csv_file)
    return Response(image_data, mimetype='image/png')


@app.route('/acceleration_graph/<userID>/<level>')
def acceleration_graph(userID, level):
    csv_file = f"Level_{level} - user{userID}.csv"  # Adjust the file naming pattern as needed
    with csv_lock:
        image_data = plot_acceleration_data(csv_file)
    return Response(image_data, mimetype='image/png')


# Route to return completion time
@app.route('/completion_time/<userID>/<level>')
def completion_time(userID, level):
    csv_file = f"Level_{level} - user{userID}.csv"  # Adjust the file naming pattern as needed

    level_completion_time = calculate_completion_time(csv_file)
    return level_completion_time

#================= Helper Functions =============================

# Function to calculate time taken to complete a level
def calculate_completion_time(csv_file):
    timestamps = []
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if row['timestamp'] != '0':
                timestamps.append(row['timestamp'])
                
    # Parse the timestamps and calculate the time duration            
    first_timestamp = timestamps[0]
    last_timestamp = timestamps[-1]
    
    format_str = '%H:%M:%S:%f'
    first_time = datetime.strptime(first_timestamp, format_str)
    last_time = datetime.strptime(last_timestamp, format_str)
    duration = last_time - first_time

    # Convert duration to a formatted string
    total_seconds = duration.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return f"{minutes} minutes {seconds} seconds"

#Retuns the image data of the mouse movment graph given a csv file
def plot_mouse_movement(csv_file):
    colors = {'Square': '#ec940e', 'Circle': '#F29595', 'Right Triangle': '#90C0FF', 'Hexagon': '#1184e2', 'Trapezoid': '#61a962', 'Equilateral Triangle': '#a1e87e', 'Yellow Diamond': '#FFCC4D', 'Purple Diamond': '#9F9AFF'}


    df = pd.read_csv(csv_file)
    strokes = []
    current_stroke = []
    unique_shapes = set()  # To keep track of unique shapes

    for _, row in df.iterrows():
        if row['x'] == "END_OF_STROKE":
            if current_stroke:
                strokes.append(current_stroke)
                current_stroke = []
        else:
            current_stroke.append(row)
            unique_shapes.add(row['shape'])  # Add the shape to the unique_shapes set

    if current_stroke:
        strokes.append(current_stroke)

    # Set a larger figure size for the graph (adjust the numbers as needed)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.invert_yaxis()  # Flip the y-axis

    for stroke in strokes:
        if len(stroke) > 1:
            shape = stroke[-1]['shape']  # Get the shape from the last row of the stroke
            # screenWidth = stroke[-1]['screenWidth']
            # screenHeight = stroke[-1]['screenHeight']
            
            #Plot Data
            data = pd.DataFrame(stroke)
            color = colors.get(shape, 'black')
            
            # Convert 'x' values to numeric
            data['x'] = pd.to_numeric(data['x'])
            # print(data['x'])
            
            plt.plot(data['x'], data['y'], color=color, label=shape)



    plt.xlabel('X Position')
    plt.ylabel('Y Position')
    plt.title('Mouse Movement Strokes')

    # Generate a single legend entry for each unique shape
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    unique_legend = [by_label[shape] for shape in unique_shapes]
    plt.legend(handles=unique_legend, labels=unique_shapes)

    # plt.gca().set_aspect('equal')  # Set aspect ratio to preserve the screen's aspect ratio



    # Add custom x-ticks with rotation
    screenWidth = strokes[-1][-1]['screenWidth']  # Get the screenWidth from the last stroke
    screenHeight = strokes[-1][-1]['screenHeight']  # Get the screenWidth from the last stroke
    
        
    
    plt.xticks([val for val in range(0, screenWidth + 1, int(screenWidth / 20))],
            [str(val) for val in range(0, screenWidth + 1, int(screenWidth / 20))], rotation=90)

    plt.grid()  # Add grid lines for better visualization

    # Convert the plot to a PNG image in memory
    image_stream = io.BytesIO()
    FigureCanvas(fig).print_png(image_stream)
    plt.close(fig)

    # Get the image data as a base64-encoded string
    image_data = image_stream.getvalue()
    

    return image_data

def plot_acceleration_data(csv_file):
    df = pd.read_csv(csv_file)

    # Remove rows with 'END_OF_STROKE' entries
    df = df[df['x(px/s^2)'] != 'END_OF_STROKE']

    # Convert timestamp column to datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S:%f')

    # Convert acceleration columns to numeric values
    df['x(px/s^2)'] = pd.to_numeric(df['x(px/s^2)'])
    df['y(px/s^2)'] = pd.to_numeric(df['y(px/s^2)'])

    # Create a new figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot acceleration x and y over time
    ax.plot(df['timestamp'], df['x(px/s^2)'], label='Acceleration x')
    ax.plot(df['timestamp'], df['y(px/s^2)'], label='Acceleration y')

    # Set plot labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Acceleration')
    ax.set_title(f'Acceleration x and y over Time - {csv_file}')
    ax.legend()

    # Convert the plot to a PNG image in memory
    image_stream = io.BytesIO()
    FigureCanvas(fig).print_png(image_stream)
    plt.close(fig)

    # Get the image data as a base64-encoded string
    image_data = image_stream.getvalue()

    return image_data

# Specify the directory for the temporary file
TEMP_FILE_DIRECTORY = './'

@app.route('/process-mouse-data', methods=['POST'])
def processMouseMovementData():
    res = request.get_json()
    data = res["data"]
    level = res["level"] #Current level that posted data is from
    userID = res["userID"] #Used to differentiate csv files from differet subjects
    
    
    # Generate a unique prefix for the tempfile using level and userID
    temp_file_name = f"Level_{level} - user{userID}.csv"

    # Create a named temporary file in memory
    # with tempfile.NamedTemporaryFile(prefix=temp_file_prefix, mode="w+b", delete=False, suffix=".csv", dir=TEMP_FILE_DIRECTORY) as temp_file:
    
    with open(temp_file_name, mode="w+b") as temp_file:

        
        # Create the header row
        header_row = ['x', 'y', 'timestamp', 'shape', 'x(px/s^2)', 'y(px/s^2)', 'screenWidth', 'screenHeight']
        csv_data = [header_row] + data

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
    response = {'message': 'Data received and processed successfully'}
    return jsonify(response)



if __name__ == '__main__':
    mqtt_client.loop_start()
    socketio.run(app, debug=True)
