import sys
import os

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)


import logging
import time
from waveshare_epd import epd3in7
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd3in7 Clock and Emoji Display")

    # Initialise and clear the screen
    epd = epd3in7.EPD()
    logging.info("Init and Clear")
    epd.init(1)  # 1 Gray      ^o  ^l ^a  ^e^m ^e   ^o ^h  ^v 
    epd.Clear(0x00, 1)  #  ^e   ^q ^c^l ^y 

    # Store image directory
    picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
    # Store path to font ttc file
    font_path = os.path.join(picdir, 'Font.ttc')
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_large = ImageFont.truetype(font_path, 50)

    # Create new black and white image '1' means 1-bit pixel
    width, height = epd.height, epd.width
    time_image = Image.new('1', (width, height), 0)  #   ^q ^i  ^c^l ^y 
    time_draw = ImageDraw.Draw(time_image)

    # Store initialisation time
    prev_time = ""
    start_time = time.time()
    total_time = 1 * 60  # 25 minutes in seconds

    #     ^c^e  ^x ^h  ^z^d     ^k  ^m    ^r^l     ^o
    # Defines emoji size/location in centre of screen
    emoji_size = 150
    emoji_x = (width - emoji_size) // 2
    emoji_y = (height - emoji_size) // 2

    # Continuously updating
    while True:
        # Get remaining time in seconds and minutes
        current_time = time.strftime('%H:%M:%S')  #  ^x      ^r ^u 
        remaining_time = max(0, int(total_time - (time.time() - start_time)))
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        countdown = f"{minutes:02}:{seconds:02}"

        if current_time != prev_time:
            # If not complete, draw remaining time

            # Make box
            #     ^t  ^e   ^q    ^e^e ^l  ^=^=     ^}    ^|^i  ^k ^u^y
            time_draw.rectangle((0, 0, width, height), fill=0)  #     ^e^e  ^q ^i      ^l ^e   ^f ^{^v

            # Draw current time
            #   ^x ^h  ^w  ^r^= ^|      ^j ^v 
            time_draw.text((10, 10), current_time, font=font_large, fill=255)

            # Draw remaining time
            #   ^x ^h  ^`^r    ^w  ^|  ^w  ^r^=  ^u  ^k
            time_draw.text((10, 70), countdown, font=font_large, fill=255)

            # Draw face
            #     ^c^e    ^c      ^s ^{   ^z
            time_draw.arc((emoji_x, emoji_y, emoji_x + emoji_size, emoji_y + emoji_size), 0, 360, fill=255, width=4)

            # Add eyes
            #  ^j   ^w ^|  ^}^{
            eye_size = 5
            time_draw.ellipse((emoji_x + emoji_size // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size, emoji_x + emoji_size // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)
            time_draw.ellipse((emoji_x + emoji_size * 2 // 3 - eye_size, emoji_y + emoji_size // 3 - eye_size, emoji_x + emoji_size * 2 // 3 + eye_size, emoji_y + emoji_size // 3 + eye_size), fill=255)

            # Draw smile
            #  ^x      ^n  ^k ^h     ^h   ^j ^`^p  ^p ^o^x ^l^v  ^l    ^j   ^w  ^` ^b 
            smile_progress = min(1.0, (total_time - remaining_time) / total_time)  #   ^n  ^m  ^q ^h      ^q ^z^d  ^{   
            mouth_y = emoji_y + emoji_size * 3 // 4
            time_draw.arc((emoji_x + emoji_size // 4, mouth_y - int(smile_progress * 10), emoji_x + emoji_size * 3 // 4, mouth_y + int(smile_progress * 10)), 0, 180, fill=255, width=3)

            # Update screen and time
            #  ^x     ^{  ^v  ^z^d ^f^e   
            epd.display_1Gray(epd.getbuffer(time_image))

            prev_time = current_time  #  ^{  ^v   ^j    ^w  ^w 

        time.sleep(1)

except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd.Clear(0x00, 0)  #   ^e ^y      ^q ^i  ^c^l ^y 
    epd.sleep()
    exit()