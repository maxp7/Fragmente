import cv2
import numpy as np
import subprocess
import os
import pygame
import pygetwindow as gw
import threading
import time

def open_image_with_cv2(image_path):
    img = cv2.imread(image_path)
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.resizeWindow('image', 3840, 2160)

    cv2.imshow('image', img)
    window = gw.getWindowsWithTitle('Image')[0]
    window.moveTo(1920, 0)
    cv2.waitKey(1)

pygame.mixer.init()
def play_audio(audio_path, fade_duration=1.5):
    global current_audio_path, changing_audio

    if current_audio_path:
        changing_audio = True
        fadeout_steps = 50 
        fadeout_step_duration = fade_duration / fadeout_steps
        for step in range(fadeout_steps):
            volume = 1.0 - (step / fadeout_steps)
            pygame.mixer.music.set_volume(volume)
            time.sleep(fadeout_step_duration)

    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(1.0)  
    pygame.mixer.music.play()

    current_audio_path = audio_path
    changing_audio = False

def show_contours(frame, contours, window_name='contours'):
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)
    cv2.imshow(window_name, frame)
    cv2.waitKey(1)

cap = cv2.VideoCapture(1)

image_folder = os.path.join("img")
audio_folder = os.path.join("sound")

reset_timer = time.time()
frame_count = 0
total_page_counter = 0
prev_total_page_counter = 0

large_page_detected = False
small_page_detected = False
first_page_detected = False

large_page_message_shown = False
small_page_message_shown = False
first_page_message_shown = False

volume = 1.0  
current_audio_path = None
changing_audio = False


while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 145, 255, cv2.THRESH_BINARY)

    contours_large, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    roi_width = int(frame.shape[1] * 0.51)
    roi_start = frame.shape[1] - roi_width
    roi = frame[:, roi_start:]
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)
    _, thresh_roi = cv2.threshold(blurred_roi, 100, 255, cv2.THRESH_BINARY)
    contours_small, _ = cv2.findContours(
        thresh_roi, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
   
    first_width = int(frame.shape[1] * 0.08)  
    first_height = int(frame.shape[0] * 0.60)  


    first_start_x = frame.shape[1] - first_width  
    first_start_y = 0  


    first_start_x_bottom = frame.shape[1] - first_width  
    first_start_y_bottom = frame.shape[0] - first_height  


    first_top = frame[first_start_y:first_start_y + first_height, first_start_x:first_start_x + first_width]


    gray_first = cv2.cvtColor(first_top, cv2.COLOR_BGR2GRAY)
    blurred_first = cv2.GaussianBlur(gray_first, (5, 5), 0)
    _, thresh_first = cv2.threshold(blurred_first, 80, 255, cv2.THRESH_BINARY)
    contours_first, _ = cv2.findContours(thresh_first, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours_large:
        c_large = max(contours_large, key=cv2.contourArea)
        area_large = cv2.contourArea(c_large)
        cv2.drawContours(frame, [c_large], -1, (0,255,0), 3) 
        show_contours(frame, [c_large])
        if area_large > 0.38 * frame.shape[0] * frame.shape[1]:
           
            if not large_page_detected:
                large_page_detected = True
                large_page_detected_time = time.time()
                large_page_message_shown = False

        else:
            large_page_detected = False

    if contours_small:
        c_small = max(contours_small, key=cv2.contourArea)
        area_small = cv2.contourArea(c_small)
        cv2.drawContours(roi, [c_small], -1, (0,255,0), 3)
        show_contours(roi, [c_small], window_name='roi_contours')
        print( area_large, 0.1 * frame.shape[0] * frame.shape[1])
        if area_large > 0.1 * frame.shape[0] * frame.shape[1] and area_large < 0.25 * frame.shape[0] * frame.shape[1]:
            
            if not small_page_detected:
                small_page_detected = True
                small_page_detected_time = time.time()
                small_page_message_shown = False
            

        else:
            small_page_detected = False
    
    if contours_first:
        c_first = max(contours_first, key=cv2.contourArea)
        area_large = cv2.contourArea(c_first)
        cv2.drawContours(first_top, [c_first], -1, (0,255,0), 3) 
        show_contours(first_top, [c_first], window_name='first_contours')
        if area_large > 0.01  * frame.shape[0] * frame.shape[1] and area_large < 0.1 * frame.shape[0] * frame.shape[1]:
            if not first_page_detected:
                first_page_detected = True
                first_page_detected_time = time.time()
                first_page_message_shown = False

        else:
            first_page_detected = False
    
    if first_page_detected:
        if time.time() - first_page_detected_time > 0.2 and not first_page_message_shown:
            print("First page")
            total_page_counter = 0
            image_path = os.path.join(image_folder, "666.png")
            open_image_with_cv2(image_path)
            if not changing_audio:
                audio_path = os.path.join(audio_folder, f"{666}.mp3")
                audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
                audio_thread.start()
            time.sleep(2)
            first_page_message_shown = True
            reset_timer = time.time()
        
    
    if large_page_detected and not first_page_detected:
        if time.time() - large_page_detected_time > 0.21 and not large_page_message_shown:
            print("Big page")
            total_page_counter += 1
            image_path = os.path.join(image_folder, f"{total_page_counter}.png")
            open_image_with_cv2(image_path)
            if not changing_audio:
                audio_path = os.path.join(audio_folder, f"{total_page_counter}.mp3")
                audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
                audio_thread.start()

            time.sleep(2)
            large_page_message_shown = True
            
            reset_timer = time.time()
            

    if small_page_detected and not first_page_detected:
        if time.time() - small_page_detected_time > 0.4 and not small_page_message_shown:
            print("Small page")
            total_page_counter += 1
            image_path = os.path.join(image_folder, f"{total_page_counter}s.png")
            open_image_with_cv2(image_path)
            if not changing_audio:
                audio_path = os.path.join(audio_folder, f"{total_page_counter}.mp3")
                audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
                audio_thread.start()
            time.sleep(2)
            small_page_message_shown = True
            
            reset_timer = time.time()
            

    if total_page_counter != prev_total_page_counter:
        print("Total pages:", total_page_counter)
        prev_total_page_counter = total_page_counter

    if total_page_counter >= 18:
        total_page_counter = 1
    
    if time.time() - reset_timer > 120:
        if large_page_detected:
            total_page_counter = 1
            image_path = os.path.join(image_folder, "1.png")
            open_image_with_cv2(image_path)
        if small_page_detected:
            total_page_counter = 1
            image_path = os.path.join(image_folder, "1s.png")
            open_image_with_cv2(image_path)
        if first_page_detected:
            total_page_counter = 1
            image_path = os.path.join(image_folder, "666.png")
            open_image_with_cv2(image_path)

    if cv2.waitKey(1) & 0xFF == 32 and not first_page_detected:
        if large_page_detected:
            total_page_counter = 1
            image_path = os.path.join(image_folder, "1.png")
            open_image_with_cv2(image_path)
            if not changing_audio:
                audio_path = os.path.join(audio_folder, f"{total_page_counter}.mp3")
                audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
                audio_thread.start()
        else:
            total_page_counter = 1
            image_path = os.path.join(image_folder, "1s.png")
            open_image_with_cv2(image_path)
            if not changing_audio:
                audio_path = os.path.join(audio_folder, f"{total_page_counter}.mp3")
                audio_thread = threading.Thread(target=play_audio, args=(audio_path,))
                audio_thread.start()
cap.release()
cv2.destroyAllWindows()
