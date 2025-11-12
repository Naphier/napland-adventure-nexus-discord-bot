# Napland Adventure Nexus Discord Bot - Deployment Guide

This guide provides a complete overview of deploying the Discord bot to either **AWS Lambda** or **self-hosted CentOS server**. The codebase now supports both platforms seamlessly.

## Quick Start

### For Self-Hosted Deployment (CentOS 7.9)

1. **Prepare the code** (do this first):
   - Follow: [`self-host-code-plan.md`](./self-host-code-plan.md)
   - Makes: Code changes to support self-hosted mode
   - Time: ~30 minutes

2. **Deploy to server** (do this second):
   - Follow: [`plan.md`](./plan.md)
   - Deploys: Bot to your CentOS server
   - Time: ~1 hour (including SSL certificate setup)

### For Lambda Deployment

- **No code changes needed!** Your existing Lambda deployment continues to work
- The new code is fully backward compatible
- Set `PLATFORM=lambda` (or leave it undefined) in Lambda environment variables
- Deploy as usual

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│         Discord Bot Codebase (Single)               │
│                                                     │
│   app/main.py          (Core logic)                 │
│   app/server.py        (Platform abstraction)       │
│   app/requirements.txt  (Dependencies)              │
└──────────────────────────┬──────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────▼─────────┐    ┌────────▼────────┐
    │   AWS Lambda      │    │  Self-Hosted    │
    │                   │    │  CentOS 7.9     │
    │ PLATFORM=lambda   │    │                 │
    │ (no server.py)    │    │ PLATFORM=       │
    │                   │    │ self-hosted     │
    │ main.lambda_      │    │                 │
    │ handler           │    │ app/server.py   │
    │                   │    │ (port 8443)     │
    └───────────────────┘    └─────────────────┘
```

## Platform Selection

### AWS Lambda

**Best for:**
- Serverless, auto-scaling deployments
- Pay-per-execution pricing
- Minimal infrastructure management
- Variable traffic patterns

**Setup:**
- Deploy Lambda function with handler: `main.lambda_handler`
- Set `PLATFORM=lambda` (or undefined) in Lambda environment
- SSL/TLS handled by API Gateway
- No `server.py` execution

**Configuration:**
```bash
PUBLIC_KEY=<from Discord Portal>
DISCORD_TOKEN=<from Discord Portal>
DATABASE_URL=<your MySQL connection>
PLATFORM=lambda  # (or omit)
```

### Self-Hosted CentOS 7.9

**Best for:**
- Full infrastructure control
- Predictable costs
- Direct system access
- Long-running bot with stable traffic

**Setup:**
- Deploy using `app/server.py` entry point
- Set `PLATFORM=self-hosted` in `.env`
- Use systemd for service management
- SSL/TLS via Let's Encrypt

**Configuration:**
```bash
PUBLIC_KEY=<from Discord Portal>
DISCORD_TOKEN=<from Discord Portal>
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/napland_bot
PLATFORM=self-hosted
BOT_PORT=8443
CERT_PATH=/etc/letsencrypt/live/your-domain.com
```

## Deployment Timeline

### Phase 1: Code Preparation (Before Any Deployment)

1. Create `app/server.py` from `self-host-code-plan.md` Step 1
2. Update `app/requirements.txt` with new dependencies
3. Test locally (optional): `python3 app/server.py`
4. Commit and push changes

**Duration:** ~30 minutes

### Phase 2: Infrastructure Setup (Self-Hosted Only)

1. Update CentOS 7.9 system
2. Install Python 3, pip, Git
3. Obtain SSL certificate from Let's Encrypt
4. Configure firewall (port 8443)
5. Set up Discord Developer Portal endpoint

**Duration:** ~30 minutes

### Phase 3: Deployment (Self-Hosted Only)

1. Clone repository to `/opt/napland-bot`
2. Create Python virtual environment
3. Install dependencies from requirements.txt
4. Create `.env` with configuration
5. Set up systemd service
6. Start and verify service

**Duration:** ~30 minutes

## Pre-Deployment Checklist

### For Both Platforms

- [ ] Discord bot application created in Discord Developer Portal
- [ ] `PUBLIC_KEY` obtained from Discord Portal > General Information
- [ ] `DISCORD_TOKEN` obtained from Discord Portal > Bot
- [ ] MySQL database exists with correct credentials
- [ ] `DATABASE_URL` connection string verified and working

### For Self-Hosted Only

- [ ] CentOS 7.9 server prepared
- [ ] Domain name obtained and DNS configured
- [ ] SSH access to server confirmed
- [ ] Firewall allows port 8443 inbound
- [ ] Let's Encrypt certificate obtained for domain
- [ ] Certificate readable by `discordbot` user

### For Lambda Only

- [ ] AWS account access
- [ ] Lambda execution role with appropriate permissions
- [ ] API Gateway endpoint configured
- [ ] Discord Portal Interactions Endpoint URL updated

## Switching Between Platforms

The bot supports seamless platform switching via the `PLATFORM` environment variable:

```bash
# For Lambda
export PLATFORM=lambda
# Lambda uses main.lambda_handler directly

