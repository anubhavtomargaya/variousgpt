
from process_csv import download_csv_from_bucket
import pandas as pd
from supabase_handler import supabase
def update_ltd(x:str ):
    print(x,"x")
    if 'Ltd.' in x:
        # print(x,"test x")
        x = x.replace('Ltd.','Limited')
        return x
    else:
        return x
nifty_code  = {'MARUTI':4470,
               'HINDUNILVR':369,
                'ULTRACEMCO':4499,
                'BAJAJ-AUTO':4946, 
                'EICHERMOT': 697,
                'BHARTIARTL':4438,
                'TATAMOTORS':354,
                'DRREDDY':87,
                'JSWSTEEL':163,
                'TATACONSUM':377,
                'SBIN':79,
                'COALINDIA':'',
                'HDFCLIFE':5978,
                'WIPRO':'',
                'HINDALCO':319,
                'BEL':'',
                'ADANIPORTS':4800,
                'NESTLE':376,
                'GRASIM':221,
                'TCS':4501,
                'TITAN':81,
                'LT':348,
                'BAJFINANCE':23,
                'TRENT':181,
                'SUNPHARMA':2757,
                'POWERGRID':43788,


                 }
error_codes = {
    87: {"status":'failing',"reason":"text not getting extracted","workers": ['pdf_extraction' ],},
    221: { "status":'garbage',"reason":"extracted intel seems garbage"},
    79: { "status":'garbage',"reason":"extracted intel has X %"},
    43788: {"status":'failing',"reason":"text not getting extracted","workers": ['pdf_extraction' ]}
}
missing_files_codes = [ 319,]
missing_codes=  [376, 181]

qa_only_codes = [ 81]


def process_nifty_dataframe(path):
    data = pd.read_csv(path)
    # print(data.head())
    data['Company Name'] = data['Company Name'].apply(lambda x :update_ltd(str(x)))
    # print(data)
    return data[['Company Name','Industry','Symbol','ISIN Code']]
    
def insert_company_data(company_name,
                        index:list,
                        indsutry,
                        symbol,
                        isin_code):
    d = {"company_name":company_name,
         "tags":{ "sectors":[],
                "indices":index,
                "industry":indsutry,
                "market_cap":[]
                },
        
        "meta":{"symbol":symbol,
                "isin_code":isin_code,
                "slug":'-'.join(company_name.split(' '))
                }
        }
    supabase.table('company-data').insert(d).execute()
    return True 
    


if __name__=='__main__':
    f = [
            'ind_nifty100list.csv',
            'ind_nifty50list.csv'
        ]   
    
    def test_read_csv():
        p = download_csv_from_bucket(f[0])
        with open(p,'r') as fl:
            print(fl.read(100))
      
        return p 
    
    def test_dataframe_proc():
        p = download_csv_from_bucket(f[0])
        return process_nifty_dataframe(p)

    def test_nifty_insert():
        p = download_csv_from_bucket(f[0])
        data = process_nifty_dataframe(p)
        # print(data,'data')
        for row in data.iterrows():
            items = row[1].to_dict()
            s = insert_company_data(company_name=items['Company Name'],
                                    index=['NIFTY100'],
                                    indsutry=items['Industry'],
                                    symbol=items['Symbol'],
                                    isin_code=items['ISIN Code']
                                    )
            print(s)
            print(items['Company Name'])
        return True
        # print('ds')

    # print(test_read_csv())
    # print(test_dataframe_proc())
    print(test_nifty_insert())