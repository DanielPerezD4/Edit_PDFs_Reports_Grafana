import calendar
import re
from datetime import date

import pymupdf as pm  # pip install pymupdf
import streamlit as st

dc_name_map = {'DC082': 'MIL29',
               'DC09': 'MIL28',
               'DC06': 'MIL21',
               'DC07': 'MIL22',
               'DC05': 'MXP73'}

DCS = list(dc_name_map)
CLIENTS = ['Macro', 'A100']

# PDF coordinates are in points; origin is bottom-left.
# Define rectangles where fields should appear (x0, y0, x1, y1).

# Small versioning table in the cover page, common to all reports
# page, (x0, y0, x1 ,y1)
versioning = ((0,  pm.Rect(18, 655, 18+45, 655+14)),            # Versioning - Report issue
              (0,  pm.Rect(18, 655+15, 18+45, 655+15+14)),      # Versioning - 1st revision date
              (0,  pm.Rect(68, 655+15, 68+30, 655+15+14)),      # Versioning - 1st revision version
              (0,  pm.Rect(100, 655+15, 100+90, 655+15+14)),    # Versioning - 1st revision reason
              (0,  pm.Rect(18, 655+30, 18+45, 655+30+14)),      # Versioning - 2st revision date
              (0,  pm.Rect(68, 655+30, 68+30, 655+30+14)),      # Versioning - 2st revision version
              (0,  pm.Rect(100, 655+30, 100+90, 655+30+14)),    # Versioning - 2st revision reason
              (0,  pm.Rect(18, 655+45, 18+45, 655+45+14)),      # Versioning - 3st revision date
              (0,  pm.Rect(68, 655+45, 68+30, 655+45+14)),      # Versioning - 3st revision version
              (0,  pm.Rect(100, 655+45, 100+90, 655+45+14)),    # Versioning - 3st revision reason
              (0,  pm.Rect(18, 655+60, 18+45, 655+60+14)),      # Versioning - 4st revision date
              (0,  pm.Rect(68, 655+60, 68+30, 655+60+14)),      # Versioning - 4st revision version
              (0,  pm.Rect(100, 655+60, 100+90, 655+60+14)))    # Versioning - 4st revision reason

positions_dcY2 = versioning + (
    (10, pm.Rect(15, 600, 15+565, 600+180)),     # A1
    (15, pm.Rect(15, 620, 15+565, 620+160)),     # A2
    (20, pm.Rect(15, 640, 15+565, 640+140)),     # B1
    (25, pm.Rect(15, 660, 15+565, 660+120)),     # B2
    (26, pm.Rect(15, 730, 15+230, 735+55)),      # Cooling
    (28, pm.Rect(425, 100, 580, 100+120)),       # UPS
    (28, pm.Rect(15, 750, 15+565, 760+40)),      # GE
    (30, pm.Rect(15, 680, 15+565, 680+100)))     # Summary

positions_dcy2_A100 = versioning + (
    (10, pm.Rect(15, 600, 15+565, 600+180)),     # A1
    (15, pm.Rect(15, 620, 15+565, 620+160)),     # A2
    (16, pm.Rect(15, 730, 15+230, 735+55)),      # Cooling
    (17, pm.Rect(425, 570, 580, 570+120)),       # UPS
    (18, pm.Rect(15, 610, 15+565, 610+130)),     # GE
    (20, pm.Rect(15, 680, 15+565, 680+100)))     # Summary

positions_dcL = versioning + (
    (6,  pm.Rect(15, 720, 15+565, 720+70)),      # A12 temp/humid
    (10, pm.Rect(15, 580, 15+565, 580+200)),     # A12 IT
    (12, pm.Rect(15, 720, 15+565, 720+70)),      # A34 temp/humid
    (16, pm.Rect(15, 580, 15+565, 580+200)),     # A34 IT
    (18, pm.Rect(15, 720, 15+565, 720+70)),      # B12 temp/humid
    (22, pm.Rect(15, 580, 15+565, 580+200)),     # B12 IT
    (24, pm.Rect(15, 720, 15+565, 720+70)),      # B34 temp/humid
    (28, pm.Rect(15, 580, 15+565, 580+200)),     # B34 IT
    (30, pm.Rect(255, 750, 580, 750+40)),        # Cooling
    (32, pm.Rect(15, 740, 15+565, 740+40)),      # UPS
    (33, pm.Rect(15, 710, 15+565, 710+80)),      # GE
    (35, pm.Rect(15, 680, 15+565, 680+100)))     # Summary

positions_dcL_Macro = versioning + (
    (12-6, pm.Rect(15, 720, 15+565, 720+70)),    # A34 temp/humid
    (16-6, pm.Rect(15, 580, 15+565, 580+200)),   # A34 IT
    (18-6, pm.Rect(15, 720, 15+565, 720+70)),    # B12 temp/humid
    (22-6, pm.Rect(15, 580, 15+565, 580+200)),   # B12 IT
    (24-6, pm.Rect(15, 720, 15+565, 720+70)),    # B34 temp/humid
    (28-6, pm.Rect(15, 580, 15+565, 580+200)),   # B34 IT
    (30-6, pm.Rect(255, 750, 580, 750+40)),      # Cooling
    (32-6, pm.Rect(15, 740, 15+565, 740+40)),    # UPS
    (33-6, pm.Rect(15, 710, 15+565, 710+80)),    # GE
    (35-6, pm.Rect(15, 680, 15+565, 680+100)))   # Summary

