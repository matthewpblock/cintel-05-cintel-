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
import plotly.express as px
from shinywidgets import render_plotly
from scipy import stats

#--------------------------------------------
# Set up the data generator
#--------------------------------------------
UPDATE_INTERVAL_SECS: int = 2
# Store the latest data up to the defined amount
DEQUE_SIZE: int = 7
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
        reactive.invalidate_later(UPDATE_INTERVAL_SECS)                 # Invalidates this calculation every UPDATE_INTERVAL_SECS to trigger updates
        temp = round(random.uniform(-21, -16), 1)                       # Gets random number between -21 and -16 C, rounded to 1 decimal place
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
    ui.input_dark_mode(mode="light")
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

# new row
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Most Recent Readings")
 
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)        # Use maximum width
            return render.DataGrid( df,width="100%")
    
 # new row
with ui.layout_columns():
    with ui.card(full_screen=True):
        ui.card_header("Chart and Current Trend")

        @render_plotly
        def display_plot():
            # Fetch from the reactive calc function
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()      # I'm curious why we list all three here, but only use df below

            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                # Convert the 'timestamp' column to datetime for better plotting
                df["timestamp"] = pd.to_datetime(df["timestamp"])

                # Create scatter plot for readings
                # pass in the df, the name of the x column, the name of the y column,
                # and more
            
                fig = px.scatter(df,                            # Dataframe to plot
                x="timestamp",                                  # Time on x-axis
                y="temp",                                       # Temperature on y-axis
                title="Temperature Readings with Regression Line",
                labels={"temp": "Temperature (°C)", "timestamp": "Time (local)"}, # Labels for the axes
                color_discrete_sequence=["blue"] )              # Color of the points

                # For x let's generate a sequence of integers from 0 to len(df)
                sequence = range(len(df))
                x_vals = list(sequence)
                y_vals = df["temp"]

                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df['best_fit_line'] = [slope * x + intercept for x in x_vals]

                # Add the regression line to the figure
                fig.add_scatter(x=df["timestamp"], y=df['best_fit_line'], mode='lines', name='Regression Line')

                # Update layout as needed to customize further
                fig.update_layout(xaxis_title="Time (local)",yaxis_title="Temperature (°C)")

            return fig
