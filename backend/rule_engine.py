from typing import List
from datetime import datetime
from backend.models import Detection, Rule, Alert
from backend import geometry

from backend.models import Detection, Rule, Alert
from backend import geometry

class RuleEngine:
    def __init__(self):
        pass

    def evaluate(self, rules: List[Rule], detections: List[Detection]) -> List[Alert]:
        """
        Evaluates all enabled rules against the current frame's detections.
        Returns a list of generated Alerts.
        """
        alerts = []
        current_time = datetime.now().strftime("%H:%M:%S")

        for rule in rules:
            if not rule.enabled:
                continue

            # Ensure we compare in lowercase so "Person" and "person" match
            obj1_target = rule.object1.lower()
            obj2_target = rule.object2.lower() if rule.object2 else None
            condition = rule.condition.lower()

            # Separate detections by class name
            obj1_detections = [d for d in detections if d.class_name.lower() == obj1_target]
            
            # --- Condition: Exists ---
            if condition == "exists":
                if len(obj1_detections) > 0:
                    alert = Alert(
                        rule_id=rule.id,
                        message=f"{rule.object1} detected in camera feed.",
                        timestamp=current_time,
                        detections=obj1_detections
                    )
                    alerts.append(alert)
            
            # --- Condition: Not Exists ---
            elif condition == "not exists":
                if len(obj1_detections) == 0:
                    alert = Alert(
                        rule_id=rule.id,
                        message=f"Missing {rule.object1}! Not found in camera feed.",
                        timestamp=current_time,
                        detections=[]
                    )
                    alerts.append(alert)

            # --- Condition: Near or Far ---
            elif condition in ["near", "far"] and obj2_target:
                obj2_detections = [d for d in detections if d.class_name.lower() == obj2_target]
                
                triggered_detections = []
                
                # Compare every obj1 against every obj2
                for det1 in obj1_detections:
                    for det2 in obj2_detections:
                        # Prevent comparing the exact same object to itself
                        if det1.id == det2.id:
                            continue
                            
                        # Check Geometry
                        is_triggered = False
                        if condition == "near":
                            is_triggered = geometry.is_near(det1.bbox, det2.bbox, rule.distance)
                        elif condition == "far":
                            is_triggered = geometry.is_far(det1.bbox, det2.bbox, rule.distance)

                        # If the rule is broken, save the objects that broke it
                        if is_triggered:
                            if det1 not in triggered_detections: triggered_detections.append(det1)
                            if det2 not in triggered_detections: triggered_detections.append(det2)

                # If we found any objects breaking the distance rule, generate one alert
                if len(triggered_detections) > 0:
                    alert = Alert(
                        rule_id=rule.id,
                        message=f"{rule.object1} is {condition} {rule.object2} ({rule.distance}px).",
                        timestamp=current_time,
                        detections=triggered_detections
                    )
                    alerts.append(alert)

        return alerts