import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import numpy as np

# Title of the dashboard
st.title("MX Stock Dashboard")

# List of tickers for the dropdown menu
tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']  # Add more tickers as needed

# Create a dropdown menu in the sidebar for ticker selection
ticker = st.sidebar.selectbox('Select Ticker', tickers)

# Date inputs for the start and end dates
start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2023-01-01'))
end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('today'))

# Fetch the data from Yahoo Finance
data = yf.download(ticker, start=start_date, end=end_date)

# Check if data is available
if not data.empty:
    # Create a candlestick chart
    candlestick_fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                     open=data['Open'],
                                                     high=data['High'],
                                                     low=data['Low'],
                                                     close=data['Close'])])
    candlestick_fig.update_layout(title=f"{ticker} Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
    
    # Create a line chart for 'Adj Close'
    line_fig = go.Figure(data=[go.Scatter(x=data.index, y=data['Adj Close'], mode='lines', name='Adj Close')])
    line_fig.update_layout(title=f"{ticker} Line Chart", xaxis_title="Date", yaxis_title="Adjusted Close Price")
    
    # Display the candlestick chart
    st.plotly_chart(candlestick_fig)

    # Display the line chart
    st.plotly_chart(line_fig)
else:
    st.write("No data available for the selected ticker and date range.")


pricing_data, fundamental_data, news = st.tabs(["Pricing Data","Fundamental Data", "Top 10 News"])

with pricing_data:
    st.header('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    data2.dropna(inplace = True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write('Annual Return is', annual_return, '%')
    stdev = np.std(data2['% Change']*np.sqrt(252))
    st.write('Standard Deviation is ',stdev*100,'%')
    st.write('Risk Adj. Return is ', annual_return/(stdev*100))

from alpha_vantage.fundamentaldata import FundamentalData
with fundamental_data:
    key = '2ec9efbd7emsha6c54dabd271c79p184fcdjsne1e4c1afe686'
    fd = FundamentalData(key,output_format = 'pandas')
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker)[0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader('Cash Flow Statement')
    cash_flow = fd. get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)

from stocknews import StockNews
with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news = False)
    df_news =  sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')