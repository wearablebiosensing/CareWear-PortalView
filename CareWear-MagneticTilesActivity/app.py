from flask import Flask, render_template, Response
import firebase_admin
from firebase_admin import credentials, storage, db
import pandas as pd
import io
import cv2
from cvzone.HandTrackingModule import HandDetector


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
        'databaseURL': 'https://carewear-77d8e-default-rtdb.firebaseio.com/'
})
ref = db.reference('/sensors_message')  # Path to your sensor data node in the database

def hand_tracking():
    cap = cv2.VideoCapture(0)
    detector = HandDetector(detectionCon=0.8, maxHands=2)
    colorR = (255,0,255)
    cx =100
    cy= 100
    w= 200
    h = 200

    while True:
        # Get image frame
        success, img = cap.read()
        img=cv2.flip(img,1)
        # Find the hand and its landmarks
        hands, img = detector.findHands(img)  # with draw
        # hands = detector.findHands(img, draw=False)  # without draw
        if hands:
            # Hand 1
            hand1 = hands[0]
            lmList1 = hand1["lmList"]  # List of 21 Landmark points
            bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
            centerPoint1 = hand1['center']  # center of the hand cx,cy
            handType1 = hand1["type"]  # Handtype Left or Right

            fingers1 = detector.fingersUp(hand1)
            # Distance function to drag and drop the tiles.
            # l, info, img = detector.findDistance(8,12,img)
            l, info, img = detector.findDistance(lmList1[8][:2], lmList1[12][:2], img)
            print("Distance: ",l)
            if l<45:
                # Detect if finger tip (#8) are within the box.
                cursor =lmList1[8]
                # check the left and the right values of the box
                if cx-w//2<cursor[0]<cy+w//2 and cy-h//2<cursor[1]<cy+h//2:
                    colorR = (0,255,0)
                    print("cursor: ",cursor)
                    cx, cy = cursor[0], cursor[1]
                else:
                    colorR = (255,0,255)

            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                lmList2 = hand2["lmList"]  # List of 21 Landmark points
                bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
                centerPoint2 = hand2['center']  # center of the hand cx,cy
                handType2 = hand2["type"]  # Hand Type "Left" or "Right"
                fingers2 = detector.fingersUp(hand2)

                # Find Distance between two Landmarks. Could be same hand or different hands
                # length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)  # with draw
                # length, info = detector.findDistance(lmList1[8], lmList2[8])  # with draw
        # Create a rectangle.
        #    cx ,cy,w,h
        cv2.rectangle(img,(cx-w//2,cy-h//2),(cx+w//2,cy+h//2),colorR, cv2.FILLED)
        # Display
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        # cap.release()
        # cv2.destroyAllWindows()
        # Convert the frame to JPEG format
        success, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')



@app.route('/video')
def video():
    return Response(hand_tracking(),mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/')
def home():
 
    return render_template("home.html")
