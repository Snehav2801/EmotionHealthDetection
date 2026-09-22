import streamlit as st
import cv2
import numpy as np
import pandas as pd
import os
import hashlib
from datetime import datetime
from PIL import Image
from tensorflow.keras.models import load_model
from chatbot.wellness_chatbot import generate_response


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="EmotionSense AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777;
        margin-bottom: 30px;
    }

    .risk-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        font-size: 20px;
        font-weight: 600;
    }

    .low-risk {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }

    .moderate-risk {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }

    .high-risk {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    .info-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #f5f5f5;
        margin-bottom: 15px;
    }

    .disclaimer {
        padding: 15px;
        border-radius: 10px;
        background-color: #fff8e1;
        border: 1px solid #ffe082;
        color: #6d4c41;
        font-size: 14px;
        margin-top: 25px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CREATE REQUIRED FOLDERS
# ============================================================

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)


USERS_FILE = os.path.join("data", "users.csv")
HISTORY_FILE = os.path.join("data", "analysis_history.csv")


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "emotion" not in st.session_state:
    st.session_state.emotion = None

if "confidence" not in st.session_state:
    st.session_state.confidence = None

if "wellness_score" not in st.session_state:
    st.session_state.wellness_score = None

if "risk" not in st.session_state:
    st.session_state.risk = None


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Convert password into a secure SHA-256 hash.
    """
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# USER FILE
# ============================================================

def initialize_users_file():
    """
    Create users.csv if it does not exist.
    """

    if not os.path.exists(USERS_FILE):

        users_df = pd.DataFrame(
            columns=[
                "Username",
                "Password",
                "Created At"
            ]
        )

        users_df.to_csv(
            USERS_FILE,
            index=False
        )


initialize_users_file()


# ============================================================
# REGISTER USER
# ============================================================

def register_user(username, password):
    """
    Register a new user.
    """

    initialize_users_file()

    users_df = pd.read_csv(USERS_FILE)

    username = username.strip()

    if username == "":
        return False, "Username cannot be empty."

    if password == "":
        return False, "Password cannot be empty."

    if len(password) < 4:
        return False, "Password must contain at least 4 characters."

    if not users_df.empty:

        existing_users = (
            users_df["Username"]
            .astype(str)
            .str.lower()
            .tolist()
        )

        if username.lower() in existing_users:
            return False, "Username already exists."

    new_user = pd.DataFrame(
        [
            {
                "Username": username,
                "Password": hash_password(password),
                "Created At": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        ]
    )

    new_user.to_csv(
        USERS_FILE,
        mode="a",
        header=not os.path.exists(USERS_FILE)
        or os.path.getsize(USERS_FILE) == 0,
        index=False
    )

    return True, "Account created successfully."


# ============================================================
# LOGIN USER
# ============================================================

def authenticate_user(username, password):
    """
    Check username and password.
    """

    initialize_users_file()

    try:

        users_df = pd.read_csv(USERS_FILE)

        if users_df.empty:
            return False

        username = username.strip()

        password_hash = hash_password(password)

        matching_user = users_df[
            users_df["Username"].astype(str).str.lower()
            == username.lower()
        ]

        if matching_user.empty:
            return False

        stored_password = str(
            matching_user.iloc[0]["Password"]
        )

        if stored_password == password_hash:
            return True

        return False

    except Exception:
        return False


# ============================================================
# LOAD EMOTION MODEL
# ============================================================

@st.cache_resource
def load_emotion_model():

    return load_model(
        "models/face_emotion_model.keras"
    )


# ============================================================
# EMOTION LABELS
# ============================================================

emotion_labels = [
    "Angry",
    "Disgust",
    "Fear",
    "Happy",
    "Neutral",
    "Sad",
    "Surprise"
]


# ============================================================
# FACE DETECTOR
# ============================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# ============================================================
# WELLNESS SCORE
# ============================================================

def calculate_wellness_score(emotion):

    score = 100

    if emotion == "Happy":
        score += 10

    elif emotion == "Neutral":
        score += 5

    elif emotion == "Sad":
        score -= 10

    elif emotion == "Fear":
        score -= 12

    elif emotion == "Angry":
        score -= 8

    elif emotion == "Surprise":
        score += 2

    elif emotion == "Disgust":
        score -= 8

    score = max(
        0,
        min(score, 100)
    )

    return score


# ============================================================
# RISK LEVEL
# ============================================================

def calculate_risk(score):

    if score >= 80:
        return "Low Risk"

    elif score >= 50:
        return "Moderate Risk"

    else:
        return "High Risk"


# ============================================================
# SAVE ANALYSIS HISTORY
# ============================================================

def save_analysis_history(
    username,
    emotion,
    confidence,
    wellness_score,
    risk
):

    try:

        new_record = pd.DataFrame(
            [
                {
                    "Date & Time": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Username": username,
                    "Emotion": emotion,
                    "Confidence": round(
                        confidence,
                        2
                    ),
                    "Wellness Score": wellness_score,
                    "Risk": risk
                }
            ]
        )

        if os.path.exists(HISTORY_FILE):

            new_record.to_csv(
                HISTORY_FILE,
                mode="a",
                header=False,
                index=False
            )

        else:

            new_record.to_csv(
                HISTORY_FILE,
                index=False
            )

        return True

    except Exception:
        return False


# ============================================================
# LOGIN / REGISTRATION PAGE
# ============================================================

if not st.session_state.logged_in:

    st.markdown(
        '<div class="main-title">🧠 EmotionSense AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Multimodal Emotion & Mental Wellness Detection'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    login_tab, register_tab = st.tabs(
        [
            "🔐 Login",
            "📝 Create Account"
        ]
    )

    # ========================================================
    # LOGIN
    # ========================================================

    with login_tab:

        st.subheader("🔐 User Login")

        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )

        login_button = st.button(
            "🔓 Login",
            use_container_width=True
        )

        if login_button:

            if username.strip() == "":
                st.error("Please enter your username.")

            elif password == "":
                st.error("Please enter your password.")

            elif authenticate_user(
                username,
                password
            ):

                st.session_state.logged_in = True
                st.session_state.username = username.strip()

                st.success(
                    "Login successful!"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    # ========================================================
    # REGISTRATION
    # ========================================================

    with register_tab:

        st.subheader("📝 Create New Account")

        new_username = st.text_input(
            "Choose Username",
            placeholder="Enter a username",
            key="register_username"
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            placeholder="Enter a password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="confirm_password"
        )

        register_button = st.button(
            "✨ Create Account",
            use_container_width=True
        )

        if register_button:

            if new_username.strip() == "":
                st.error(
                    "Please enter a username."
                )

            elif new_password == "":
                st.error(
                    "Please enter a password."
                )

            elif len(new_password) < 4:
                st.error(
                    "Password must contain at least 4 characters."
                )

            elif new_password != confirm_password:
                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    new_username,
                    new_password
                )

                if success:

                    st.success(message)

                    st.info(
                        "Your account has been created. "
                        "Please go to the Login tab."
                    )

                else:

                    st.error(message)

    st.markdown(
        """
        <div class="disclaimer">
        <b>Privacy & Disclaimer:</b><br>
        This application is a college project prototype.
        Facial emotion detection and wellness scores are
        experimental and should not be considered a medical
        diagnosis or professional mental-health assessment.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# MAIN APPLICATION
