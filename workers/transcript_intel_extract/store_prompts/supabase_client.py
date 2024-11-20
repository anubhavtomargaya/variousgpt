import json
from pathlib import Path

from typing import Optional
from supabase import create_client, Client

CONFIG_FILE='env.json'
def _load_config():
    with open(Path(Path(__file__).parent.resolve(),CONFIG_FILE)) as f:
        return json.load(f)
    
configs = _load_config()
SUPABASE_URL =configs['SUPABASE_URL']
SUPABASE_SERVICE_KEY = configs['SUPABASE_SERVICE_KEY']
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
