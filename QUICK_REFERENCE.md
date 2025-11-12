# Quick Reference: Bot Deployment Cheat Sheet

## Platform Selection Matrix

| Aspect | AWS Lambda | Self-Hosted |
|--------|-----------|------------|
| **Code Entry Point** | `main.lambda_handler` | `app/server.py` |
| **PLATFORM Value** | `lambda` (or undefined) | `self-hosted` |
| **Requires Server** | ❌ No | ✅ Yes (CentOS 7.9) |
| **Requires SSL Cert** | ❌ No (API Gateway) | ✅ Yes (Let's Encrypt) |
| **Port Configuration** | N/A | `BOT_PORT=8443` |
| **Cost Model** | Pay-per-execution | Fixed monthly |
| **Scaling** | Auto | Manual |
| **Infrastructure** | Managed by AWS | Self-managed |
| **Code Changes** | ❌ None | ✅ Required |

## Environment Variables Checklist

### Always Required
- [ ] `PUBLIC_KEY` - From Discord Portal > App > General Information
- [ ] `DISCORD_TOKEN` - From Discord Portal > App > Bot > Token
- [ ] `DATABASE_URL` - MySQL connection string

### Platform Selection
- [ ] `PLATFORM=lambda` OR `PLATFORM=self-hosted`

### Self-Hosted Only
- [ ] `BOT_PORT` - Default: 8443
- [ ] `CERT_PATH` - SSL certificate directory

## Deployment Checklist

### Phase 1: Code Preparation (All Users)
```bash
# Steps from self-host-code-plan.md:
[ ] Step 1: Create app/server.py
[ ] Step 2: Update requirements.txt
[ ] Step 3: Set environment variables
[ ] Step 9: pip install -r requirements.txt
[ ] Optional: Test locally with python3 app/server.py
```

### Phase 2: Infrastructure (Self-Hosted Only)
```bash
# Steps from plan.md:
[ ] Verify MySQL running
[ ] Install Python 3, pip, Git
[ ] Obtain SSL certificate (Let's Encrypt)
[ ] Configure firewall (port 8443)
[ ] Update Discord Developer Portal Endpoint URL
```

### Phase 3: Deployment (Self-Hosted Only)
```bash
# Steps from plan.md:
[ ] Clone repository to /opt/napland-bot
[ ] Create Python virtual environment
[ ] Install dependencies
[ ] Create .env file with configuration
[ ] Set up systemd service
[ ] Start service: sudo systemctl start napland-bot
[ ] Verify: sudo systemctl status napland-bot
```

## Command Reference

### System Service (Self-Hosted)
```bash
# Start service
sudo systemctl start napland-bot

# Stop service
sudo systemctl stop napland-bot

# View status
sudo systemctl status napland-bot

# View logs
sudo journalctl -u napland-bot -f

# Enable auto-start
sudo systemctl enable napland-bot
```

### Health Checks
```bash
# Check service
curl https://your-domain.com:8443/health

# Check certificate validity
openssl s_client -connect your-domain.com:8443

# Check port listening
sudo netstat -tuln | grep 8443
```

### Troubleshooting Commands
```bash
# Find process using port
sudo lsof -i :8443

# Check certificate path
ls -la /etc/letsencrypt/live/your-domain.com/

# Verify MySQL connection
mysql -u user -p -h localhost

# Test .env variables
source .env && echo $PLATFORM
```

## Files to Create/Update

### New Files
- `app/server.py` - Platform abstraction server

### Files to Update
- `app/requirements.txt` - Add Flask, PyOpenSSL, PyMySQL, SQLAlchemy

### Configuration Files (Create)
- `/opt/napland-bot/.env` - Environment variables (self-hosted only)
- `/etc/systemd/system/napland-bot.service` - System service (self-hosted only)

## Typical Timeline

| Task | Duration | Phase |
|------|----------|-------|
| Code changes | 30 min | Before deployment |
| SSL certificate setup | 15 min | Infrastructure (self-hosted) |
| Server configuration | 30 min | Infrastructure (self-hosted) |
| Bot deployment | 15 min | Deployment (self-hosted) |
| Testing & verification | 15 min | Post-deployment |
| **Total (Self-Hosted)** | **1.75 hours** | All phases |
| **Total (Lambda)** | **0 min** | Already working |

## Endpoints

### Self-Hosted
```
Discord Interactions: https://your-domain.com:8443/interactions
Health Check: https://your-domain.com:8443/health
```

### Lambda
```
Discord Interactions: https://api-gateway-url/interactions
(Configured in Discord Developer Portal)
```

## Common Mistakes to Avoid

❌ **Don't:**
- Run `server.py` in Lambda environment
- Forget to set `PLATFORM` variable
- Use HTTP instead of HTTPS for self-hosted
- Forget to open firewall port 8443
- Hardcode credentials instead of using environment variables
- Run bot as root (use `discordbot` user)
- Deploy before updating Discord Developer Portal endpoint URL

✅ **Do:**
- Set `PLATFORM=self-hosted` for self-hosted deployments
- Use environment variables for all secrets
- Test locally before deploying to server
- Verify service is running after deployment
- Check logs for errors: `journalctl -u napland-bot -f`
- Keep certificates updated with certbot auto-renewal

## Switching Platforms

### Lambda → Self-Hosted
```bash
# 1. Update code (self-host-code-plan.md)
# 2. Deploy infrastructure (plan.md)
# 3. Set in .env:
PLATFORM=self-hosted
# 4. Keep Lambda running as backup during transition
```

### Self-Hosted → Lambda
```bash
# 1. No code changes needed
# 2. Deploy to Lambda normally
# 3. Set in Lambda environment:
PLATFORM=lambda
# 4. Disable self-hosted service:
sudo systemctl disable napland-bot
```

## Documentation Map

```
Start Here
    ↓
DEPLOYMENT_GUIDE.md (overview & architecture)
    ├─→ AWS Lambda? (no changes needed)
    │
    └─→ Self-Hosted?
         ├─→ self-host-code-plan.md (code changes)
         └─→ plan.md (infrastructure & deployment)

Need Help?
    ├─→ UPDATE_SUMMARY.md (what changed)
    ├─→ self-host-code-plan.md (troubleshooting)
    └─→ plan.md (troubleshooting)
```

## Emergency Commands

### Bot Won't Start
```bash
# Check for errors
sudo journalctl -u napland-bot -n 50

# Check if port is in use
sudo lsof -i :8443

# Manually test server (will show errors)
cd /opt/napland-bot
source venv/bin/activate
source .env
python3 app/server.py
```

### Lost Connection to Bot
```bash
# Verify service is running
sudo systemctl status napland-bot

# Restart service
sudo systemctl restart napland-bot

# Check firewall
sudo firewall-cmd --list-ports

# Verify DNS
nslookup your-domain.com
```

### Database Connection Failed
```bash
# Test MySQL locally
mysql -u napland_user -p -h localhost -D napland_bot

# Check connection string in .env
source .env && echo $DATABASE_URL

# Verify user has correct permissions
mysql -u root -p -e "SHOW GRANTS FOR 'napland_user'@'localhost';"
```

---

**Last Updated:** November 10, 2025  
**Version:** 0.0.1  
**Platforms Supported:** AWS Lambda, Self-Hosted CentOS 7.9
