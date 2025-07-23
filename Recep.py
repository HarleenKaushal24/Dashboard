# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 10:39:45 2025

@author: Harleen
"""

import streamlit as st
import requests
import time

st.set_page_config(page_title="Reception Assistant", layout="centered")

st.title("👋 Welcome to Our Office")
st.write("Please enter your details to notify the person you're here to meet.")

# Guest details
guest_name = st.text_input("Your Name")
guest_reason = st.text_input("Reason for Visit")

# Employee list — you can later load this from a file or API
employee_list = ["Emp1", "Emp2", "Emp3", "Emp4"]
e_email=["harleen@boscoandroxys.com"]
#selected_employee="Emp1"
selected_employee = st.selectbox("Who would you like to meet?", employee_list)

if st.button("Notify"):
    if guest_name and selected_employee:
        payload = {
            "guest_name": guest_name,
            "guest_reason": guest_reason,
            "employee": selected_employee,
            "e_email":e_email     
        }
        response = requests.post("https://boscoandroxys.app.n8n.cloud/webhook/webhook/reception", json=payload)

        if response.status_code == 200:
            st.success("The person you want to meet has been notified!")
            st.write("Waiting for their response...")
        else:
            st.error("Something went wrong. Please try again.")
    else:
        st.warning("Please enter your name and choose someone to meet.")




response_placeholder = st.empty()

polling_url = "https://boscoandroxys.app.n8n.cloud/webhook/webhook/reception"
params = {"guest_name": guest_name}


payload = {
    "data": {
        "text": "coming"
    }
}


response = requests.get(url)

# 📥 Import the response (text in this case)
print("Status Code:", response.status_code)
print("Response Body:", response.text)


for _ in range(20):  # Poll for up to 1 minute (20 x 3 seconds)
    time.sleep(3)
    try:
        res = requests.get(polling_url, params=params)
        if res.status_code == 200 and res.json().get("response"):
            reply = res.json()["data"]
            response_placeholder.success(f"✉️ Reply from {selected_employee}: {reply}")
            break
    except:
        pass
    response_placeholder.info("Still waiting for response...")
else:
    response_placeholder.warning("⏳ No response received yet.")
