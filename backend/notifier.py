import cv2
import platform
import os
import time
from typing import List
from backend.models import Alert

class Notifier:
    def __init__(self):
        # Cooldown timer to prevent the beep from triggering 30 times a second!
        self.last_beep_time = 0
        self.cooldown_seconds = 2.0  # Wait 2 seconds between beeps

    def process_alerts(self, alerts: List[Alert]):
        """
        Takes a list of triggered alerts and triggers the appropriate notifications.
        """
        for alert in alerts:
            # 1. Console Alert
            print(f"[ALERT | {alert.timestamp} | Rule #{alert.rule_id}] {alert.message}")
            
            # 2. Play Audible Alarm
            self._play_alarm()

    def _play_alarm(self):
        """
        Plays an actual sound based on your Operating System.
        Includes a cooldown so it doesn't break your speakers!
        """
        current_time = time.time()
        
        # If 2 seconds haven't passed since the last beep, skip this beep
        if current_time - self.last_beep_time < self.cooldown_seconds:
            return  

        print("   -> [SOUND] Playing audible alarm!")
        self.last_beep_time = current_time

        # Detect the Operating System and play the native beep sound
        os_name = platform.system()

        if os_name == "Windows":
            import winsound
            winsound.Beep(1000, 500) # Frequency 1000Hz, Duration 500ms
            
        elif os_name == "Linux":
            # Most Ubuntu/Linux laptops have this default sound file.
            # >/dev/null 2>&1 hides the terminal output of the audio player
            os.system("aplay /usr/share/sounds/alsa/Front_Center.wav >/dev/null 2>&1")
            
        elif os_name == "Darwin": # Mac
            os.system("afplay /System/Library/Sounds/Glass.aiff")

    def highlight_objects(self, frame, alerts: List[Alert]):
        """
        Modifies the OpenCV frame by drawing bright red boxes around objects 
        that triggered an alert.
        """
        if frame is None:
            return frame

        for alert in alerts:
            for det in alert.detections:
                x1, y1, x2, y2 = map(int, det.bbox)
                
                # Draw a thick RED bounding box (0, 0, 255 in BGR)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                
                label = f"ALERT: {det.class_name.upper()}"
                (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                
                cv2.rectangle(frame, (x1, y1 - 25), (x1 + text_width, y1), (0, 0, 255), -1)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame