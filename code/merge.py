# import sys
# import os

# libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
# if os.path.exists(libdir):
#     sys.path.append(libdir)

# import logging
# import time
# from waveshare_epd import epd3in7
# from PIL import Image, ImageDraw, ImageFont
# import RPi.GPIO as GPIO
# import threading

# # ========== GPIO ==========
# STEP_DIR_PIN_1 = 22
# STEP_PIN_1 = 20
# BUTTON_PIN = 22 

# STEPS_PER_REV = 200
# STEPS_FOR_80_DEG = (STEPS_PER_REV * 80) // 360

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(STEP_PIN_1, GPIO.OUT)
# GPIO.setup(STEP_DIR_PIN_1, GPIO.OUT)
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# # ========== motor control ==========
# motor_running = False

# def rotate_motor():
#     global motor_running
#     while motor_running:
#         GPIO.output(STEP_DIR_PIN_1, GPIO.HIGH)
#         for _ in range(STEPS_FOR_80_DEG):
#             if not motor_running:
#                 return
#             GPIO.output(STEP_PIN_1, GPIO.HIGH)
#             time.sleep(0.005)
#             GPIO.output(STEP_PIN_1, GPIO.LOW)
#             time.sleep(0.005)
#         time.sleep(1)

#         GPIO.output(STEP_DIR_PIN_1, GPIO.LOW)
#         for _ in range(STEPS_FOR_80_DEG):
#             if not motor_running:
#                 return
#             GPIO.output(STEP_PIN_1, GPIO.HIGH)
#             time.sleep(0.005)
#             GPIO.output(STEP_PIN_1, GPIO.LOW)
#             time.sleep(0.005)
#         time.sleep(1)

# # ========== E-Paper ==========
# logging.basicConfig(level=logging.DEBUG)

# try:
#     logging.info("epd3in7 Clock and Emoji Display")

#     epd = epd3in7.EPD()
#     logging.info("Init and Clear")
#     epd.init(1)
#     epd.Clear(0x00, 1)

#     picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
#     font_path = os.path.join(picdir, 'Font.ttc')
#     if not os.path.exists(font_path):
#         font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
#     font_large = ImageFont.truetype(font_path, 50)

#     width, height = epd.height, epd.width
#     time_image = Image.new('1', (width, height), 0)
#     time_draw = ImageDraw.Draw(time_image)

#     emoji_size = 150
#     emoji_x = (width - emoji_size) // 2
#     emoji_y = (height - emoji_size) // 2

#     prev_time = ""
#     countdown_started = False
#     start_time = 0
#     total_time = 1 * 60
#     motor_thread = None

#     while True:
#         if GPIO.input(BUTTON_PIN) == GPIO.LOW:
#             time.sleep(0.1)
#             if not countdown_started:
#                 logging.info("start")
#                 while GPIO.input(BUTTON_PIN) == GPIO.LOW:
#                     time.sleep(0.05)
#                 start_time = time.time()
#                 logging.debug("start_time: %s", start_time)
#                 countdown_started = True

#                 motor_running = True
#                 motor_thread = threading.Thread(target=rotate_motor)
#                 motor_thread.start()
#             else:
#                 logging.info("stop")
#                 countdown_started = False
#                 motor_running = False
#                 if motor_thread:
#                     motor_thread.join()
#                 while GPIO.input(BUTTON_PIN) == GPIO.LOW:
#                     time.sleep(0.05)

#         current_time = time.strftime('%H:%M:%S')

#         if countdown_started:
#             elapsed = time.time() - start_time
#             remaining_time = max(0, int(total_time - elapsed))
#             logging.debug("elapsed: %.2f, remaining_time: %d", elapsed, remaining_time)
#             if remaining_time == 0:
#                 logging.info("end")
#                 countdown_started = False
#                 motor_running = False
#                 if motor_thread:
#                     motor_thread.join()
#         else:
#             remaining_time = total_time

#         minutes = remaining_time // 60
#         seconds = remaining_time % 60
#         countdown = f"{minutes:02}:{seconds:02}"

#         if current_time != prev_time:
#             time_draw.rectangle((0, 0, width, height), fill=0)
#             time_draw.text((10, 10), current_time, font=font_large, fill=255)
#             time_draw.text((10, 70), countdown, font=font_large, fill=255)

#             time_draw.arc((emoji_x, emoji_y, emoji_x + emoji_size, emoji_y + emoji_size), 0, 360, fill=255, width=4)
#             eye_size = 5
#             time_draw.ellipse((emoji_x + emoji_size // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size,
#                                emoji_x + emoji_size // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)
#             time_draw.ellipse((emoji_x + emoji_size * 2 // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size,
#                                emoji_x + emoji_size * 2 // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)

