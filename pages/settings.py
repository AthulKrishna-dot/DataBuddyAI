import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Settings", layout="wide")

st.title("⚙️ Settings")

st.subheader("AWS Configuration")

col1, col2 = st.columns(2)
with col1:
    st.write("**AWS Bucket:**")
    st.code(os.getenv("AWS_BUCKET", "Not set"))

with col2:
    st.write("**AWS Region:**")
    st.code(os.getenv("AWS_REGION", "us-east-1"))

st.divider()

st.subheader("📖 AWS Free Tier Services")

services = {
    "S3 (Storage)": {
        "limit": "5 GB storage/month for 12 months",
        "use_case": "Store datasets, CSV files, exports",
    },
    "Lambda": {
        "limit": "1M requests/month (always free)",
        "use_case": "Run serverless data processing jobs",
    },
    "DynamoDB": {
        "limit": "25 GB storage/month for 12 months",
        "use_case": "NoSQL database for metadata",
    },
    "CloudWatch": {
        "limit": "5 GB logs ingestion/month",
        "use_case": "Monitor application logs",
    },
    "EC2": {
        "limit": "750 hours/month for 12 months (t2.micro)",
        "use_case": "Host API servers and backend",
    },
    "RDS": {
        "limit": "750 hours/month for 12 months (db.t3.micro)",
        "use_case": "Managed PostgreSQL/MySQL database",
    },
}

for service, details in services.items():
    st.markdown(f"**{service}**")
    st.markdown(f"- **Limit**: {details['limit']}")
    st.markdown(f"- **Use Case**: {details['use_case']}")
    st.divider()

st.subheader("🚀 Next Steps")
st.markdown(
    """
    1. **Configure AWS**: Set AWS_BUCKET and AWS_REGION in `.env`
    2. **Run Dashboard**: `streamlit run streamlit_app.py`
    3. **Upload Data**: Use the Upload tab to add files to S3
    4. **Process Data**: Use the Data Processor page to filter and transform CSV files
    5. **Monitor**: Check Analytics tab for bucket usage
    """
)

st.divider()
st.markdown(
    """
    **Security Tips:**
    - Never commit `.env` to Git
    - Use IAM roles with minimal permissions
    - Rotate AWS access keys regularly
    - Enable S3 bucket versioning for data protection
    """
)
