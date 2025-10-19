import streamlit as st
import pandas as pd
import numpy as np
import random as rand
import matplotlib.pyplot as plt
import pymysql
import plotly.express as px
import altair as alt
import math
import statistics

#sql database connection
def create_dbconnection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="2007",
            database="policelogs",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection
    except Exception as e:
        st.error(f'Database Connection failed:{e}')
        return None
    
#fetch data from db
def fetch_data(query):
    connection= create_dbconnection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result=cursor.fetchall()
                df=pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()
#UI

st.set_page_config(page_title="Police Dashboard",layout="wide")
st.title("🚨SecureCheck: Police Post Digital Ledger")

#overview of Data

st.header("Police Log overview👀")
query="SELECT * FROM traffic_stops"
data=fetch_data(query)
st.dataframe(data,use_container_width=True)


df=pd.read_csv("traffic_stops.csv")

if df.empty:
    st.warning("No data found in the database.")
else:
    # check column exists
    country_options = [''] + list(df['country_name'].unique())
    country = st.selectbox("Select Country", country_options)

# Only filter if a real country is selected
if country:
    filtered_df = df[df['country_name'] == country]
    st.subheader("Vehicle Stop Records in "+country)
    st.dataframe(filtered_df)
    total_stops = len(filtered_df)
    st.write(f"**Total Stops in {country}:** {total_stops}")
else:
    st.write("Please select a country to see records.")


#Handling missing data using pandas

df = pd.read_csv("traffic_stops.csv", low_memory=False)
df = df.dropna(axis=1, how='all')
df.drop(['driver_age_raw', 'violation_raw'], axis=1, inplace=True)
df['search_type'].fillna('None', inplace=True)
df['stop_date'] = pd.to_datetime(df['stop_date'], format='%Y-%m-%d', errors='coerce')
df['is_arrested'] = df['is_arrested'].astype(str).str.strip().replace({'True': True, 'False': False, '1': True, '0': False}).fillna(False).astype(bool)
df.info()
total_stops=len(df)


#Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops=df.shape[0]
    st.metric("Totoal Stops",total_stops)

with col2:
    arrests=df[df['stop_outcome'].str.contains("arrest", case=False,na=False)].shape[0]
    st.metric("Total Arrests",arrests)

with col3:
    warnings=df[df['stop_outcome'].str.contains("warning",case=False,na=False)].shape[0]
    st.metric("Total Warnings",warnings)

with col4:
    drugs_related_stop=df[df['drugs_related_stop']==1].shape[0]
    st.metric("Drug Related Stops",drugs_related_stop)

#chart Visuals
st.subheader("Visual Insights")

tab1, tab2=st.tabs(["Stops by Violation","Driver Gender Distribution"])

with tab1:
    if not df.empty and 'violation' in df.columns:
        violation_data=df['violation'].value_counts().reset_index()
        violation_data.columns=['violation','Count']
        fig=px.bar(violation_data,x='violation',y='Count', title="Stops by Violation types", color='violation')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data for Violation Chart")

with tab2:
    if not df.empty and 'driver_gender' in df.columns:
        gender_data=df['driver_gender'].value_counts().reset_index()
        gender_data.columns=['Gender','Count']
        fig=px.pie(gender_data,names="Gender",values='Count',title="Driver gender")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.warning("No Data for Driver Gender")


#Medium Queries

st.header("Queries")

select_query=st.selectbox("Select a Query",[
    " Top 10 vehicle_Number involved in drug-related stops",
    " Most frequently searched Vehicles",
    " Highest arrest rate by Driver age group",
    " Gender of drivers stopped in each country",
    " Highest search rate by race and gender combination",
    " The most traffic stops in time of day",
    " Average stop duration for violations",
    " Stops during the night likely to arrests?",
    " Violations most associated with searches or arrests",
    " Violations among younger drivers",
    " Rare violations in search or arrest",
    " Highest rate of drug-related stops by a country",
    " Arrest rate by country and violation",
    " Country With most stops with search conducted"
])

