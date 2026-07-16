# Brahma – AI Rule-Based Intelligent Video Monitoring System

> **Project Name:** Brahma  
> **Meaning:** Inspired by the Hindu deity Brahma, the creator with multiple eyes, symbolizing an AI system that continuously observes, understands, and reasons about its environment through multiple intelligent "eyes".

---

# Table of Contents

1. Project Overview
2. Motivation
3. Features
4. Current Project Status
5. System Architecture
6. Project Workflow
7. Folder Structure
8. Backend Architecture
9. Frontend Architecture
10. AI Rule Engine
11. LLM Rule Parser
12. Detection Pipeline
13. Rule Evaluation Engine
14. Alert System
15. API Endpoints
16. Current Supported Rules
17. Example Workflow
18. Technologies Used
19. Future Scope

---

# 1. Project Overview

Brahma is an AI-powered real-time video monitoring platform that combines:

- Object Detection
- Natural Language Processing
- Rule-Based Reasoning
- Real-Time Alerts
- Modern Dashboard UI

Instead of forcing users to manually write JSON rules, Brahma allows users to simply describe monitoring requirements in plain English.

Example:

> Alert me if a person stays near a bottle for more than 10 seconds.

The system automatically converts this sentence into structured JSON rules that the backend can execute in real time.

---

# 2. Motivation

Traditional CCTV systems only record videos.

Traditional AI object detection systems only detect objects.

Brahma goes one step further.

It understands **relationships**, **events**, and **behaviors** occurring inside the scene.

Instead of asking:

> What objects exist?

Brahma answers:

> What is happening?

---

# 3. Features

## Natural Language Rule Creation

Users can type:

```
Alert if person is near bottle.
```

instead of

```json
{
    "object1":"person",
    "object2":"bottle",
    "condition":"near",
    "distance":300
}
```

---

## Real-Time Object Detection

Current detector:

- YOLOv8

Detects

- Person
- Bottle
- Chair
- Car
- etc.

---

## Rule Engine

Every frame is analyzed.

Rules are checked continuously.

If a rule is satisfied,

→ Alert is generated.

---

## Dashboard

Current dashboard contains

- Live Camera Feed
- Rule Management
- Notification Panel
- Modern UI
- Future About Page
- Multiple Dashboard Pages

---

# 4. Current Project Status

Completed

✔ FastAPI Backend

✔ Rule CRUD APIs

✔ JSON Rule Storage

✔ YOLO Detection

✔ Rule Manager

✔ Rule Evaluator

✔ LLM Rule Parsing

✔ Dashboard UI

✔ Real-Time Detection Pipeline

✔ Notification Framework

Currently Under Development

- Duration rules
- Appearance tracking
- Zone monitoring
- Alert history
- Authentication
- Database migration

---

# 5. High Level Architecture

```
                    User
                      │
                      ▼
             Natural Language Prompt
                      │
                      ▼
              Sentence Transformer
            (LLM Rule Understanding)
                      │
                      ▼
             Structured Rule JSON
                      │
          FastAPI Rule Management API
                      │
          rules.json Database Storage
                      │
                      ▼
             Rule Evaluation Engine
                      ▲
                      │
            YOLO Object Detection
                      ▲
                      │
               Webcam / CCTV Feed
                      │
                      ▼
              Detection Results
                      │
                      ▼
            Rule Matching Engine
                      │
          Rule Satisfied?
                │
      ┌─────────┴─────────┐
      │                   │
     NO                  YES
      │                   │
      ▼                   ▼
 Continue         Generate Alert
                      │
                      ▼
             Dashboard Notification
```

---

# 6. Complete Workflow

Step 1

User opens dashboard.

↓

Step 2

User writes

```
Notify me if a person comes near a bottle.
```

↓

Step 3

LLM understands the sentence.

↓

Step 4

LLM converts it into

```json
{
    "object1":"person",
    "object2":"bottle",
    "condition":"near",
    "distance":300,
    "action":"alert"
}
```

↓

Step 5

FastAPI stores the rule.

↓

Step 6

YOLO detects objects every frame.

↓

Step 7

Detection results are passed into Rule Engine.

↓

Step 8

Rule Engine checks every rule.

↓

Step 9

If matched

↓

Alert appears instantly.

---

# 7. Current Folder Structure

```
Brahma/

│
├── backend/
│   │
│   ├── app.py
│   ├── detector.py
│   ├── evaluator.py
│   ├── rule_manager.py
│   ├── llm_parser.py
│   ├── rules.json
│   ├── models.py
│   └── utils.py
│
├── frontend/
│   │
│   ├── src/
│   │
│   ├── components/
│   ├── pages/
│   ├── dashboard/
│   ├── alerts/
│   └── rules/
│
├── yolov8n.pt
│
├── README.md
│
└── requirements.txt
```

---

# 8. Backend Architecture

```
                  FastAPI

                     │

        ┌────────────┼────────────┐

        │            │            │

        ▼            ▼            ▼

 Rule Manager    Rule Engine   LLM Parser

        │            │

        ▼            ▼

   rules.json    Detection Results

                     ▲

                     │

                YOLO Detector
```

