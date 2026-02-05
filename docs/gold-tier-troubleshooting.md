# Gold Tier AI Employee - Troubleshooting Guide

Common issues and solutions for the Gold Tier Autonomous AI Employee.

## Table of Contents

1. [MCP Server Issues](#mcp-server-issues)
2. [Odoo Integration Issues](#odoo-integration-issues)
3. [Social Media Issues](#social-media-issues)
4. [Ralph Wiggum Loop Issues](#ralph-wiggum-loop-issues)
5. [CEO Briefing Issues](#ceo-briefing-issues)
6. [Queue and Error Recovery Issues](#queue-and-error-recovery-issues)
7. [Audit Logging Issues](#audit-logging-issues)
8. [Performance Issues](#performance-issues)
9. [Security Issues](#security-issues)

---

## MCP Server Issues

### Issue: MCP Server Won't Start

**Symptoms:**
- Error: `listen EADDRINUSE: address already in use`
- Server exits immediately after starting

**Diagnosis:**
```bash
# Check if port is in use
# Windows:
netstat -ano | findstr :3100

# Linux/macOS:
lsof -i :3100
```

**Solutions:**

1. **Kill existing process:**
   ```bash
   # Windows:
   taskkill /PID <pid> /F

   # Linux/macOS:
   kill -9 <pid>
   ```

2. **Change port in .env:**
   ```bash
   ODOO_MCP_PORT=3200  # Use different port
   ```

3. **Check for zombie processes:**
   ```bash
   # Windows:
   tasklist | findstr node

   # Linux/macOS:
   ps aux | grep node
   ```

### Issue: MCP Server Health Check Fails

**Symptoms:**
- `curl http://localhost:3100/health` returns connection refused
- Health check shows `connected: false`

**Diagnosis:**
```bash
# Check server logs
# Look for startup errors in terminal where server is running

# Test basic connectivity
curl -v http://localhost:3100/health
```

**Solutions:**

1. **Verify environment variables:**
   ```bash
   # Check .env file has all required variables
   cat .env | grep ODOO_URL
   cat .env | grep FACEBOOK_PAGE_ACCESS_TOKEN
   ```

2. **Check external service connectivity:**
   ```bash
   # Test Odoo connection
   curl http://localhost:8069

   # Test Facebook API
   curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_TOKEN"
   ```

3. **Restart server with verbose logging:**
   ```bash
   NODE_ENV=development node odoo-server.js
   ```

### Issue: MCP Server Memory Leak

**Symptoms:**
- Server memory usage grows over time
- Server becomes unresponsive after hours of operation
- System runs out of memory

**Diagnosis:**
```bash
# Monitor memory usage
# Windows:
tasklist /FI "IMAGENAME eq node.exe" /FO TABLE

# Linux/macOS:
ps aux | grep node | awk '{print $2, $4, $11}'
```

**Solutions:**

1. **Restart servers periodically:**
   ```bash
   # Add to cron (Linux/macOS) or Task Scheduler (Windows)
   # Restart every 24 hours
   0 3 * * * pkill -f "node.*-server.js" && sleep 5 && node /path/to/server.js
   ```

2. **Check for unclosed connections:**
   - Review server code for unclosed HTTP connections
   - Ensure all axios requests have timeouts
   - Add connection pooling

3. **Monitor with PM2:**
   ```bash
   npm install -g pm2
   pm2 start odoo-server.js --max-memory-restart 500M
   ```

---

## Odoo Integration Issues

### Issue: Odoo Connection Refused

**Symptoms:**
- Error: `Connection refused` or `ECONNREFUSED`
- Cannot create invoices or record transactions

**Diagnosis:**
```bash
# Test Odoo connectivity
curl http://localhost:8069

# Check Odoo is running
# Docker:
docker ps | grep odoo

# Service:
systemctl status odoo  # Linux
```

**Solutions:**

1. **Start Odoo:**
   ```bash
   # Docker:
   docker start odoo

   # Service:
   sudo systemctl start odoo
   ```

2. **Verify Odoo URL in .env:**
   ```bash
   # Should match your Odoo installation
   ODOO_URL=http://localhost:8069
   ```

3. **Check firewall:**
   ```bash
   # Linux:
   sudo ufw allow 8069

   # Windows:
   netsh advfirewall firewall add rule name="Odoo" dir=in action=allow protocol=TCP localport=8069
   ```

### Issue: Invalid Odoo Credentials

**Symptoms:**
- Error: `Invalid credentials` or `Authentication failed`
- 401 Unauthorized response

**Diagnosis:**
```bash
# Test credentials manually
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "authenticate",
      "args": ["gold_tier_accounting", "admin", "password", {}]
    },
    "id": 1
  }'
```

**Solutions:**

1. **Verify credentials:**
   - Log into Odoo web interface with same credentials
   - Check database name matches
   - Ensure user has API access permissions

2. **Reset Odoo password:**
   ```bash
   # Docker:
   docker exec -it odoo odoo shell -d gold_tier_accounting
   # Then in Python shell:
   user = env['res.users'].search([('login', '=', 'admin')])
   user.password = 'new_password'
   ```

3. **Create dedicated API user:**
   - Log into Odoo as admin
   - Settings → Users → Create
   - Grant "Accounting / Accountant" permissions
   - Use this user for AI Employee

### Issue: Invoice Creation Fails

**Symptoms:**
- Error: `Missing required fields` or `Validation error`
- Invoice not appearing in Odoo

**Diagnosis:**
```bash
# Check Odoo logs
# Docker:
docker logs odoo | tail -50

# Service:
tail -50 /var/log/odoo/odoo-server.log
```

**Solutions:**

1. **Verify required fields:**
   - Customer name must exist in Odoo partners
   - Amount must be positive number
   - Date must be valid ISO format

2. **Create customer first:**
   ```python
   # In Odoo shell or via API
   partner = env['res.partner'].create({
       'name': 'Acme Corp',
       'email': 'contact@acme.com'
   })
   ```

3. **Check account configuration:**
   - Ensure default income account exists
   - Verify journal is configured
   - Check fiscal position settings

---

## Social Media Issues

### Issue: Facebook Token Invalid

**Symptoms:**
- Error: `Invalid token` or `Token expired`
- 401 Unauthorized when posting

**Diagnosis:**
```bash
# Test token validity
curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_TOKEN"

# Check token expiration
curl "https://graph.facebook.com/v19.0/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_APP_TOKEN"
```

**Solutions:**

1. **Generate new long-lived token:**
   - Go to Facebook Developers → Tools → Access Token Tool
   - Generate new Page Access Token
   - Select "Never expire" option (60 days max)
   - Update .env file

2. **Extend token expiration:**
   ```bash
   curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
   ```

3. **Verify permissions:**
   - Token must have `pages_manage_posts` permission
   - Token must have `pages_read_engagement` for metrics
   - Regenerate with correct permissions if missing

### Issue: Instagram Post Fails

**Symptoms:**
- Error: `Container not ready` or `Publishing failed`
- Post stuck in pending state

**Diagnosis:**
```bash
# Check container status
curl -X GET "http://localhost:3102/media/CONTAINER_ID" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Solutions:**

1. **Wait for container to finish:**
   - Instagram requires 2-step publishing
   - Container must have status "FINISHED" before publishing
   - Wait up to 30 seconds between steps

2. **Verify image URL:**
   - Image must be publicly accessible (https://)
   - Image format: JPG, PNG (GIF not supported)
   - Image size: Max 8MB
   - Test URL in browser

3. **Check Instagram Business Account:**
   - Verify account is linked to Facebook Page
   - Ensure account has posting permissions
   - Check account is not restricted

### Issue: Twitter Rate Limit Exceeded

**Symptoms:**
- Error: `Rate limit exceeded` or `429 Too Many Requests`
- Tweets not posting

**Diagnosis:**
```bash
# Check rate limit status
curl -X GET "http://localhost:3103/rate_limit_status" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Solutions:**

1. **Wait for rate limit reset:**
   - Twitter limits: 300 tweets per 3 hours
   - Check reset time in rate limit response
   - Queued tweets will retry automatically

2. **Reduce posting frequency:**
   - Edit `config/social_media_config.json`
   - Lower `tweets_per_hour` setting
   - Space out posts more evenly

3. **Use multiple accounts:**
   - Create separate Twitter accounts for different purposes
   - Distribute posts across accounts
   - Configure multiple MCP servers with different credentials

---

## Ralph Wiggum Loop Issues

### Issue: Loop Not Continuing

**Symptoms:**
- Claude stops after each step instead of continuing
- Task remains in In_Progress/ folder
- Stop hook not preventing stop

**Diagnosis:**
```bash
# Test stop hook manually
# Windows:
powershell .claude\hooks\stop.ps1

# Linux/macOS:
./.claude/hooks/stop.sh

# Check exit code
echo $?  # Should be 1 if task in progress, 0 if complete
```

**Solutions:**

1. **Verify stop hook exists:**
   ```bash
   # Windows:
   Test-Path .claude\hooks\stop.ps1

   # Linux/macOS:
   ls -la .claude/hooks/stop.sh
   ```

2. **Make hook executable (Linux/macOS):**
   ```bash
   chmod +x .claude/hooks/stop.sh
   ```

3. **Check task file exists:**
   ```bash
   ls -la AI_Employee_Vault/In_Progress/
   # Should contain .md files for active tasks
   ```

4. **Verify Claude Code settings:**
   - Ensure hooks are enabled in Claude Code settings
   - Check hook execution permissions
   - Review Claude Code logs for hook errors

### Issue: Max Iterations Reached

**Symptoms:**
- Task stops with "Max iterations reached" message
- Task incomplete but loop exits

**Diagnosis:**
```bash
# Check task state file
cat AI_Employee_Vault/In_Progress/task_*.md
# Look for iteration_count and max_iterations
```

**Solutions:**

1. **Increase max iterations:**
   ```json
   // config/ralph_wiggum_config.json
   {
     "autonomous_loop": {
       "max_iterations": 20  // Increase from 10
     }
   }
   ```

2. **Break task into smaller steps:**
   - Reduce number of steps per task
   - Create sub-tasks for complex operations
   - Each step should complete in < 5 minutes

3. **Optimize step execution:**
   - Profile slow steps
   - Cache repeated operations
   - Parallelize independent operations

### Issue: Task Stuck in In_Progress

**Symptoms:**
- Task file remains in In_Progress/ indefinitely
- Loop stopped but task not complete
- Cannot start new tasks

**Diagnosis:**
```bash
# Read task state
cat AI_Employee_Vault/In_Progress/task_*.md

# Check for errors in audit logs
tail -50 AI_Employee_Vault/Audit_Logs/$(date +%Y-%m-%d).json
```

**Solutions:**

1. **Manually complete task:**
   ```bash
   # Move to Done if actually complete
   mv AI_Employee_Vault/In_Progress/task_*.md AI_Employee_Vault/Done/
   ```

2. **Move to Blocked if needs attention:**
   ```bash
   mv AI_Employee_Vault/In_Progress/task_*.md AI_Employee_Vault/Blocked/
   ```

3. **Resume task:**
   ```
   # In Claude Code:
   Resume the task in In_Progress/ and continue from where it left off
   ```

---

## CEO Briefing Issues

### Issue: Briefing Not Generated

**Symptoms:**
- No briefing file created on Monday morning
- Scheduler running but no output

**Diagnosis:**
```bash
# Check scheduler logs
# Look for errors in terminal where scheduler is running

# Manually trigger briefing
python -c "from services.ceo_briefing_service import CEOBriefingService; service = CEOBriefingService(); print(service.generate_weekly_briefing())"
```

**Solutions:**

1. **Verify Odoo has data:**
   - Check Odoo has transactions for the week
   - Ensure invoices and expenses exist
   - Verify date range is correct

2. **Check Business_Goals.md exists:**
   ```bash
   cat AI_Employee_Vault/Business_Goals.md
   # Should contain revenue targets and subscriptions
   ```

3. **Verify scheduler is running:**
   ```bash
   # Check process
   ps aux | grep ceo_briefing_scheduler

   # Restart scheduler
   python AI_Employee_Vault/scheduler/ceo_briefing_scheduler.py
   ```

### Issue: Briefing Missing Data

**Symptoms:**
- Briefing generated but sections are empty
- Revenue shows $0
- No bottlenecks detected

**Diagnosis:**
```bash
# Check Odoo connection
curl http://localhost:3100/health

# Check transaction data
curl -X GET "http://localhost:3100/transactions/summary?start_date=2026-02-01&end_date=2026-02-07" \
  -H "X-API-Key: YOUR_API_KEY"
```

**Solutions:**

1. **Import historical data:**
   - Add past transactions to Odoo
   - Ensure transactions have correct dates
   - Verify transaction types (invoice, payment, expense)

2. **Check date range:**
   - Briefing uses Monday-Sunday week
   - Verify system timezone matches business timezone
   - Adjust date range if needed

3. **Verify vault data:**
   ```bash
   # Check for completed tasks
   ls -la AI_Employee_Vault/Done/

   # Check for social media metrics
   ls -la AI_Employee_Vault/Social_Media_Metrics/
   ```

---

## Queue and Error Recovery Issues

### Issue: Operations Not Retrying

**Symptoms:**
- Failed operations remain in Queue/ indefinitely
- No retry attempts logged
- Queue processing not working

**Diagnosis:**
```bash
# Check queue files
ls -la AI_Employee_Vault/Queue/

# Read queue file
cat AI_Employee_Vault/Queue/operation_*.json
```

**Solutions:**

1. **Manually process queue:**
   ```python
   from services.queue_service import QueueService
   queue_service = QueueService()
   queue_service.process_queue()
   ```

2. **Check retry schedule:**
   ```json
   // Queue file should have next_retry timestamp
   {
     "next_retry": "2026-02-05T10:45:00Z",
     "retry_count": 2
   }
   ```

3. **Verify exponential backoff:**
   - Retry 1: 2 minutes
   - Retry 2: 4 minutes
   - Retry 3: 8 minutes
   - Retry 4: 16 minutes
   - Retry 5+: 30 minutes

### Issue: Queue Expired Operations

**Symptoms:**
- Alert: "Operation expired after 24 hours"
- Operation never succeeded

**Diagnosis:**
```bash
# Check expired operations
python -c "from services.queue_service import QueueService; service = QueueService(); print(service.check_expired_operations())"
```

**Solutions:**

1. **Investigate root cause:**
   - Check audit logs for error details
   - Verify external service is accessible
   - Test operation manually

2. **Retry manually:**
   ```python
   # Read operation details from queue file
   # Retry operation with corrected parameters
   ```

3. **Adjust expiry time:**
   ```python
   # In queue_service.py
   self.expiry_hours = 48  # Increase from 24
   ```

---

## Audit Logging Issues

### Issue: Logs Not Created

**Symptoms:**
- No log files in Audit_Logs/ directory
- Actions not being logged

**Diagnosis:**
```bash
# Check directory permissions
ls -la AI_Employee_Vault/Audit_Logs/

# Test log creation
python -c "from services.audit_service import AuditService; service = AuditService(); service.log_action('test', 'user', 'target', {}, 'success')"
```

**Solutions:**

1. **Create directory:**
   ```bash
   mkdir -p AI_Employee_Vault/Audit_Logs
   chmod 755 AI_Employee_Vault/Audit_Logs
   ```

2. **Check disk space:**
   ```bash
   df -h
   # Ensure sufficient space available
   ```

3. **Verify permissions:**
   ```bash
   # Ensure write permissions
   touch AI_Employee_Vault/Audit_Logs/test.json
   rm AI_Employee_Vault/Audit_Logs/test.json
   ```

### Issue: Sensitive Data in Logs

**Symptoms:**
- Passwords or tokens visible in audit logs
- Compliance violation

**Diagnosis:**
```bash
# Search for sensitive patterns
grep -r "password" AI_Employee_Vault/Audit_Logs/
grep -r "token" AI_Employee_Vault/Audit_Logs/
```

**Solutions:**

1. **Verify redaction is working:**
   ```python
   from services.audit_service import AuditService
   service = AuditService()

   # Test redaction
   data = {"password": "secret123", "api_key": "abc123"}
   redacted = service.redact_sensitive_data(data)
   print(redacted)  # Should show "***REDACTED***"
   ```

2. **Add more redaction patterns:**
   ```python
   # In audit_service.py
   sensitive_keys = [
       'password', 'token', 'api_key', 'secret',
       'access_token', 'refresh_token', 'bearer_token',
       'private_key', 'ssh_key', 'credit_card'
   ]
   ```

3. **Rotate logs immediately:**
   ```bash
   # Archive current logs
   tar -czf audit_logs_backup_$(date +%Y%m%d).tar.gz AI_Employee_Vault/Audit_Logs/

   # Clear sensitive logs
   rm AI_Employee_Vault/Audit_Logs/*.json
   ```

---

## Performance Issues

### Issue: Slow CEO Briefing Generation

**Symptoms:**
- Briefing takes > 5 minutes to generate
- High CPU usage during generation

**Diagnosis:**
```bash
# Profile briefing generation
python -m cProfile -o briefing.prof -c "from services.ceo_briefing_service import CEOBriefingService; service = CEOBriefingService(); service.generate_weekly_briefing()"

# Analyze profile
python -m pstats briefing.prof
```

**Solutions:**

1. **Optimize Odoo queries:**
   - Add indexes to frequently queried fields
   - Use batch queries instead of individual requests
   - Cache transaction data

2. **Reduce data processing:**
   - Limit transaction history to last 90 days
   - Sample large datasets instead of processing all
   - Use incremental updates

3. **Parallelize operations:**
   - Process revenue and expenses in parallel
   - Use multiprocessing for independent calculations

### Issue: High Memory Usage

**Symptoms:**
- System runs out of memory
- MCP servers crash with OOM errors

**Diagnosis:**
```bash
# Monitor memory usage
# Windows:
tasklist /FI "IMAGENAME eq node.exe" /FO TABLE
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE

# Linux/macOS:
ps aux | grep -E "node|python" | awk '{print $2, $4, $11}'
```

**Solutions:**

1. **Increase system memory:**
   - Add more RAM (8GB minimum, 16GB recommended)
   - Configure swap space (Linux)

2. **Optimize memory usage:**
   - Process data in chunks instead of loading all at once
   - Clear caches periodically
   - Use generators instead of lists for large datasets

3. **Restart services periodically:**
   ```bash
   # Add to cron/Task Scheduler
   # Restart MCP servers daily at 3 AM
   0 3 * * * /path/to/restart_mcp_servers.sh
   ```

---

## Security Issues

### Issue: Unauthorized API Access

**Symptoms:**
- Unexpected API calls in audit logs
- Unknown operations in queue

**Diagnosis:**
```bash
# Check audit logs for suspicious activity
grep "INVALID_API_KEY" AI_Employee_Vault/Audit_Logs/*.json

# Review recent operations
tail -100 AI_Employee_Vault/Audit_Logs/$(date +%Y-%m-%d).json
```

**Solutions:**

1. **Rotate MCP_API_KEY immediately:**
   ```bash
   # Generate new key
   openssl rand -hex 32

   # Update .env
   MCP_API_KEY=new_secure_key

   # Restart all MCP servers
   ```

2. **Review access logs:**
   - Check for unauthorized IP addresses
   - Look for unusual access patterns
   - Verify all operations are legitimate

3. **Implement IP whitelisting:**
   ```javascript
   // In shared-utils.js
   const allowedIPs = ['127.0.0.1', '::1'];

   function authenticateApiKey(req, res, next) {
     const clientIP = req.ip;
     if (!allowedIPs.includes(clientIP)) {
       return res.status(403).json({error: 'Forbidden'});
     }
     // ... rest of authentication
   }
   ```

### Issue: Credentials Exposed

**Symptoms:**
- .env file committed to git
- Credentials visible in logs or error messages

**Diagnosis:**
```bash
# Check git history
git log --all --full-history -- .env

# Search for exposed credentials
grep -r "password" .
grep -r "api_key" .
```

**Solutions:**

1. **Remove from git history:**
   ```bash
   # Remove .env from git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (WARNING: destructive)
   git push origin --force --all
   ```

2. **Rotate all credentials:**
   - Generate new Odoo password
   - Regenerate Facebook/Instagram tokens
   - Regenerate Twitter API keys
   - Generate new MCP_API_KEY

3. **Add to .gitignore:**
   ```bash
   echo ".env" >> .gitignore
   echo "*.log" >> .gitignore
   echo "AI_Employee_Vault/Audit_Logs/*.json" >> .gitignore
   git add .gitignore
   git commit -m "Add sensitive files to .gitignore"
   ```

---

## Getting Help

If you can't resolve an issue:

1. **Check audit logs:**
   ```bash
   tail -100 AI_Employee_Vault/Audit_Logs/$(date +%Y-%m-%d).json
   ```

2. **Run health check:**
   ```bash
   python scripts/health_check.py
   ```

3. **Collect diagnostic info:**
   ```bash
   # System info
   python --version
   node --version

   # Service status
   curl http://localhost:3100/health
   curl http://localhost:3101/health
   curl http://localhost:3102/health
   curl http://localhost:3103/health

   # Recent errors
   grep "error" AI_Employee_Vault/Audit_Logs/*.json | tail -20
   ```

4. **Report issue:**
   - GitHub Issues: https://github.com/your-org/ai-employee/issues
   - Include diagnostic info above
   - Describe steps to reproduce
   - Attach relevant log excerpts (redact sensitive data)

## Related Documentation

- [Setup Guide](gold-tier-setup.md)
- [API Credentials Guide](api-credentials.md)
- [Skills Documentation](.claude/skills/)
