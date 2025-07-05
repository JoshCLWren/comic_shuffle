import json
import random
import streamlit as st

READING_ORDER_FILE_PATH = "reading_orders.json"

def get_reading_order():
    with open(READING_ORDER_FILE_PATH, "r") as f:
        return json.load(f)

def save_reading_order(data):
    with open(READING_ORDER_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_next_unread(reading_order):
    weighted_candidates = []

    for group in reading_order["comics"]:
        unread_entries = [entry for entry in group["entries"] if entry["status"] != "read"]

        if unread_entries:
            weight = 1 / len(unread_entries)  # shorter runs = higher weight
            for entry in unread_entries:
                weighted_candidates.append((group["label"], entry, group, weight))

    if not weighted_candidates:
        return None

    labels, entries, groups, weights = zip(*weighted_candidates)
    index = random.choices(range(len(entries)), weights=weights, k=1)[0]

    return labels[index], entries[index], groups[index]

def mark_as_read(group, comic):
    for entry in group["entries"]:
        if entry["comic"] == comic:
            entry["status"] = "read"
            return

# Streamlit UI
st.title("📚 Comic Shuffle")

reading_data = get_reading_order()

if "last_pick" not in st.session_state:
    st.session_state.last_pick = None

if st.button("🎲 Shuffle Comic"):
    result = get_next_unread(reading_data)
    if result:
        label, entry, group = result
        st.session_state.last_pick = {
            "label": label,
            "comic": entry["comic"]
        }
    else:
        st.warning("You've read everything! 🎉")

if st.session_state.last_pick:
    comic = st.session_state.last_pick["comic"]
    label = st.session_state.last_pick["label"]
    st.success(f"Next up: **{comic}** from _{label}_")

    if st.button("✅ Mark as Read"):
        for group in reading_data["comics"]:
            if group["label"] == label:
                mark_as_read(group, comic)
                save_reading_order(reading_data)
                st.success(f"Marked {comic} as read ✅")
                st.session_state.last_pick = None
                st.rerun()