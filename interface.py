import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from tools.stock import Stock
from tools.processor import ProcessorFactory
from utils.utils import display_stock_charts, get_sentiment_color, calculate_bollinger_bands, color_metric, safe_get, color_sharpe_ratio
import json

def main():
    st.set_page_config(layout="wide", page_title="Stock Analysis Dashboard")
    
    # Custom CSS for improved styling
    st.markdown("""
    <style>
    .news-container {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 10px;
    }
    .news-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        height: 80px;
        overflow: hidden;
        display: flex;
        align-items: center;
    }
    .news-card .sentiment-score {
        font-size: 1.4rem;
        font-weight: bold;
        width: 80px;
        text-align: center;
        flex-shrink: 0;
    }
    .news-card .title-container {
        flex-grow: 1;
        overflow: hidden;
        margin-left: 10px;
    }
    .news-card .title {
        font-size: 0.9rem;
        line-height: 1.2;
        max-height: 3.6em;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }

    .news-card a {
        color: white;
        text-decoration: none;
    }
    .news-card a:hover {
        text-decoration: underline;
        opacity: 0.8;
    }
    .sentiment-border {
        border-left-width: 25px;
        border-left-style: solid;
    }
    </style>
    """, unsafe_allow_html=True)


    st.title("Stock Analysis Dashboard")

    # User input for ticker symbol
    ticker = st.text_input("Enter a stock ticker symbol (e.g., AAPL):", "")

    if st.button("Analyze", key="analyze_button"):
        try:
            # Create Stock object
            stock = Stock(ticker)

            # Create processors
            stock_info_processor = ProcessorFactory.get_processor("stock_info")
            news_processor = ProcessorFactory.get_processor("news")
            stock_history_processor = ProcessorFactory.get_processor("stock_history")

            # Tabs for different analyses
            tabs = st.tabs([ "Stock & Company Information", "Stock Price Analysis & Charts", "News Analysis"])

            with tabs[0]:
                with st.spinner("Processing stock information..."):
                    st.header("Stock & Company Information")
                    stock_info = stock.get_info()
                    data = stock_info_processor.process(stock_info)
                    
                    st.title(f"{safe_get(data, 'company_name', 'Company')} ({safe_get(data, 'symbol', 'Symbol')}) Dashboard")
                    
                    # Company Overview
                    st.header("Company Overview")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"${safe_get(data, 'current_price', 0):.2f}")
                    with col2:
                        st.metric("Market Cap", f"${safe_get(data, 'market_cap', 0):,.0f}")
                    with col3:
                        st.metric("Recommendation", safe_get(data, 'recommendation', 'N/A').upper())

                    # Stock Performance
                    st.header("Stock Performance")
                    fig = go.Figure()
                    current_price = safe_get(data, 'current_price')
                    if current_price is not None:
                        fig.add_trace(go.Indicator(
                            mode="number+delta",
                            value=current_price,
                            delta={'reference': safe_get(data, '50_day_average'), 'relative': True, 'position': "top"},
                            title={'text': "Current Price vs 50-Day Avg"},
                            domain={'x': [0, 0.5], 'y': [0, 1]}
                        ))
                        fig.add_trace(go.Indicator(
                            mode="number+delta",
                            value=current_price,
                            delta={'reference': safe_get(data, '200_day_average'), 'relative': True, 'position': "top"},
                            title={'text': "Current Price vs 200-Day Avg"},
                            domain={'x': [0.5, 1], 'y': [0, 1]}
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.write("Stock performance data not available.")

                    # Financial Metrics
                    st.header("Financial Metrics")
                    metrics = [
                        ("P/E Ratio", safe_get(data, 'pe_ratio')),
                        ("Forward P/E", safe_get(data, 'forward_pe')),
                        ("PEG Ratio", safe_get(data, 'peg_ratio')),
                        ("Price to Sales", safe_get(data, 'price_to_sales')),
                        ("Price to Book", safe_get(data, 'price_to_book')),
                        ("Dividend Yield", f"{safe_get(data, 'dividend_yield', 0):.2%}"),
                    ]
                    df_metrics = pd.DataFrame(metrics, columns=["Metric", "Value"])
                    st.dataframe(df_metrics.set_index("Metric"), use_container_width=True)

                    # Growth and Returns
                    st.header("Growth and Returns")
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = px.bar(
                            x=["Revenue Growth", "Earnings Growth"],
                            y=[safe_get(data, 'revenue_growth', 0), safe_get(data, 'earnings_growth', 0)],
                            labels={'x': 'Metric', 'y': 'Growth Rate'},
                            title="Growth Rates"
                        )
                        fig.update_traces(text=[f"{safe_get(data, 'revenue_growth', 0):.2%}", f"{safe_get(data, 'earnings_growth', 0):.2%}"], textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        fig = px.bar(
                            x=["Return on Assets", "Return on Equity"],
                            y=[safe_get(data, 'return_on_assets', 0), safe_get(data, 'return_on_equity', 0)],
                            labels={'x': 'Metric', 'y': 'Return Rate'},
                            title="Return Rates"
                        )
                        fig.update_traces(text=[f"{safe_get(data, 'return_on_assets', 0):.2%}", f"{safe_get(data, 'return_on_equity', 0):.2%}"], textposition='outside')
                        st.plotly_chart(fig, use_container_width=True)

                    # Risk Assessment
                    st.header("Risk Assessment")
                    risk_data = {
                        'Risk Type': ['Overall', 'Audit', 'Board', 'Compensation', 'Shareholder Rights'],
                        'Risk Score': [
                            safe_get(data, 'overall_risk', 0),
                            safe_get(data, 'audit_risk', 0),
                            safe_get(data, 'board_risk', 0),
                            safe_get(data, 'compensation_risk', 0),
                            safe_get(data, 'shareholder_rights_risk', 0)
                        ]
                    }
                    df_risk = pd.DataFrame(risk_data)
                    fig = px.bar(df_risk, x='Risk Type', y='Risk Score', title="Risk Assessment")
                    fig.update_traces(marker_color='rgba(58, 71, 80, 0.6)', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
                    st.plotly_chart(fig, use_container_width=True)

                    # Analyst Recommendations
                    st.header("Analyst Recommendations")
                    target_median_price = safe_get(data, 'target_median_price')
                    week_52_low = safe_get(data, '52_week_low')
                    week_52_high = safe_get(data, '52_week_high')
                    current_price = safe_get(data, 'current_price')
                    
                    if all([target_median_price, week_52_low, week_52_high, current_price]):
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=target_median_price,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Median Target Price", 'font': {'size': 24}},
                            gauge={
                                'axis': {'range': [week_52_low, week_52_high], 'tickwidth': 1, 'tickcolor': "darkblue"},
                                'bar': {'color': "darkblue"},
                                'bgcolor': "white",
                                'borderwidth': 2,
                                'bordercolor': "gray",
                                'steps': [
                                    {'range': [week_52_low, current_price], 'color': 'cyan'},
                                    {'range': [current_price, week_52_high], 'color': 'royalblue'}],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': current_price}}))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.write("Analyst recommendations data not available.")

                    # Additional Information
                    st.header("Additional Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Company Details")
                        st.write(f"**Industry:** {safe_get(data, 'industry', 'N/A')}")
                        st.write(f"**Sector:** {safe_get(data, 'sector', 'N/A')}")
                        st.write(f"**Employees:** {safe_get(data, 'employees', 'N/A'):,}")
                        website = safe_get(data, 'website', '#')
                        st.write(f"**Website:** [{website}]({website})")
                    with col2:
                        st.subheader("Trading Information")
                        st.write(f"**Beta:** {safe_get(data, 'beta', 'N/A'):.2f}")
                        st.write(f"**Average Volume:** {safe_get(data, 'average_volume', 'N/A'):,}")
                        st.write(f"**Shares Outstanding:** {safe_get(data, 'shares_outstanding', 'N/A'):,}")
                        st.write(f"**Float Shares:** {safe_get(data, 'float_shares', 'N/A'):,}")

            with tabs[1]:
                with st.spinner("Processing stock history..."):
                    stock_history = stock.get_history()
                    indicators = stock_history_processor.preprocess(stock_history)
                    history_analysis = json.loads(stock_history_processor.process(indicators))
                    
                    st.header("Stock Price Analysis & Charts")

                    # Display Rating and Key Indicators in cards
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    # Custom CSS for cards
                    st.markdown("""
                    <style>
                    .metric-card {
                        border: 1px solid #e0e0e0;
                        border-radius: 5px;
                        padding: 10px;
                        text-align: center;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .metric-title {
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 5px;
                    }
                    .metric-value {
                        font-size: 20px;
                        font-weight: bold;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    with col1:
                        rating_color = "green" if history_analysis["Rating"] == "Buy" else "red" if history_analysis["Rating"] == "Sell" else "orange"
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Rating</div>
                            <div class="metric-value" style="color: {rating_color};">{history_analysis['Rating']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Latest Price</div>
                            <div class="metric-value">${indicators['latest_price']:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        annualized_return = indicators['annualized_return']
                        color = color_metric(annualized_return, [0, 10])
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Annualized Return</div>
                            <div class="metric-value" style="color: {color};">{annualized_return:.2f}%</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        sharpe_ratio = indicators['sharpe_ratio']
                        color = color_sharpe_ratio(sharpe_ratio)
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">Sharpe Ratio</div>
                            <div class="metric-value" style="color: {color};">{sharpe_ratio:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col5:
                        rsi = indicators['RSI']
                        color = color_metric(rsi, [30, 70])
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-title">RSI</div>
                            <div class="metric-value" style="color: {color};">{rsi:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Display Analysis Reasons
                    st.subheader("Analysis Reasons")
                    for i in range(1, 6):
                        reason_key = f"Reason {i}"
                        if reason_key in history_analysis:
                            st.info(f"{i}. {history_analysis[reason_key]}")

                    # Visualizations
                    st.subheader("Charts")
                    full_stock_history = stock.get_full_history()
                    
                    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
                    
                    # Add Close Price
                    fig.add_trace(go.Scatter(x=full_stock_history.index, y=full_stock_history['Close'], mode='lines', name='Close Price'))
                    
                    # Add SMAs
                    for period in [5, 20, 50, 200]:
                        sma = full_stock_history['Close'].rolling(window=period).mean()
                        fig.add_trace(go.Scatter(x=full_stock_history.index, y=sma, mode='lines', name=f'{period}-day SMA'))
                    
                    # Calculate and add Bollinger Bands
                    upper_band, lower_band = calculate_bollinger_bands(full_stock_history)
                    fig.add_trace(go.Scatter(x=full_stock_history.index, y=upper_band, mode='lines', name='Upper Bollinger Band', line=dict(dash='dash')))
                    fig.add_trace(go.Scatter(x=full_stock_history.index, y=lower_band, mode='lines', name='Lower Bollinger Band', line=dict(dash='dash')))
                    
                    fig.update_layout(
                        title='Stock Price with SMAs and Bollinger Bands',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Display additional charts
                    display_stock_charts(full_stock_history)

            with tabs[2]:
                st.header("News Analysis")
                with st.spinner("Processing news..."):
                    news_analysis, title_url_sentiment = news_processor.process(ticker)
                    sentiment_score = news_analysis['Sentiment Score']
                    st.markdown(f"<h3>Overall Sentiment Score: <span style='color: {get_sentiment_color(sentiment_score)};'>{sentiment_score:.2f}</span></h3>", unsafe_allow_html=True)
                    for i in range(1, 4):
                        st.info(f"Reason {i}: {news_analysis[f'Reason {i}']}")
                    
                    # Display news cards
                    st.subheader("News Articles")
                    
                    # Create a container for news cards
                    st.markdown('<div class="news-container">', unsafe_allow_html=True)
                    
                    # Create rows of 4 cards each
                    for i in range(0, len(title_url_sentiment), 4):
                        cols = st.columns(4)
                        for j, ((title, url), sentiment_data) in enumerate(list(title_url_sentiment.items())[i:i+4]):
                            with cols[j]:
                                sentiment_score = sentiment_data['Sentiment Score']
                                sentiment_color = get_sentiment_color(sentiment_score)
                                st.markdown(f"""
                                <div class="news-card sentiment-border" style="border-left-color: {sentiment_color};">
                                    <div class="sentiment-score" style="color: {sentiment_color};">{sentiment_score:.2f}</div>
                                    <div class="title-container">
                                        <div class="title"><a href="{url}" target="_blank" title="{title}">{title}</a></div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                                
                                with st.expander("Show Reasons"):
                                    st.write(f"Reason 1: {sentiment_data['Reason 1']}")
                                    st.write(f"Reason 2: {sentiment_data['Reason 2']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Not a valid ticker name. Please enter a valid stock ticker symbol.")
            st.stop()


if __name__ == "__main__":
    main()
