from pydantic import BaseModel, Field
from typing import List, Optional

class Detection(BaseModel):
    """
    Represents a single object detected by YOLO.
    """
    id: int
    class_name: str = Field(alias="class")  # 'class' is a reserved keyword in Python, so we alias it
    confidence: float
    bbox: List[int] # [x1, y1, x2, y2]

class Rule(BaseModel):
    """
    Represents a user-defined rule for the monitoring system.
    """
    id: int
    enabled: bool = True
    object1: str
    object2: Optional[str] = None  # Optional because 'Exists' condition only needs object1
    condition: str                 # 'Near', 'Far', 'Exists', 'Not Exists'
    distance: Optional[int] = 0    # Distance threshold in pixels
    action: str                    # 'Alert', 'Alarm', 'Highlight'

class Alert(BaseModel):
    """
    Represents a triggered alert when a rule condition is met.
    """
    rule_id: int
    message: str
    timestamp: str
    detections: List[Detection]    # The specific objects that triggered this alert