# import sys
# import os

# # ========== 路径设置 ==========
# libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
# if os.path.exists(libdir):
#     sys.path.append(libdir)
    
# import logging
# import time
# import threading
# import cv2
# import subprocess
# import requests
# from PIL import Image, ImageDraw, ImageFont
# import RPi.GPIO as GPIO
# from waveshare_epd import epd3in7

# # ========== GPIO 设置 ==========
# DIR_PIN = 22
# STEP_PIN = 27
# BUTTON_PIN = 21

# STEPS_PER_REV = 200
# STEPS_FOR_80_DEG = (STEPS_PER_REV * 80) // 360

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(STEP_PIN, GPIO.OUT)
# GPIO.setup(DIR_PIN, GPIO.OUT)
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# # ========== detection ==========
# def is_person_present():
#     image_path = "/tmp/pic.jpg"
#     try:
#         subprocess.run(["libcamera-jpeg", "-o", image_path, "-n", "--width", "320", "--height", "240"], check=True)
#     except subprocess.CalledProcessError:
#         print("❌ Failed to capture image via libcamera")
#         return False

#     try:
#         with open(image_path, "rb") as f:
#             res = requests.post("http://192.168.115.32:5080/detect", files={"file": f})
#             if res.text.strip() == "yes":
#                 print("✅ Person detected (via server)!")
#                 return True
#             else:
#                 print("❌ No person detected (via server)")
#                 return False
#     except Exception as e:
#         print("❌ Error connecting to server:", e)
#         return False

# # ========== motor ==========

# moved_steps = 0 

# def rotate_motor_linear():
#     global motor_running, moved_steps
#     step_interval = total_time / STEPS_FOR_80_DEG 
#     step_delay = step_interval 

#     GPIO.output(DIR_PIN, GPIO.HIGH)

#     while motor_running and moved_steps < STEPS_FOR_80_DEG:
#         if paused:
#             time.sleep(0.1)
#             continue
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(0.005)
#         moved_steps += 1
#         time.sleep(step_delay)
        
# def rotate_motor_reverse():
#     global moved_steps
#     GPIO.output(DIR_PIN, GPIO.LOW)
#     for _ in range(moved_steps):
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(0.005)
#     moved_steps = 0 

# # ========== Main ==========
# logging.basicConfig(level=logging.DEBUG)

# try:
#     logging.info("epd3in7 Countdown + Camera Detection")

#     epd = epd3in7.EPD()
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
#     paused = False
#     start_time = 0
#     total_time = 60
#     motor_thread = None
#     last_check_time = 0
#     check_interval = 2
#     elapsed_time = 0

#     while True:
#         if GPIO.input(BUTTON_PIN) == GPIO.LOW:
#             time.sleep(0.1)
#             if not countdown_started:
#                 logging.info("▶️ Start Button Pressed")
#                 while GPIO.input(BUTTON_PIN) == GPIO.LOW:
#                     time.sleep(0.05)

#                 countdown_started = True
#                 paused = True  
#                 start_time = time.time()
#                 motor_running = True
#                 moved_steps = 0
#                 motor_thread = threading.Thread(target=rotate_motor_linear)
#                 motor_thread.start()
#             else:
#                 logging.info("⏸️ Pause/Resume Button Pressed")
#                 paused = not paused
#                 if paused:
#                     logging.info("⏸️ Countdown Paused (by button)")
#                 else:
#                     logging.info("▶️ Countdown Resumed (by button)")
#                 while GPIO.input(BUTTON_PIN) == GPIO.LOW:
#                     time.sleep(0.05)

#         current_time = time.strftime('%H:%M:%S')

#         if countdown_started:
#             if time.time() - last_check_time >= check_interval:
#                 last_check_time = time.time()
#                 if not paused:
#                     if not is_person_present():
#                         logging.info("🚫 No one detected. Countdown paused.")
#                         paused = True
#                 else:
#                     if is_person_present():
#                         logging.info("👤 Person detected. Countdown resumed.")
#                         paused = False

#             if not paused:
#                 elapsed_time = time.time() - start_time
#                 remaining_time = max(0, int(total_time - elapsed_time))

#             if remaining_time == 0:
#                 logging.info("✅ Countdown Complete")
#                 countdown_started = False
#                 motor_running = False
#                 if motor_thread:
#                     motor_thread.join()
#                 logging.info("🔁 Reversing motor to original position")
#                 rotate_motor_reverse()
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

# except Exception as e:
#     logging.error(e)
# except KeyboardInterrupt:
#     logging.info("ctrl + c exit")
# finally:
#     motor_running = False
#     if motor_thread:
#         motor_thread.join()
#     epd.Clear(0x00, 0)
#     epd.sleep()
#     GPIO.cleanup()



