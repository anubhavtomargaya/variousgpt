# worker.py
import yfinance as yf
from datetime import datetime
import pandas as pd
import logging
from typing import Dict, Any, List
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class CompanyDataWorker:
    def __init__(self, supabase_client, tickers: List[str]):
        """
        Initialize the worker with Supabase client and list of tickers to monitor
        """
        self.supabase = supabase_client
        self.tickers = tickers
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the worker"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('company_data_worker.log'),
                logging.StreamHandler()
            ]
        )
    
    def serialize_value(self, val: Any) -> tuple:
        """Serialize a value and return its string representation and type"""
        if isinstance(val, (pd.Timestamp, datetime)):
            return val.strftime('%Y-%m-%d'), 'date'
        elif isinstance(val, float):
            return str(val), 'float'
        elif isinstance(val, int):
            return str(val), 'integer'
        elif isinstance(val, dict):
            return json.dumps(val), 'json'
        elif isinstance(val, (list, tuple)):
            return json.dumps(list(val)), 'json'
        elif pd.isna(val):
            return None, None
        return str(val), 'string'

    def _flatten_data(self, data: Dict, prefix='') -> Dict[str, Any]:
        """Flatten nested dictionary structure"""
        items = {}
        for k, v in data.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                items.update(self._flatten_data(v, f"{new_key}_"))
            else:
                items[new_key] = v
        return items

    def process_ticker(self, ticker: str):
        """Process a single ticker"""
        logger.info(f"Processing ticker: {ticker}")
        try:
            # Fetch data
            stock = yf.Ticker(f"{ticker}.NS")
            data = self._get_stock_data(stock)
            
            # Flatten the data structure
            flat_data = self._flatten_data(data)
            
            # Get non-null fields
            non_null_fields = {
                field: value for field, value in flat_data.items()
                if value is not None and not pd.isna(value)
            }
            
            # Update metadata
            self._update_metadata(ticker, non_null_fields)
            
            # Update historical data
            self._update_historical_data(ticker, non_null_fields)
            
            logger.info(f"Successfully processed {ticker}")
            
        except Exception as e:
            logger.error(f"Error processing {ticker}: {str(e)}", exc_info=True)
            
    def _get_stock_data(self, stock) -> Dict:
        """Get all relevant stock data"""
        info = stock.info
        return {
            'basic_info': {
                'long_name': info.get('longName'),
                'industry': info.get('industry'),
                'sector': info.get('sector'),
                'employee_count': info.get('fullTimeEmployees'),
                'website': info.get('website'),
                'country': info.get('country'),
                'state': info.get('state'),
                'city': info.get('city'),
            },
            'financial': {
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'profit_margins': info.get('profitMargins'),
                'operating_margins': info.get('operatingMargins'),
                'price_to_book': info.get('priceToBook'),
            },
            'balance_sheet': {
                'total_assets': info.get('totalAssets'),
                'total_debt': info.get('totalDebt'),
                'total_cash': info.get('totalCash'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
            },
            'growth': {
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),
            },
            'dividend': {
                'dividend_rate': info.get('dividendRate'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio'),
            }
        }
    
    def _update_metadata(self, ticker: str, non_null_fields: Dict):
        """Update the company metadata in Supabase"""
        # Get field types
        field_types = {
            field: self.serialize_value(value)[1]
            for field, value in non_null_fields.items()
        }
        
        # Check if metadata exists
        result = self.supabase.table('company_metadata').select('*').eq('ticker', ticker).execute()
        
        metadata = {
            'ticker': ticker,
            'last_updated': datetime.utcnow().isoformat(),
            'available_fields': list(non_null_fields.keys()),
            'field_types': field_types
        }
        
        if result.data:
            # Update existing record
            self.supabase.table('company_metadata').update(metadata).eq('ticker', ticker).execute()
        else:
            # Insert new record
            self.supabase.table('company_metadata').insert(metadata).execute()
    
    def _update_historical_data(self, ticker: str, non_null_fields: Dict):
        """Update historical data for changes in Supabase"""
        current_time = datetime.utcnow().isoformat()
        
        for field, value in non_null_fields.items():
            # Get the last recorded value for this field
            result = (self.supabase.table('company_data_history')
                     .select('*')
                     .eq('ticker', ticker)
                     .eq('field_name', field)
                     .order('timestamp', desc=True)
                     .limit(1)
                     .execute())
            
            # Serialize the current value
            value_str, value_type = self.serialize_value(value)
            
            # If no previous record or value has changed, add new record
            if not result.data or result.data[0]['value'] != value_str:
                new_record = {
                    'ticker': ticker,
                    'field_name': field,
                    'value': value_str,
                    'value_type': value_type,
                    'timestamp': current_time
                }
                self.supabase.table('company_data_history').insert(new_record).execute()
    
    def run(self):
        """Process all tickers"""
        logger.info(f"Starting data collection for {len(self.tickers)} tickers")
        
        for ticker in self.tickers:
            try:
                self.process_ticker(ticker)
            except Exception as e:
                logger.error(f"Failed to process ticker {ticker}: {str(e)}", exc_info=True)
        
        logger.info("Completed data collection")

# SQL for creating tables in Supabase
CREATE_TABLES_SQL = """
-- Enable Row Level Security
alter table company_metadata enable row level security;
alter table company_data_history enable row level security;

-- Create company_metadata table
create table if not exists company_metadata (
    id bigint primary key generated always as identity,
    ticker text not null unique,
    last_updated timestamp with time zone not null,
    available_fields jsonb not null,
    field_types jsonb not null
);

-- Create company_data_history table
create table if not exists company_data_history (
    id bigint primary key generated always as identity,
    ticker text not null,
    field_name text not null,
    value text not null,
    value_type text not null,
    timestamp timestamp with time zone not null
);

-- Create index for faster queries
create index if not exists idx_company_history_ticker_field 
on company_data_history(ticker, field_name, timestamp desc);

-- Add RLS policies
create policy "Enable read access for all users"
on company_metadata for select
to authenticated
using (true);

create policy "Enable read access for all users"
on company_data_history for select
to authenticated
using (true);
"""

# Example usage
def run_daily_update(supabase_client, tickers):
    """Run daily update for specified tickers"""
    worker = CompanyDataWorker(supabase_client, tickers)
    worker.run()

if __name__=='__main__':
    from supabse import supabase
    run_daily_update(supabase,['PCBL','GRAVITA'])