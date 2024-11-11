# --------------------------------------------
# Admin - Imports at the top
# --------------------------------------------
from collections import deque
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg
import pandas as pd

#--------------------------------------------
# Set up the data generator
#--------------------------------------------
UPDATE_INTERVAL_SECS: int = 2

DEQUE_SIZE: int = 7
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
        reactive.invalidate_later(UPDATE_INTERVAL_SECS)                 # Invalidates this calculation every UPDATE_INTERVAL_SECS to trigger updates
        temp = round(random.uniform(-18, -16), 1)                       # Gets random number between -18 and -16 C, rounded to 1 decimal place
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")        # Gets a timestamp in the format "YYYY-MM-DD HH:MM:SS"
        latest_dictionary_entry = {"temp": temp, "timestamp": timestamp} # Creates a dictionary entry with the temperature and timestamp
        reactive_value_wrapper.get().append(latest_dictionary_entry)    # Appends the latest dictionary entry to the deque
        deque_snapshot = reactive_value_wrapper.get()                   # Gets a snapshot of the deque
        df = pd.DataFrame(deque_snapshot)                               # Converts the deque to a pandas DataFrame
        
        return deque_snapshot, df, latest_dictionary_entry              # Return a tuple with everything we need every time we call this function

#--------------------------------------------
# Define the Shiny UI Page layout
#--------------------------------------------
ui.page_opts(title="Flying Penguin PyShiny Express Block: Live Data", fillable=True)    # Header
with ui.sidebar(open="open"):                                                           # Sidebar
    ui.h2("Flying Penguin Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings by flying penguins.",
        class_="text-left",
    )

#main content
#--------------------------------------------
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("person-skating"),
        theme="bg-gradient-blue-purple",
    ):

        # Three inputs required for the value_box
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"
        "Too cold for me!"

    with ui.card(full_screen=True):
        ui.card_header("Current Date and Time")

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"


with ui.layout_columns():
    with ui.card():
        ui.card_header("Current Data (placeholder only)")

with ui.layout_columns():
    with ui.card():
        ui.card_header("Current Chart (placeholder only)")
