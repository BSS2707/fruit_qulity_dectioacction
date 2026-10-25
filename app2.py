import streamlit as st
from PIL import Image
import numpy as np
import sqlite3
import pandas as pd
import tensorflow as tf
import os

st.set_page_config(page_title="Fruit Quality Detector", layout="centered")

db = sqlite3.connect("fruit.db", check_same_thread=False)
c = db.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
email TEXT UNIQUE,
password TEXT)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS prediction(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
fruit TEXT,
condition TEXT,
accuracy REAL)
""")
db.commit()

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:

    st.title("Fruit Quality Detector")

    login, signup = st.tabs(["Login", "Sign Up"])

    with login:
        username = st.text_input("Username", key="lu")
        password = st.text_input("Password", type="password", key="lp")

        if st.button("Login"):
            c.execute(
                "SELECT id,username FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = c.fetchone()

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid username or password")

    with signup:
        username = st.text_input("Username", key="su")
        email = st.text_input("Email", key="se")
        password = st.text_input("Password", type="password", key="sp")

        if st.button("Sign Up"):
            if username and email and password:
                try:
                    c.execute(
                        "INSERT INTO users(username,email,password) VALUES(?,?,?)",
                        (username, email, password)
                    )
                    db.commit()
                    st.success("Account created. Please login.")
                except sqlite3.IntegrityError:
                    st.error("Username or email already exists")
            else:
                st.error("Fill all fields")

    st.stop()

user_id, username = st.session_state.user

st.sidebar.write(f"Welcome, {username}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

page = st.sidebar.radio("Menu", ["Prediction", "History"])

if page == "Prediction":

    if not os.path.exists("fruit_model.keras"):
        st.error("Model not found!")
        st.info("Please run train_model.py first.")
        st.stop()

    model = tf.keras.models.load_model("fruit_model.keras")

    classes = [
        "FreshApple",
        "RottenApple",
        "FreshBanana",
        "RottenBanana",
        "FreshOrange",
        "RottenOrange"
    ]

    st.title("Fruit Quality Detector")
    st.write("Upload a fruit image to detect fruit quality.")

    uploaded_file = st.file_uploader(
        "Upload Fruit Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Image", use_container_width=True)

        img = np.array(
            image.resize((64, 64)),
            dtype=np.float32
        ) / 255.0

        prediction = model.predict(
            np.expand_dims(img, axis=0),
            verbose=0
        )

        index = np.argmax(prediction)
        label = classes[index]
        confidence = float(prediction[0][index] * 100)

        if "Apple" in label:
            fruit = "Apple"
        elif "Banana" in label:
            fruit = "Banana"
        else:
            fruit = "Orange"

        condition = "Fresh" if "Fresh" in label else "Rotten"

        st.divider()
        st.subheader("Prediction Result")

        st.write("Fruit")
        st.success(fruit)

        st.write("Condition")
        if condition == "Fresh":
            st.success("Fresh")
        else:
            st.error("Rotten")

        st.write("Confidence")
        st.progress(min(confidence / 100, 1.0))
        st.write(f"**{confidence:.2f}%**")

        st.write("Safe to Eat?")
        if condition == "Fresh":
            st.success("Classified as Fresh by the model.")
        else:
            st.error("Classified as Rotten by the model.")

        c.execute(
            """
            INSERT INTO prediction(user_id,fruit,condition,accuracy)
            VALUES(?,?,?,?)
            """,
            (user_id, fruit, condition, confidence)
        )
        db.commit()

if page == "History":

    st.title(f"{username}'s Prediction History")

    history = pd.read_sql_query(
        """
        SELECT id,fruit,condition,accuracy
        FROM prediction
        WHERE user_id=?
        ORDER BY id DESC
        """,
        db,
        params=(user_id,)
    )

    if len(history):

        history["accuracy"] = history["accuracy"].round(2)

        history.columns = [
            "ID",
            "Fruit",
            "Condition",
            "Confidence (%)"
        ]

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total", len(history))
        col2.metric(
            "Fresh",
            len(history[history["Condition"] == "Fresh"])
        )
        col3.metric(
            "Rotten",
            len(history[history["Condition"] == "Rotten"])
        )

        if st.button("Clear My History"):
            c.execute(
                "DELETE FROM prediction WHERE user_id=?",
                (user_id,)
            )
            db.commit()
            st.rerun()

    else:
        st.info("No prediction history yet.")

st.divider()

st.caption(
    "Fruit Quality Detector | Python • TensorFlow • CNN • Streamlit • SQLite"
)