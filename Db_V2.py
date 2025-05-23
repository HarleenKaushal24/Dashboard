# -*- coding: utf-8 -*-
"""
Created on Mon May  5 15:08:14 2025

@author: Harleen
"""

#pip install smartsheet-python-sdk
import smartsheet
import pandas as pd
import numpy as np
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


image_url5="Images/logo.png"
logo = get_base64_image(image_url5)
# Streamlit page setup
st.set_page_config(layout="wide")
#st.title("Factory Map")
col1, col2 = st.columns([1,20])
with col1:
    st.image(logo, width=100)  # Adjust path and size as needed
with col2:
    st.title("Factory Map")
    
st_autorefresh(interval=300000, key="auto-refresh")  # refresh every 5 minutes (1 second=1000 milliseconds)

image_url="Images/Map.png"
image_base64 = get_base64_image(image_url)

# Load and encode image to base64
# with open("Images/spec_sheet.png", "rb") as f:
#     image_base64_spec = base64.b64encode(f.read()).decode()
# image_url1 = f"data:image/png;base64,{image_base64_spec}"
image_url1="Images/spec_sheet.png"
image_base64_spec = get_base64_image(image_url1)
image_url2="Images/ss.png"
image_base64_ss = get_base64_image(image_url2)
image_url3="Images/spec_rbt.png"
image_base64_spec_r = get_base64_image(image_url3)
image_url4="Images/spec_pkg.png"
image_base64_spec_p = get_base64_image(image_url4)
image_url6="Images/diag.png"
image_base64_diag = get_base64_image(image_url6)
image_url7="Images/bse.png"
image_base64_bse = get_base64_image(image_url7)
image_url8="Images/cot.png"
image_base64_cot = get_base64_image(image_url8)

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


