import cv2
import numpy as np
import subprocess
import os
import sys
import time
import requests

class EmotionsVisualization:
    def __init__(self):
        self.emotion_colors = {
            'surprise': (184, 183, 83),
            'angry': (35, 50, 220),
            'disgust': (79, 164, 36),
            'sad': (186, 119, 4),
            'happy': (27, 151, 239),
            'fear': (128, 37, 146),
            'fatigue_low': (0, 255, 0),
            'fatigue_high': (0, 0, 255)
        }
        self.showText = True
        self.button_color = (50, 150, 255)
        self.button_hover_color = (30, 130, 235)
        self.button_pressed_color = (0, 100, 200)
        self.button_position = (50, 50, 200, 100)
        self.button_text = "Restart"
        self.button_clicked = False
        self.state = {"fatigue_score": 65, "reset": False}
        self.send_messages = 0

    def fatiga(self, original_image, fatigue_score, text):
        fatigue_color = self.emotion_colors['fatigue_low'] if fatigue_score < 60 else self.emotion_colors['fatigue_high']
        
        cv2.putText(original_image, text, (50, 700), cv2.FONT_HERSHEY_SIMPLEX, 2.5,
                    fatigue_color, 5, cv2.LINE_AA)

        cv2.putText(original_image, "FATIGUE", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                    fatigue_color, 2, cv2.LINE_AA)

        bar_length = int(fatigue_score * 4)
        bar_start_x = 180
        bar_end_x = bar_start_x + bar_length
        bar_height = 50

        cv2.rectangle(original_image, (bar_start_x, 20), (bar_end_x, 20 + bar_height),
                      fatigue_color, -1)
        cv2.rectangle(original_image, (bar_start_x, 20), (550, 20 + bar_height), (255, 255, 255), 2)

    def draw_button(self, image, hover=False, pressed=False):
        color = self.button_color
        if pressed:
            color = self.button_pressed_color
        elif hover:
            color = self.button_hover_color
        
        x1, y1, x2, y2 = self.button_position
        cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
        cv2.putText(image, self.button_text, (x1 + 30, y1 + 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    def click_event(self, event, x, y, flags, param):
        x1, y1, x2, y2 = self.button_position
        if x1 < x < x2 and y1 < y < y2:
            if event == cv2.EVENT_LBUTTONDOWN:
                self.button_clicked = True
            elif event == cv2.EVENT_LBUTTONUP and self.button_clicked:
                print("Button Clicked! Resetting fatigue and restarting script...")
                self.button_clicked = False
                param['fatigue_score'] = 0  
                self.state["reset"] = True 
                self.showText = True
                #os.system("python .\examples\video_stream.py")
                url = 'http://localhost:1880/detect_face'
                payload = {'estado': False}
                print(f"Intentando enviar: {payload} a {url}")
                try:
                   response = requests.post(url, json=payload, timeout=1)
                   print(f"Respuesta de Node-RED: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                   print(f"Error al enviar la señal: {e}")
                

                subprocess.Popen(["python", "./examples/video_stream.py"])
                sys.exit("salir")

    def main(self, emotions: dict, original_image: np.ndarray):
        if 'fatigue' in emotions:
            fatigue_score = emotions['fatigue']
            
            if self.state["reset"]:
                fatigue_score = 0
                emotions['fatigue'] = 0
                self.state["reset"] = False  

            fatigue_percentage = int(fatigue_score)
            text = f"{fatigue_percentage}%"

            if self.showText:
                self.fatiga(original_image, fatigue_score, text)
            else:
                if self.send_messages < 1:
                    url = 'http://localhost:1880/detect_face'
                    payload = {'estado': True}
                    print(f"Intentando enviar: {payload} a {url}")
                    try:
                        self.send_messages += 1
                        response = requests.post(url, json=payload, timeout=1)
                        print(f"Respuesta de Node-RED: {response.status_code} - {response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error al enviar la señal: {e}")

                cv2.setMouseCallback('Emotion Recognition', self.click_event, self.state)
                emotions['fatigue'] = self.state["fatigue_score"]

                text_size = cv2.getTextSize("WARNING!", cv2.FONT_HERSHEY_SIMPLEX, 3, 7)[0]
                text_x = (original_image.shape[1] - text_size[0]) // 2
                text_y = (original_image.shape[0] + text_size[1]) // 2
                cv2.putText(original_image, "WARNING!", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 3,
                            (0, 0, 255), 7, cv2.LINE_AA)

                x, y = cv2.getWindowImageRect('Emotion Recognition')[:2]
                hover = (self.button_position[0] < x < self.button_position[2]) and (self.button_position[1] < y < self.button_position[3])

                self.draw_button(original_image, hover=hover, pressed=self.button_clicked)

            if fatigue_score > 60:
                self.showText = False

        return original_image
