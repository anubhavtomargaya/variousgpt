
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