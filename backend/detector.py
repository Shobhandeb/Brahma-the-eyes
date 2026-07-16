from ultralytics import YOLO
from typing import List
from backend.models import Detection

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):
        """
        Initializes the YOLO model when the system starts.
        We load it once here to prevent reloading it every single frame.
        """
        print(f"Loading YOLO model from {model_path}...")
        self.model = YOLO(model_path)

    def process_frame(self, frame) -> List[Detection]:
        """
        Takes an OpenCV video frame, runs YOLO tracking, and parses the 
        results into a clean list of Detection objects.
        """
        detections = []

        # Run YOLO with ByteTrack to get persistent IDs
        # stream=True optimizes memory for continuous video feeds
        results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False, stream=True)

        for result in results:
            boxes = result.boxes
            
            # If the AI sees nothing, boxes.id will be None. We must check for this!
            if boxes.id is not None:
                # zip() lets us loop through the coordinates, IDs, confidences, and class numbers simultaneously
                for box, track_id, conf, cls in zip(boxes.xyxy, boxes.id, boxes.conf, boxes.cls):
                    
                    # Convert raw tensor math into standard Python numbers
                    x1, y1, x2, y2 = map(int, box)
                    class_name = self.model.names[int(cls)]
                    confidence = float(conf)
                    
                    # Package the raw data into our strict Pydantic model
                    # We use a dictionary because "class" is a reserved word in Python, 
                    # matching our Pydantic Field(alias="class")
                    detection_data = {
                        "id": int(track_id),
                        "class": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2]
                    }
                    
                    # Create the Detection object and add it to our list
                    det_obj = Detection(**detection_data)
                    detections.append(det_obj)

        return detections