# motor_running = False
# def rotate_motor():
#     global motor_running
#     while motor_running:
#         GPIO.output(DIR_PIN, GPIO.HIGH)
#         for _ in range(STEPS_FOR_80_DEG):
#             if not motor_running:
#                 return
#             GPIO.output(STEP_PIN, GPIO.HIGH)
#             time.sleep(0.005)
#             GPIO.output(STEP_PIN, GPIO.LOW)
#             time.sleep(0.005)
#         time.sleep(1)

#         GPIO.output(DIR_PIN, GPIO.LOW)
#         for _ in range(STEPS_FOR_80_DEG):
#             if not motor_running:
#                 return
#             GPIO.output(STEP_PIN, GPIO.HIGH)
#             time.sleep(0.005)
#             GPIO.output(STEP_PIN, GPIO.LOW)
#             time.sleep(0.005)
#         time.sleep(1)

import sys
import os

# ========== Path ==========
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
import time
import threading
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from waveshare_epd import epd3in7

# ========== Pin setting ==========
DIR_PIN = 22
STEP_PIN = 27
DIR_PIN_2 = 20
STEP_PIN_2 = 12


BUTTON_PIN = 21

STEPS_PER_REV = 200
STEPS_FOR_80_DEG = (STEPS_PER_REV * 80) // 360

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN_2, GPIO.OUT)
GPIO.setup(DIR_PIN_2, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ========== detection ==========
detection_result = False

def is_person_present():
    image_path = "/tmp/pic.jpg"
    try:
        subprocess.run([
            "libcamera-jpeg", "-o", image_path, "-n",
            "--width", "240", "--height", "180"
        ], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to capture image via libcamera")
        return False

    try:
        with open(image_path, "rb") as f:
            res = requests.post("http://192.168.115.32:5080/detect", files={"file": f})
            return res.text.strip() == "yes"
    except Exception as e:
        print("❌ Error connecting to server:", e)
        return False

def detection_loop():
    global detection_result, detection_running
    while detection_running:
        detection_result = is_person_present()
        time.sleep(1.5)

# ========== motor ==========
moved_steps = 0

# def rotate_motor_linear():
#     global motor_running, moved_steps
#     step_interval = total_time / STEPS_FOR_80_DEG
#     GPIO.output(DIR_PIN, GPIO.HIGH)
#     while motor_running and moved_steps < STEPS_FOR_80_DEG:
#         if paused:
#             time.sleep(0.1)
#             continue
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(0.005)
#         moved_steps += 1
#         time.sleep(step_interval)

# def rotate_motor_reverse():
#     global moved_steps
#     GPIO.output(DIR_PIN, GPIO.LOW)
#     for _ in range(moved_steps):
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         time.sleep(0.005)
#     moved_steps = 0

# def rotate_motor_linear():
#     global motor_running, moved_steps
#     step_interval = total_time / STEPS_FOR_80_DEG
#     GPIO.output(DIR_PIN, GPIO.HIGH)
#     GPIO.output(DIR_PIN_2, GPIO.HIGH)
#     while motor_running and moved_steps < STEPS_FOR_80_DEG:
#         if paused:
#             time.sleep(0.1)
#             continue
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         GPIO.output(STEP_PIN_2, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         GPIO.output(STEP_PIN_2, GPIO.LOW)
#         time.sleep(0.005)
#         moved_steps += 1
#         time.sleep(step_interval)

def rotate_motor_linear():
    global motor_running, moved_steps

    step_interval = total_time / STEPS_FOR_80_DEG

    GPIO.output(DIR_PIN, GPIO.HIGH)
    GPIO.output(DIR_PIN_2, GPIO.HIGH)

    pwm2 = GPIO.PWM(STEP_PIN_2, 1000) 
    pwm2.start(50)

    while motor_running and moved_steps < STEPS_FOR_80_DEG:
        if paused:
            pwm2.ChangeDutyCycle(0) 
            time.sleep(0.1)
            continue
        pwm2.ChangeDutyCycle(50) 
        
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.005)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.005)

        moved_steps += 1
        time.sleep(step_interval)

    pwm2.stop()


def rotate_motor_linear():
    global motor_running, moved_steps
    step_interval = total_time / STEPS_FOR_80_DEG
    GPIO.output(DIR_PIN, GPIO.HIGH)
    GPIO.output(DIR_PIN_2, GPIO.HIGH)

    while motor_running and moved_steps < STEPS_FOR_80_DEG:
        if paused:
            time.sleep(0.1)
            continue
        
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.005)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.005)

        for _ in range(2): 
            GPIO.output(STEP_PIN_2, GPIO.HIGH)
            time.sleep(0.003)
            GPIO.output(STEP_PIN_2, GPIO.LOW)
            time.sleep(0.003)

        moved_steps += 1
        time.sleep(step_interval)
        
# def rotate_motor_reverse():
#     global moved_steps
#     GPIO.output(DIR_PIN, GPIO.LOW)
#     GPIO.output(DIR_PIN_2, GPIO.LOW)
#     for _ in range(moved_steps):
#         GPIO.output(STEP_PIN, GPIO.HIGH)
#         GPIO.output(STEP_PIN_2, GPIO.HIGH)
#         time.sleep(0.005)
#         GPIO.output(STEP_PIN, GPIO.LOW)
#         GPIO.output(STEP_PIN_2, GPIO.LOW)
#         time.sleep(0.005)
#     moved_steps = 0

# ========== main ==========
logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd3in7 Countdown + Camera Detection")

    epd = epd3in7.EPD()
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

    emoji_size = 150
    emoji_x = (width - emoji_size) // 2
    emoji_y = (height - emoji_size) // 2

    prev_countdown = ""
    countdown_started = False
    paused = False
    start_time = 0
    accumulated_time = 0
    total_time = 60
    motor_thread = None
    detection_running = False
    detection_thread = None
    last_full_clear_time = time.time()

    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            time.sleep(0.1)
            if not countdown_started:
                logging.info("▶️ Start Button Pressed")
                while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    time.sleep(0.05)

                countdown_started = True
                paused = True
                start_time = time.time()
                accumulated_time = 0
                motor_running = True
                moved_steps = 0

                motor_thread = threading.Thread(target=rotate_motor_linear)
                motor_thread.start()

                if detection_thread is None or not detection_thread.is_alive():
                    detection_running = True
                    detection_thread = threading.Thread(target=detection_loop, daemon=True)
                    detection_thread.start()

            else:
                logging.info("⏸️ Pause/Resume Button Pressed")
                paused = not paused
                logging.info("⏸️ Paused" if paused else "▶️ Resumed")
                while GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    time.sleep(0.05)

        if countdown_started:
            if not paused and not detection_result:
                logging.info("🚫 No one detected. Countdown paused.")
                paused = True
                accumulated_time += time.time() - start_time  # ✅ accumulate time so far

            elif paused and detection_result:
                logging.info("👤 Person detected. Countdown resumed.")
                paused = False
                start_time = time.time()  # ✅ reset timer for resumed session

            if not paused:
                elapsed_time = accumulated_time + (time.time() - start_time)
                remaining_time = max(0, int(total_time - elapsed_time))

                if remaining_time == 0:
                    logging.info("✅ Countdown Complete")
                    countdown_started = False
                    motor_running = False
                    if motor_thread:
                        motor_thread.join()
                    logging.info("🔁 Reversing motor to original position")
                    rotate_motor_reverse()
            else:
                elapsed_time = accumulated_time
                remaining_time = max(0, int(total_time - elapsed_time))
        else:
            remaining_time = total_time

        minutes = remaining_time // 60
        seconds = remaining_time % 60
        countdown = f"{minutes:02}:{seconds:02}"
        time_draw.rectangle((0, 0, width, height), fill=0)
        time_draw.text((10, 10), time.strftime('%H:%M:%S'), font=font_large, fill=255)

        if countdown != prev_countdown:
            time_draw.text((10, 70), countdown, font=font_large, fill=255)

            time_draw.arc((emoji_x, emoji_y, emoji_x + emoji_size, emoji_y + emoji_size), 0, 360, fill=255, width=4)
            eye_size = 5
            time_draw.ellipse((emoji_x + emoji_size // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size,
                               emoji_x + emoji_size // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)
            time_draw.ellipse((emoji_x + emoji_size * 2 // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size,
                               emoji_x + emoji_size * 2 // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)

            smile_progress = min(1.0, (total_time - remaining_time) / total_time) if countdown_started else 0
            mouth_y = emoji_y + emoji_size * 3 // 4
            time_draw.arc((emoji_x + emoji_size // 4, mouth_y - int(smile_progress * 10),
                           emoji_x + emoji_size * 3 // 4, mouth_y + int(smile_progress * 10)),
                          0, 180, fill=255, width=3)
            prev_countdown = countdown
            epd.display_1Gray(epd.getbuffer(time_image))
        epd.display_1Gray(epd.getbuffer(time_image))
        if time.time() - last_full_clear_time > 120:
            logging.info("🧹 Performing full screen clear to reduce ghosting...")
            epd.Clear(0x00, 1)
            last_full_clear_time = time.time()

        time.sleep(0.1)

except Exception as e:
    logging.error(e)
except KeyboardInterrupt:
    logging.info("ctrl + c exit")
finally:
    motor_running = False
    if motor_thread:
        motor_thread.join()
    detection_running = False
    if detection_thread:
        detection_thread.join()
    epd.Clear(0x00, 0)
    epd.sleep()
    GPIO.cleanup()
