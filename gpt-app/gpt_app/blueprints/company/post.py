from datetime import datetime, timedelta
from flask import  current_app, jsonify, make_response, request
import yfinance as yf
from . import company_app

@company_app.route('/ticker', methods=['POST'])
def company_info():
    data = request.get_json()
    ticker = data.get('ticker')
    
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    # Fetch stock data
    stock = yf.Ticker(f"{ticker}.NS")  # Append .NS for NSE stocks
    
    # Get the stock info
    info = stock.info
    
    # Prepare the data
    stock_data = {
        'name': info.get('longName', 'N/A'),
        'ticker': ticker,
        'price': info.get('currentPrice', 'N/A'),
        'change': info.get('regularMarketChangePercent', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'dividend_yield': info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A',
        'high_52_week': info.get('fiftyTwoWeekHigh', 'N/A'),
        'low_52_week': info.get('fiftyTwoWeekLow', 'N/A'),
    }
    
    # Fetch historical data for the chart
    history = stock.history(period="1y")
    chart_data = [{'date': date.strftime('%Y-%m-%d'), 'price': price} 
                  for date, price in zip(history.index, history['Close'])]
    
    # Combine stock_data and chart_data in the response
    print("chart",chart_data)
    response_data = {
        'stock_data': stock_data,
        'chart_data': chart_data
    }
    
    response = make_response(jsonify(response_data))
    response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    return response




@company_app.route('/historical_data/<ticker>', methods=['POST'])
def get_historical_data(ticker):
    try:
        data = request.json
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        print("fetching",end_date)
        # Ensure the ticker ends with .NS for NSE stocks
        if not ticker.endswith('.NS'):
            ticker += '.NS'

        # Fetch data using yfinance
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date + timedelta(days=1))

        # Convert the data to the format expected by the frontend
        historical_data = []
        for date, row in hist.iterrows():
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'close': row['Close']
            })

            
        response = make_response(jsonify(historical_data))
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response
    except Exception as e:
        current_app.logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
        return jsonify({"error": "Failed to fetch historical data"}), 500

