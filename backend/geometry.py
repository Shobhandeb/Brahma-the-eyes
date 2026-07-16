import math
from typing import List

def calculate_center(bbox: List[int]) -> tuple:
    """
    Calculates the exact center (x, y) pixel coordinate of a bounding box.
    bbox format: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return (center_x, center_y)

def calculate_distance(bbox1: List[int], bbox2: List[int]) -> float:
    """
    Calculates the straight-line (Euclidean) distance between the centers of two bounding boxes.
    """
    center1 = calculate_center(bbox1)
    center2 = calculate_center(bbox2)
    
    # Pythagorean theorem: a^2 + b^2 = c^2
    # Distance = sqrt( (x2 - x1)^2 + (y2 - y1)^2 )
    distance = math.sqrt((center2[0] - center1[0])**2 + (center2[1] - center1[1])**2)
    return distance

def is_near(bbox1: List[int], bbox2: List[int], threshold: int) -> bool:
    """
    Returns True if the distance between two objects is LESS than or equal to the threshold.
    """
    distance = calculate_distance(bbox1, bbox2)
    return distance <= threshold

def is_far(bbox1: List[int], bbox2: List[int], threshold: int) -> bool:
    """
    Returns True if the distance between two objects is GREATER than the threshold.
    """
    distance = calculate_distance(bbox1, bbox2)
    return distance > threshold