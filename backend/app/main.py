from fastapi import FastAPI
from app.core.supabase_client import supabase
from app.api import vapi_webhooks
from app.api import tenants



app = FastAPI(title="Dental Voice AI")


# Include Vapi routes

app.include_router(vapi_webhooks.router, prefix="/vapi", tags=["Vapi Webhooks"])
app.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])



@app.get("/")

def health_check():

    return {"status": "ok"}


@app.get("/test-db")
def test_db():
    result = supabase.table("calls").insert({
        "tenant_id": "1",
        "caller_number": "+15555555555",
        "status": "in_progress"
    }).execute()
    return {"inserted": result.data}


@app.get("/test-insert")
def test_insert():
    # Replace with an actual tenant_id from Supabase
    tenant_id = "00000000-0000-0000-0000-000000000000"
    response = supabase.table("calls").insert({
        "tenant_id": tenant_id,
        "caller_number": "+15555555555",
        "status": "in_progress"
    }).execute()
    return {"inserted": response.data}

@app.get("/test-read")
def test_read():
    response = supabase.table("calls").select("*").limit(5).execute()
    return {"calls": response.data}

@app.get("/test-read-tenants")
def test_read_tenants():
    response = supabase.table("tenants").select("*").order("created_at", desc=True).limit(5).execute()
    return {"recent_tenants": response.data}
