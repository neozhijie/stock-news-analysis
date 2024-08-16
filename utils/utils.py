import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import pandas as pd
import numpy as np
import json
import requests

def display_stock_charts(stock_history):
    # Prepare data
    df = stock_history.reset_index()
    df['time'] = df['Date'].dt.strftime('%Y-%m-%d')
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    
    COLOR_BULL = 'rgba(38,166,154,0.9)'
    COLOR_BEAR = 'rgba(239,83,80,0.9)'
    df['color'] = np.where(df['open'] > df['close'], COLOR_BEAR, COLOR_BULL)
    
    # Calculate MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    df['MACD'] = macd
    df['Signal'] = signal
    df['Histogram'] = hist

    # Prepare JSON data
    candles = json.loads(df[['time', 'open', 'high', 'low', 'close', 'color']].to_json(orient="records"))
    volume = json.loads(df[['time', 'volume']].rename(columns={"volume": "value"}).to_json(orient="records"))
    macd = json.loads(df[['time', 'MACD']].rename(columns={"MACD": "value"}).to_json(orient="records"))
    signal = json.loads(df[['time', 'Signal']].rename(columns={"Signal": "value"}).to_json(orient="records"))
    histogram = json.loads(df[['time', 'Histogram']].rename(columns={"Histogram": "value"}).to_json(orient="records"))

    # Line chart with volume options
    line_volume_options = {
        "height": 300,
        "rightPriceScale": {
            "scaleMargins": {"top": 0.2, "bottom": 0.25},
            "borderVisible": False,
        },
        "overlayPriceScales": {
            "scaleMargins": {"top": 0.7, "bottom": 0}
        },
        "layout": {
            "background": {"type": 'solid', "color": 'black'},
            "textColor": 'white',
        },
        "grid": {
            "vertLines": {"color": 'rgba(42, 46, 57, 0.1)'},
            "horzLines": {"color": 'rgba(42, 46, 57, 0.1)'}
        },
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'top',
            "color": 'white',
            "text": 'Stock Price',
        }
    }

    line_volume_series = [
        {
            "type": 'Area',
            "data": json.loads(df[['time', 'close']].rename(columns={"close": "value"}).to_json(orient="records")),
            "options": {
                "topColor": 'rgba(33, 150, 243, 0.56)',
                "bottomColor": 'rgba(33, 150, 243, 0.04)',
                "lineColor": 'rgba(33, 150, 243, 1)',
                "lineWidth": 2,
            }
        },
        {
            "type": 'Histogram',
            "data": volume,
            "options": {
                "color": 'rgba(76, 175, 80, 0.5)',
                "priceFormat": {"type": 'volume'},
                "priceScaleId": ""
            },
            "priceScale": {
                "scaleMargins": {"top": 0.7, "bottom": 0}
            }
        }
    ]

    # Multipane chart options
    candlestick_options = {
        "height": 300,
        "layout": {
            "background": {"type": "solid", "color": 'black'},
            "textColor": "white"
        },
        "grid": {
            "vertLines": {"color": "rgba(197, 203, 206, 0.5)"},
            "horzLines": {"color": "rgba(197, 203, 206, 0.5)"}
        },
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'top',
            "color": 'white',
            "text": 'Candlestick',
        }
    }

    volume_options = {
        "height": 100,
        "layout": {
            "background": {"type": 'solid', "color": 'black'},
            "textColor": 'white',
        },
        "grid": {
            "vertLines": {"color": 'rgba(42, 46, 57, 0)'},
            "horzLines": {"color": 'rgba(42, 46, 57, 0.6)'}
        },
        "timeScale": {"visible": False},
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'top',
            "color": 'white',
            "text": 'Volume',
        }
    }

    macd_options = {
        "height": 200,
        "layout": {
            "background": {"type": "solid", "color": 'black'},
            "textColor": "white"
        },
        "grid": {
            "vertLines": {"color": 'rgba(42, 46, 57, 0)'},
            "horzLines": {"color": 'rgba(42, 46, 57, 0.6)'}
        },
        "timeScale": {"visible": False},
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": 'left',
            "vertAlign": 'top',
            "color": 'white',
            "text": 'MACD',
        }
    }

    # Series configurations for multipane chart
    candlestick_series = [{
        "type": 'Candlestick',
        "data": candles,
        "options": {
            "upColor": COLOR_BULL,
            "downColor": COLOR_BEAR,
            "borderVisible": False,
            "wickUpColor": COLOR_BULL,
            "wickDownColor": COLOR_BEAR
        }
    }]

    volume_series = [{
        "type": 'Histogram',
        "data": volume,
        "options": {
            "priceFormat": {"type": 'volume'},
            "priceScaleId": ""
        },
        "priceScale": {
            "scaleMargins": {"top": 0, "bottom": 0},
            "alignLabels": False
        }
    }]

    macd_series = [
        {
            "type": 'Line',
            "data": macd,
            "options": {"color": 'orange', "lineWidth": 2}
        },
        {
            "type": 'Line',
            "data": signal,
            "options": {"color": 'rgba(33, 150, 243, 1)', "lineWidth": 2}
        },
        {
            "type": 'Histogram',
            "data": histogram,
            "options": {"color": 'red', "lineWidth": 1}
        }
    ]

    # Display charts
    renderLightweightCharts([
        {"chart": line_volume_options, "series": line_volume_series}
    ], 'lineVolume')

    renderLightweightCharts([
        {"chart": candlestick_options, "series": candlestick_series},
        {"chart": volume_options, "series": volume_series},
        {"chart": macd_options, "series": macd_series}
    ], 'multipane')
    
def get_sentiment_color(score):
    if score == 0:
        return "#808080"  # Grey
    elif -0.2 < score <= 0:
        return "#FFD700"  # Yellow
    elif -0.5 < score <= -0.2:
        return "#FFA500"  # Orange
    elif -1 <= score <= -0.5:
        return "#FF0000"  # Red
    elif 0 < score <= 0.2:
        return "#006400"  # Dark Green
    elif 0.2 < score <= 0.5:
        return "#008000"  # Green
    else:
        return "#00FF00"  # Bright Green
    

def chat(prompt):
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return response.json()['response']
    else:
        return "Error: Unable to generate analysis"
    
def calculate_bollinger_bands(data, window=20, num_std=2):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, lower_band


def color_metric(value, thresholds):
    if value < thresholds[0]:
        return "red"
    elif value < thresholds[1]:
        return "yellow"
    else:
        return "green"
    
def color_sharpe_ratio(value):
    thresholds = [0, 1, 2, 3]
    if value < thresholds[0]:
        return "red"  # Poor performance
    elif value < thresholds[1]:
        return "orange"  # Suboptimal performance
    elif value < thresholds[2]:
        return "yellow"  # Good performance
    elif value < thresholds[3]:
        return "light_green"  # Very good performance
    else:
        return "dark_green"  # Excellent performance
    
def safe_get(dictionary, key, default=None):
    return dictionary.get(key, default)
