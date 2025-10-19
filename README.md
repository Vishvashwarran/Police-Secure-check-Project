SecureCheck: A Python-SQL Digital Ledger for Police Post Logs
Project Overview

SecureCheck is a centralized digital ledger system designed for police check posts to log, track, and analyze vehicle movements.
It uses Python, SQL, and Streamlit to provide real-time analytics and monitoring of traffic stops, ensuring faster, data-driven law enforcement decisions.

Skills Takeaway

Python
SQL
Streamlit


Problem Statement

Police check posts often depend on manual logging systems that are inefficient and prone to data loss.
This project aims to build a centralized SQL-based database integrated with a Python-powered dashboard for real-time insights, reports, and alerts on vehicle stops and violations.

Business Use Cases

Real-time logging of vehicles and personnel
Automated identification of suspect vehicles
Check post performance and efficiency tracking
Crime pattern analysis using Python & SQL
Centralized multi-location database

Approach
Step 1: Python for Data Processing

Removed columns containing only missing values
Handled NaN and null entries in key columns (e.g., filled search_type nulls with "None")

Step 2: Database Design (SQL)

Created table traffic_stops in MySQL
Inserted cleaned dataset into SQL database

Step 3: Streamlit Dashboard

Visualized vehicle logs, violations, and outcomes
Integrated SQL queries for quick lookups
Displayed real-time insights such as stop counts, arrest rates, and violation trends

Example Data Entry

A 27-year-old male driver was stopped for speeding at 2:30 PM.
No search was conducted, and he received a citation.
The stop lasted 6–15 minutes and was not drug-related.

Results

Faster check post operations
Automated alerts for flagged vehicles
Real-time reporting of violations
Data-backed decision-making
Evaluation Metrics
Query Execution Time
Data Accuracy
System Uptime
User Engagement
Violation Detection Rate


Dataset Details

File Name: traffic_stops.csv

Column	Description
stop_date	Date of stop
stop_time	Time of stop
country_name	Country where stop occurred
driver_gender	Gender of driver
driver_age	Cleaned driver age
driver_race	Race/Ethnicity of driver
violation	Type of violation
search_conducted	Whether a search occurred (True/False)
search_type	Type of search (Frisk, Vehicle Search, None)
stop_outcome	Result (Warning, Citation, Arrest)
is_arrested	Whether driver was arrested
stop_duration	Duration of stop
drugs_related_stop	Whether stop was drug-related
vehicle_number	Unique vehicle identifier



Credits

Project Title: SecureCheck: A Python-SQL Digital Ledger for Police Post Logs
Created by: Vishvashwarran V B
