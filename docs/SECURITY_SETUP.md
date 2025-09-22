# 🔒 Security Setup Guide - Healthcare Voice AI

## **CRITICAL: API Key Security**

### **❌ NEVER DO THIS:**
```bash
# DON'T expose API keys in terminal commands
export VAPI_API_KEY=b592d0ba-66a7-4449-9e8c-422811a53b7f && python -m uvicorn...
```

### **✅ ALWAYS DO THIS:**

#### **1. Create Environment File**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env
```

#### **2. Set Environment Variables**
```bash
# In your .env file
VAPI_API_KEY=your-actual-vapi-key-here
JWT_SECRET=your-super-secret-jwt-key-here
SUPABASE_URL=your-supabase-url-here
SUPABASE_KEY=your-supabase-key-here
```

#### **3. Start Server Securely**
```bash
# Use the secure startup script
python start_server.py

# OR manually (but ensure .env is loaded)
python -m uvicorn dental_voice_ai.main:app --reload --host 0.0.0.0 --port 8000
```

## **Security Features Implemented**

### **🔐 API Key Protection**
- ✅ Environment variables only
- ✅ Never logged or exposed
- ✅ Masked in all log messages
- ✅ Secure startup script

### **🛡️ Input Validation**
- ✅ Pydantic model validation
- ✅ Sanitized user inputs
- ✅ Protected against injection attacks

### **📝 Secure Logging**
- ✅ Sensitive data masking
- ✅ Structured JSON logs
- ✅ No API key exposure in logs

### **🚫 Rate Limiting**
- ✅ API rate limiting
- ✅ DoS attack protection
- ✅ Configurable limits

## **Environment Variables**

### **Required for Production:**
```bash
VAPI_API_KEY=your-vapi-key
JWT_SECRET=your-jwt-secret
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### **Optional Configuration:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=10
```

## **Security Checklist**

- [ ] API keys stored in environment variables only
- [ ] No hardcoded secrets in code
- [ ] Secure logging enabled
- [ ] Input validation implemented
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Environment file not committed to git

## **Production Deployment**

### **1. Set Production Environment**
```bash
ENVIRONMENT=production
DEBUG=false
```

### **2. Use Strong Secrets**
```bash
JWT_SECRET=your-very-long-random-secret-key-here
```

### **3. Configure CORS**
```bash
CORS_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com"]
```

### **4. Enable HTTPS**
- Use reverse proxy (nginx/Apache)
- SSL certificates
- HSTS headers

## **Monitoring & Alerts**

### **Log Monitoring**
- Monitor for failed authentication attempts
- Watch for rate limit violations
- Track API key usage

### **Security Alerts**
- Unusual API usage patterns
- Failed login attempts
- Rate limit violations

## **Emergency Response**

### **If API Key is Compromised:**
1. **Immediately** revoke the key in VAPI dashboard
2. Generate new API key
3. Update environment variables
4. Restart application
5. Review logs for unauthorized usage

### **If System is Breached:**
1. Stop the application
2. Revoke all API keys
3. Review access logs
4. Update all secrets
5. Implement additional security measures

## **Best Practices**

### **Development:**
- Never commit .env files
- Use different keys for dev/staging/prod
- Regular security audits
- Code reviews for security

### **Production:**
- Use secrets management service
- Regular key rotation
- Monitor API usage
- Implement backup security measures

## **Support**

For security issues or questions:
- Create a private issue
- Contact security team
- Follow responsible disclosure

---

**Remember: Security is everyone's responsibility!**
