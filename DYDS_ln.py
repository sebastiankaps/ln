import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import os

# Define the directory for storing user data
user_data_dir = "user_data"
os.makedirs(user_data_dir, exist_ok=True)

# Check if a user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "magic_word" not in st.session_state:
    st.session_state.magic_word = None
if "profile_setup" not in st.session_state:
    st.session_state.profile_setup = False
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {
        "values": [
            {"value": "freedom", "emoji": "💨", "question": "Did I spend my time self-directed today?", "weight": 1},
            {"value": "connection", "emoji": "🍄‍🟫", "question": "Did I invest into my relationships?", "weight": 2},
            {"value": "authenticity", "emoji": "💧", "question": "Did I connect with my queerness?", "weight": 1},
            {"value": "pleasure", "emoji": "✨", "question": "Did I experience joy or pleasure today?", "weight": 2},
            {"value": "sustainability", "emoji": "🍃", "question": "Was I kind to my body?", "weight": 2},
            {"value": "curiosity", "emoji": "☁️", "question": "Did I learn something new or explore something?", "weight": 1},
            {"value": "progress", "emoji": "🌱", "question": "Did I move closer to one of my dreams?", "weight": 3}
        ]
    }

# Initialize session state for toggles and data
if "toggles" not in st.session_state:
    st.session_state.toggles = {q["question"]: False for q in st.session_state.user_profile["values"]}
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Log", "Date", "Values", "Total Score", "Frequency"])

# Calculate value frequencies if data exists
value_counts = {v: 0 for v in ["freedom", "connection", "authenticity", "pleasure", "sustainability", "curiosity", "progress"]}
sorted_values = []

# Only include values that have been logged at least once
if not st.session_state.data.empty:
    for info in st.session_state.user_profile["values"]:
        value_counts[info["value"]] += st.session_state.data["Values"].str.count(info["emoji"]).sum()
    sorted_values = sorted([(v, count) for v, count in value_counts.items() if count > 0], key=lambda x: x[1], reverse=True)

# Display sorted emojis in a horizontal line for values that have been selected (only on the main page)
if sorted_values and not st.session_state.get("profile_setup", False):
    emoji_summary_html = "<div class='emoji-summary'>"
    for value, count in sorted_values:
        emoji = next(info["emoji"] for info in st.session_state.user_profile["values"] if info["value"] == value)
        size = max(16, count * 10 + 16)
        emoji_summary_html += f"<span style='font-size: {size}px;'>{emoji}</span>"
    emoji_summary_html += "</div>"
    st.markdown(emoji_summary_html, unsafe_allow_html=True)

# Display the login page if the user is not logged in
if not st.session_state.logged_in:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1c0b2d; /* Darker purple */
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("IS YOUR DAY SHIT?")
    st.write("Choose your magic word to find out...")

    # Use a sparkle emoji as the placeholder
    magic_word = st.text_input("🪄", placeholder="✨")

    if st.button("Open sesame"):
        if magic_word:
            st.session_state.magic_word = magic_word
            st.session_state.logged_in = True

            # Check if the user's log file exists
            user_csv_file_path = os.path.join(user_data_dir, f"{magic_word}_logs.csv")
            if not os.path.exists(user_csv_file_path):
                # If no log file exists for this user, direct them to the profile setup
                st.session_state.profile_setup = True

            st.experimental_rerun()
        else:
            st.error("Please enter a magic word to continue.")

