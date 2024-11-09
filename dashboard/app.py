from collections import deque
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg

# --------------------------------------------
# SET UP THE REACTIVE CONTENT
# --------------------------------------------
#set a constant UPDATE INTERVAL for all live data
UPDATE_INTERVAL_SECS: int = 1

# Initialize a REACTIVE CALC that our display components can call
@reactive.calc()
def reactive_calc_combined():
        reactive.invalidate_later(UPDATE_INTERVAL_SECS) # Invalidates this calculation every UPDATE_INTERVAL_SECS to trigger updates
        temp = round(random.uniform(-18, -16), 1) # Gets random number between -18 and -16 C, rounded to 1 decimal place
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Gets a timestamp in the format "YYYY-MM-DD HH:MM:SS"
        latest_dictionary_entry = {"temp": temp, "timestamp": timestamp}
        
        return latest_dictionary_entry #Displays the results

# ------------------------------------------------
# Define the Shiny UI Page layout 
# ------------------------------------------------
ui.page_opts(title="Flying Penguin PyShiny Express Block: Live Data (Basic)", fillable=True) # Header
with ui.sidebar(open="open"): # Sidebar
    ui.h2("Flying Penguin Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings by flying penguins.",
        class_="text-center",
    )

ui.h2("Current Temperature")
@render.text
def display_temp():
    """Get the latest reading and return a temperature string"""
    latest_dictionary_entry = reactive_calc_combined()
    return f"{latest_dictionary_entry['temp']} C"
icon_svg("person-skating")
ui.p("Too cold for me!")

ui.hr() # Horizontal line

ui.h2("Current Date and Time")
@render.text
def display_time():
    """Get the latest reading and return a timestamp string"""
    latest_dictionary_entry = reactive_calc_combined()
    return f"{latest_dictionary_entry['timestamp']}"