# --------------------------------------------
# Admin - Imports at the top
# --------------------------------------------
from collections import deque
from shiny import reactive, render
from shiny.express import ui, input
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
# Store the latest data up to the defined amount
DEQUE_SIZE: int = 60
# DEQUE_SIZE: int = input.deque_size()
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))

@reactive.calc()
def reactive_calc_combined():
        reactive.invalidate_later(input.update_interval())               # Invalidates this calculation by a variable amount of time defined by the input slider
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
ui.page_opts(title="Flying Penguin PyShiny Express Block: Live Data", fillable=False)    # Header
with ui.sidebar(open="open"):                                                           # Sidebar
    ui.input_dark_mode(mode="light")
    ui.h2("Flying Penguin Explorer", class_="text-center")
    ui.p(
        "A demonstration of real-time temperature readings by flying penguins.",
        class_="text-left",
    )
    ui.hr()
    # Input for the number of data points to display (deque length)
    ui.input_slider("chart_limit", "Number of data points:", min=1, max=60, value=15)
    
    # Input for the update interval in seconds
    ui.input_slider("update_interval", "Update Interval (seconds):", min=1, max=30, value=2)

    ui.hr()
    ui.p("Original requirements completed. Pending recommended enhancements.", class_="text-left")
    # Read the comments. Organize the code. When you get your version implemented, save it - use a good commit message to indicate you've recreated the functionality as requested. 

# Main content
#--------------------------------------------
with ui.layout_columns():
    with ui.value_box(
        showcase=icon_svg("person-skating"),
        theme="bg-gradient-cyan-pink",
    ):

        # Three inputs required for the value_box
        "Current Temperature"
        @render.text
        def display_temp():
            """Get the latest reading and return a temperature string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['temp']} C"
        "Too cold for me!"

    with ui.value_box(
        showcase=icon_svg("clock"),
        theme="bg-gradient-cyan-purple",
        ):
        "Current Date and Time"

        @render.text
        def display_time():
            """Get the latest reading and return a timestamp string"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            return f"{latest_dictionary_entry['timestamp']}"

# new row
with ui.layout_columns():
    with ui.card(height="250px"):
        ui.card_header("Most Recent Readings")
 
        @render.data_frame
        def display_df():
            """Get the latest reading and return a dataframe with current readings"""
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option('display.width', None)        # Use maximum width
            return render.DataGrid( df,width="100%")
    
 # new row
with ui.layout_columns():
    with ui.card(height="600px"):
        ui.card_header("Chart and Current Trend")

        @render_plotly
        def display_plot():
            # Fetch from the reactive calc function
            deque_snapshot, df, latest_dictionary_entry = reactive_calc_combined()      # I'm curious why we list all three here, but only use df below. Could the other two be removed?

            # Ensure the DataFrame is not empty before plotting
            if not df.empty:
                df_limited = df.tail(input.chart_limit()) # Limit the number of data points to display based on input slider

                # Convert the 'timestamp' column to datetime for better plotting
                df_limited["timestamp"] = pd.to_datetime(df_limited["timestamp"])

                # Create scatter plot for readings
                # pass in the df, the name of the x column, the name of the y column,
                # and more
            
                fig = px.scatter(df_limited,                            # Dataframe to plot
                x="timestamp",                                  # Time on x-axis
                y="temp",                                       # Temperature on y-axis
                title="Temperature Readings with Regression Line", height=500,
                labels={"temp": "Temperature (°C)", "timestamp": "Time (local)"}, # Labels for the axes
                color_discrete_sequence=["blue"] )              # Color of the points

                # Set the range for the y-axis 
                fig.update_yaxes(range=[-22, 0]) # Adjusts the range to keep a consistent y-axis including the zero line

                # For x let's generate a sequence of integers from 0 to len(df)
                sequence = range(len(df_limited))
                x_vals = list(sequence)
                y_vals = df_limited["temp"]

                slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
                df_limited['best_fit_line'] = [slope * x + intercept for x in x_vals]

                # Add the regression line to the figure
                fig.add_scatter(x=df_limited["timestamp"], y=df_limited['best_fit_line'], mode='lines', name='Regression Line')

                # Update layout as needed to customize further
                fig.update_layout(xaxis_title="Time (local)",yaxis_title="Temperature (°C)")

            return fig
