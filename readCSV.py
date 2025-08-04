import pandas as pd
import base64
import ast
from io import BytesIO
import streamlit as st
import os

# ---- CSV LOADING ----
latest_csv = 'YOUR_CSV_FILE.csv'  # Replace with your actual CSV file path
if not os.path.isfile(latest_csv):
    st.error(f"CSV file not found: {latest_csv}")
    st.stop()

st.set_page_config(layout="wide")

# ---- BIG TABLE AND IMAGE CSS ----
st.markdown("""
    <style>
    .block-container .stColumns {
        gap: 0 !important;
        margin-top: -20px !important;
        margin-bottom: -20px !important;
    }
    .stCaption {
        margin-top: 2px !important;
        margin-bottom: 2px !important;
        font-size: 17px !important;
    }
    .stImage img {
        margin-bottom: 0px !important;
        margin-top: 0px !important;
        display: block;
    }
    .stDataFrame {
        margin-bottom: 20px !important;
        margin-top: 30px !important;
        padding: 10px !important;
        min-width: 2200px !important;
        max-width: 99vw !important;
        width: 99vw !important;
        overflow-x: auto !important;
        box-sizing: border-box;
    }
    .stDataFrame [data-testid="stDataFrameCell"], 
    .stDataFrame th {
        font-size: 38px !important;
        font-family: 'Times New Roman', Times, serif !important;
        line-height: 4 !important;  /* ADD THIS FOR LINE SPACING */
        vertical-align: middle !important;
        min-height: 110px !important;
        padding-top: 38px !important;
        padding-bottom: 38px !important;
        padding-left: 44px !important;
        padding-right: 44px !important;
        min-width: 300px !important;
    }
    .stDataFrame th {
        background: #232323 !important;
        color: #fff !important;
        padding-top: 32px !important;
        padding-bottom: 32px !important;
        padding-left: 36px !important;
        padding-right: 36px !important;
        min-width: 300px !important;
    }
    .stDataFrame {
        margin-left: auto !important;
        margin-right: auto !important;
    }
    .stColumn {
        min-height: 900px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)


st.info(f"Loading CSV: {latest_csv}")

df = pd.read_csv(latest_csv)

st.title("Recipe Extraction Results: All Data + Images")

if 'full_page_image' in df.columns:
    df_noimg = df.drop(columns=['full_page_image'])
else:
    df_noimg = df

for row_num, (idx, row) in enumerate(df.iterrows(), 1):
    st.markdown(f"## Row {row_num} — Pages {row.get('Page_Numbers', '')}:")
    st.dataframe(df_noimg.iloc[[idx]], use_container_width=True)

    # Show images, 3 per row, tight spacing
    if 'full_page_image' in df.columns:
        img_list = row.get("full_page_image", "[]")
        try:
            images = ast.literal_eval(img_list) if isinstance(img_list, str) else img_list
        except Exception:
            images = []
        valid_images = [b64 for b64 in images if b64 and len(b64) > 100]
        n_imgs = len(valid_images)

        for i in range(0, n_imgs, 3):
            img_chunk = valid_images[i:i+3]
            # Begin center-aligned flex row
            st.markdown(
                "<div style='display: flex; justify-content: center; gap: 0; width: 100%;'>",
                unsafe_allow_html=True,
            )
            cols = st.columns(len(img_chunk))
            for j, b64 in enumerate(img_chunk):
                try:
                    img_bytes = base64.b64decode(b64)
                    cols[j].image(BytesIO(img_bytes), caption=f"Page {i+j+1}", width=620)
                except Exception as e:
                    cols[j].warning(f"Could not display image: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

st.success("All done!")
