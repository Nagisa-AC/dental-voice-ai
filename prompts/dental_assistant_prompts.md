# Dental Assistant Prompts

This file tracks all prompts used in the VAPI dental assistant.

## Current Prompts

### 1. Dental Assistant - Riley (Core)
**File**: `prompts/core/dental_assistant.md`
**Purpose**: Main dental assistant prompt for Riley
**Tools**: 
- get_tenant_appointment_availability
- post_tenant_apointment
- google_calendar_check_availability_tool
- google_calendar_event_create_tool
- google_calendar_event_update_tool
- google_calendar_event_delete_tool

### 2. Final Assistant Prompt
**File**: `prompts/final_assistant_prompt.md`
**Purpose**: Final production-ready dental assistant prompt
**Tools**: Same as core prompt

## Usage
1. Edit the prompt files in the `prompts/` directory
2. Copy the content from the markdown files
3. Paste directly into VAPI assistant configuration
4. Deploy the assistant

## Notes
- Prompts are stored locally for version control
- Copy-paste workflow into VAPI
- No complex validation or loading logic
- Simple markdown format for easy editing