---

## Rule Manager

Responsibilities

- Create rules
- Delete rules
- Update rules
- Enable/Disable rules
- Store rules in JSON

---

## Detector

Responsibilities

- Read webcam
- Run YOLO
- Detect objects
- Return object list

Example output

```python
[
    {
        "label":"person",
        "x":120,
        "y":180
    },
    {
        "label":"bottle",
        "x":200,
        "y":190
    }
]
```

---

## Evaluator

The evaluator receives

```
Rules

+

Detected Objects
```

and decides

```
True

or

False
```

---

# 9. Frontend Architecture

```
React Dashboard

        │

        ▼

FastAPI REST API

        │

        ▼

Rules

Alerts

Live Detection

Statistics
```

Current Pages

Dashboard

Rules

Alerts

About (planned)

Analytics (planned)

---

# 10. LLM Rule Parser

Instead of asking users to fill forms

```
Object:

Condition:

Distance:
```

Users simply type English.

Example

```
Alert me if a person is near a bottle.
```

Parser extracts

```
Object 1

↓

person

Object 2

↓

bottle

Condition

↓

near

Distance

↓

300
```

---

## Supported Conditions

Current supported conditions

```
exists

not exists

near

far

count

appears

disappears

inside zone

outside zone

duration
```

Each condition has its own parser logic and default values (for example, `near` defaults to 300 pixels if no distance is provided).

---

# 11. Rule Evaluation Logic

Every frame

```
Read detections

↓

Loop over every rule

↓

Evaluate condition

↓

Generate Alert

↓

Repeat
```

No frame is skipped.

---

# 12. Detection Pipeline

```
Camera

↓

OpenCV

↓

YOLO

↓

Bounding Boxes

↓

Detected Objects

↓

Rule Evaluator

↓

Alerts
```

---

# 13. Alert System

Current alerts contain

- Rule ID
- Timestamp
- Message

Example

```
[11:24:10]

Person detected near Bottle.

Rule #4 Triggered.
```

Future

- Alert History
- Alert Severity
- Screenshots
- Email
- SMS
- WhatsApp

---

# 14. API Endpoints

## Get Rules

```
GET /rules
```

Returns

```json
[
    ...
]
```

---

## Create Rule

```
POST /rules
```

---

## Update Rule

```
PUT /rules/{id}
```

---

## Delete Rule

```
DELETE /rules/{id}
```

---

# 15. Example Rule Flow

Input

```
Notify me if person comes near bottle.
```

↓

LLM

↓

```json
{
    "object1":"person",
    "object2":"bottle",
    "condition":"near",
    "distance":300
}
```

↓

Store Rule

↓

YOLO detects

```
Person

Bottle
```

↓

Distance

```
250 pixels
```

↓

Rule

```
Near < 300

TRUE
```

↓

Alert Generated

---

# 16. Technologies Used

## Backend

- Python
- FastAPI
- OpenCV
- YOLOv8
- Uvicorn

---

## AI

- SentenceTransformer (`all-MiniLM-L6-v2`) for natural-language rule understanding
- Rule-based semantic parsing
- Object Detection (YOLO)

---

## Frontend

- React
- TypeScript
- Tailwind CSS
- Modern Dashboard Components

---

## Storage

Current

```
rules.json
```

Future

```
SQLite

↓

PostgreSQL

↓

Cloud Database
```

---

# 17. Current Limitations

- Rules are stored in a JSON file (not yet database-backed).
- Alerts are currently session-based and not persisted.
- Zone-based rules are defined but need full UI support.
- Duration tracking requires persistent object identity across frames.
- No user authentication or multi-user support yet.
- Rule parser is optimized for supported rule patterns and can be expanded with additional NLP capabilities.

---

# 18. Future Scope

## AI Improvements

- Multi-object relationship reasoning
- Action recognition (running, falling, fighting)
- Gesture recognition
- Pose estimation
- Face recognition integration
- Scene understanding
- Anomaly detection

## Rule Engine Enhancements

- Temporal event reasoning
- Rule chaining
- Boolean operators (AND, OR, NOT)
- Nested conditions
- Rule priorities

## Dashboard

- Live analytics
- Alert timeline
- Detection heatmaps
- Camera management
- Multi-camera monitoring
- User roles and permissions

## Notifications

- Email alerts
- SMS alerts
- WhatsApp integration
- Push notifications
- WebSocket-based real-time updates

## Deployment

- Docker
- Kubernetes
- GPU acceleration
- Cloud deployment
- Distributed edge inference

---

# 19. Vision

Brahma aims to evolve from a simple object detection application into an **AI-powered visual reasoning platform**. Rather than merely identifying objects in a scene, it will understand spatial relationships, temporal events, and user-defined behaviors expressed in natural language.

By combining computer vision, semantic rule parsing, and real-time reasoning, Brahma aspires to become an intelligent surveillance assistant capable of monitoring complex scenarios with minimal user configuration.
