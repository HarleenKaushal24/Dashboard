# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 10:39:45 2025

@author: Harleen
"""

import streamlit as st
import requests
import uuid
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Read service account info from Streamlit secrets
service_account_info = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(service_account_info), [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
])
client = gspread.authorize(creds)
sheet = client.open("RecepReply").sheet1

st.set_page_config(page_title="Reception Assistant", layout="centered")

st.title("👋 Welcome to Bosco and Roxys's")
st.write("Please enter your details to notify the person you're here to meet.")

# Guest details
guest_name = st.text_input("Your Name")
guest_reason = st.text_input("Reason for Visit")

# Employee list — you can later load this from a file or API
employee_list = ["Emp1", "Emp2", "Emp3", "Emp4"]

employee_emails = {
    "Emp1": "harleen@boscoandroxys.com",
    "Emp2": "teddy@boscoandroxys.com",
    "Emp3": "harleen@boscoandroxys.com",
    "Emp4": "teddy@boscoandroxys.com"
}
#selected_employee="Emp1"
selected_employee = st.selectbox("Who would you like to meet?", employee_list)

if st.button("Notify"):
    if guest_name and selected_employee:
        visit_id = str(uuid.uuid4())  # Unique ID for the visit
        payload = {
            "guest_name": guest_name,
            "guest_reason": guest_reason,
            "employee": selected_employee,
            "e_email":employee_emails[selected_employee],
            "visit_id": visit_id 
        }
        response = requests.post("https://boscoandroxys.app.n8n.cloud/webhook/webhook/reception", json=payload)

        if response.status_code == 200:
            st.success("Notification sent. Waiting for response...")
            
            # Poll every 5 seconds for up to 2 (120/5 = 24) minute 
            for i in range(24):  
               time.sleep(5)
               data = sheet.get_all_records()
               df = pd.DataFrame(data)

               result = df[df["visit_id"] == visit_id]
               if not result.empty:
                   st.success("Employee Response:")
                   st.write(result.iloc[0]["response"])
                   break
               # else:
               #      st.info("Still waiting...")
            else:
                st.warning("No response yet. Please wait or contact the front desk.")
        else:
            st.error("Failed to notify. Try again.")
    else:
        st.warning("Please enter your name and choose someone to meet.")
