# Dental Voice AI - Revised Implementation Plan
**VAPI Workflow-Driven Architecture | 6 Sprints | 4-6 Weeks to MVP**

---

## 🎯 PROJECT VISION

**Build a dental voice AI system using VAPI workflows for:**
- Service integrations (Google Calendar, email, SMS)
- Appointment booking/canceling/rescheduling
- Multi-tenant call handling
- Scalable, maintainable architecture

**Key Innovation**: Use VAPI's built-in workflow capabilities instead of custom FastAPI endpoints for core voice interactions.

---

## 🏗️ REVISED ARCHITECTURE 2.0

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Patient Call  │───▶│  VAPI Voice  │───▶│  VAPI Workflows │
│   (Phone)       │    │  Interface   │    │  (Core Logic)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    │                                │                                │
            ┌───────▼────────┐          ┌───────────▼──────────┐          ┌─────────▼─────────┐
            │  FastAPI       │          │  Supabase            │          │  VAPI Functions   │
            │  (Webhooks &   │          │  (Database)          │          │  (Service APIs)   │
            │   Dashboard)   │          │                      │          │                  │
            └────────────────┘          └──────────────────────┘          └───────────────────┘
                    │                                │                                │
            ┌───────▼────────┐          ┌───────────▼──────────┐          ┌─────────▼─────────┐
            │  Call Logging  │          │  Tenant Management   │          │  External APIs    │
            │  & Analytics   │          │  & Data Storage      │          │  (Google Calendar,│
            └────────────────┘          └──────────────────────┘          └───────────────────┘
                                                              │
                                                              │
                    ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
                    │                                         │                                         │
            ┌───────▼────────┐                    ┌───────────▼──────────┐                    ┌─────────▼─────────┐
            │  VAPI          │                    │  VAPI                │                    │  VAPI             │
            │  Workflows     │                    │  Knowledge Base      │                    │  Functions        │
            │                │                    │                      │                    │                  │
            │  • Main Call   │                    │  • FAQ Database      │                    │  • Calendar API   │
            │    Handler     │                    │  • Intent Detection  │                    │  • Email API      │
            │  • Appointment │                    │  • Conversation      │                    │  • SMS API        │
            │    Workflow    │                    │    Memory            │                    │  • Payment API    │
            │  • FAQ         │                    │  • Multi-turn        │                    │  • Insurance API  │
            │    Workflow    │                    │    Support           │                    │                  │
            │  • Emergency   │                    │  • Context           │                    │                  │
            │    Workflow    │                    │    Management        │                    │                  │
            └────────────────┘                    └──────────────────────┘                    └───────────────────┘
```

**VAPI Platform Handles Everything:**
- **Workflows**: Main call handler, appointment booking, FAQ system, emergency triage
- **Knowledge Base**: FAQ database, intent detection, conversation memory
- **Functions**: Service integrations (Google Calendar, email, SMS, payments, insurance)
- **Built-in Features**: TTS/STT, intent recognition, conversation management

**FastAPI Handles:**
- Webhook endpoints for VAPI callbacks
- Admin dashboard backend
- Analytics and reporting
- Tenant management and configuration

**Supabase Handles:**
- Multi-tenant data storage
- Call logs and analytics
- Appointment requests and status tracking
- User authentication and permissions

---

## 📋 REVISED SPRINT PLAN

### **SPRINT 0: Environment & Skeleton Setup (1-2 days)** ✅ **COMPLETE**
**Goal**: Have a clean project skeleton running locally.

**Tasks**:
- [x] Create project structure (using condensed commands)
- [x] Set up virtual environment & install dependencies: FastAPI, uvicorn, supabase, python-dotenv
- [x] Add .env for Supabase & Vapi keys
- [x] Implement health check endpoint at `/` returning `{"status": "ok"}`
- [x] Run with uvicorn to confirm app boots

**Deliverable**: ✅ Local FastAPI app running on http://127.0.0.1:8000 + Git repo initialized

---

### **SPRINT 1: Database & Supabase Integration (2-3 days)** ✅ **COMPLETE**
**Goal**: Persist tenants and call logs in Supabase.

**Tasks**:
- [x] Create Supabase Project
- [x] Tables: `tenants`, `calls`, `appointment_requests`
- [x] Generate service role key for backend use
- [x] Configure `supabase_client.py` to connect
- [x] Implement `/test-db` route → insert dummy call log to Supabase
- [x] Verification: Confirm data appears in Supabase dashboard

**Deliverable**: ✅ Backend can write/read tenants and call logs from Supabase

---

### **SPRINT 2: VAPI Webhook & Basic Call Handling (3-4 days)** 🔄 **IN PROGRESS**
**Goal**: Accept real phone calls and log them.

**Tasks**:
- [x] Buy a number in VAPI & configure webhook to `/vapi/incoming_call`
- [x] Implement `vapi_webhooks.py`:
  - Receive incoming call payload
  - Identify tenant by number
  - Log call start to Supabase
- [ ] Test by calling your number → confirm log in Supabase

**Deliverable**: 🔄 Calls to your Vapi number appear in Supabase calls table

---

### **SPRINT 3: VAPI Workflow FAQ System (4-6 days)** 📋 **PLANNED**
**Goal**: Use VAPI workflows to handle all FAQ interactions intelligently.

**Tasks**:
- [ ] Create VAPI workflow for FAQ handling:
  - **Intent Detection**: Use VAPI's built-in intent recognition
  - **FAQ Database**: Store dental FAQs in VAPI knowledge base
  - **Dynamic Responses**: Generate contextual answers using LLM
  - **Multi-turn FAQ**: Handle follow-up questions naturally
- [ ] Implement FAQ categories:
  - Office hours and location
  - Insurance and payment options
  - Services and procedures
  - Emergency care information
  - Pre/post appointment instructions
- [ ] Test conversation flow and response quality
- [ ] Optimize for <1s response time

**Deliverable**: Natural FAQ conversations handled entirely by VAPI workflows

---

### **SPRINT 4: Appointment Capture Flow (4-6 days)** 📋 **PLANNED**
**Goal**: Capture lead info during a call and store in Supabase.

**Tasks**:
- [ ] Extend VAPI workflow to detect appointment intent
- [ ] Collect caller information:
  - Caller name
  - Phone number (fallback to caller ID)
  - Reason for appointment
- [ ] Store in `appointment_requests` table
- [ ] Notify office via email or SMS (SendGrid / Twilio SMS)
- [ ] Implement VAPI workflow for appointment booking flow

**Deliverable**: Call leads to a stored appointment request in Supabase + notification

---

### **SPRINT 5: Admin Dashboard (Optional for MVP) (5-7 days)** 📋 **PLANNED**
**Goal**: Multi-tenant management & logs viewing.

**Tasks**:
- [ ] Simple React + Tailwind frontend hosted on Vercel
- [ ] Features:
  - Login (use Supabase Auth)
  - View call logs
  - View appointment requests
- [ ] Connect to Supabase with RLS (Row Level Security) per tenant

**Deliverable**: Office can log in and see their calls & appointment requests

---

### **SPRINT 6: Polish & Pilot Launch (1-2 weeks)** 📋 **PLANNED**
**Goal**: Prepare for 1-2 pilot offices.

**Tasks**:
- [ ] Logging & error handling
- [ ] Call recording (Vapi → S3 or Supabase Storage)
- [ ] HIPAA checklist & call recording consent message
- [ ] Deploy backend (Railway, Render, or Fly.io for MVP)

**Deliverable**: Fully functional MVP for first dental office pilot

---

## 🔄 VAPI WORKFLOW ARCHITECTURE

### **Core Workflows**

#### **1. Main Call Handler Workflow**
```javascript
// VAPI Workflow
export default defineWorkflow((steps) => {
  const { input } = steps;
  
  // 1. Identify tenant by phone number
  const tenant = await steps.run('identify_tenant', {
    phone_number: input.phone_number
  });
  
  // 2. Route to appropriate handler
  if (tenant.intent === 'appointment') {
    return steps.run('appointment_workflow', { tenant, input });
  } else if (tenant.intent === 'faq') {
    return steps.run('faq_workflow', { tenant, input });
  } else {
    return steps.run('general_inquiry_workflow', { tenant, input });
  }
});
```

#### **2. Appointment Workflow**
```javascript
export default defineWorkflow((steps) => {
  const { tenant, input } = steps;
  
  // 1. Check Google Calendar availability
  const availability = await steps.run('check_calendar', {
    calendar_id: tenant.calendar_id,
    date_range: 'next_7_days'
  });
  
  // 2. Present options to caller
  const response = await steps.run('present_slots', {
    available_slots: availability.slots,
    caller_name: input.caller_name
  });
  
  // 3. Collect appointment details
  const appointment = await steps.run('collect_appointment_details', {
    selected_slot: response.selected_slot,
    caller_info: input.caller_info
  });
  
  // 4. Send notifications
  await steps.run('send_notifications', {
    appointment: appointment,
    tenant: tenant
  });
  
  return { success: true, appointment_id: appointment.id };
});
```

#### **3. FAQ Workflow**
```javascript
export default defineWorkflow((steps) => {
  const { tenant, input } = steps;
  
  // 1. Use VAPI's built-in intent recognition
  const intent = await steps.run('detect_intent', {
    speech: input.speech,
    context: 'dental_faq'
  });
  
  // 2. Route to appropriate FAQ category
  if (intent.category === 'hours_location') {
    return steps.run('hours_location_faq', { tenant, intent });
  } else if (intent.category === 'insurance_payment') {
    return steps.run('insurance_payment_faq', { tenant, intent });
  } else if (intent.category === 'services_procedures') {
    return steps.run('services_faq', { tenant, intent });
  } else if (intent.category === 'emergency_care') {
    return steps.run('emergency_faq', { tenant, intent });
  } else {
    // 3. Use VAPI's knowledge base for general questions
    return steps.run('general_faq', {
      question: intent.question,
      tenant_knowledge_base: tenant.faq_data
    });
  }
});
```

### **Service Integrations via VAPI**

#### **Google Calendar Integration**
```javascript
// VAPI Function
export default defineFunction({
  name: 'check_calendar_availability',
  description: 'Check Google Calendar for available appointment slots',
  parameters: {
    calendar_id: { type: 'string' },
    date_range: { type: 'string' }
  },
  returns: { type: 'object' }
}, async ({ calendar_id, date_range }) => {
  // Google Calendar API call
  const calendar = google.calendar({ version: 'v3', auth });
  const response = await calendar.freebusy.query({
    requestBody: {
      timeMin: start_date,
      timeMax: end_date,
      items: [{ id: calendar_id }]
    }
  });
  
  return { available_slots: processAvailability(response) };
});
```

#### **Email/SMS Notifications**
```javascript
// VAPI Function
export default defineFunction({
  name: 'send_appointment_notification',
  description: 'Send email to office and SMS to patient',
  parameters: {
    appointment: { type: 'object' },
    tenant: { type: 'object' }
  }
}, async ({ appointment, tenant }) => {
  // Send email to office
  await sendEmail({
    to: tenant.office_email,
    subject: 'New Appointment Request',
    template: 'appointment_request',
    data: appointment
  });
  
  // Send SMS to patient
  await sendSMS({
    to: appointment.patient_phone,
    message: `Appointment requested for ${appointment.date} at ${appointment.time}. Add to calendar: ${appointment.calendar_link}`
  });
  
  return { success: true };
});
```

---

## 🛠️ TECHNICAL STACK

### **VAPI Platform**
- **Voice AI**: VAPI for call handling and workflows
- **Functions**: Custom functions for service integrations
- **Workflows**: Orchestrate complex conversation flows
- **TTS/STT**: Built-in speech processing
- **Intent Recognition**: Built-in intent detection and classification
- **Knowledge Base**: FAQ management and dynamic responses
- **Conversation Memory**: Multi-turn conversation handling

### **Backend Services**
- **API Framework**: FastAPI (Python) - minimal, webhook-focused
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **File Storage**: Supabase Storage

### **External Integrations**
- **Calendar**: Google Calendar API (via VAPI functions)
- **Email**: SendGrid (via VAPI functions)
- **SMS**: Twilio (via VAPI functions)
- **Analytics**: Custom dashboard + Supabase

---

## 📊 IMPLEMENTATION TIMELINE

### **Week 1: Foundation** ✅ **COMPLETE**
- **Days 1-2**: ✅ Sprint 0 (Environment setup)
- **Days 3-5**: ✅ Sprint 1 (Database & Supabase)

### **Week 2: Basic Call Handling** 🔄 **IN PROGRESS**
- **Days 1-4**: 🔄 Sprint 2 (VAPI webhook & call logging)

### **Week 3-4: AI & Appointment Flow** 📋 **PLANNED**
- **Days 1-6**: 📋 Sprint 3 (FAQ workflow)
- **Days 7-12**: 📋 Sprint 4 (Appointment capture workflow)

### **Week 5-6: Polish & Launch** 📋 **PLANNED**
- **Days 1-7**: 📋 Sprint 5 (Admin dashboard - optional)
- **Days 8-14**: 📋 Sprint 6 (Polish & pilot launch)

**Total Timeline**: 4-6 weeks to MVP
**Current Progress**: 2/6 sprints complete (33%)

---

## 🎯 KEY ADVANTAGES OF VAPI WORKFLOW APPROACH

### **1. Scalability**
- VAPI handles conversation complexity
- Built-in load balancing and scaling
- No custom conversation state management needed
- Built-in FAQ knowledge base scaling

### **2. Maintainability**
- Workflows are declarative and easy to modify
- Service integrations are isolated in functions
- Clear separation of concerns

### **3. Development Speed**
- Less custom code to write
- Built-in speech processing and intent recognition
- Rapid iteration on conversation flows
- No custom FAQ system to build

### **4. Reliability**
- VAPI's proven infrastructure
- Built-in error handling and retries
- Professional voice AI capabilities

### **5. Cost Efficiency**
- Pay-per-use model
- No infrastructure management
- Focus on business logic, not plumbing

---

## 📋 SUCCESS METRICS

### **Technical KPIs**
- **Response Time**: < 1 second for all interactions
- **Call Success Rate**: 95%+ calls handled without human intervention
- **Workflow Reliability**: 99.9% uptime
- **Integration Success**: 98%+ successful API calls

### **Business KPIs**
- **Appointment Capture**: 80%+ of appointment requests captured
- **Patient Satisfaction**: 4.5/5 average rating
- **Office Efficiency**: 60% reduction in admin time
- **Pilot Success**: 2+ dental offices using system within 6 weeks

---

## 🚀 NEXT STEPS

### **Immediate Actions**
1. **Set up VAPI account** and explore workflow capabilities
2. **Create Supabase project** and database schema
3. **Design workflow architecture** for appointment booking
4. **Plan service integrations** (Google Calendar, email, SMS)

### **Development Priority**
1. **Sprint 0**: Get basic environment running
2. **Sprint 1**: Database foundation
3. **Sprint 2**: First real call handling
4. **Sprint 3**: AI conversation capabilities
5. **Sprint 4**: Appointment booking workflow
6. **Sprint 5-6**: Polish and launch

---

## 💡 KEY INSIGHTS

### **Why VAPI Workflows Are Better**
1. **Faster Development**: Less custom code, more focus on business logic
2. **Better Scalability**: VAPI handles the heavy lifting
3. **Easier Maintenance**: Workflows are declarative and self-documenting
4. **Professional Quality**: Built-in speech processing and conversation management
5. **Cost Effective**: Pay for what you use, no infrastructure overhead

### **Architecture Benefits**
1. **Separation of Concerns**: VAPI handles voice, FastAPI handles webhooks
2. **Service Isolation**: Each integration is a separate VAPI function
3. **Multi-tenant Ready**: Built-in tenant identification and routing
4. **Extensible**: Easy to add new workflows and integrations

---

**This revised approach will get you to a working MVP much faster with better scalability and maintainability! 🚀**