# ============================================================

st.markdown(
    '<div class="main-title">🧠 EmotionSense AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multimodal Emotion & Mental Wellness Detection with AI Chatbot'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 👤 User")

    st.write(
        f"Welcome, **{st.session_state.username}**"
    )

    st.markdown("---")

    st.markdown("### 🧠 Current Analysis")

    if st.session_state.emotion:

        st.write(
            f"**Emotion:** "
            f"{st.session_state.emotion}"
        )

        st.write(
            f"**Confidence:** "
            f"{st.session_state.confidence:.2f}%"
        )

        st.write(
            f"**Wellness Score:** "
            f"{st.session_state.wellness_score}/100"
        )

        st.write(
            f"**Risk:** "
            f"{st.session_state.risk}"
        )

    else:

        st.info(
            "No emotion analysis available yet."
        )

    st.markdown("---")

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.messages = []

        st.session_state.emotion = None
        st.session_state.confidence = None
        st.session_state.wellness_score = None
        st.session_state.risk = None

        st.rerun()


# ============================================================
# MAIN COLUMNS
# ============================================================

left_column, right_column = st.columns(
    [1, 1]
)


# ============================================================
# LEFT COLUMN - EMOTION DETECTION
# ============================================================

with left_column:

    st.subheader(
        "📷 Emotion Detection"
    )

    st.write(
        "Upload a clear face image to analyze the "
        "detected facial emotion."
    )

    uploaded_file = st.file_uploader(
        "Choose an image",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )

    if uploaded_file is not None:

        image = Image.open(
            uploaded_file
        ).convert("RGB")

        # Display smaller image
        st.image(
            image,
            caption="Uploaded Image",
            width=300
        )

        analyze_button = st.button(
            "🔍 Analyze Emotion",
            use_container_width=True
        )

        if analyze_button:

            try:

                # Load model
                model = load_emotion_model()

                # Convert image to NumPy
                image_array = np.array(
                    image
                )

                # Convert RGB to BGR
                image_bgr = cv2.cvtColor(
                    image_array,
                    cv2.COLOR_RGB2BGR
                )

                # Convert to grayscale
                gray = cv2.cvtColor(
                    image_bgr,
                    cv2.COLOR_BGR2GRAY
                )

                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.3,
                    minNeighbors=5
                )

                if len(faces) == 0:

                    st.error(
                        "No face detected. "
                        "Please upload a clear front-facing face image."
                    )

                else:

                    # Use first detected face
                    x, y, w, h = faces[0]

                    face = gray[
                        y:y + h,
                        x:x + w
                    ]

                    # Resize to model input
                    face = cv2.resize(
                        face,
                        (48, 48)
                    )

                    # Normalize
                    face = face.astype(
                        "float32"
                    ) / 255.0

                    # Add dimensions
                    face = np.expand_dims(
                        face,
                        axis=0
                    )

                    face = np.expand_dims(
                        face,
                        axis=-1
                    )

                    # Prediction
                    prediction = model.predict(
                        face,
                        verbose=0
                    )[0]

                    emotion_index = int(
                        np.argmax(prediction)
                    )

                    emotion = emotion_labels[
                        emotion_index
                    ]

                    confidence = float(
                        prediction[
                            emotion_index
                        ] * 100
                    )

                    # Calculate score
                    score = calculate_wellness_score(
                        emotion
                    )

                    # Calculate risk
                    risk = calculate_risk(
                        score
                    )

                    # Save results in session
                    st.session_state.emotion = emotion

                    st.session_state.confidence = confidence

                    st.session_state.wellness_score = score

                    st.session_state.risk = risk

                    # Save analysis
                    saved = save_analysis_history(
                        st.session_state.username,
                        emotion,
                        confidence,
                        score,
                        risk
                    )

                    # Display results
                    st.success(
                        "Emotion analysis completed!"
                    )

                    st.markdown("### 🎯 Detection Result")

                    result_col1, result_col2 = st.columns(2)

                    with result_col1:

                        st.metric(
                            "Detected Emotion",
                            emotion
                        )

                    with result_col2:

                        st.metric(
                            "Confidence",
                            f"{confidence:.2f}%"
                        )

                    st.markdown("### 💚 Wellness Score")

                    st.progress(
                        score / 100
                    )

                    st.write(
                        f"**Wellness Score: "
                        f"{score}/100**"
                    )

                    # Risk card
                    if risk == "Low Risk":

                        st.markdown(
                            f"""
                            <div class="risk-card low-risk">
                            🟢 {risk}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    elif risk == "Moderate Risk":

                        st.markdown(
                            f"""
                            <div class="risk-card moderate-risk">
                            🟡 {risk}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    else:

                        st.markdown(
                            f"""
                            <div class="risk-card high-risk">
                            🔴 {risk}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # Recommendation
                    st.markdown(
                        "### 💡 Recommendation"
                    )

                    if emotion == "Happy":

                        st.success(
                            "Your detected expression is positive. "
                            "Continue activities that support your wellbeing."
                        )

                    elif emotion == "Neutral":

                        st.info(
                            "Your detected expression appears neutral. "
                            "Maintain healthy sleep, activity, and social habits."
                        )

                    elif emotion == "Sad":

                        st.warning(
                            "The detected expression appears sad. "
                            "Consider taking a break, talking with someone "
                            "you trust, or doing a relaxing activity."
                        )

                    elif emotion == "Fear":

                        st.warning(
                            "The detected expression may indicate fear. "
                            "Try slow breathing and a calm environment."
                        )

                    elif emotion == "Angry":

                        st.warning(
                            "The detected expression appears angry. "
                            "Taking a short break and practicing relaxation "
                            "may be helpful."
                        )

                    elif emotion == "Surprise":

                        st.info(
                            "The detected expression appears surprised. "
                            "Take a moment to identify what caused the reaction."
                        )

                    elif emotion == "Disgust":

                        st.warning(
                            "The detected expression appears to show disgust. "
                            "A calm environment and short break may help."
                        )

                    if saved:

                        st.caption(
                            "✓ Analysis saved to history."
                        )

                    else:

                        st.warning(
                            "Analysis completed, but history "
                            "could not be saved."
                        )

            except Exception as e:

                st.error(
                    "An error occurred while analyzing the image."
                )

                st.exception(e)


# ============================================================
# RIGHT COLUMN - CHATBOT
# ============================================================

with right_column:

    st.subheader(
        "🤖 AI Wellness Chatbot"
    )

    st.write(
        "Ask questions about emotions, stress, "
        "relaxation, sleep, or general wellbeing."
    )

    if st.session_state.emotion:

        st.info(
            f"Current detected emotion: "
            f"**{st.session_state.emotion}**"
        )

    else:

        st.info(
            "Upload and analyze a face image first "
            "to give the chatbot your detected emotion."
        )

    # Display chat history
    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # Chat input
    user_message = st.chat_input(
        "Ask your wellness question..."
    )

    if user_message:

        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        with st.chat_message("user"):

            st.markdown(
                user_message
            )

        # Get current emotion
        current_emotion = (
            st.session_state.get(
                "emotion",
                None
            )
        )

        # Generate chatbot response
        try:

            response = generate_response(
                user_message,
                current_emotion
            )

        except Exception:

            response = (
                "I'm sorry, I couldn't generate a response "
                "right now. Please try again."
            )

        # Display response
        with st.chat_message("assistant"):

            st.markdown(
                response
            )

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">

    <b>⚠️ Important Disclaimer</b><br><br>

    EmotionSense AI is an educational research prototype.
    Facial emotion detection only identifies observed expressions and cannot diagnose 
    mental-health conditions. Wellness scores are experimental indicators, 
    not medical diagnoses. For serious concerns, consult a qualified professional.

    </div>
    """,
    unsafe_allow_html=True
)