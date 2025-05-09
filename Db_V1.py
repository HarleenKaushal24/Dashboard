# -*- coding: utf-8 -*-
"""
Created on Mon May  5 15:08:14 2025

@author: Harleen
"""

#pip install smartsheet-python-sdk
import smartsheet
import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
import base64
from streamlit_autorefresh import st_autorefresh
import json

token = st.secrets["smartsheet"]["token"]

client = smartsheet.Smartsheet(token)
sheets_response = client.Sheets.list_sheets(include_all=True)
reports_response = client.Reports.list_reports(include_all=True)

# Prepare sheets and reports data
sheets_data = [{"Sheet Name": sheet.name, "Sheet ID": sheet.id} for sheet in sheets_response.data]
report_data = [{"Report Name": report.name, "Report ID": report.id} for report in reports_response.data]
# Create DataFrames for display
df_sheets = pd.DataFrame(sheets_data)
df_reports = pd.DataFrame(report_data)


# Load local image and convert to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"


def reports_data(report_name):
    report_id = df_reports[df_reports['Report Name']==report_name]['Report ID'].values[0]
    report = client.Reports.get_report(report_id)
    # Extract column names from the report
    columns = [col.title for col in report.columns]
    # Extract row data
    rows = []
    for row in report.rows:
        row_data = []
        for cell in row.cells:
            value = cell.display_value if cell.display_value is not None else (cell.value if cell.value else "")
            row_data.append(value)
        rows.append(row_data)
    df_report = pd.DataFrame(rows, columns=columns)
    return df_report
def sheets_data(sheet_name):
    sheet_id = df_sheets[df_sheets['Sheet Name']==sheet_name]['Sheet ID'].values[0]
    sheet = client.Sheets.get_sheet(sheet_id)
    # Extract column names from the report
    columns = [col.title for col in sheet.columns]
    # Extract row data
    rows = []
    for row in sheet.rows:
        row_data = []
        for cell in row.cells:
            value = cell.display_value if cell.display_value is not None else (cell.value if cell.value else "")
            row_data.append(value)
        rows.append(row_data)
    df_sheet = pd.DataFrame(rows, columns=columns)
    return df_sheet
# Function to clean BSE values
def extract_bse(val):
    if isinstance(val, str):
        parts = val.split(".")
        if len(parts) == 2:
            if parts[1].isdigit():
                return parts[0]  # Keep only integer part
            else:
                return val       # Keep full if non-numeric after dot
        else:
            return val
    return str(int(val)) if float(val).is_integer() else str(int(float(val)))

# Streamlit page setup
st.set_page_config(layout="wide")
st.title("Factory Map")

st_autorefresh(interval=60000, key="auto-refresh")  # refresh every 1 minutes (1 second=1000 milliseconds)

image_url="Images/Map.png"
image_base64 = get_base64_image(image_url)

bak_report=reports_data('BakingWhiteBoardReport')
bak_report['Quantity Ahead/ Behind']=bak_report['Quantity Ahead/ Behind'].astype(float)
bak_report['Minutes Ahead/ Behind']=bak_report['Minutes Ahead/ Behind'].astype(float)
bak_report['BSE1'] = bak_report['BSE'].apply(extract_bse)
# bak_sum=bak_report['Date'].drop_duplicates().to_frame()
# bak_sum['Quantity Ahead/ Behind']=sum(bak_report['Quantity Ahead/ Behind'])
# bak_sum['Minutes Ahead/ Behind']=sum(bak_report['Minutes Ahead/ Behind'])
#bak_sum['Equipment']="Overall(exc. janssen)"

bak_report_jan=reports_data('BakingWhiteBoardReport-Janssen')
bak_sum_jan=bak_report_jan['Date'].drop_duplicates().to_frame()
if bak_report_jan.shape[0]>0:
    bak_report_jan['Quantity Ahead/ Behind']=bak_report_jan['Quantity Ahead/ Behind'].astype(float)
    bak_report_jan['Minutes Ahead/ Behind']=bak_report_jan['Minutes Ahead/ Behind'].astype(float)
    
    bak_sum_jan['Quantity Ahead/ Behind']=sum(bak_report_jan['Quantity Ahead/ Behind'])
    bak_sum_jan['Minutes Ahead/ Behind']=sum(bak_report_jan['Minutes Ahead/ Behind'])
