import RPi.GPIO as GPIO
import time

DIR_PIN = 16 
STEP_PIN = 20 

STEPS_PER_REV = 200  
STEPS_FOR_80_DEG = (STEPS_PER_REV * 80) // 360


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(DIR_PIN, GPIO.HIGH) 
        
        for _ in range(STEPS_FOR_80_DEG):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.005)

        time.sleep(1)

        GPIO.output(DIR_PIN, GPIO.LOW)

        for _ in range(STEPS_FOR_80_DEG):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(0.005)

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