# Main app logic
if st.session_state.logged_in and st.session_state.magic_word:
    magic_word = st.session_state.magic_word
    user_csv_file_path = os.path.join(user_data_dir, f"{magic_word}_logs.csv")

    if os.path.exists(user_csv_file_path):
        st.session_state.data = pd.read_csv(user_csv_file_path)

    # Redirect to the profile setup page if the flag is set
    if st.session_state.profile_setup:
        st.title("What do you actually want?")
        st.write("Enter your personal 7 values and corresponding daily questions.")

        nature_emojis = [
            "💨", "🍄‍🟫", "💧", "✨", "🍃", "☁️", "🌱", "🌊", "🔥", "🌳", "🏔️", "🍁", "🌟", 
            "🌿", "🌵", "🪨", "🍂", "🪴", "🌄", "🌍", "🍀", "🪶", "🌌", "☀️", "🌕", "🌙", 
            "💫", "🌈", "🌪️", "🌋", "🏝️", "🏞️", "🌺", "🌀", "🏜️", "🏕️", "🪵", "🌌", "🌻",
            "💐", "🌾", "🪁", "🏵️", "⚡", "🪄", "🧊", "🛤️", "🌠", "💦", "🌬️", "🌲",
            "🏔️", "🌿", "🌴", "🏝️", "🏞️", "💎", "🌸", "🏕️", "🧂", "🪵"
        ]

        for i in range(7):
            with st.container():
                st.markdown("<div class='value-block'>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    value = st.text_input(f"Value {i+1}", st.session_state.user_profile["values"][i]["value"], key=f"value_{i}")
                with col2:
                    emoji_choice = st.selectbox("Symbol", nature_emojis, index=nature_emojis.index(st.session_state.user_profile["values"][i]["emoji"]), key=f"emoji_{i}")
                with col3:
                    weight = st.slider("Importance", 1, 3, st.session_state.user_profile["values"][i]["weight"], key=f"weight_{i}")

                question = st.text_input(
                    f"Daily question regarding {value}",
                    st.session_state.user_profile["values"][i]["question"],
                    key=f"question_{i}"
                )
                st.markdown("</div>", unsafe_allow_html=True)

                st.session_state.user_profile["values"][i] = {
                    "value": value,
                    "emoji": emoji_choice,
                    "question": question,
                    "weight": weight
                }

        if st.button("Internalize values"):
            st.session_state.profile_setup = False
            st.success("Profile updated successfully!")
            st.experimental_rerun()
    else:
        st.title("DID I HAVE A SHIT DAY?")

        questions = {
            entry["question"]: {
                "weight": entry["weight"],
                "value": entry["value"],
                "emoji": entry["emoji"]
            }
            for entry in st.session_state.user_profile["values"]
        }

        # Display questions as buttons
        responses = {}
        for question, info in questions.items():
            col1, col2 = st.columns([9, 1])
            with col1:
                if st.button(f"{info['emoji']} &nbsp; {question}", key=question):
                    st.session_state.toggles[question] = not st.session_state.toggles[question]
            with col2:
                emoji_display = "🌟" if st.session_state.toggles[question] else "⭐"
                col2.markdown(f"<span class='circle-emoji'>{emoji_display}</span>", unsafe_allow_html=True)
            responses[question] = st.session_state.toggles[question]

        # Calculate the total score for today's responses
        total_score = sum(info["weight"] for q, info in questions.items() if responses[q])
        total_aura_collected = st.session_state.data["Total Score"].sum()

        # Display Today's Aura
        st.markdown(f"<div class='aura-display' style='color: orange; font-weight: bold;'>Today's Aura: +{total_score}</div>", unsafe_allow_html=True)

        # Button to submit today's log
        if st.button("Not so shit ain't it"):
            emojis = "".join([info["emoji"] for q, info in questions.items() if responses[q]])
            visual_score = "🟠" * total_score + "⚪️" * (12 - total_score)
            log_entry = len(st.session_state.data) + 1
            entry = {"Log": log_entry, "Date": date.today(), "Values": emojis, "Total Score": total_score, "Frequency": visual_score}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([entry])], ignore_index=True)
            st.success("Another day, another slay!")
            st.session_state.toggles = {q: False for q in questions}
            st.experimental_rerun()

        # Display logs
        st.write("### My Life")
        st.dataframe(st.session_state.data[["Date", "Values", "Total Score", "Frequency"]])

        # Display My Priorities
        if sorted_values:
            st.write("### My Priorities")
            for value, count in sorted_values:
                emoji = next(info["emoji"] for info in st.session_state.user_profile["values"] if info["value"] == value)
                st.write(f"{emoji} {value} {emoji}")

        # Display frequency chart
        st.write("### My Frequency")
        chart_data = st.session_state.data[["Date", "Total Score"]].copy()
        chart_data["Date"] = pd.to_datetime(chart_data["Date"])
        combined_chart = alt.layer(
            alt.Chart(chart_data).mark_line(color='orange').encode(
                x='Date:T',
                y='Total Score:Q'
            ),
            alt.Chart(pd.DataFrame({"y": [chart_data["Total Score"].mean()]})).mark_rule(color='red').encode(y='y:Q')
        ).configure_axis(grid=False, labelColor='white', titleColor='white')
        st.altair_chart(combined_chart, use_container_width=True)

        # Display Total Aura Collected
        st.markdown(f"<div class='aura-display' style='color: orange; font-weight: bold;'>Total Aura Collected: +{total_aura_collected}</div>", unsafe_allow_html=True)

        # Button to go to the profile edit page
        if st.button("Reconsider values"):
            st.session_state.profile_setup = True
            st.experimental_rerun()