query_map={
    " Top 10 vehicle_Number involved in drug-related stops": "SELECT vehicle_Number, COUNT(*) AS stop_count FROM traffic_stops WHERE drugs_related_stop = True GROUP BY vehicle_Number ORDER BY stop_count DESC LIMIT 10", #1

    " Most frequently searched Vehicles": "SELECT COUNT(DISTINCT vehicle_Number) AS unique_vehicles, COUNT(*) AS total_rows FROM traffic_stops", #2

    " Highest arrest rate by Driver age group": """SELECT CASE 
        WHEN driver_age < 20 THEN 'Under 20'
        WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
        WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
        WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
        WHEN driver_age BETWEEN 50 AND 59 THEN '50-59'
        WHEN driver_age BETWEEN 60 AND 69 THEN '60-69'
        ELSE '70 and above'
    END AS age_group,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY age_group
ORDER BY arrest_rate_percent DESC;""",  #3

    " Gender of drivers stopped in each country":"""SELECT COUNTRY_NAME, DRIVER_GENDER,COUNT(*)AS DRIVER_COUNT FROM TRAFFIC_STOPS
GROUP BY COUNTRY_NAME,DRIVER_GENDER
ORDER BY COUNTRY_NAME ASC;""",  #4

    " Highest search rate by race and gender combination": """SELECT DRIVER_RACE,DRIVER_GENDER,COUNT(*) AS TOTAL_STOPS,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
    ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS search_rate_percent
FROM traffic_stops
GROUP BY driver_race, driver_gender
ORDER BY search_rate_percent DESC
LIMIT 1;""",  #5

    " The most traffic stops in time of day":"""SELECT 
    HOUR(stop_time) AS hour_of_day,
    COUNT(*) AS total_stops
FROM traffic_stops
GROUP BY hour_of_day
ORDER BY total_stops DESC
LIMIT 1;""",  #6

    " Average stop duration for violations":"""SELECT 
    violation,
    ROUND(AVG(
        CASE 
            WHEN stop_duration = '0-15 Min' THEN 7.5
            WHEN stop_duration = '16-30 Min' THEN 23
            WHEN stop_duration = '30+ Min' THEN 35
            ELSE NULL
        END
    ), 2) AS avg_stop_duration
FROM traffic_stops
GROUP BY violation
ORDER BY avg_stop_duration DESC;
""",  #7

    " Stops during the night likely to arrests?":"""SELECT
    CASE
        WHEN HOUR(stop_time) BETWEEN 0 AND 17 THEN 'Morning (0-17)'
        WHEN HOUR(stop_time) BETWEEN 18 AND 24 THEN 'Night (18-24)'
    END AS time_period,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY time_period
ORDER BY arrest_rate_percent DESC;""", #8

    " Violations most associated with searches or arrests":"""SELECT VIOLATION,COUNT(*)AS STOP_COUNT FROM TRAFFIC_STOPS
WHERE search_type = 'VEHICLE SEARCH' OR stop_outcome = 'ARREST'
GROUP BY VIOLATION
ORDER BY STOP_COUNT DESC;""",  #9

    " Violations among younger drivers":"""SELECT VIOLATION,COUNT(*) AS NUM_STOPS FROM TRAFFIC_STOPS
WHERE driver_age < 25
GROUP BY VIOLATION
ORDER BY NUM_STOPS DESC;""",  #10

    " Rare violations in search or arrest":"""SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_type = 'VEHICLE SEARCH' OR is_arrested = TRUE THEN 1 ELSE 0 END) AS stops_with_search_or_arrest,
    ROUND(
        SUM(CASE WHEN search_type = 'VEHICLE SEARCH' OR is_arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2
    ) AS percent_searched_or_arrested
FROM traffic_stops
GROUP BY violation
ORDER BY percent_searched_or_arrested DESC
LIMIT 10;""",  #11

    " Highest rate of drug-related stops by a country":"""SELECT country_name,COUNT(*)AS TOTAL_STOPS,
		SUM(CASE WHEN drugs_related_stop=TRUE THEN 1 ELSE 0 END)AS drug_related_stops,
        ROUND(SUM(CASE WHEN drugs_related_stop=TRUE THEN 1 ELSE 0 END)/COUNT(*) *100,2)AS RATE_OF_PERCENT
FROM traffic_stops
GROUP BY COUNTRY_NAME
ORDER BY RATE_OF_PERCENT DESC;""", #12

    " Arrest rate by country and violation":"""SELECT country_name,violation,COUNT(*)AS STOP_COUNT,
	SUM(CASE WHEN IS_ARRESTED = TRUE THEN 1 ELSE 0 END)AS NO_OF_ARRESTS,
	ROUND(SUM(CASE WHEN IS_ARRESTED = TRUE THEN 1 ELSE 0 END)/COUNT(*)*100,2) AS PERCENT_ARREST_RATE
FROM traffic_stops
GROUP BY country_name,violation
ORDER BY PERCENT_ARREST_RATE DESC;""",  #13

    " Country With most stops with search conducted":"""SELECT country_name,COUNT(*) AS STOP_COUNT,
	SUM(CASE WHEN search_conducted = TRUE THEN  1 ELSE 0 END) AS COUNT_OF_SEARCH_CONDUCTED,
    ROUND(SUM(CASE WHEN search_conducted = TRUE THEN  1 ELSE 0 END)/COUNT(*)*100,2) AS PERCENT_OF_SC
FROM TRAFFIC_STOPS
GROUP BY country_name
ORDER BY COUNT_OF_SEARCH_CONDUCTED DESC
LIMIT 1;"""   #14
}



