import json
import random
import streamlit as st
from pathlib import Path
import shutil
from datetime import datetime

READING_ORDER_FILE_PATH = Path("reading_orders.json")

def get_reading_order():
    """Load reading order with basic error handling"""
    try:
        with open(READING_ORDER_FILE_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Reading order file not found: {READING_ORDER_FILE_PATH}")
        return {"comics": []}
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON in reading order file: {e}")
        return {"comics": []}
    except Exception as e:
        st.error(f"Error loading reading order: {e}")
        return {"comics": []}

def save_reading_order(data):
    """Save reading order with backup"""
    try:
        # Create backup before saving
        if READING_ORDER_FILE_PATH.exists():
            backup_path = READING_ORDER_FILE_PATH.with_suffix('.json.bak')
            shutil.copy2(READING_ORDER_FILE_PATH, backup_path)
        
        # Write to temporary file first
        temp_path = READING_ORDER_FILE_PATH.with_suffix('.json.tmp')
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        
        # Atomic rename
        temp_path.replace(READING_ORDER_FILE_PATH)
        return True
    except Exception as e:
        st.error(f"Error saving reading order: {e}")
        return False

def get_next_unread(reading_order):
    """Select next comic with weighting that favors longer series"""
    weighted_candidates = []

    for group in reading_order["comics"]:
        unread_entries = [entry for entry in group["entries"] if entry["status"] != "read"]

        if unread_entries:
            # Favor longer series - more unread comics = higher weight
            base_weight = len(unread_entries)
            
            # Category adjustments
            if group.get("category") == "main":
                weight = base_weight * 2.0  # Double weight for main storyline
            elif group.get("category") == "side_quest":
                weight = base_weight * 1.0  # Normal weight for side quests
            else:  # one_off
                weight = base_weight * 0.3  # Lower weight for one-offs
            
            for entry in unread_entries:
                weighted_candidates.append((group["label"], entry, group, weight))

    if not weighted_candidates:
        return None

    labels, entries, groups, weights = zip(*weighted_candidates)
    
    # Add small random variation to prevent deterministic patterns
    weights = [w * random.uniform(0.9, 1.1) for w in weights]
    
    index = random.choices(range(len(entries)), weights=weights, k=1)[0]

    return labels[index], entries[index], groups[index]

def mark_as_read(group, comic):
    """Mark comic as read with timestamp"""
    for entry in group["entries"]:
        if entry["comic"] == comic:
            entry["status"] = "read"
            entry["read_date"] = datetime.now().isoformat()
            return True
    return False

# Streamlit UI
st.title("📚 Comic Shuffle")

reading_data = get_reading_order()

if not reading_data["comics"]:
    st.error("No comics data available!")
    st.stop()

if "last_pick" not in st.session_state:
    st.session_state.last_pick = None

# Show basic stats in sidebar
with st.sidebar:
    st.header("📊 Progress")
    
    # Calculate totals
    total_comics = sum(len(group["entries"]) for group in reading_data["comics"])
    read_comics = sum(1 for group in reading_data["comics"] 
                     for entry in group["entries"] 
                     if entry["status"] == "read")
    
    if total_comics > 0:
        progress = read_comics / total_comics
        st.metric("Overall", f"{read_comics}/{total_comics}", f"{progress*100:.1f}%")
        st.progress(progress)
    
    # Show unread counts by category
    st.subheader("Unread by Category")
    category_stats = {}
    for group in reading_data["comics"]:
        category = group.get("category", "unknown")
        unread = sum(1 for entry in group["entries"] if entry["status"] != "read")
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += unread
    
    for category, count in sorted(category_stats.items()):
        if count > 0:
            st.write(f"**{category}**: {count}")

# Main shuffle interface
if st.button("🎲 Shuffle Comic", type="primary", use_container_width=True):
    result = get_next_unread(reading_data)
    if result:
        label, entry, group = result
        st.session_state.last_pick = {
            "label": label,
            "comic": entry["comic"],
            "category": group.get("category", "unknown"),
            "format": group.get("format", "unknown")
        }
    else:
        st.warning("You've read everything! 🎉")

if st.session_state.last_pick:
    comic = st.session_state.last_pick["comic"]
    label = st.session_state.last_pick["label"]
    
    # Display selection with more info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"### Next up: **{comic}**")
        st.info(f"From: _{label}_ | {st.session_state.last_pick['category']} | {st.session_state.last_pick['format']}")
    
    # Action buttons
    col_read, col_skip = st.columns(2)
    
    with col_read:
        if st.button("✅ Mark as Read", use_container_width=True):
            for group in reading_data["comics"]:
                if group["label"] == label:
                    if mark_as_read(group, comic):
                        if save_reading_order(reading_data):
                            st.success(f"Marked {comic} as read ✅")
                            st.session_state.last_pick = None
                            st.rerun()
                        else:
                            st.error("Failed to save progress")
                    break
    
    with col_skip:
        if st.button("⏭️ Skip for Now", use_container_width=True):
            st.session_state.last_pick = None
            st.rerun()