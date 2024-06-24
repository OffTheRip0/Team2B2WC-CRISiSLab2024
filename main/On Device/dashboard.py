import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
from collections import deque
import serial
import threading
import time
from emailsender import *
import discordWebhook

# Initialize serial communication
ser = serial.Serial('COM9', 115200, timeout=1)
ser2 = serial.Serial('COM11', 9600, timeout=1)

# Setup
app = dash.Dash(__name__)
app.title = "2B2WC Dashboard"
max_length = 50
data_frequency = 100
threshold = 100
y_data = deque(maxlen=max_length)
raw_pressure_data = deque(maxlen=max_length)
x_data = deque(maxlen=max_length)
temperature = 0
average_water_height = None
triggered_time = 1704020400
air_pressure = 1015

# Function to reset data arrays
def reset_data_arrays():
    global y_data, raw_pressure_data, x_data
    y_data = deque(maxlen=max_length)
    raw_pressure_data = deque(maxlen=max_length)
    x_data = deque(maxlen=max_length)
    for i in range(max_length):
        y_data.append(0)
        raw_pressure_data.append(0)
        x_data.append(i)

# Initialize the data with zeros
reset_data_arrays()

# Function to read data from serial port asynchronously
def read_serial():
    global y_data, x_data, temperature, triggered_time, raw_pressure_data, air_pressure
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.startswith("t: "):
                try:
                    # Here we do some parsing and setting variables and arrays
                    parts = line.split('\t\t')
                    temp_str = parts[0].split(": ")[1]
                    pressure_str = parts[1].split(": ")[1]

                    temperature = float(temp_str)
                    pressure1 = float(pressure_str) - air_pressure
                    pressure = pressure1
                    # Update data
                    y_data.append(pressure)
                    raw_pressure_data.append(float(pressure_str))
                    x_data.append(x_data[-1] + 1)
                    current_time = time.time()
                    # Check threshold and cooldown time
                    if pressure >= threshold and (current_time > (triggered_time+20)):
                        triggered_time = time.time()
                        ser2_output = "TRIGGERED"
                        ser2.write(ser2_output.encode())
                        discordWebhook.send(pressure)
                        trigger(pressure)
                        print(ser2.readline().decode('utf-8', errors='ignore').strip())

                except (IndexError, ValueError) as e:
                    print(f"Error parsing line: {line} - {e}")

# Start a separate thread for reading serial data (so it can let the rest of the code run while being in a loop)
serial_thread = threading.Thread(target=read_serial)
serial_thread.daemon = True
serial_thread.start()

# Layout of the app, html and css
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                dcc.Graph(id="live-graph", config={'displayModeBar': False},),
                dcc.Graph(id="raw-pressure-graph", config={'displayModeBar': False}),
                html.Div(id='main-div',
                    children=[
                        html.Div(id="max-value"),
                        html.Div(id="temp-value"),
                        html.Div(id="current-value"),
                        dcc.Input(
                            id="threshold-input",
                            type="number",
                            placeholder="Enter threshold value",
                            style={'margin-top': '20px', 'border': 'none'}
                        ),
                        html.Button('Set Air Pressure', id='calibrate-button')
                    ],
                    style={'display': 'flex', 'flex-direction': 'column', 'margin-left': '10px'}
                ),
            ],
            style={'display': 'flex', 'flex-direction': 'row', 'align-items': 'flex-start', 'margin-top': '0'}
        ),
        dcc.Interval(
            id="interval-component",
            interval=data_frequency,
            n_intervals=0
        )
    ],
    style={'height': '100vh', 'display': 'flex', 'flex-direction': 'column', 'justify-content': 'flex-start', 'margin-top': '0'}
)
# Callback to update the values
@app.callback(
    [Output("live-graph", "figure"),
     Output("raw-pressure-graph", "figure"),
     Output("max-value", "children"),
     Output("current-value", "children"),
     Output("temp-value", "children")],
    [Input("interval-component", "n_intervals"),
     State("threshold-input", "value")]
)
def update_graph_live(n_intervals, threshold_value):
    global threshold, temperature, average_water_height

    # Calculate average water height for the first 50 data points.
    if average_water_height is None and len(y_data) >= max_length:
        time.sleep(5)
        average_water_height = sum(y_data) / max_length
    print(average_water_height)

    # Sets threshold in relation to average water height
    if threshold_value is not None:
        threshold = threshold_value + average_water_height
        print(threshold)

    # Data for the first graph
    data = go.Scatter(
        x=list(x_data),
        y=list(y_data),
        mode='lines',
        line=dict(color='aqua'),
        fill='tozeroy',
        name='Water Height'
    )

    # Data for the second graph (raw pressure)
    raw_pressure = go.Scatter(
        x=list(x_data),
        y=list(raw_pressure_data),
        mode='lines',
        line=dict(color='green'),
        fill='tozeroy',
        name='Raw Pressure'
    )

    # Threshold Line
    red_line = go.Scatter(
        x=list(x_data),
        y=[threshold] * len(x_data),
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Threshold'
    )

    # Building Graph Layout for the first graph
    layout = go.Layout(
        plot_bgcolor='#131313',
        paper_bgcolor='#131313',
        font=dict(color='white'),
        xaxis=dict(range=[x_data[0], x_data[-1]], gridcolor='#262626', showticklabels=False),
        yaxis=dict(range=[min(y_data) - 5, max(y_data) + 5], gridcolor='#262626'),
        title="Water Height (cm)",
    )

    # Building Graph Layout for the second graph
    layout_raw = go.Layout(
        plot_bgcolor='#131313',
        paper_bgcolor='#131313',
        font=dict(color='white'),
        xaxis=dict(range=[x_data[0], x_data[-1]], gridcolor='#262626', showticklabels=False),
        yaxis=dict(range=[min(raw_pressure_data) - 5, max(raw_pressure_data) + 5], gridcolor='#262626'),
        title="Raw Pressure Data (hpa)",
    )

    return {
        "data": [data, red_line],
        "layout": layout
    }, {
        "data": [raw_pressure],
        "layout": layout_raw
    }, f"Max Height: {round(max(y_data),3)}cm", f"Temperature: {temperature}°C", f"Current Height: {round((y_data[-1]),3)}cm"

# Callback to update air_pressure when calibrate-button is clicked
@app.callback(
    Output('calibrate-button', 'n_clicks'),
    Input('calibrate-button', 'n_clicks'),
)
def calibrate_air_pressure(n_clicks):
    global air_pressure
    if n_clicks is not None and len(raw_pressure_data) > 0:
        air_pressure = raw_pressure_data[-1]
        print(f"Calibrated air pressure: {air_pressure}")
    return None  # Return None to reset the n_clicks to 0

if __name__ == '__main__':
    app.run_server(debug=False)
