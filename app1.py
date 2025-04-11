# pomodoro_timer.py
import streamlit as st
import time
import datetime

# --- Configuration (Default Values) ---
DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK_MINUTES = 5
DEFAULT_LONG_BREAK_MINUTES = 15
POMODOROS_BEFORE_LONG_BREAK = 4

# --- Session State Initialization ---
# Use session state to preserve variables across reruns
def initialize_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.timer_running = False
        st.session_state.current_mode = "Work"  # Initial mode
        # Store durations in seconds
        st.session_state.work_duration = DEFAULT_WORK_MINUTES * 60
        st.session_state.short_break_duration = DEFAULT_SHORT_BREAK_MINUTES * 60
        st.session_state.long_break_duration = DEFAULT_LONG_BREAK_MINUTES * 60
        st.session_state.pomodoros_completed = 0
        # Set initial remaining time based on the starting mode
        st.session_state.remaining_time = st.session_state.work_duration
        # print("State Initialized") # For debugging

# Ensure state is initialized only once
initialize_state()

# --- Helper Functions ---
def format_time(seconds):
    """Formats seconds into MM:SS or HH:MM:SS"""
    return str(datetime.timedelta(seconds=int(seconds)))

def switch_mode():
    """Switches the timer mode based on Pomodoro rules."""
    current_mode = st.session_state.current_mode
    pomodoros_completed = st.session_state.pomodoros_completed

    if current_mode == "Work":
        st.session_state.pomodoros_completed += 1
        pomodoros_completed += 1 # Use updated value for check
        if pomodoros_completed % POMODOROS_BEFORE_LONG_BREAK == 0:
            st.session_state.current_mode = "Long Break"
            st.session_state.remaining_time = st.session_state.long_break_duration
            st.toast(f"Pomodoro {pomodoros_completed} done! Time for a long break.", icon="🎉")
        else:
            st.session_state.current_mode = "Short Break"
            st.session_state.remaining_time = st.session_state.short_break_duration
            st.toast(f"Pomodoro {pomodoros_completed} done! Time for a short break.", icon="👍")
    else:  # If current mode is Short Break or Long Break
        st.session_state.current_mode = "Work"
        st.session_state.remaining_time = st.session_state.work_duration
        st.toast("Break's over! Back to work.", icon="💪")

    st.session_state.timer_running = False # Stop timer automatically when mode switches

def start_timer():
    """Starts the timer if time is remaining."""
    if st.session_state.remaining_time > 0:
        st.session_state.timer_running = True
        # print("Timer Started") # For debugging

def pause_timer():
    """Pauses the timer."""
    st.session_state.timer_running = False
    # print("Timer Paused") # For debugging

def reset_current_timer():
    """Resets the timer to the beginning of the current mode."""
    st.session_state.timer_running = False
    mode = st.session_state.current_mode
    if mode == "Work":
        st.session_state.remaining_time = st.session_state.work_duration
    elif mode == "Short Break":
        st.session_state.remaining_time = st.session_state.short_break_duration
    elif mode == "Long Break":
        st.session_state.remaining_time = st.session_state.long_break_duration
    # print("Current Timer Reset") # For debugging

def reset_cycle():
     """Resets the entire pomodoro cycle and count."""
     st.session_state.timer_running = False
     st.session_state.current_mode = "Work"
     st.session_state.remaining_time = st.session_state.work_duration
     st.session_state.pomodoros_completed = 0
     st.toast("Pomodoro cycle reset.")
     # print("Full Cycle Reset") # For debugging


# --- UI Layout ---
st.set_page_config(page_title="Pomodoro Timer", layout="centered")

