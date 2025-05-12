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

st_autorefresh(interval=300000, key="auto-refresh")  # refresh every 5 minutes (1 second=1000 milliseconds)

image_url="Images/Map.png"
image_base64 = get_base64_image(image_url)

# Load and encode image to base64
with open("Images/spec_sheet.png", "rb") as f:
    image_base64_spec = base64.b64encode(f.read()).decode()
image_url1 = f"data:image/png;base64,{image_base64_spec}"
#image_url1="Images/spec_sheet.png"
#image_base64_spec = get_base64_image(image_url1)


bak_report=reports_data('BakingWhiteBoardReport')
bak_report['Quantity Ahead/ Behind']=bak_report['Quantity Ahead/ Behind'].astype(float)
bak_report['Minutes Ahead/ Behind']=bak_report['Minutes Ahead/ Behind'].astype(float)
bak_report['BSE1'] = bak_report['BSE'].apply(extract_bse)

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

enr_report=reports_data('EnrobingWhiteboardReport')
enr_report['Quantity Ahead/ Behind']=enr_report['Quantity Ahead/ Behind'].astype(float)
enr_report['Minutes Ahead/ Behind']=enr_report['Minutes Ahead/ Behind'].astype(float)
enr_report['BSE1'] = enr_report['BSE'].apply(extract_bse)
enr_report['Equipment']= "E"+ enr_report['Line'].astype(str)
enr_sum_mach=enr_report.groupby(['Date','Equipment'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
#enr_report1=pd.concat([enr_sum_mach,bak_sum_jan],axis=0)
enr_report1=enr_sum_mach
enr_report1["Colour"]= ["Green" if x >= 0 else "Red" for x in enr_sum_mach['Minutes Ahead/ Behind']]

dept_report=pd.concat([bak_report1,enr_report1],axis=0)
#Dashboard Links
dbs={'Equip': ['Cutter','Waterjet', 'Depositor','Janssen','E1','E2','E3','E4','E5'],
        'Db': ['https://app.smartsheet.com/b/publish?EQBCT=68d4a48e7f1145b2b01d2718523e0acd',
               'https://app.smartsheet.com/b/publish?EQBCT=5b843cc8d84c463db6cf4a46e303d65f',
               'https://app.smartsheet.com/b/publish?EQBCT=8a8434ebdf72462abc9d9dc7e53494f7',
               'https://app.smartsheet.com/b/publish?EQBCT=452450ac6b0a4584b9b427848083253a',
               'https://app.smartsheet.com/b/publish?EQBCT=5f0b2f98993745629eb15614336b61ad',
               'https://app.smartsheet.com/b/publish?EQBCT=bc6438fd46d94ac588989a0e9837837a',
               'https://app.smartsheet.com/b/publish?EQBCT=0b9711dc34c84f839627f7440c967f9c',
               'https://app.smartsheet.com/b/publish?EQBCT=2d1535f74b874cc4a06d2905b99853c1',
               'https://app.smartsheet.com/b/publish?EQBCT=e878059ed284453c943b603196c8f05c'],
        'x':[600,800,655,755,480,420,380,320,260],
        'y':[1040,1040,1090,1090,890,840,890,840,890]}

db = pd.DataFrame(dbs)
report1=pd.merge(dept_report, db,left_on="Equipment", right_on="Equip", how="right")
#report1=report1[report1['Colour'].notna()]
report1["Status"]=["Ahead by " if x >= 0 else "Behind by " for x in report1['Minutes Ahead/ Behind']]
report1["Description"]=report1["Status"] + round(abs(report1["Minutes Ahead/ Behind"]),0).astype(str) +" minutes"

spec=sheets_data('SpecSheetLinks')

bak_bse=bak_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
bak_bse['Dept']='Baking'
bak_bse=pd.merge(bak_bse, spec,left_on=["BSE1",'Dept'], right_on=["BSE",'Dept'], how="left")

enr_bse=enr_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
enr_bse['Dept']='Enrobing'
enr_bse=pd.merge(enr_bse, spec,left_on=["BSE1",'Dept'], right_on=["BSE",'Dept'], how="left")
 
links=pd.concat([bak_bse,enr_bse],axis=0)   
links['img']=image_url1
# ----- HTML with embedded JS -----
overlay_html = f"""
<div style="width: 100%; overflow-x: auto;">
<div style="width: 1600px; margin: 0 auto; display: flex; align-items: flex-start;">

  <!-- Factory Map with Equipment Buttons -->
  <div style="position: relative; width: 1500px; height: 1600px; 
      background-image: url('{image_base64}'); background-repeat: no-repeat;
      background-size: contain; background-position: center; border: 2px solid #ccc;margin: 0 auto;">"""

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
  <div id="side-options" style="
    width: 400px;
    max-height: 1600px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 20px;
    border-left: 2px solid #ccc;
    box-sizing: border-box;
    background: #f9f9f9;
    margin-left: 20px;">
    <p style="color: #777;">Click on an equipment button to see options here.</p>
  </div>

</div>

<script>
   
    // Equipment descriptions from report1
    window.equipData = """ + json.dumps(
        report1[['Equip', 'Description','Colour']].dropna().to_dict(orient="records")
    ) + """;

    // BSE spec data for all equipment
    window.bseData = """ + json.dumps(links[['Equipment', 'BSE', 'img','Links']].dropna().to_dict(orient="records")) + """;

    // Function to show dashboard and spec buttons in side panel
    function showOptions(equip, link) {
        const panel = document.getElementById('side-options');
        panel.innerHTML = '<h4 style="margin-bottom: 10px; font-size: 30px;"> ' + equip + '</h4>';
        
        const dashBtn = document.createElement('button');
        dashBtn.innerText = '📊 Smartsheet Dashboards';
        dashBtn.style.fontSize = '25px';
        dashBtn.style.marginBottom = '12px';
        dashBtn.style.padding = '8px 14px';
        dashBtn.style.background = '#ACDDDE';
        dashBtn.style.color = 'Black';
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
                //Images/Spec.png
                btn.innerText = ' Parameter Sheets ' + row.BSE;
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.color = 'black';
                btn.style.fontSize = '20px';
                btn.style.fontWeight = "bold";
                btn.style.textDecoration = "underline"; // default (solid)
                //btn.style.textDecorationStyle = "dotted";     // dotted underline
                btn.style.textDecorationStyle = "dashed";     // dashed underline
                //btn.style.textDecorationStyle = "double";     // double underline
                //btn.style.textDecorationStyle = "wavy";       // wavy underline
                btn.style.textDecorationColor = "black";       // custom underline color
                btn.style.textDecorationThickness = "2px";    // custom thickness
                btn.style.textAlign = 'center';
                btn.style.border = 'none';
                btn.style.borderRadius = '10px';
                btn.style.cursor = 'pointer';
                btn.style.margin = '10px';
                btn.style.padding = '10px';
                
                // Adding background image
                btn.style.backgroundImage = "url('https://www.shutterstock.com/shutterstock/photos/2239154457/display_1500/stock-photo-digital-tablet-with-sample-spreadsheet-document-on-the-screen-2239154457.jpg')";
                btn.style.backgroundImage = `url('${row.img}')`;
                btn.style.opacity = "0.8";
                btn.style.backgroundRepeat = "no-repeat";
                btn.style.backgroundSize = 'cover'; 
                btn.style.backgroundPosition = 'center'; 
                // Adjusting button size to match the rectangular image's aspect ratio
                btn.style.width = '111px'; 
                btn.style.height = '160px';
                
                btn.onclick = () => window.open(row.Links, '_blank');
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
           descBox.innerText = '⌛Overall Status:' + descData.Description + '🕒';
           descBox.style.marginTop = '12px';
           descBox.style.padding = '10px 14px';
           descBox.style.background = descData.Colour;
           descBox.style.color = 'white';
           descBox.style.borderRadius = '8px';
           descBox.style.boxShadow = '1px 1px 3px rgba(0,0,0,0.1)';
           descBox.style.fontSize = '25px';
           // descBox.style.borderLeft = '4px solid #2857a7'; // accent strip
           panel.appendChild(descBox);
        }
        
        
    }
</script>
"""

# Render to Streamlit
html(overlay_html, height=1800)

