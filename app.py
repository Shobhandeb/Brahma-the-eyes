import cv2
import threading
import uvicorn
import time
import asyncio

# Import our custom modules
import backend.api as api_module
from backend.api import app as fastapi_app
from backend.detector import YOLODetector
from backend.rule_engine import RuleEngine
from backend.notifier import Notifier
from backend.websocket_manager import ws_manager

def run_api_server():
    """Runs the FastAPI server in a background thread."""
    print("Starting FastAPI server on http://127.0.0.1:8000 ...")
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="error")

def main():
    print("--- Starting AI Rule-Based Monitoring System (Enterprise Edition) ---")
    
    # 1. Launch the API server in a background thread
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start()

    # 2. Initialize core modules
    detector = YOLODetector("yolov8n.pt")
    engine = RuleEngine()
    notifier = Notifier()
    
    # Use the shared RuleManager instance from the API module
    rule_manager = api_module.rule_manager

    # 3. Open the Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        return

    print("Webcam is live. Press 'q' on the video window to exit.")
    
    # Setup an event loop specifically for this thread to handle WebSocket broadcasts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Load latest rules from the database manager
        current_rules = rule_manager.get_rules()
        
        # Process frame with YOLO
        detections = detector.process_frame(frame)

        # Draw standard green boxes for diagnostics
        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{det.class_name}", (x1, y1 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Evaluate current rules against live detections
        alerts = engine.evaluate(current_rules, detections)
        
        # Clear and update legacy polling array
        api_module.latest_alerts.clear()
        api_module.latest_alerts.extend(alerts)

        # Process standard console notifications and audio alarms
        notifier.process_alerts(alerts)
        
        # Broadcast each alert immediately across open WebSockets
        for alert in alerts:
            # Broadcast as a clean JSON-serializable dictionary
            alert_dict = alert.model_dump()
            try:
                loop.run_until_complete(ws_manager.broadcast_alert(alert_dict))
            except Exception as e:
                print(f"[Broadcast Error] Could not send alert: {e}")

        # Paint red highlight boxes for rule violations
        frame = notifier.highlight_objects(frame, alerts)

        # Render video feed to screen
        cv2.imshow("AI Monitoring Dashboard", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Shutting down system...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()