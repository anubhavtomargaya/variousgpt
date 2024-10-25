from datetime import datetime, timedelta
from flask import  current_app, jsonify, make_response, request
import yfinance as yf
import pandas as pd
from . import company_app

import pandas as pd
from datetime import datetime

@company_app.route('/ticker/explore/<ticker>')
def explore_ticker_data(ticker):
    """GET endpoint to fetch ticker data"""
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        # Initialize ticker object
        stock = yf.Ticker(f"{ticker}.NS")
        info = stock.info
        
        def serialize_value(val):
            """Helper function to serialize values"""
            if isinstance(val, pd.Timestamp):
                return val.strftime('%Y-%m-%d')
            if isinstance(val, datetime):
                return val.strftime('%Y-%m-%d')
            if pd.isna(val):
                return None
            return val

        def safe_dataframe_to_dict(df):
            """Safely convert DataFrame to serializable dictionary"""
            if df is None:
                return None
            
            try:
                # Convert DataFrame to records
                records = []
                if isinstance(df, pd.DataFrame):
                    # Convert index to datetime if it's not already
                    if isinstance(df.index, pd.DatetimeIndex):
                        df.index = df.index.strftime('%Y-%m-%d')
                    
                    # Convert all timestamps in the data
                    for column in df.columns:
                        if isinstance(df[column].dtype, pd.DatetimeDtype):
                            df[column] = df[column].apply(lambda x: serialize_value(x))
                    
                    # Convert to records
                    df_dict = df.reset_index().to_dict('records')
                    
                    # Serialize any remaining timestamps
                    records = [{k: serialize_value(v) for k, v in record.items()} 
                             for record in df_dict]
                    return records
                return None
            except Exception as e:
                print(f"Error converting DataFrame: {e}")
                return None

        # Prepare the data structures with serialization
        org_info = {
            'basic_info': {
                'long_name': info.get('longName'),
                'short_name': info.get('shortName'),
                'industry': info.get('industry'),
                'sector': info.get('sector'),
                'website': info.get('website'),
                'country': info.get('country'),
                'state': info.get('state'),
                'city': info.get('city'),
                'address': info.get('address1'),
                'phone': info.get('phone'),
            },
            'business_details': {
                'business_summary': info.get('longBusinessSummary'),
                'employee_count': info.get('fullTimeEmployees'),
                'company_officers': [{k: serialize_value(v) for k, v in officer.items()} 
                                   if isinstance(officer, dict) else officer 
                                   for officer in info.get('companyOfficers', [])],
                'audit_risk': info.get('auditRisk'),
                'board_risk': info.get('boardRisk'),
                'compensation_risk': info.get('compensationRisk'),
                'share_holder_rights_risk': info.get('shareHolderRightsRisk'),
            }
        }

        financial_metrics = {
            'market_data': {
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'float_shares': info.get('floatShares'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'shares_short': info.get('sharesShort'),
                'shares_percent_shares_out': info.get('sharesPercentSharesOut'),
            },
            'financial_ratios': {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'enterprise_to_revenue': info.get('enterpriseToRevenue'),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda'),
            }
        }

        balance_sheet_metrics = {
            'assets_and_liabilities': {
                'total_assets': info.get('totalAssets'),
                'total_debt': info.get('totalDebt'),
                'total_cash': info.get('totalCash'),
                'total_cash_per_share': info.get('totalCashPerShare'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
            }
        }

        growth_metrics = {
            'revenue_growth': {
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
            },
            'returns': {
                'return_on_equity': info.get('returnOnEquity'),
                'return_on_assets': info.get('returnOnAssets'),
                'return_on_capital': info.get('returnOnCapital'),
            }
        }

        dividend_info = {
            'dividend_rate': info.get('dividendRate'),
            'dividend_yield': info.get('dividendYield'),
            'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
            'payout_ratio': info.get('payoutRatio'),
            'dividend_date': serialize_value(info.get('dividendDate')),
            'ex_dividend_date': serialize_value(info.get('exDividendDate')),
            'last_dividend_value': info.get('lastDividendValue'),
            'last_dividend_date': serialize_value(info.get('lastDividendDate')),
        }

        # Convert all DataFrames to serializable format
        analysis_data = {
            'recommendations': safe_dataframe_to_dict(stock.recommendations),
            'major_holders': safe_dataframe_to_dict(stock.major_holders),
            'institutional_holders': safe_dataframe_to_dict(stock.institutional_holders),
            'balance_sheet': safe_dataframe_to_dict(stock.balance_sheet),
            'quarterly_balance_sheet': safe_dataframe_to_dict(stock.quarterly_balance_sheet),
            'cashflow': safe_dataframe_to_dict(stock.cashflow),
            'quarterly_cashflow': safe_dataframe_to_dict(stock.quarterly_cashflow),
            'earnings': safe_dataframe_to_dict(stock.earnings),
            'quarterly_earnings': safe_dataframe_to_dict(stock.quarterly_earnings),
            'sustainability': safe_dataframe_to_dict(stock.sustainability),
            'calendar': safe_dataframe_to_dict(stock.calendar)
        }

        # Compile all data
        complete_data = {
            'organizational_info': org_info,
            'financial_metrics': financial_metrics,
            'balance_sheet_metrics': balance_sheet_metrics,
            'growth_metrics': growth_metrics,
            'dividend_info': dividend_info,
            'analysis_data': analysis_data
        }

        return jsonify(complete_data)

    except Exception as e:
        import traceback
        return jsonify({
            'error': 'Failed to fetch data',
            'details': str(e),
            'traceback': traceback.format_exc()
        }), 500
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

