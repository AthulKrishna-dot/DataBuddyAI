import os
import io
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from aws_integration import (
    download_object,
    get_s3_client,
    list_bucket_objects,
    upload_demo_file,
)

# Load environment variables
load_dotenv()

st.set_page_config(page_title="DataBuddyAI - AWS S3 Dashboard", layout="wide")

# Sidebar configuration
st.sidebar.title("⚙️ AWS Configuration")
aws_bucket = os.getenv("AWS_BUCKET")
aws_region = os.getenv("AWS_REGION", "us-east-1")

if not aws_bucket:
    st.sidebar.error("❌ AWS_BUCKET not configured. Please set it in your .env file.")
    st.stop()

st.sidebar.info(
    f"**Bucket**: {aws_bucket}\n**Region**: {aws_region}"
)

# Main title
st.title("🤖 DataBuddyAI - S3 Data Manager")
st.markdown(
    """
    Manage your data on AWS S3 with a simple, interactive dashboard.
    """
)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Browse", "📤 Upload", "📥 Download", "📈 Analytics"]
)

# Tab 1: Browse S3 Bucket
with tab1:
    st.header("Browse S3 Bucket")
    try:
        objects = list_bucket_objects()
        if objects:
            st.success(f"Found {len(objects)} object(s) in {aws_bucket}")
            df_objects = pd.DataFrame({"Object Key": objects})
            st.dataframe(df_objects, use_container_width=True)
        else:
            st.info(f"No objects found in {aws_bucket}. Upload a file to get started!")
    except Exception as e:
        st.error(f"Error listing bucket objects: {e}")

# Tab 2: Upload Files
with tab2:
    st.header("Upload Data to S3")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Option 1: Upload Local File")
        uploaded_file = st.file_uploader(
            "Choose a file to upload", type=["csv", "json", "xlsx", "txt"]
        )

        if uploaded_file is not None:
            s3_key = st.text_input(
                "S3 path (e.g., data/myfile.csv):",
                value=f"uploads/{uploaded_file.name}",
            )

            if st.button("Upload File", key="upload_local"):
                try:
                    # Save uploaded file temporarily
                    temp_path = f"/tmp/{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Upload to S3
                    location = upload_demo_file(temp_path, s3_key)
                    st.success(f"✅ File uploaded to {location}")

                    # Clean up
                    os.remove(temp_path)
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    with col2:
        st.subheader("Option 2: Create Sample Data")
        if st.button("Upload Sample Data", key="upload_sample"):
            try:
                location = upload_demo_file("sample_data.csv", "demo/sample_data.csv")
                st.success(f"✅ Sample data uploaded to {location}")
            except FileNotFoundError:
                st.error("sample_data.csv not found in project directory.")
            except Exception as e:
                st.error(f"Upload failed: {e}")

# Tab 3: Download & Preview Files
with tab3:
    st.header("Download & Preview Data")

    try:
        objects = list_bucket_objects()
        if objects:
            selected_object = st.selectbox("Select a file to download/preview:", objects)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Preview File", key="preview"):
                    try:
                        # Download to memory
                        local_path = download_object(selected_object)
                        st.success(f"✅ Downloaded: {selected_object}")

                        # Try to display as dataframe
                        if selected_object.endswith(".csv"):
                            df = pd.read_csv(local_path)
                            st.dataframe(df, use_container_width=True)
                        elif selected_object.endswith(".json"):
                            import json

                            with open(local_path, "r") as f:
                                data = json.load(f)
                            st.json(data)
                        else:
                            with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                            st.text(content[:1000])  # Show first 1000 chars
                    except Exception as e:
                        st.error(f"Preview failed: {e}")

            with col2:
                if st.button("Download File", key="download"):
                    try:
                        local_path = download_object(selected_object)
                        with open(local_path, "rb") as f:
                            file_content = f.read()
                        st.download_button(
                            label=f"Click to download {Path(selected_object).name}",
                            data=file_content,
                            file_name=Path(selected_object).name,
                            key="download_btn",
                        )
                    except Exception as e:
                        st.error(f"Download failed: {e}")
        else:
            st.info("No files in bucket to download.")
    except Exception as e:
        st.error(f"Error loading files: {e}")

# Tab 4: Analytics
with tab4:
    st.header("📈 S3 Bucket Analytics")

    try:
        objects = list_bucket_objects()

        if objects:
            # Basic stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Objects", len(objects))
            with col2:
                csv_count = sum(1 for obj in objects if obj.endswith(".csv"))
                st.metric("CSV Files", csv_count)
            with col3:
                json_count = sum(1 for obj in objects if obj.endswith(".json"))
                st.metric("JSON Files", json_count)

            # File type distribution
            st.subheader("File Type Distribution")
            extensions = [Path(obj).suffix for obj in objects]
            ext_counts = pd.Series(extensions).value_counts()
            st.bar_chart(ext_counts)

            # Object list with sizes
            st.subheader("All Objects in Bucket")
            client = get_s3_client()
            try:
                response = client.list_objects_v2(Bucket=os.getenv("AWS_BUCKET"))
                if "Contents" in response:
                    data = [
                        {
                            "Key": item["Key"],
                            "Size (KB)": round(item["Size"] / 1024, 2),
                            "Last Modified": item["LastModified"],
                        }
                        for item in response["Contents"]
                    ]
                    df_analytics = pd.DataFrame(data)
                    st.dataframe(df_analytics, use_container_width=True)
            except Exception as e:
                st.error(f"Error fetching object details: {e}")
        else:
            st.info("No data to analyze. Upload some files first!")
    except Exception as e:
        st.error(f"Analytics failed: {e}")

# Footer
st.divider()
st.markdown(
    """
    ---
    **DataBuddyAI** | AWS S3 Dashboard | Free Tier Integration

    💡 **Tips**:
    - Use `.env` file to configure AWS_BUCKET and AWS_REGION
    - Run with: `streamlit run streamlit_app.py`
    - All data stored on AWS S3 (free tier: 5GB/month for 12 months)
    """
)
