# 📞 Call Storage Solution for VAPI Integration

## ❌ **Current Issue**

**Question**: "If call will my db update itself with the latest call too?"

**Answer**: **NO** - Currently, calls are NOT being stored in the database.

### **Current State:**
- ✅ VAPI webhooks are received at `/webhooks/incoming_call`
- ✅ Call data is logged to console/logs
- ❌ **Call data is NOT stored in database**
- ❌ No database table exists for call records
- ❌ No call history or analytics available

---

## 🔧 **Solution: Add Call Storage**

### **1. Database Table Needed**

Add a `calls` table to store call data:

```sql
CREATE TABLE calls (
    id VARCHAR PRIMARY KEY,
    tenant_id VARCHAR(50) NOT NULL,
    assistant_id VARCHAR(100),
    vapi_call_id VARCHAR(100) UNIQUE,
    customer_phone VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'started',
    duration_seconds INTEGER,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    transcript TEXT,
    summary TEXT,
    outcome VARCHAR(50), -- 'appointment_booked', 'no_show', 'cancelled', etc.
    recording_url VARCHAR(500),
    cost DECIMAL(10,4),
    currency VARCHAR(3) DEFAULT 'USD',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (assistant_id) REFERENCES assistants(vapi_assistant_id)
);
```

### **2. Update Webhook Handler**

Modify `/webhooks/incoming_call` to store call data:

```python
@router.post("/incoming_call")
async def handle_vapi_webhook(request: Request):
    """Handle incoming VAPI webhook calls and store in database."""
    try:
        # Parse webhook data
        body = await request.body()
        webhook_data = json.loads(body)
        
        # Store call data in database
        call_record = await store_call_data(webhook_data)
        
        # Handle different webhook types
        webhook_type = webhook_data.get('type', '')
        
        if webhook_type == 'call-started':
            # Create new call record
            await create_call_record(webhook_data)
        elif webhook_type == 'call-ended':
            # Update call record with end time and duration
            await update_call_record(webhook_data)
        elif webhook_type == 'function-call':
            # Log function call details
            await log_function_call(webhook_data)
        elif webhook_type == 'speech-update':
            # Update transcript
            await update_call_transcript(webhook_data)
        
        return {"status": "success", "message": "Webhook processed and stored"}
        
    except Exception as e:
        logger.error(f"❌ Error processing VAPI webhook: {e}")
        return {"status": "error", "message": str(e)}
```

### **3. Call Storage Functions**

```python
async def create_call_record(webhook_data: dict):
    """Create a new call record in the database."""
    call_data = webhook_data.get('call', {})
    
    call_record = {
        'id': str(uuid.uuid4()),
        'tenant_id': extract_tenant_id(webhook_data),
        'assistant_id': extract_assistant_id(webhook_data),
        'vapi_call_id': call_data.get('id'),
        'customer_phone': extract_customer_phone(webhook_data),
        'customer_name': extract_customer_name(webhook_data),
        'status': 'started',
        'started_at': datetime.utcnow(),
        'created_at': datetime.utcnow()
    }
    
    # Insert into database
    await db.execute(insert(calls_table).values(**call_record))

async def update_call_record(webhook_data: dict):
    """Update call record when call ends."""
    call_data = webhook_data.get('call', {})
    vapi_call_id = call_data.get('id')
    
    # Calculate duration
    duration = call_data.get('duration', 0)
    ended_at = datetime.utcnow()
    
    # Update database
    await db.execute(
        update(calls_table)
        .where(calls_table.c.vapi_call_id == vapi_call_id)
        .values(
            status='completed',
            duration_seconds=duration,
            ended_at=ended_at,
            updated_at=ended_at
        )
    )
```

---

## 🚀 **Implementation Steps**

### **Step 1: Add Call Table to Database**

1. **Create migration**:
   ```bash
   python3 -m alembic revision --autogenerate -m "add_calls_table"
   ```

2. **Run migration**:
   ```bash
   python3 -m alembic upgrade head
   ```

### **Step 2: Update Webhook Handler**

1. **Add call storage logic** to `/webhooks/incoming_call`
2. **Create call service functions**
3. **Add error handling** for database operations

### **Step 3: Add Call Management Endpoints**

```python
@router.get("/calls")
async def get_calls(
    tenant_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get call history for a tenant."""

@router.get("/calls/{call_id}")
async def get_call_details(
    call_id: str,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get detailed call information."""

@router.get("/calls/analytics")
async def get_call_analytics(
    tenant_id: str,
    start_date: datetime,
    end_date: datetime,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get call analytics and statistics."""
```

---

## 📊 **Benefits of Call Storage**

### **1. Call History & Analytics**
- Track all incoming calls
- Monitor call volume and patterns
- Analyze call outcomes (appointments booked, etc.)

### **2. Business Intelligence**
- Call duration statistics
- Peak calling hours
- Success rates for appointment booking
- Cost tracking per call

### **3. HIPAA Compliance**
- Complete audit trail of all calls
- Patient interaction records
- Data retention for compliance

### **4. Customer Service**
- Access to call transcripts
- Call recordings for quality assurance
- Follow-up on missed appointments

---

## 🎯 **Quick Implementation**

**To enable call storage immediately:**

1. **Add call table** to database schema
2. **Update webhook handler** to store call data
3. **Add call management endpoints**
4. **Update essential_endpoints.json** to include call endpoints

**Result**: Every VAPI call will be automatically stored in the database with full details, transcripts, and outcomes.

---

## ❓ **Answer to Original Question**

**"If call will my db update itself with the latest call too?"**

**Current Answer**: ❌ **NO** - Calls are not stored in database

**After Implementation**: ✅ **YES** - Every call will be automatically stored with:
- Call details (phone, duration, status)
- Transcript and summary
- Appointment outcomes
- Cost and analytics data
- Full audit trail for compliance

*Would you like me to implement the call storage solution?*
