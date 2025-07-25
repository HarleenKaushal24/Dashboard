# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 10:39:45 2025

@author: Harleen
"""

import streamlit as st
import requests
import time
import uuid

st.set_page_config(page_title="Reception Assistant", layout="centered")

st.title("👋 Welcome to Our Office")
st.write("Please enter your details to notify the person you're here to meet.")

# Guest details
guest_name = st.text_input("Your Name")
guest_reason = st.text_input("Reason for Visit")

# Employee list — you can later load this from a file or API
employee_list = ["Emp1", "Emp2", "Emp3", "Emp4"]
e_email=["harleen@boscoandroxys.com"]
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
        response = requests.post("https://boscoandroxys.app.n8n.cloud/webhook-test/webhook/reception", json=payload)

        if response.status_code == 200:
            st.success("Notification sent. Waiting for response...")
            
    #         # Poll every 5 seconds for up to 1 minute (adjust as needed)
    #         for i in range(12):
    #             time.sleep(5)
    #             check = requests.get(f"https://your-api.com/check-response/{visit_id}")
                
    #             if check.status_code == 200 and check.json().get("response"):
    #                 st.success("Employee Response:")
    #                 st.write(check.json()["response"])
    #                 break
    #             else:
    #                 st.info("Still waiting...")
    #         else:
    #             st.warning("No response yet. Please wait or contact the front desk.")
    #     else:
    #         st.error("Failed to notify. Try again.")
    # else:
    #     st.warning("Please enter your name and choose someone to meet.")
