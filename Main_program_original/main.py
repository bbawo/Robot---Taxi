import sys
import time
import math 
import serial
import pickle
from struct import unpack
import threading
import numpy as np
import socket as socket
import tensorflow as tf
from graph import Graph
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
from keras.models import load_model
from keras.preprocessing import image
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# define pi GPIO
GPIO_TRIGGER = 23

GPIO_ECHO0 = 22
GPIO_ECHO1 = 24

# output pin: Trigger
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
# input pin: Echo
GPIO.setup(GPIO_ECHO0,GPIO.IN)
GPIO.setup(GPIO_ECHO1,GPIO.IN)
# initialize trigger pin to low
GPIO.output(GPIO_TRIGGER, False)

def distance_sensor():
    

    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()

    while GPIO.input(GPIO_ECHO0)==0:
        start = time.time()
    while GPIO.input(GPIO_ECHO1)==0:
        start = time.time()
        
    while GPIO.input(GPIO_ECHO0)==1:
        stop = time.time()
    while GPIO.input(GPIO_ECHO1)==1:
        stop = time.time()


    elapsed = stop-start
    distance = (elapsed * 34300)/2

    return distance

class packet_processing(object):

    def __init__(self, packet):
       self.startx1,self.starty1, self.loc1, self.x1, self.y1,self.startx2,self.starty2, self.loc2, self.x2, self.y2= unpack('<bbbiibbbii',packet)
    def location_type(self):
        return (self.loc1)

    def x_coordinate(self):
        return (self.x1)

    def y_coordinate(self):
        return (self.y1)

class MainNeuralnetwork():
    def __init__(self):
         self.model = load_model("mymodel.h5")

    def prediction(self, image):
        return (self.model.predict(image))

    #processing image before feeding to model for prediction
    def image_processing(image):
        img = image.load_img(image, target_size = (width, height))
        img_tensor = image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis = 0)
        img_tensor /= 255.

        return img_tensor

class signNetwork():
    def __init__(self, modelname):
        self.model_s = load_model(str(modelname))

    #detect obj_type
    def detect_sign(frame):
        frame = self.preprocess(frame)
        prediction = self.model_s.predict(frame)
        return prediction[0]

    def preprocess(frame):
        return(np.array(frame).reshape(frame.shape[0], 50, 50, 3).astype('float32')/255.0 )


