from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, storage
import pandas as pd
import io

app = Flask(__name__)
# /Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/Project_Carehub/CareWearDataDashboard/google-services.json
cred = credentials.Certificate('/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/Project_Carehub/CareWearDataDashboard/carewear-77d8e-b0c3a74e907c.json')
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
    'storageBucket': 'carewear-77d8e.appspot.com'
})
def num_mins():
    pass

########################################################
#  Ge the number of files from a given dates directory.
########################################################
def number_files():
    pass

def read_csv_from_firebase():
    bucket = storage.bucket()
    blobs = bucket.list_blobs()
    dfs = []
    main_list = []
    for blob in blobs:
        if blob.name.endswith('.csv'): 
            main_list.append(blob.name.split("/"))
    files_list_df = pd.DataFrame(main_list,columns=["deviceID","date","file_name"])
    file_count_json = {}
    for i in files_list_df["deviceID"].unique():
        # first subset the pandas df by unique device ID.
        files_list_df_device = files_list_df[files_list_df["deviceID"]==i] 
        # then subet by files: scc,gry,hr, and battery changed.
        files_list_df_acc = files_list_df_device[files_list_df_device["file_name"].str.contains('acc')]
        files_list_df_gry = files_list_df_device[files_list_df_device["file_name"].str.contains('gry')]
        files_list_df_hr = files_list_df_device[files_list_df_device["file_name"].str.contains('hr')]
        files_list_df_battery = files_list_df_device[files_list_df_device["file_name"].str.contains('on')]
        print("files_list_df_acc:::: ",files_list_df_acc)
        len_acc_files = files_list_df_acc.shape
        len_gry_files = files_list_df_gry.shape
        len_hr_files =files_list_df_hr.shape
        len_battery_files = files_list_df_battery.shape
        print("FILE ACC INFO ",i,len_acc_files[0])
        file_count_json[i] =[len_acc_files[0],len_gry_files[0],len_hr_files[0],len_battery_files[0]]
    return file_count_json
@app.route('/')
def home():
    file_count_json = read_csv_from_firebase()
    count_devices = len(file_count_json.keys())
    return render_template("home.html",file_count_json=file_count_json,count_devices=count_devices)
