import streamlit as st
import pandas as pd
import os

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EmotionSense AI - Admin",
    page_icon="🔐",
    layout="wide"
)

# =========================================================
# FILE LOCATION
# =========================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(
    DATA_FOLDER,
    "analysis_history.csv"
)

os.makedirs(DATA_FOLDER, exist_ok=True)


# =========================================================
# ADMIN LOGIN
# =========================================================

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


if not st.session_state.admin_logged_in:

    st.title("🔐 EmotionSense AI")
    st.subheader("Admin Login")

    username = st.text_input(
        "Admin Username"
    )

    password = st.text_input(
        "Admin Password",
        type="password"
    )

    st.info(
        "Demo Admin Login\n\n"
        "Username: admin\n"
        "Password: admin123"
    )

    if st.button(
        "🔓 Admin Login",
        use_container_width=True
    ):

        if username == "admin" and password == "admin123":

            st.session_state.admin_logged_in = True

            st.success(
                "Admin login successful!"
            )

            st.rerun()

        else:

            st.error(
                "Invalid admin username or password."
            )

    st.stop()


# =========================================================
# ADMIN DASHBOARD
# =========================================================

st.title("🔐 Admin Dashboard")

st.markdown(
    "### 🧠 EmotionSense AI Management Panel"
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Admin Panel")

    st.write("📊 Dashboard")
    st.write("📋 Analysis History")
    st.write("📈 Statistics")

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.admin_logged_in = False

        st.rerun()


# =========================================================
# LOAD DATA
# =========================================================

if os.path.exists(DATA_FILE):

    try:

        df = pd.read_csv(DATA_FILE)

    except Exception:

        df = pd.DataFrame()

else:

    df = pd.DataFrame()


# =========================================================
# EMPTY DATA
# =========================================================

if df.empty:

    st.info(
        "📭 No analysis records are available yet."
    )

    st.markdown(
        """
        Analysis records will appear here after
        users perform emotion analysis in the main application.
        """
    )

    st.stop()


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

st.subheader("📊 Dashboard Overview")

total_analyses = len(df)

average_score = df["Wellness Score"].mean()

high_risk = len(
    df[df["Risk"] == "High Risk"]
)

moderate_risk = len(
    df[df["Risk"] == "Moderate Risk"]
)

low_risk = len(
    df[df["Risk"] == "Low Risk"]
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Analyses",
        total_analyses
    )


with col2:

    st.metric(
        "Average Wellness Score",
        f"{average_score:.1f}/100"
    )


with col3:

    st.metric(
        "Low Risk",
        low_risk
    )


with col4:

    st.metric(
        "High Risk",
        high_risk
    )


st.divider()


# =========================================================
# EMOTION STATISTICS
# =========================================================

st.subheader("🧠 Emotion Statistics")

emotion_counts = df[
    "Emotion"
].value_counts()

st.bar_chart(
    emotion_counts
)


# =========================================================
# RISK STATISTICS
# =========================================================

st.subheader("🚦 Risk Distribution")

risk_counts = df[
    "Risk"
].value_counts()

st.bar_chart(
    risk_counts
)


# =========================================================
# ANALYSIS HISTORY
# =========================================================

st.divider()

st.subheader("📋 Analysis History")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DOWNLOAD DATA
# =========================================================

st.subheader("📥 Export Data")

csv_data = df.to_csv(
    index=False
)

st.download_button(
    label="⬇️ Download Analysis History",
    data=csv_data,
    file_name="analysis_history.csv",
    mime="text/csv",
    use_container_width=True
)


# =========================================================
# DELETE HISTORY
# =========================================================

st.divider()

st.subheader("🗑️ Data Management")

if st.button(
    "Delete All Analysis History",
    type="secondary"
):

    if os.path.exists(DATA_FILE):

        os.remove(DATA_FILE)

        st.success(
            "Analysis history deleted successfully."
        )

        st.rerun()