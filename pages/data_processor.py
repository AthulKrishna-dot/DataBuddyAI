import os
import io
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from aws_integration import upload_demo_file, download_object, list_bucket_objects

load_dotenv()

st.set_page_config(page_title="Data Processor", layout="wide")

st.title("🔄 Data Processor")
st.markdown("Process and transform your CSV data stored on S3.")

aws_bucket = os.getenv("AWS_BUCKET")
if not aws_bucket:
    st.error("AWS_BUCKET not configured.")
    st.stop()

# Select file to process
objects = list_bucket_objects()
csv_files = [obj for obj in objects if obj.endswith(".csv")]

if csv_files:
    selected_file = st.selectbox("Select a CSV file to process:", csv_files)

    if st.button("Load File"):
        try:
            local_path = download_object(selected_file)
            df = pd.read_csv(local_path)

            st.success(f"Loaded {selected_file} ({len(df)} rows)")
            st.dataframe(df, use_container_width=True)

            # Processing options
            st.subheader("🛠️ Processing Options")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Show Statistics"):
                    st.dataframe(df.describe(), use_container_width=True)

            with col2:
                if st.button("Show Data Types"):
                    st.dataframe(
                        pd.DataFrame(
                            {"Column": df.columns, "Type": df.dtypes}
                        ),
                        use_container_width=True,
                    )

            # Filter columns
            st.subheader("📋 Column Selection")
            selected_cols = st.multiselect(
                "Select columns to keep:", df.columns, default=list(df.columns)
            )
            if selected_cols:
                filtered_df = df[selected_cols]
                st.dataframe(filtered_df, use_container_width=True)

                # Save processed file
                if st.button("Save Processed File to S3"):
                    output_key = st.text_input(
                        "S3 output path:",
                        value=f"processed/{selected_file.split('/')[-1]}",
                    )
                    temp_path = "/tmp/processed.csv"
                    filtered_df.to_csv(temp_path, index=False)
                    try:
                        location = upload_demo_file(temp_path, output_key)
                        st.success(f"✅ Saved to {location}")
                        os.remove(temp_path)
                    except Exception as e:
                        st.error(f"Save failed: {e}")

        except Exception as e:
            st.error(f"Error loading file: {e}")
else:
    st.info("No CSV files found in S3. Upload some data first!")