# For Self-Hosted
export PLATFORM=self-hosted
# Systemd service executes app/server.py
```

**To switch:** Simply change the environment variable and restart/redeploy.

## File Structure After Updates

```
napland-adventure-nexus-discord-bot/
├── README.md
├── DEPLOYMENT_GUIDE.md          (This file)
├── plan.md                       (Self-hosted deployment steps)
├── self-host-code-plan.md       (Code changes needed)
├── app/
│   ├── __init__.py
│   ├── main.py                   (Core logic - unchanged)
│   ├── server.py                 (NEW - Platform abstraction)
│   ├── database_handler_sql.py
│   ├── database_connector.py
│   ├── log_hours_handler.py
│   ├── display_handler.py
│   ├── discord_utils.py
│   ├── logger.py
│   ├── utils.py
│   ├── requirements.txt           (Updated with Flask, etc.)
│   ├── requirements_dev.txt
│   └── tests/
├── iac/
│   └── (Terraform files for AWS)
```

## Key Configuration Files

### `.env` (Self-Hosted)
Located at: `/opt/napland-bot/.env`

```bash
PLATFORM=self-hosted
PUBLIC_KEY=your_key
DISCORD_TOKEN=your_token
BOT_PORT=8443
CERT_PATH=/etc/letsencrypt/live/your-domain.com
DATABASE_URL=mysql+pymysql://user:pass@host:3306/napland_bot
```

### `.env` (Lambda)
Configure in Lambda environment variables:

```
PLATFORM=lambda
PUBLIC_KEY=your_key
DISCORD_TOKEN=your_token
DATABASE_URL=mysql+pymysql://user:pass@host:3306/napland_bot
```

### Systemd Service (Self-Hosted Only)
Located at: `/etc/systemd/system/napland-bot.service`

Executes: `python3 app/server.py`

## Security Considerations

### Lambda
- API Gateway handles SSL/TLS
- IAM roles control resource access
- Environment variables stored in AWS Systems Manager Parameter Store

### Self-Hosted
- SSL/TLS via Let's Encrypt certificates
- Firewall rules restrict port access
- Dedicated `discordbot` user (non-root)
- Database credentials in `.env` (file permissions: 600)
- systemd service with automatic restart

## Monitoring and Logs

### Lambda
```bash
# CloudWatch Logs
aws logs tail /aws/lambda/napland-bot --follow
```

### Self-Hosted
```bash
# systemd journalctl
sudo journalctl -u napland-bot -f

# Bot health check
curl https://your-domain.com:8443/health
```

## Troubleshooting

### Common Issues

1. **Discord Endpoint Verification Fails**
   - Verify bot is running: `sudo systemctl status napland-bot`
   - Check firewall: `sudo firewall-cmd --list-ports`
   - Verify certificate: `openssl s_client -connect your-domain.com:8443`

2. **Database Connection Error**
   - Verify MySQL running: `mysql -u user -p -e "SHOW DATABASES;"`
   - Check DATABASE_URL format
   - Verify credentials in `.env`

3. **Port Already in Use**
   - Check: `sudo lsof -i :8443`
   - Kill: `sudo kill -9 <PID>`
   - Or change BOT_PORT to different port

4. **Certificate Not Found**
   - Verify path: `ls -la /etc/letsencrypt/live/your-domain.com/`
   - Check permissions: `sudo chgrp discordbot /etc/letsencrypt/live/`

### Debug Mode

For troubleshooting, you can test the server locally:

```bash
cd /opt/napland-bot
source venv/bin/activate
export PLATFORM=self-hosted
export PUBLIC_KEY=your_key
export DISCORD_TOKEN=your_token
export DATABASE_URL=mysql+pymysql://user:pass@host:3306/napland_bot
export BOT_PORT=8443
export CERT_PATH=/etc/letsencrypt/live/your-domain.com

python3 app/server.py
```

## Support Documentation

- **Code Changes**: See `self-host-code-plan.md`
- **Deployment**: See `plan.md`
- **Discord Developer Portal**: https://discord.com/developers/applications
- **Let's Encrypt**: https://letsencrypt.org/
- **CentOS 7 Documentation**: https://wiki.centos.org/

## Next Steps

**Choose your deployment platform:**

1. **Self-Hosted (CentOS 7.9)**
   - Start: `self-host-code-plan.md` for code changes
   - Then: `plan.md` for deployment

2. **AWS Lambda**
   - No changes needed
   - Deploy using existing Lambda workflow
   - Set `PLATFORM=lambda` in environment

## Version Information

- **Bot Version**: 0.0.1
- **Python**: 3.6+
- **CentOS**: 7.9.2009
- **MySQL**: 5.7+ recommended
- **Discord.py**: See `requirements.txt`
