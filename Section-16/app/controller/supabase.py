from config.supabase import supabase_config

supabase = supabase_config() 

def getUser(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).execute()