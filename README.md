# Real-Time Football Prediction System

This project is a web-based real-time football match prediction application developed as a Big Data Analytics final project. The system integrates data streaming, machine learning, backend APIs, and a web frontend to predict football match outcomes both before a match starts (prematch) and during live matches when available.

The application demonstrates the use of distributed systems, streaming pipelines, and machine learning models in a practical, end-to-end analytics product.


## Features

- **Prematch Match Prediction**
  - Generates outcome probabilities for upcoming fixtures before kickoff
  - Uses historical match data, team performance, and contextual features

- **Live Match Data Processing**
  - Supports real-time ingestion of live match data when matches are available
  - Event-driven architecture using Kafka

- **Machine Learning Integration**
  - Predicts probabilities for home win, draw, and away win
  - Modular model design allows easy replacement or retraining

- **Backend REST API**
  - Flask-based API serving leagues, seasons, fixtures, and predictions
  - Handles database access and data serialization

- **Interactive Frontend**
  - React-based user interface for browsing leagues and viewing predictions

- **Dockerized Deployment**
  - Entire system can be deployed using Docker Compose for consistency and portability



## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** React, JavaScript
- **Database:** PostgreSQL
- **Streaming Platform:** Apache Kafka
- **Machine Learning:** scikit-learn
- **Deployment:** Docker, Docker Compose