st.title("🍅 Pomodoro Timer")

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("⚙️ Settings")

    work_minutes = st.number_input(
        "Work Duration (minutes)",
        min_value=1,
        value=st.session_state.work_duration // 60, # Display in minutes
        step=5,
        key="work_min_input" # Use key to prevent issues with state updates
    )
    short_break_minutes = st.number_input(
        "Short Break Duration (minutes)",
        min_value=1,
        value=st.session_state.short_break_duration // 60,
        step=1,
        key="short_break_min_input"
    )
    long_break_minutes = st.number_input(
        "Long Break Duration (minutes)",
        min_value=1,
        value=st.session_state.long_break_duration // 60,
        step=5,
        key="long_break_min_input"
    )

    # Apply settings button - updates state and resets *current* timer
    if st.button("Apply Settings & Reset Current Timer"):
        st.session_state.work_duration = work_minutes * 60
        st.session_state.short_break_duration = short_break_minutes * 60
        st.session_state.long_break_duration = long_break_minutes * 60
        reset_current_timer() # Reset to apply new duration if it's the current mode
        st.success("Settings applied. Current timer phase reset.")
        time.sleep(1) # Give user time to see message
        st.rerun() # Rerun to reflect changes immediately

    st.divider()
    st.button("Reset Full Pomodoro Cycle", on_click=reset_cycle, key="reset_full_cycle", help="Resets the timer to the first work phase and sets completed Pomodoros to 0.")

# --- Main Timer Display ---

# Display current mode and pomodoros completed
mode_color = "red" if st.session_state.current_mode == "Work" else "green"
st.header(f"Current Mode: :{mode_color}[{st.session_state.current_mode}]")
st.metric(label="Pomodoros Completed", value=st.session_state.pomodoros_completed)

# --- Timer Display Placeholder ---
# Use a placeholder to update the time without rewriting other elements
timer_placeholder = st.empty()
timer_placeholder.markdown(f"<h1 style='text-align: center; font-size: 6em;'>{format_time(st.session_state.remaining_time)}</h1>", unsafe_allow_html=True)

# --- Control Buttons ---
# Arrange buttons horizontally
col1, col2, col3 = st.columns(3)

with col1:
    if not st.session_state.timer_running:
        st.button("▶️ Start", on_click=start_timer, key="start", use_container_width=True, type="primary", disabled=(st.session_state.remaining_time <= 0))
    else:
        st.button("⏸️ Pause", on_click=pause_timer, key="pause", use_container_width=True)

with col2:
    st.button("🔄 Reset Phase", on_click=reset_current_timer, key="reset", use_container_width=True, help="Resets the timer to the start of the current Work/Break phase.")

with col3:
     # Add a skip button only when timer might be running or paused
     st.button("⏩ Skip Phase", on_click=switch_mode, key="skip", use_container_width=True, type="secondary", help="Finish current phase immediately and move to the next.")


# --- Timer Logic Loop ---
# This part runs only when the timer is active
if st.session_state.timer_running:
    while st.session_state.remaining_time > 0 and st.session_state.timer_running:
        # Update display in the placeholder
        timer_placeholder.markdown(f"<h1 style='text-align: center; font-size: 6em;'>{format_time(st.session_state.remaining_time)}</h1>", unsafe_allow_html=True)

        # Decrement time
        st.session_state.remaining_time -= 1

        # Wait for 1 second - This is the core timing mechanism
        time.sleep(1)

        # Need to rerun to check button states and update the display loop
        # Check if timer was stopped by pause/reset button during sleep
        if not st.session_state.timer_running:
            break

    # After the loop (timer finished or was stopped)
    # Ensure final display is accurate
    timer_placeholder.markdown(f"<h1 style='text-align: center; font-size: 6em;'>{format_time(st.session_state.remaining_time)}</h1>", unsafe_allow_html=True)

    # --- Handle Timer Finish ---
    # Check if timer actually finished naturally (wasn't paused/reset)
    if st.session_state.remaining_time <= 0 and st.session_state.timer_running:
        # Timer has reached zero
        # Optional: Add sound alert here if desired (requires more setup)
        # st.audio("path/to/alert.wav") # Example

        switch_mode() # Switch to the next mode
        st.rerun() # Rerun immediately to show the new mode and reset timer display

# --- Instructions / Footer ---
st.divider()
st.markdown("""
**How to Use:**
1.  Adjust durations in the sidebar (optional). Click 'Apply Settings' to save.
2.  Click 'Start' to begin the timer.
3.  Use 'Pause' to temporarily stop, and 'Start' again to resume.
4.  'Reset Phase' restarts the *current* work or break period.
5.  'Skip Phase' ends the current period and moves to the next one.
6.  'Reset Full Pomodoro Cycle' in the sidebar restarts the entire cycle count.
""")

# --- Debugging (Optional) ---
# Uncomment to see session state changes
# st.sidebar.divider()
# st.sidebar.write("Debug Info:")
# st.sidebar.json(st.session_state)