if st.button("Run Query"):
    result=fetch_data(query_map[select_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query.")


st.header("Complex Queries")

select_query=st.selectbox("Select A Query",[
    "Yearly Breakdown of Stops and Arrests by Country ",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"
])


query_map={
    "Yearly Breakdown of Stops and Arrests by Country ":"""SELECT
    country_name,
    YEAR(stop_date) AS stop_year,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)/COUNT(*)*100, 2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY country_name, YEAR(stop_date)
ORDER BY country_name, YEAR(stop_date);""",  #1

    "Driver Violation Trends Based on Age and Race":"""SELECT 
    driver_race,
    CASE
        WHEN driver_age < 20 THEN 'Below 20'
        WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
        WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
        WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
        ELSE '50 and above'
    END AS age_group,
    COUNT(violation) AS total_violations
FROM traffic_stops
GROUP BY driver_race, age_group
ORDER BY total_violations DESC;""",  #2

    "Time Period Analysis of Stops":"""SELECT YEAR(stop_date)AS STOP_YEAR,MONTHNAME(stop_date) AS STOP_MONTH,HOUR(stop_time) AS STOP_HOUR,COUNT(*)AS TOTAL_COUNT FROM TRAFFIC_STOPS
GROUP BY STOP_MONTH,STOP_HOUR,STOP_YEAR
ORDER BY STOP_YEAR;""",  #3

    "Violations with High Search and Arrest Rates":"""SELECT *,
    RANK() OVER (ORDER BY search_rate DESC) AS search_rank,
    RANK() OVER (ORDER BY arrest_rate DESC) AS arrest_rank
FROM (
    SELECT
        violation,
        SUM(CASE WHEN search_type IN ('VEHICLE SEARCH', 'FRISK') THEN 1 ELSE 0 END) AS total_searched,
        SUM(is_arrested) AS total_arrested,
        COUNT(*) AS total_stops,
        ROUND(SUM(CASE WHEN search_type IN ('VEHICLE SEARCH', 'FRISK') THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS search_rate,
        ROUND(SUM(is_arrested)*100.0/COUNT(*),2) AS arrest_rate
    FROM traffic_stops
    GROUP BY violation
) AS violation_rates
ORDER BY search_rate DESC, arrest_rate DESC;""",   #4

    "Driver Demographics by Country":"""SELECT COUNTRY_NAME,DRIVER_GENDER,driver_race,CASE
        WHEN driver_age < 20 THEN 'Below 20'
        WHEN driver_age BETWEEN 20 AND 29 THEN '20-29'
        WHEN driver_age BETWEEN 30 AND 39 THEN '30-39'
        WHEN driver_age BETWEEN 40 AND 49 THEN '40-49'
        ELSE '50 and above'
    END AS age_group,COUNT(*) AS TOTAL_COUNT FROM TRAFFIC_STOPS
GROUP BY age_group,COUNTRY_NAME,DRIVER_GENDER,driver_race
ORDER BY TOTAL_COUNT DESC;
""",  #5


    "Top 5 Violations with Highest Arrest Rates" :"""SELECT VIOLATION,COUNT(*)AS TOTAL_COUNT,
SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS TOTAL_ARREST,
ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)/COUNT(*)*100,2)AS ARREST_PERCENT FROM TRAFFIC_STOPS
GROUP BY VIOLATION
ORDER BY ARREST_PERCENT DESC
LIMIT 5;""" #6

}



if st.button("Run Query",key="complex"):
    result=fetch_data(query_map[select_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query.")

st.subheader("Violation Summary")
st.bar_chart(df['violation'].value_counts())


st.markdown("Build with ❤️ for Police Securecheck")

st.subheader("Custom Filter")
st.write("Fill the details below to get the prediction of Stop outcome based existing data")


st.subheader("🔎 Add New Police Log & Predict Outcome & Violation")


with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ['Male', 'Female'])
    driver_age = st.number_input("Driver Age", min_value=18, max_value=80, step=1)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ['0', '1'])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ['0', '1'])
    stop_duration = st.selectbox("Stop Duration", df["stop_duration"].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome and Violation")

    if submitted:
        # -----------------------------
        # 1. Map form inputs to CSV values
        # -----------------------------
        driver_gender_input = 'M' if driver_gender.lower().startswith('m') else 'F'
        search_conducted_input = 1 if search_conducted == '1' else 0
        drugs_related_stop_input = 1 if drugs_related_stop == '1' else 0
        driver_age_input = int(driver_age)

        # -----------------------------
        # 2. Ensure DataFrame types match
        # -----------------------------
        df['driver_gender'] = df['driver_gender'].str.strip().str.upper()
        df['driver_age'] = df['driver_age'].astype(int)
        df['search_conducted'] = df['search_conducted'].astype(int)
        df['drugs_related_stop'] = df['drugs_related_stop'].astype(int)

        # -----------------------------
        # 3. Filter DataFrame for exact match
        # -----------------------------
        filtered_df = df[
            (df['driver_gender'] == driver_gender_input) &
            (df['driver_age'] == driver_age_input) &
            (df['search_conducted'] == search_conducted_input) &
            (df['drugs_related_stop'] == drugs_related_stop_input)
        ]

        # -----------------------------
        # 4. Determine predictions
        # -----------------------------
        if not filtered_df.empty:
            predicted_outcome = filtered_df['stop_outcome'].mode()[0]
            predicted_violation = filtered_df['violation'].mode()[0]
        else:
            # If no exact match exists, fallback: pick the mode from similar rows
            similar_df = df[df['driver_gender'] == driver_gender_input]
            if not similar_df.empty:
                predicted_outcome = similar_df['stop_outcome'].mode()[0]
                predicted_violation = similar_df['violation'].mode()[0]
            else:
                # absolute fallback if nothing matches
                predicted_outcome = "warning"
                predicted_violation = "speeding"

        # -----------------------------
        # 5. Display results
        # -----------------------------
        search_text = "A Search Was Conducted" if search_conducted_input else "No Search was Conducted"
        drug_text = "was drug related" if drugs_related_stop_input else "was not drug-related"

        st.markdown(f"""
        🎯 **Prediction Summary**
                    
        - **Predicted Violation:** {predicted_violation}
        - **Predicted Stop Outcome:** {predicted_outcome}

        📑 A {driver_age_input}-year-old {driver_gender_input} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}
        {search_text}, and the stop {drug_text}.
        Stop Duration: **{stop_duration}**.
        Vehicle Number: **{vehicle_number}**.
        """)
        st.balloons()






    # if submitted:
    #     # Convert form inputs to match DataFrame types
    #     search_conducted_bool = True if search_conducted == '1' else False
    #     drugs_related_stop_bool = True if drugs_related_stop == '1' else False

    #     # Filter DataFrame
    #     filtered_df = df[
    #         (df['driver_gender'].str.lower() == driver_gender.lower().strip()) &
    #         (df['driver_age'] == driver_age) &
    #         (df['search_conducted'] == int(search_conducted_bool)) &
    #         (df['drugs_related_stop'] == int(drugs_related_stop_bool))

    #     ]

    #     # Determine predictions
    #     if not filtered_df.empty:
    #         predicted_outcome = filtered_df['stop_outcome'].mode()[0]
    #         predicted_violation = filtered_df['violation'].mode()[0]
    #     else:
    #         predicted_outcome = "warning"
    #         predicted_violation = "speeding"

    #     # Text for display
    #     search_text = "A Search Was Conducted" if int(search_conducted_bool) else "No Search was Conducted"
    #     drug_text = "was drug related" if int(drugs_related_stop_bool) else "was not drug-related"

    #     # Display results
    #     st.markdown(f"""
    #     🎯 **Prediction Summary**
                    
    #     - **Predicted Violation:** {predicted_violation}
    #     - **Predicted Stop Outcome:** {predicted_outcome}

    #     📑 A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}
    #     {search_text}, and the stop {drug_text}.
    #     Stop Duration: **{stop_duration}**.
    #     Vehicle Number: **{vehicle_number}**.
    #     """)
    #     st.balloons()

























