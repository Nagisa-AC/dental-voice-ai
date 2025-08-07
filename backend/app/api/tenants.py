from fastapi import APIRouter
from app.core.supabase_client import supabase

router = APIRouter()

# POST version
@router.post("/seed-tenant")
def seed_tenant():
    # Example tenant
    new_tenant = {
        "name": "Bright Smile Dental",
        "phone_number": "+15551112222",
        "hours_json": {
            "mon": ["9-5"], "tue": ["9-5"], "wed": ["9-5"], 
            "thu": ["9-5"], "fri": ["9-3"]
        },
        "insurances_json": ["Delta Dental", "Aetna", "Cigna"],
        "faq_json": {
            "Do you do teeth whitening?": "Yes, we offer professional whitening.",
            "What insurances do you accept?": "We accept Delta Dental, Aetna, and Cigna."
        }
    }

    response = supabase.table("tenants").insert(new_tenant).execute()
    return {"tenant": response.data}

# GET version to allow browser testing
@router.get("/seed-tenant")
def seed_tenant_get():
    return seed_tenant()
