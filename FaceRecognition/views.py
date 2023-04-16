from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from pathlib import Path
import numpy as np
from PIL import Image
from .models import User,Visitors
import cv2
import face_recognition
import os


def create_dataset(request):
    if request.method == 'POST':
        Id = request.POST['userId']
        name = request.POST['userId1']
        user_dir = os.path.join(str(settings.BASE_DIR), 'static/images/TrainingImage', str(Id))
        os.makedirs(user_dir, exist_ok=True)
        visitor = Visitors(Visitor_id=Id, Visitor_Name=name)
        visitor.save()
        cam = cv2.VideoCapture(0)
        detector = cv2.CascadeClassifier(str(settings.BASE_DIR)+'/algorithms/haarcascade_frontalface_default.xml')
        sampleNum = 0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # incrementing sample number
                sampleNum = sampleNum + 1
                # saving the captured face in the dataset folder TrainingImage
                cv2.imwrite(os.path.join(user_dir, f"{name}.{Id}.{str(sampleNum)}.jpg"), gray[y:y+h, x:x+w])
                # display the frame
                cv2.imshow('frame', img)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is more than 60
            elif sampleNum > 60:
                break
        cam.release()
        cv2.destroyAllWindows()

        # Train the facial recognition model with the captured dataset
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier(str(settings.BASE_DIR)+'/algorithms/haarcascade_frontalface_default.xml')
        faces, Ids = getImagesAndLabels(user_dir)
        recognizer.train(faces, np.array(Ids))
        recognizer.save(str(settings.BASE_DIR)+"/algorithms/TrainingImageLabel/Trainner.yml")
        cv2.destroyAllWindows()

        return render(request, 'dashboard.html')
    else:
        return render(request, 'register.html')
def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
        
    #create empth face list
    faces=[]
    #create empty ID list
    Ids=[]
    #now looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the Id from the image
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        Ids.append(Id)     
        cv2.imshow("Training", imageNp)
        cv2.waitKey(10)   
    return faces,Ids





def register(request):
    return render(request, 'register.html')


def face_recognition(request):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(settings.BASE_DIR)+'/algorithms/TrainingImageLabel/Trainner.yml')
    harcascadePath = "algorithms/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y : y + h, x : x + w])

            if conf < 100:
                # Get the user's profile from the database
                Visitor = Visitors.objects.get(Visitor_id=Id)
                # Log in the user by setting session variables or other authentication mechanisms
                request.session['user_id'] = Visitor.Visitor_id
                request.session['user_name'] = Visitor.Visitor_Name
                return redirect('/dashboard/' + str(Id))
            else:
                Id = 'Unknown'
                tt = str(Id)

            cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)

        cv2.imshow('im', im)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    return redirect('home')

def login(request):
    return render(request, 'login.html')


def dashboard(request):
    return render(request, 'dashboard.html')