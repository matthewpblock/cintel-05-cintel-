from collections import deque
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg

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