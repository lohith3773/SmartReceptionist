import cv2
import os
import numpy as np
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import UserProfile
from django.http import HttpResponse
from .models import User
import pickle
import os
import pandas as pd
from keras.layers import Dense, GlobalAveragePooling2D
from keras.preprocessing import image
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras.optimizers import Adam
from keras_vggface.vggface import VGGFace
from keras.models import load_model
from django.shortcuts import render, redirect

camera = 1
BASE_DIR = str(settings.BASE_DIR)

def create_dataset(user):
    # Get user ID and name from the user object
    user_id = user.id
    name = user.username
    dataset_path = os.path.join(BASE_DIR,'media','dataimages','TrainingImage')
    # Capture face images using OpenCV
    cam = cv2.VideoCapture(camera)
    detector = cv2.CascadeClassifier(BASE_DIR + '/algorithms/haarcascade_frontalface_default.xml')
    sample_num = 0
    images = []
    path = os.path.join(dataset_path,name)
    os.mkdir(path)
    
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) # type: ignore
            # Incrementing sample number
            sample_num += 1
            # Saving the captured face in the TrainingImage directory
            images.append(gray[y:y+h,x:x+w])
            cv2.imwrite(path+'/' + name+ '.' + str(user_id) + '.' + str(sample_num) + '.jpg', gray[y:y+h,x:x+w])
            # Display the frame
            cv2.imshow('frame',img)
        # Wait for 100 milliseconds
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        # Break if the sample number is more than 60
        elif sample_num > 30:
            break
    cam.release()
    cv2.destroyAllWindows() 

def train_model():
    train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    train_generator = train_datagen.flow_from_directory(
        (BASE_DIR+'/media/dataimages/TrainingImage/'),
        target_size=(224,224),
        color_mode='rgb',
        batch_size=8,
        class_mode='categorical',
        shuffle=True)


    class_dictionary = train_generator.class_indices
    class_dictionary = {
        value:key for key, value in class_dictionary.items()
    }
    print(class_dictionary.keys)

    NO_CLASSES = len(train_generator.class_indices.values())


    base_model = VGGFace(include_top=False,model='vgg16',input_shape=(224, 224, 3))
    print(base_model)
    if base_model is not None:
        base_model.summary()
        print(len(base_model.layers))
        # 19 layers after excluding the last few layers
        x = base_model.output
        x = GlobalAveragePooling2D()(x)

        x = Dense(1024, activation='relu')(x)
        x = Dense(1024, activation='relu')(x)
        x = Dense(512, activation='relu')(x)

        # final layer with softmax activation
        preds = Dense(NO_CLASSES, activation='softmax')(x)

        model = Model(inputs = base_model.input, outputs = preds)
        model.summary()

        for layer in model.layers[:19]:
            layer.trainable = False
            
        for layer in model.layers[19:]:
            layer.trainable = True
        
        model.compile(optimizer='Adam',
            
            loss='categorical_crossentropy',
            metrics=['accuracy'])
        model.fit(train_generator,batch_size = 8, verbose = 1, epochs = 20) # type: ignore

        model.save('face_cnn_model.h5')

    # save the class dictionary to pickle
    face_label_filename = 'face-labels.pickle'
    with open(face_label_filename, 'wb') as f: pickle.dump(class_dictionary, f)

def recognize_face():
    face_cascade = cv2.CascadeClassifier(BASE_DIR + '/algorithms/haarcascade_frontalface_default.xml')

    # resolution of the webcam
    screen_width = 1280       # try 640 if code fails
    screen_height = 720

    # size of the image to predict
    image_width = 224
    image_height = 224
    model_path = BASE_DIR + "/models/face_cnn_model.h5"
    # load the trained model
    model = load_model(model_path)
    pic = BASE_DIR + "/models/face-labels.pickle"
    # the labels for the trained model
    with open(pic, 'rb') as f:
        og_labels = pickle.load(f)
        labels = {key: value for key, value in og_labels.items()}
        print(labels)

    # default webcam
    stream = cv2.VideoCapture(camera)
    verified_label = None
    verification_counter = 0
    verified_count = 0
    verified = False
    name = None
    if model is not None: 
        while not verified:
            # Capture frame-by-frame
            (grabbed, frame) = stream.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # try to detect faces in the webcam
            faces = face_cascade.detectMultiScale(rgb, scaleFactor=1.3, minNeighbors=5)

            # for each face found
            for (x, y, w, h) in faces: 
                roi_rgb = rgb[y:y+h, x:x+w]
                # Draw a rectangle around the face
                color = (255, 0, 0)  # in BGR
                stroke = 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, stroke) # type: ignore

                # resize the image
                size = (image_width, image_height)
                resized_image = cv2.resize(roi_rgb, size)
                image_array = np.array(resized_image, "uint8")
                img = image_array.reshape(1, image_width, image_height, 3) 
                img = img.astype('float32')
                img /= 255
                threshold = 0.7
                # predict the image
                predicted_prob = model.predict(img)
                if predicted_prob[0].max() > threshold:
                    name = labels[predicted_prob[0].argmax()]
                    if verified_count < 7:
                        if verified_count == 0:
                            verified_label = name
                        if name == verified_label:
                            verified_count += 1
                        else:
                            verified_count = 0
                    verification_counter += 1
                else:
                    name = "Unknown"
                    verification_counter = 0
                    verified_count = 0

                # Display the label
                font = cv2.FONT_HERSHEY_SIMPLEX
                color = (255, 0, 255)
                stroke = 2
                cv2.putText(frame, f'({name})', (x, y-8), font, 1, color, stroke, cv2.LINE_AA)

                # Show the frame
                cv2.imshow("Image", frame)
                key = cv2.waitKey(camera) & 0xFF
                if key == ord("q"):    # Press q to break out of the loop
                    break  
                if verified_count >= 7:
                    stream.release()
                    cv2.waitKey(camera)
                    cv2.destroyAllWindows()
                    cv2.waitKey(camera)
                    return name    