class Main(object):
    def __init__(self):
       

        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout = 1)
        self.fmaps = open('new_reduced_features.pkl', 'rb')
        self.feautre_map = pickle.load(self.fmaps)


        self.camera = PiCamera()
        self.network = MainNeuralnetwork()
        self.directions = Graph('data.txt')
        self.sensor_d = distance_sensor() 
        self.sign = signNetwork('trafficsigns.h5')
        self.direction_list = self.directions.get_directions(1, 1, 0)
        self.current_vertex = 1   #starting_vertex
        self.taxi_destination_index = 0
        self.main = threading.Thread(target= self.coordinate_server, args = ('192.168.1.100', 9999))
        

        
        client = threading.Thread(target= self.coordinate_server, args = ('192.168.1.100',9999 ))
        client.start()
        try:
            self.camera.resolution = (320, 240)      # pi camera resolution
            self.camera.framerate = 10 
            rawCapture = PiRGBArray(self.camera, size=(320, 240))             # 10 frames/sec
            time.sleep(1)  
            ### process the angle to arduino executable form
            for index in range(len(self.direction_list)):
                try:
                    print ('hey you')
                    vertex, angle, distance = self.direction_list[index]
                    start_time = time.time()
                    total_stop_time  = 0
                    self.current_vertex = vertex
                    self.ser.write(encode('f', angle))
                    for foo in self.camera.capture_continuous(rawCapture, format = "bgr", use_video_port = True):
                        image = foo.array
                        roi = image[120:240, :]
                        strng_prcssd_img  = self.network.image_processing(roi)
                        steering = self.network.prediction(strng_prcssd_img)
                        obj_type = self.sign.detect_sign(image) #image detection size - 50x50

                        current_dist = (time.time()-start_time - total_stop_time)*1.025

                        if((distance - current_dist <=0.10*distance) or (distance - current_dist >=0.9*distance)):
                            steering = angle     #process this to arduino executable
                        if int(steering) in self.feautre_map:
                            steering = int(steering)
                        else:
                            steering = int(steering)+1

                        if (distance_sensor()  <= 40):
                            self.ser.write('s'+str(self.feautre_map[steering]))
                            rawCapture.truncate(0)
                            continue

                       
                        if(obj_type == 6):       #indicating red                       
                            self.ser.write('s'+str(self.feautre_map[steering]))
                        elif(obj_type == 5):   #indicating Green
                            self.ser.write('f'+str(self.feautre_map[steering]))
                        elif(obj_type == 4 ):   # D-sign
                            self.ser.write('s'+str(self.feautre_map[steering]))
                            time.sleep(5)
                            total_stop_time += 5
                        elif(obj_type == 3 and self.direction_list[index+1][1] > 45):   #NoRightTurn
                            self.direction_list = self.directions.remove_edge(vertex, self.direction_list[index+1][0])

                        elif(obj_type == 2 and self.direction_list[index+1][1] < -45):   #NoLeftTurn
                            self.direction_list = self.directions.remove_edge(vertex, self.direction_list[index+1][0])
                        elif(obj_type == 1):  #No parking
                            pass
                        elif(obj_type == 0):#No entry
                            self.direction_list = self.directions.remove_edge(vertex, self.direction_list[index+1][0])
                        else:
                            self.ser.write('f'+str(self.feautre_map[steering]))



                        if (hasattr(self, taxi_task) and len(self.taxi_task) == 4 and  self.taxi_destination_index == 0 ):
                                self.direction_list = direction_list.get_direction(current_vertex, taxi_task[taxi_destination_index], angle)
                                self.taxi_destination_index += 1
                                index = 0
                                break

                        if(hasattr(self, taxi_task) and  index == len(self.direction_list)-1):
                            self.direction_list = direction_list.get_direction(current_vertex, taxi_task[taxi_destination_index], angle)
                            self.taxi_destination_index += 1
                            index = 0
                            break

                            if (current_dist == distance):
                                self.ser.write('s'+str(self.feautre_map[steering]))
                                break
                            rawCapture.truncate(0)

                except IndexError:
                        pass
        finally:
                GPIO.cleanup()
                "Round ended over !"

    def coordinate_server(self, ip_adress, port):
        packetList = []
        while True:
            client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip_adress, port))
            data = client.recv(1024)
        
            if data != "":
                packetList.append(data)

            if len(packetList) == 2:
                break

            pkt1 = packet_processing(packetList[0])
            pkt2 =  packet_processing(packetList[1])
        if(pkt1.location_type() == 0 and pkt2.location_type() == 1):
            self.directions.eval_line_equations(pkt1.x_coordinate(), pkt1.y_coordinate())
            v1, v2 = self.directions.pickup_dropoff_vertices()
            self.directions.eval_line_equations(pkt2.x_coordinate(), pkt2.y_coordinate())
            v3, v4 = self.directions.pickup_dropoff_vertices()
            self.taxi_task = [v1, v2, v3, v4]
        elif(pkt1.location_type() == 1 and pkt2.location_type() == 0):
            self.directions.eval_line_equations(pkt2.x_coordinate(), pkt2.y_coordinate())
            v1, v2 = self.directions.pickup_dropoff_vertices()
            self.directions.eval_line_equations(pkt1.x_coordinate(), pkt1.y_coordinate())
            v3, v4 = self.directions.pickup_dropoff_vertices()
            self.taxi_task = [v1, v2, v3, v4]
        else:
            print"packet error !"
            

if __name__ == '__main__':
    Main()