positions_dcL_A100 = versioning + (
    (6,  pm.Rect(15, 720, 15+565, 720+70)),      # A12 temp/humid
    (10, pm.Rect(15, 700, 15+565, 700+80)),      # A12 IT
    (30-19, pm.Rect(255, 750, 580, 750+40)),     # Cooling
    (32-20, pm.Rect(15, 690, 15+565, 690+100)),  # UPS
    (33-20, pm.Rect(15, 610, 15+565, 610+180)),  # GE
    (35-20, pm.Rect(15, 680, 15+565, 680+100)))  # Summary

positions = {"DC06": positions_dcY2,
             "DC07_Macro": positions_dcL_Macro,
             "DC07_A100": positions_dcL_A100,
             "DC082": positions_dcL,
             "DC09": positions_dcL,
             "DC05": positions_dcy2_A100}


def detect_dc(filename):
    for match in re.findall(r'DC\d+', filename, re.IGNORECASE):
        if match.upper() in DCS:
            return match.upper()
    return None


def detect_client(filename, dc):
    name = filename.upper()
    if 'A100' in name:
        return 'A100'
    if 'MACRO' in name:
        return 'Macro'
    if dc == 'DC05':  # Only an A100 report exists for DC05
        return 'A100'
    return None


def get_positions(dc, client):
    if dc == 'DC07':
        return positions[f'{dc}_{client}']
    return positions[dc]


def output_report_name(dc, client, month, year):
    dc_client = dc_name_map[dc]
    if dc == 'DC07' and client == 'A100':
        dc_client = 'MXP86'
    return f'{dc}_{dc_client}_{month}_{year}_Energy Report_{client}.pdf'


@st.cache_data(show_spinner="Adding comment fields...")
def add_comment_fields(pdf_bytes, dc, client):
    doc = pm.open(stream=pdf_bytes, filetype="pdf")
    try:
        for i, (page_id, rect) in enumerate(get_positions(dc, client)):
            if page_id >= doc.page_count:
                raise ValueError(f"The layout for {dc} / {client} expects page {page_id + 1}, "
                                 f"but the PDF only has {doc.page_count} pages. "
                                 "Check the selected building and client.")
            if page_id == 0:  # Small versioning table in cover page
                textsize = 8
                default_text = '-'
            else:
                textsize = 10
                default_text = 2*"- \n"

            # Create a multiline text field
            w1 = pm.Widget()
            w1.field_name = f"Comments_p{i+1}"  # make names unique, otherwise they are not displayed
            w1.field_type = pm.PDF_WIDGET_TYPE_TEXT
            w1.rect = rect
            w1.text_font = "helv"
            w1.text_fontsize = textsize
            w1.field_flags = (
                pm.PDF_TX_FIELD_IS_MULTILINE |
                pm.PDF_TX_FIELD_IS_DO_NOT_SCROLL
            )
            w1.border_color = (1, 1, 1)
            w1.fill_color = (1, 1, 1)

            w1.field_default_value = default_text   # DV (used by Reset Form)
            w1.field_value = default_text           # visible on open

            page = doc[page_id]  # keep a reference, otherwise the widget gets unbound from the page
            page.add_widget(w1)
            w1.update()
        return doc.tobytes()
    finally:
        doc.close()


st.set_page_config(page_title="Grafana PDF Report Editor", page_icon="📄")
st.title("Grafana PDF Report Editor")
st.write("Upload a Grafana energy report to add the editable comment fields and rename it.")

uploaded = st.file_uploader("Grafana PDF", type="pdf")
if uploaded is None:
    st.stop()

file_key = getattr(uploaded, "file_id", f"{uploaded.name}_{uploaded.size}")

detected_dc = detect_dc(uploaded.name)
dc = st.radio("Building (DC)", DCS,
              index=DCS.index(detected_dc) if detected_dc else None,
              horizontal=True, key=f"dc_{file_key}")
if detected_dc:
    st.caption(f"{detected_dc} detected from the file name.")
else:
    st.warning("No building detected in the file name, please select it manually.")

detected_client = detect_client(uploaded.name, detected_dc)
client = st.radio("Client", CLIENTS,
                  index=CLIENTS.index(detected_client) if detected_client else None,
                  horizontal=True, key=f"client_{file_key}")
if detected_client:
    st.caption(f"{detected_client} detected from the file name.")
else:
    st.warning("No client detected in the file name, please select it manually.")

# Reports are produced after the month ends, so default to the previous month
today = date.today()
default_year, default_month = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
months = list(calendar.month_name)[1:]
col_month, col_year = st.columns(2)
month = col_month.selectbox("Month", months, index=default_month - 1)
year = col_year.number_input("Year", min_value=2000, max_value=2100, value=default_year, step=1)

if dc is None or client is None:
    st.info("Select the building and the client to generate the report.")
    st.stop()

out_name = output_report_name(dc, client, month, year)

try:
    pdf_out = add_comment_fields(uploaded.getvalue(), dc, client)
except Exception as e:
    st.error(f"Could not process the PDF: {e}")
    st.stop()

st.success(f"Report ready: **{out_name}**")
st.download_button("Download PDF", data=pdf_out, file_name=out_name,
                   mime="application/pdf", type="primary")
