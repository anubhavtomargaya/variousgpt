from supabase import create_client, Client
import os
from config import SUPABASE_URL ,SUPABASE_SERVICE_KEY


supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)