rb_report=reports_data('Robot Whiteboard Report')
rb_report['Quantity Ahead/ Behind']=rb_report['Quantity Ahead/ Behind'].astype(float)
rb_report['Minutes Ahead/ Behind']=rb_report['Minutes Ahead/ Behind'].astype(float)
rb_report['BSE1'] = rb_report['Item Code']
rb_report['Equipment']= "R"+ rb_report['Line'].astype(str)
rb_sum_mach=rb_report.groupby(['Date','Equipment'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
#enr_report1=pd.concat([enr_sum_mach,bak_sum_jan],axis=0)
rb_report1=rb_sum_mach
rb_report1["Colour"]= ["Green" if x >= 0 else "Red" for x in rb_sum_mach['Minutes Ahead/ Behind']]

pk_report=reports_data('PackingWhiteBoardReport')
pk_report['Quantity Ahead/ Behind']=pk_report['Quantity Ahead/ Behind'].astype(float)
pk_report['Minutes Ahead/ Behind']=pk_report['Minutes Ahead/ Behind'].astype(float)
pk_report['BSE1'] = pk_report['ItemName']
pk_report['Equipment']= "P"+ pk_report['Line'].astype(str)
pk_sum_mach=pk_report.groupby(['Date','Equipment'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
#enr_report1=pd.concat([enr_sum_mach,bak_sum_jan],axis=0)
pk_report1=pk_sum_mach
pk_report1["Colour"]= ["Green" if x >= 0 else "Red" for x in pk_report1['Minutes Ahead/ Behind']]



dept_report=pd.concat([bak_report1,enr_report1,rb_report1,pk_report1],axis=0)
#Dashboard Links
dbs={'Equip': ['Cutter','Waterjet', 'Depositor','Janssen', 'Frozen Yogurt','E1','E2','E5','E3','E4','R1','R2','R3','P1',
               'P2','P3','P4','P5'],
        'Db': ['https://app.smartsheet.com/b/publish?EQBCT=68d4a48e7f1145b2b01d2718523e0acd',#C
               'https://app.smartsheet.com/b/publish?EQBCT=5b843cc8d84c463db6cf4a46e303d65f',#W
               'https://app.smartsheet.com/b/publish?EQBCT=8a8434ebdf72462abc9d9dc7e53494f7',#D
               'https://app.smartsheet.com/b/publish?EQBCT=452450ac6b0a4584b9b427848083253a',#J
               'https://app.smartsheet.com/b/publish?EQBCT=8d9616a3f51a432cb033a0d4a02c9ffa',#FY
               'https://app.smartsheet.com/b/publish?EQBCT=5f0b2f98993745629eb15614336b61ad',#E1
               'https://app.smartsheet.com/b/publish?EQBCT=bc6438fd46d94ac588989a0e9837837a',#E2
               'https://app.smartsheet.com/b/publish?EQBCT=e878059ed284453c943b603196c8f05c',#E5
               'https://app.smartsheet.com/b/publish?EQBCT=0b9711dc34c84f839627f7440c967f9c',#E3
               'https://app.smartsheet.com/b/publish?EQBCT=2d1535f74b874cc4a06d2905b99853c1',#E4              
               'https://app.smartsheet.com/b/publish?EQBCT=bdd655650d9646a6a5608b224086e128',#R1
               'https://app.smartsheet.com/b/publish?EQBCT=9dce60cfe82f4ed4baed99325b61c250',#R2
               'https://app.smartsheet.com/b/publish?EQBCT=1f42c61dfbe54c3ab6852db9080cd516',#R3
               'https://app.smartsheet.com/b/publish?EQBCT=d7a42d313d4045db95d53ce760d0846a',#P1
               'https://app.smartsheet.com/b/publish?EQBCT=9840fc9707c74cf08f4599ecc066b568',#P2
               'https://app.smartsheet.com/b/publish?EQBCT=1ae547ca4cd4462885e4ec920ab0e539',#P3
               'https://app.smartsheet.com/b/publish?EQBCT=97d08666bb6b4c718ef970068038e7cd',#P4
               'https://app.smartsheet.com/b/publish?EQBCT=928aab297b2045378263e28e7a83b090'],#P5
        'x':[600,685,645,785,745,480,420,380,320,260,480,400,320,460,390,310,270,180],
        'y':[1040,1040,1090,1040,1090,890,840,890,840,890,600,600,600,400,350,400,350,400]}

db = pd.DataFrame(dbs)
report1=pd.merge(dept_report, db,left_on="Equipment", right_on="Equip", how="right")
#report1=report1[report1['Colour'].notna()]
report1["Status"]=["Ahead by " if x >= 0 else "Behind by " for x in report1['Minutes Ahead/ Behind']]
report1["Description"]=report1["Status"] + round(abs(report1["Minutes Ahead/ Behind"]),0).astype(str) +" minutes"
report1["img1"]=image_base64_ss

spec=sheets_data('SpecSheetLinks')
spec_rb=sheets_data('RobotParameterSheets')
spec_pk=sheets_data('PackingSpec')
diag_pk=sheets_data('PackingDiagrams')
cot_enr=sheets_data('EnrobingSpecs')

bak_bse=bak_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
bak_bse['Dept']='Baking'
bak_bse=pd.merge(bak_bse, spec,left_on=["BSE1",'Dept'], right_on=["BSE",'Dept'], how="left")

enr_bse=enr_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
enr_bse['Dept']='Enrobing'
enr_bse=pd.merge(enr_bse, spec,left_on=["BSE1",'Dept'], right_on=["BSE",'Dept'], how="left")

rb_fin=rb_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
rb_fin['Dept']='Robot'
rb_fin=pd.merge(rb_fin, spec_rb,left_on=["BSE1",'Dept'], right_on=["FINS",'Dept'], how="left")
 
pk_itm=pk_report.groupby(['Date','Equipment','BSE1'])[['Quantity Ahead/ Behind','Minutes Ahead/ Behind']].sum().reset_index()
pk_itm['Dept']='Packing'
pk_itm=pd.merge(pk_itm, spec_pk,left_on=["BSE1",'Dept'], right_on=["ITMS",'Dept'], how="left")
pk_itm['Dept']='Spec'

links=pd.concat([bak_bse,enr_bse,rb_fin,pk_itm],axis=0)   
#links['img']=image_base64_spec
links['img'] = [
    image_base64_spec_p if x[0] == "P" 
    else image_base64_spec_r if x[0] == "R" 
    else image_base64_spec if x[0] == "E"
    else image_base64_bse 
    for x in links['Equipment']
]

diag=pk_report[['Equipment','Packing Diagram']].drop_duplicates()
diag.rename(columns={'Packing Diagram': 'BSE1'}, inplace=True)
diag1=pd.merge(diag, diag_pk, left_on='BSE1', right_on="DiagramCode", how='left')
diag1['Dept']="Packing"
diag1['img']=image_base64_diag

cots=enr_report[['Equipment','Item Code']].drop_duplicates()
cots.rename(columns={'Item Code': 'BSE1'}, inplace=True)
cots1=pd.merge(cots, cot_enr, left_on='BSE1', right_on="Cots", how='left')
cots1['Dept']="Spec"
cots1['img']=image_base64_cot

links=pd.concat([links,diag1,cots1],axis=0)  

link_url = "https://www.boscoandroxys.com/"

# ----- HTML with embedded JS -----
#<div style="width: 100%; overflow-x: auto;">
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
        <a href="javascript:void(0)" onclick="showOptions('{row['Equip']}', '{row['Db']}','{row['img1']}')"
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
  <div id="side-options" tabindex="0" style="
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
        report1[['Equip', 'Description','Colour','img1']].dropna().to_dict(orient="records")
    ) + """;

    // BSE spec data for all equipment
    window.bseData = """ + json.dumps(links[['Equipment', 'BSE1', 'img','Links','Dept']].dropna().to_dict(orient="records")) + """;

    // Function to show dashboard and spec buttons in side panel
    function showOptions(equip, link,img1) {
        const panel = document.getElementById('side-options');         
        panel.innerHTML = '<h4 style="margin-bottom: 10px; font-size: 30px;"> ' + equip + '</h4>';
        panel.focus();
        panel.scrollIntoView({ behavior: 'smooth' });
        const dashBtn = document.createElement('button');
        dashBtn.innerText = 'Smartsheet Dashboards';
        dashBtn.style.backgroundImage = `url('${img1}')`;
        dashBtn.style.opacity = "0.8";
        dashBtn.style.backgroundRepeat = "no-repeat";
        dashBtn.style.backgroundSize = 'cover'; 
        dashBtn.style.backgroundPosition = 'center'; 
        dashBtn.style.width = '155px'; 
        dashBtn.style.height = '90px';
        dashBtn.style.fontSize = '20px';
        dashBtn.style.fontWeight = "bold";
        //dashBtn.style.marginBottom = '12px';
        //dashBtn.style.padding = '8px 14px';
        //dashBtn.style.background = '#ACDDDE';
        dashBtn.style.color = 'Black';
        dashBtn.style.border = 'none';
        dashBtn.style.borderRadius = '8px';
        dashBtn.style.cursor = 'pointer';
        dashBtn.onclick = () => window.open(link, '_blank');
        panel.appendChild(dashBtn);
        

        const filtered = window.bseData.filter(row => row.Equipment === equip && row.Dept !== 'Spec');
        if (filtered.length > 0) {
            const label = document.createElement('div');
            label.innerHTML = '<h5 style="margin: 5px 0;font-size: 24px;">Parameter Sheets:</h5>';
            panel.appendChild(label);
            filtered.forEach(row => {
                const btn = document.createElement('button');
                btn.innerText =   row.BSE1;
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.color = 'black';
                btn.style.fontSize = '30px';
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
                //btn.style.margin = '10px';
                //btn.style.marginTop = '5px';
                btn.style.marginBottom = '5px';
                btn.style.padding = '10px';
                
                // Adding background image
                //btn.style.backgroundImage = "url('https://www.shutterstock.com/shutterstock/photos/2239154457/display_1500/stock-photo-digital-tablet-with-sample-spreadsheet-document-on-the-screen-2239154457.jpg')";
                btn.style.backgroundImage = `url('${row.img}')`;
                btn.style.opacity = "0.8";
                btn.style.backgroundRepeat = "no-repeat";
                btn.style.backgroundSize = 'cover'; 
                btn.style.backgroundPosition = 'center'; 
                // Adjusting button size to match the image's aspect ratio
                btn.style.width = '111px'; 
                btn.style.height = '160px';
                
                btn.onclick = () => window.open(row.Links, '_blank');
                panel.appendChild(btn);
            });
        } else {
            const msg = document.createElement('p');
            msg.innerText = 'No parameter sheets found for this equipment.';
            panel.appendChild(msg);
        }
            
        const filtered1 = window.bseData.filter(row => row.Equipment === equip && row.Dept === 'Spec');
        if (filtered1.length > 0) {
            const label1 = document.createElement('div');
            label1.innerHTML = '<h5 style="margin: 5px 0;font-size: 24px;">Specification Sheets:</h5>';
            panel.appendChild(label1);
            filtered1.forEach(row => {
                const btn1 = document.createElement('button');
                btn1.innerText =   row.BSE1;
                btn1.style.display = 'flex';
                btn1.style.alignItems = 'center';
                btn1.style.justifyContent = 'center';
                btn1.style.color = 'black';
                btn1.style.fontSize = '20px';
                btn1.style.fontWeight = "bold";
                btn1.style.textDecoration = "underline"; // default (solid)
                btn1.style.textDecorationStyle = "dashed";     // dashed underline
                btn1.style.textDecorationColor = "black";       // custom underline color
                btn1.style.textDecorationThickness = "2px";    // custom thickness
                btn1.style.textAlign = 'center';
                btn1.style.border = 'none';
                btn1.style.borderRadius = '1px';
                btn1.style.cursor = 'pointer';
                btn1.style.marginBottom = '1px';
                btn1.style.padding = '1px';
                
                btn1.style.whiteSpace = 'normal';
                btn1.style.width = '100%';
                btn1.style.maxWidth = '100%';
                btn1.style.overflow = 'visible';
                btn1.style.wordBreak = 'break-word';
                btn1.style.lineHeight = '1.2';
                
                // Adding background image
                btn1.style.backgroundImage = `url('${row.img}')`;
                btn1.style.opacity = "0.8";
                btn1.style.backgroundRepeat = "no-repeat";
                btn1.style.backgroundSize = 'cover'; 
                btn1.style.backgroundPosition = 'center'; 
                // Adjusting button size to match the image's aspect ratio
                btn1.style.width = '111px'; 
                btn1.style.height = '160px';
                
                btn1.onclick = () => window.open(row.Links, '_blank');
                panel.appendChild(btn1);
            });
        } else {
            const msg1 = document.createElement('p');
            msg1.innerText = '';
            panel.appendChild(msg1);
        }
            
         // Show description
        const descData = window.equipData.find(row => row.Equip === equip);
        if (descData) {
           const descBox = document.createElement('div');
           descBox.innerText = '⌛Overall:' + descData.Description + '🕒';
           descBox.style.marginTop = '12px';
           descBox.style.padding = '10px 14px';
           descBox.style.background = descData.Colour;
           descBox.style.color = 'white';
           descBox.style.borderRadius = '8px';
           descBox.style.boxShadow = '1px 1px 3px rgba(0,0,0,0.1)';
           descBox.style.fontSize = '25px';
           descBox.style.opacity = "0.5";
           // descBox.style.borderLeft = '4px solid #2857a7'; // accent strip
           panel.appendChild(descBox);
        }
        
        
    }
</script>
"""


# logo_html = f"""
# <div style="position: fixed; top: 10px; right: 20px; z-index: 1000;">
#     <a href="{link_url}" target="_blank">
#         <img src="{logo}" alt="Company Logo" style="height: 100px;">
#     </a>
# </div>
# """




# Render to Streamlit
html(overlay_html, height=1800)

