# import required modules
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from collections import deque
import re, subprocess
import numpy as np
import time
import serial

ser = serial.Serial(
        port='/dev/ttyACM0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

nSamples = 50

# define a function to get CPU temperature data
def check_HR(nSamples):
    HR = []
    pulse = []
    for i in range(nSamples):
        #if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        x = line.split(',')
        while len(x)!=3:      
            line = ser.readline().decode('utf-8').rstrip()
            x = line.split(',')
        HR.append(float(x[0]))
        pulse.append(float(x[2]))
    return HR, pulse

# X and Y axes will be managed with deque array queues, instead of simple arrays
X = deque(maxlen=1000)
X.extend(np.linspace(1,nSamples+1,nSamples))
Y = deque(maxlen=1000)
[HR, pulse] = check_HR(nSamples)                     
Y.extend(pulse)

# initialize Dash application
app = dash.Dash(__name__)

colors = {'background': '#111111',
          'text': '#7FDBFF'}

# define HTML layout and dcc component
app.layout = html.Div(style={'backgroundColor': colors['background']},
      children=[
    html.Div([
    html.H1('Heart Rate Trace', style={'textAlign': 'center', 'color':colors['text']}),
    dcc.Graph(id='live-graph1', figure={'layout':{
            'plot_bgcolor':colors['background'],
            'paper_bgcolor':colors['background'],
            'font':{'color':colors['text']}
            }}),#, animate=True),
    dcc.Interval(id="refresh1", interval=4 * 1000, n_intervals=0)]),
    html.Div([
    html.H1('Detail'),
    dcc.Graph(id='live-graph2', figure={'layout':{
            'plot_bgcolor':colors['background'],
            'paper_bgcolor':colors['background'],
            'font':{'color':colors['text']}
            }}),#, animate=True),
    dcc.Interval(id="refresh2", interval=2 * 1000, n_intervals=0)]),
    ]
)

# define a callback, which updates the graph
@app.callback(Output("live-graph1", "figure"), [Input("refresh1", "n_intervals")])

# define what to do on each update
def update1(n_intervals):
    #X.append(X[-1]+1)
    #Y.append(check_CPU_temp())
    X.extend(np.linspace(X[-1]+1, X[-1]+nSamples, nSamples))
    [HR, pulse] = check_HR(nSamples)                     
    Y.extend(pulse)
    data = go.Scatter(
            x=list(X),
            y=list(Y),
            name='Heart Rate Trace',
            showlegend=False,
            mode= 'lines+markers',
            marker= dict(color='#FFFFFF', size=2, line=dict(color='MediumPurple', width=1)),
            line= dict(color='#FF0000', width=7)
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[400,600]),
                                                plot_bgcolor=colors['background'],
                                                paper_bgcolor=colors['background'],
                                                font={'color':colors['text']})}

# define a callback, which updates the graph
@app.callback(Output("live-graph2", "figure"), [Input("refresh2", "n_intervals")])

# define what to do on each update
def update2(n_intervals):
    X2=list(X)[-nSamples:]
    Y2=list(Y)[-nSamples:]
    data = go.Scatter(
            x=X2,
            y=Y2,
            name='Trace Detail',
            showlegend=False,
            mode= 'lines+markers',
            marker= dict(color='#FFFFFF', size=2, line=dict(color='MediumPurple', width=5)),
            line= dict(color='#FF0000', width=15)
            )

    return {'data': [data],
            'layout' : go.Layout(xaxis=dict(range=[min(X2),max(X2)]),
                                                yaxis=dict(range=[min(Y), max(Y)]),
                                                plot_bgcolor=colors['background'],
                                                paper_bgcolor=colors['background'],
                                                font={'color':colors['text']})}

# main program, running the server and binding to external connections
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port='8050')