#             smile_progress = min(1.0, (total_time - remaining_time) / total_time) if countdown_started else 0
#             mouth_y = emoji_y + emoji_size * 3 // 4
#             time_draw.arc((emoji_x + emoji_size // 4, mouth_y - int(smile_progress * 10),
#                            emoji_x + emoji_size * 3 // 4, mouth_y + int(smile_progress * 10)),
#                           0, 180, fill=255, width=3)

#             epd.display_1Gray(epd.getbuffer(time_image))
#             prev_time = current_time

#         time.sleep(0.1)

# except IOError as e:
#     logging.info(e)
# except KeyboardInterrupt:
#     logging.info("ctrl + c:")
#     motor_running = False
#     if motor_thread:
#         motor_thread.join()
#     epd.Clear(0x00, 0)
#     epd.sleep()
#     GPIO.cleanup()
#     exit()


import sys
import os

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
from waveshare_epd import epd3in7
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import threading

# ========== GPIO ==========
BUTTON_PIN = 22 

# Pins for first stepper motor
STEP_DIR_PIN_1 = 22
STEP_PIN_1 = 20

# Pins for second stepper motor
STEP_DIR_PIN_2 = None
STEP_PIN_2 = None

# Pins for DC/perystaltic motor
DC_DIR_PIN = None
DC_PIN = None

STEPS_PER_REV = 200
STEPS_FOR_80_DEG = (STEPS_PER_REV * 80) // 360

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(STEP_PIN_1, GPIO.OUT)
GPIO.setup(STEP_DIR_PIN_1, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ========== motor control ==========
motor_running = False
motor_thread = None

def rotate_motor():
    global motor_running
    while motor_running:
        GPIO.output(STEP_DIR_PIN_1, GPIO.HIGH)
        for _ in range(STEPS_FOR_80_DEG):
            if not motor_running:
                return
            GPIO.output(STEP_PIN_1, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(STEP_PIN_1, GPIO.LOW)
            time.sleep(0.005)
        time.sleep(1)
        GPIO.output(STEP_DIR_PIN_1, GPIO.LOW)
        for _ in range(STEPS_FOR_80_DEG):
            if not motor_running:
                return
            GPIO.output(STEP_PIN_1, GPIO.HIGH)
            time.sleep(0.005)
            GPIO.output(STEP_PIN_1, GPIO.LOW)
            time.sleep(0.005)
        time.sleep(1)

# ========== E-Paper ==========
logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd3in7 Clock and Emoji Display")
    epd = epd3in7.EPD()
    logging.info("Init and Clear")
    epd.init(1)
    epd.Clear(0x00, 1)
    
    picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
    font_path = os.path.join(picdir, 'Font.ttc')
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_large = ImageFont.truetype(font_path, 50)
    
    width, height = epd.height, epd.width
    time_image = Image.new('1', (width, height), 0)
    time_draw = ImageDraw.Draw(time_image)
    
    total_time = 1 * 60 
    paused_remaining = total_time  
    countdown_started = False
    start_time = 0
    initial_remaining = total_time

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                time.sleep(0.05)
            if countdown_started:
                elapsed = time.time() - start_time
                remaining = max(0, int(initial_remaining - elapsed))
                paused_remaining = remaining
                countdown_started = False
                logging.info("button click: countdown", paused_remaining)
                # 停止电机
                motor_running = False
                if motor_thread:
                    motor_thread.join()
            else:
                if paused_remaining > 0:
                    logging.info("button click: resume countdown，从 %d 秒开始", paused_remaining)
                    initial_remaining = paused_remaining
                    start_time = time.time()
                    countdown_started = True
                    motor_running = True
                    motor_thread = threading.Thread(target=rotate_motor)
                    motor_thread.start()
                else:
                    logging.info("countdown achieve 00:00")
        
        if countdown_started:
            elapsed = time.time() - start_time
            remaining_time = max(0, int(initial_remaining - elapsed))
            logging.debug("elapsed: %.2f, remaining_time: %d", elapsed, remaining_time)
            if remaining_time == 0:
                logging.info("countdown end")
                countdown_started = False
                paused_remaining = 0
                motor_running = False
                if motor_thread:
                    motor_thread.join()
        else:
            remaining_time = paused_remaining

        minutes = remaining_time // 60
        seconds = remaining_time % 60
        countdown_str = f"{minutes:02}:{seconds:02}"
        
        time_draw.rectangle((0, 0, width, height), fill=0)
        time_draw.text((10, 10), countdown_str, font=font_large, fill=255)
        epd.display_1Gray(epd.getbuffer(time_image))
        
        time.sleep(0.1)

except Exception as e:
    logging.error(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    motor_running = False
    if motor_thread:
        motor_thread.join()
    epd.Clear(0x00, 0)
    epd.sleep()
    GPIO.cleanup()
    exit()