else: bak_sum_jan[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']]=0,0
bak_sum_jan['Equipment']="Janssen"


bak_sum_mach=bak_report.groupby(['Date','Equipment'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
bak_report1=pd.concat([bak_sum_mach,bak_sum_jan],axis=0)
bak_report1["Colour"]= ["Green" if x >= 0 else "Red" for x in bak_report1['Minutes Ahead/ Behind']]


#Dashboard Links
dbs={'Equip': ['Cutter','Waterjet', 'Depositor','Janssen'],
        'Db': ['https://app.smartsheet.com/b/publish?EQBCT=68d4a48e7f1145b2b01d2718523e0acd',
               'https://app.smartsheet.com/b/publish?EQBCT=5b843cc8d84c463db6cf4a46e303d65f',
               'https://app.smartsheet.com/b/publish?EQBCT=8a8434ebdf72462abc9d9dc7e53494f7',
               'https://app.smartsheet.com/b/publish?EQBCT=452450ac6b0a4584b9b427848083253a'],
        'x':[720,920,775,875],
        'y':[1050,1050,1100,1100]}

db = pd.DataFrame(dbs)
report1=pd.merge(bak_report1, db,left_on="Equipment", right_on="Equip", how="right")
#report1=report1[report1['Colour'].notna()]
report1["Status"]=["Ahead by " if x >= 0 else "Behind by " for x in report1['Minutes Ahead/ Behind']]
report1["Description"]=report1["Status"] + report1["Minutes Ahead/ Behind"].astype(str) +" minutes"

spec=sheets_data('SpecSheetLinks')
bak_his=sheets_data('WhiteBoard_HistoricalData(manual)')
bak_curr=sheets_data('WhiteBoard_HistoricalDataMonthly')
bak=pd.concat([bak_his,bak_curr],axis=0)
bak['BSE1'] = bak['BSE'].apply(extract_bse)

bak_bse=bak_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
bak_bse=pd.merge(bak_bse, spec,left_on="BSE1", right_on="BSE", how="left")


        
bse_spec_list = bak_bse[['Equipment', 'BSE', 'Baking Links']].dropna().rename(columns={'Baking Links': 'Link'}).to_dict(orient='records')

# ----- HTML with embedded JS -----
overlay_html = f"""
<div style="display: flex; gap: 40px;">

  <!-- Factory Map with Equipment Buttons -->
  <div style="position: relative; width: 1500px; height: 1600px; background-image: url('{image_base64}'); background-size: contain; background-position: center; border: 2px solid #ccc;">
"""

# Add equipment buttons
for _, row in report1.iterrows():
    overlay_html += f"""
    <div style="position: absolute; top: {row['y']}px; left: {row['x']}px;">
        <a href="javascript:void(0)" onclick="showOptions('{row['Equip']}', '{row['Db']}')"
            style="background: {row['Colour']}; padding: 6px 12px; border-radius: 26px;
                    text-decoration: none; font-weight: bold; color: white; box-shadow: 1px 1px 3px #999;">
            {row['Equip']}
        </a>
    </div>
    """

# Close map div and start side panel
overlay_html += """
  </div>

  <!-- Side Options Panel -->
  <div id="side-options" style="margin-top: 20px; padding: 20px; border-left: 2px solid #ccc; width: 400px; min-height: 200px;">
    <p style="color: #777;">Click on an equipment button to see options here.</p>
  </div>

</div>

<script>
    // Equipment descriptions from report1
    window.equipData = """ + json.dumps(
        report1[['Equip', 'Description','Colour']].dropna().to_dict(orient="records")
    ) + """;

    // BSE spec data for all equipment
    window.bseData = """ + json.dumps(bak_bse[['Equipment', 'BSE', 'Baking Links']].dropna().rename(columns={"Baking Links": "Link"}).to_dict(orient="records")) + """;

    // Function to show dashboard and spec buttons in side panel
    function showOptions(equip, link) {
        const panel = document.getElementById('side-options');
        panel.innerHTML = '<h4 style="margin-bottom: 10px; font-size: 30px;"> ' + equip + '</h4>';
        
        const dashBtn = document.createElement('button');
        dashBtn.innerText = 'Open Hourly Dashboard';
        dashBtn.style.fontSize = '30px';
        dashBtn.style.marginBottom = '12px';
        dashBtn.style.padding = '8px 14px';
        dashBtn.style.background = '#2857a7';
        dashBtn.style.color = 'white';
        dashBtn.style.border = 'none';
        dashBtn.style.borderRadius = '8px';
        dashBtn.style.cursor = 'pointer';
        dashBtn.onclick = () => window.open(link, '_blank');
        panel.appendChild(dashBtn);

        const filtered = window.bseData.filter(row => row.Equipment === equip);
        if (filtered.length > 0) {
            const label = document.createElement('div');
            // label.innerHTML = '<h5 style="margin-top: 20px;">Spec Sheets</h5>';
            panel.appendChild(label);
            filtered.forEach(row => {
                const btn = document.createElement('button');
                btn.innerText = 'Open Spec ' + row.BSE;
                btn.style.margin = '6px 6px 6px 0';
                btn.style.padding = '6px 12px';
                btn.style.borderRadius = '6px';
                btn.style.background = '#007bff';
                btn.style.color = 'white';
                btn.style.fontSize = '30px';
                btn.style.border = 'none';
                btn.style.cursor = 'pointer';
                btn.onclick = () => window.open(row.Link, '_blank');
                panel.appendChild(btn);
            });
        } else {
            const msg = document.createElement('p');
            msg.innerText = 'No specs found for this equipment.';
            panel.appendChild(msg);
        }
            
            
         // Show description
        const descData = window.equipData.find(row => row.Equip === equip);
        if (descData) {
           const descBox = document.createElement('div');
           descBox.innerText = 'Overall Status: ' + descData.Description;
           descBox.style.marginTop = '12px';
           descBox.style.padding = '10px 14px';
           descBox.style.background = descData.Colour;
           descBox.style.color = 'white';
           descBox.style.borderRadius = '8px';
           descBox.style.boxShadow = '1px 1px 3px rgba(0,0,0,0.1)';
           descBox.style.fontSize = '30px';
           descBox.style.borderLeft = '4px solid #2857a7'; // accent strip
           panel.appendChild(descBox);
        }
        
        
    }
</script>
"""

# Render to Streamlit
html(overlay_html, height=1800)


#HTML with absolute positioning
# overlay_html = f"""
# <div style="position: relative; width: 1280px; height: 1600px; background-image: url('{image_base64}'); background-size: contain; background-position: center;border: 2px solid #ccc;">
# """

# for _, row in report1.iterrows():
#     overlay_html += f"""
#     <div style="position: absolute; top: {row['y']}px; left: {row['x']}px;">
#         <a href="{row['Db']}" target="_blank"
#             style="background:  {row['Colour']}; padding: 6px 12px; border-radius: 26px;
#                     text-decoration: none; font-weight: bold; color: white; box-shadow: 1px 1px 3px #999;">
#             {row['Equip']}
#         </a>
#     </div>
#     """

# overlay_html += "</div>"



# # Render map with overlay
# html(overlay_html, height=1600)