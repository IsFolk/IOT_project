import pygame
from datetime import datetime
import RPi.GPIO as GPIO
import time

import picam
from pyngrok import ngrok

from picamera import PiCamera
from subprocess import call 

import globals

result = datetime.now().strftime("%H:%M:%S")
print(result)


# Initiate the camera module with pre-defined settings.
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 15


def record(file_h264):
    camera.start_recording(file_h264)
    camera.wait_recording()
    
def convert(file_h264, file_mp4):
    camera.stop_recording()
    camera.close()
    print("Rasp_Pi => Video Recorded! \r\n")
    # Convert the h264 format to the mp4 format.
    command = "MP4Box -add " + file_h264 + " " + file_mp4
    call([command], shell=True)
    print("\r\nRasp_Pi => Video Converted! \r\n")

def upload(mp4):
    command = 'python3 uploadvideo.py --file="'+ mp4 + '"' + ' --title="'+str(datetime.now())+'"'+' --privacyStatus="private"'
    call([command], shell=True)

def PIRdetect():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #enter whether detected
    GPIO.setup(3, GPIO.OUT) #VCC

    try:
        loop = 0
        while True:
            i = GPIO.input(11)
            if i == 0: #Turn off
                print("No intruders")
                GPIO.output(3,0)
                time.sleep(0.1)
            elif i == 1: #Turn on
                print("Intruder detected")
                loop += 1
                GPIO.output(3,1)
                time.sleep(0.1)
            
            if loop > 10:
                #time.sleep(5)
                return True
    except KeyboardInterrupt:
        GPIO.cleanup()


def opensg90():
    CONTROL_PIN = 12
    PWM_FREQ = 50
    STEP=15

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CONTROL_PIN, GPIO.OUT)
     
    pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQ)
    pwm.start(0)
     
    def angle_to_duty_cycle(angle=0):
        duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
        print(angle)
        
        return duty_cycle
    pwm.ChangeDutyCycle(angle_to_duty_cycle(0))
    
    try:
        print('按下 Ctrl-C 可停止程式')
        for angle in range(0, 151, STEP):
            dc = angle_to_duty_cycle(angle)
            pwm.ChangeDutyCycle(dc)
            print('角度={: >3}, 工作週期={:.2f}'.format(angle, dc))
            time.sleep(0.1)
        pwm.ChangeDutyCycle(angle_to_duty_cycle(151))
        
        #if PIRdetect():            
            #time.sleep(3)
            #pwm.ChangeDutyCycle(angle_to_duty_cycle(0))
            #print('ok')
        #pwm.ChangeDutyCycle(angle_to_duty_cycle(0))            
        #pwm.ChangeDutyCycle(angle_to_duty_cycle(0))
        #while True:
            #next
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        pwm.stop()
        GPIO.cleanup()
        
def closesg90():
    CONTROL_PIN = 12
    PWM_FREQ = 50
    STEP=15

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CONTROL_PIN, GPIO.OUT)
     
    pwm = GPIO.PWM(CONTROL_PIN, PWM_FREQ)
    pwm.start(0)
     
    def angle_to_duty_cycle(angle=0):
        duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
        print(angle)
        
        return duty_cycle
    pwm.ChangeDutyCycle(angle_to_duty_cycle(0))
    
    try:
        print('按下 Ctrl-C 可停止程式')
        for angle in range(151, -1, -STEP):
            dc = angle_to_duty_cycle(angle)
            print('角度={: >3}, 工作週期={:.2f}'.format(angle, dc))
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        
        #while True:
            #next
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        pwm.stop()
        GPIO.cleanup()
        
def playsound():
    pygame.mixer.init()
    pygame.mixer.music.load('sample.mp3')
    pygame.mixer.music.play()
        
    while pygame.mixer.music.get_busy() == True:
        continue
    
def run(time_list):
    #globals.initialize()
    result = datetime.now().strftime("%H:%M:%S")
    #print(result)
    out = []
    if(time_list != []):
        if (result in time_list):
            file_h264 = 'test.h264'
            file_mp4 = 'test.mp4'
            record(file_h264)
            playsound()
            opensg90()
                        
            if PIRdetect():
                time.sleep(10)
                closesg90()
                convert(file_h264, file_mp4)
                upload(file_mp4)
                #print(globals.youtubeid)
                out.append("藥物已被拿取")
                #out.append(globals.youtubeid)
                return out
        return

        

