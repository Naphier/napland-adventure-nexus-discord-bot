# Update Summary: Platform-Agnostic Bot Deployment

## Overview

The Discord bot codebase has been refactored to support **both AWS Lambda and self-hosted deployments** simultaneously. The same codebase now runs on either platform via the `PLATFORM` environment variable.

## What Changed

### Files Updated

1. **`self-host-code-plan.md`** - Refactored as platform-agnostic guide
   - Step 1: Create `app/server.py` with platform detection
   - Includes both Lambda and self-hosted configurations
   - Deployment instructions for both platforms
   - Comprehensive troubleshooting for each platform

2. **`plan.md`** - Self-hosted deployment plan
   - References the new code changes
   - Instructions for CentOS 7.9 deployment
   - Updated to use `app/server.py`
   - System service configuration

3. **`DEPLOYMENT_GUIDE.md`** - NEW comprehensive guide
   - Overview of both deployment options
   - Architecture diagrams
   - Quick-start instructions
   - Security considerations
   - Monitoring and troubleshooting

### Code Changes Required

Create new file: **`app/server.py`**

This file:
- Detects `PLATFORM` environment variable
- Routes to appropriate execution mode (Lambda or self-hosted)
- Handles HTTPS/SSL for self-hosted mode
- Provides Flask web server wrapper
- Maintains backward compatibility with `main.lambda_handler`

Update: **`app/requirements.txt`**

Add:
```
flask>=2.3.0
pyopenssl>=23.0.0
pymysql>=1.1.0
sqlalchemy>=2.0.0
```

## Platform Selection

### AWS Lambda (PLATFORM=lambda)
- ✅ No code changes needed for existing Lambda deployments
- ✅ `main.lambda_handler` continues to work unchanged
- ✅ New dependencies packaged but not used
- ⚠️ Don't execute `server.py` in Lambda environment
- ✅ Fully backward compatible

### Self-Hosted (PLATFORM=self-hosted)
- ✅ Execute `app/server.py` as entry point
- ✅ Uses Flask with HTTPS/SSL
- ✅ Runs on custom port (default 8443)
- ✅ systemd service management
- ✅ Full infrastructure control

## Environment Variables

### Both Platforms
```bash
PLATFORM=lambda  # or self-hosted
PUBLIC_KEY=<from Discord Portal>
DISCORD_TOKEN=<from Discord Portal>
DATABASE_URL=<MySQL connection string>
```

### Self-Hosted Only
```bash
BOT_PORT=8443
CERT_PATH=/etc/letsencrypt/live/your-domain.com
```

## Backward Compatibility

✅ **Fully maintained**

- Existing Lambda deployments require NO code changes
- Existing environment variables continue to work
- New code is an abstraction layer on top of existing `main.py`
- `main.lambda_handler` unchanged and still functional
- Can switch between platforms anytime via `PLATFORM` variable

## Documentation Structure

```
DEPLOYMENT_GUIDE.md        ← Start here for overview
├── Quick Start
├── Architecture
├── Platform Selection
└── Troubleshooting

self-host-code-plan.md     ← Code changes required
├── Step 1-9: Implementation
├── Environment setup
└── Testing

plan.md                    ← Infrastructure deployment
├── Pre-deployment
├── System setup
├── Deployment steps
├── Service configuration
└── Monitoring
```

## Migration Path

### From Lambda to Self-Hosted

1. Update code using `self-host-code-plan.md`
2. Deploy using `plan.md`
3. Set `PLATFORM=self-hosted` in `.env`
4. Keep Lambda running until verified

### From Self-Hosted to Lambda

1. Deploy to Lambda normally
2. Set `PLATFORM=lambda` in Lambda environment
3. Disable self-hosted service: `sudo systemctl disable napland-bot`
4. Bot works with same codebase

## Testing

### Before Deployment

```bash
# Test self-hosted mode locally
export PLATFORM=self-hosted
export PUBLIC_KEY=your_key
export DISCORD_TOKEN=your_token
export BOT_PORT=8443
export CERT_PATH=/path/to/certs
python3 app/server.py

# Test health endpoint
curl https://localhost:8443/health
```

### After Deployment

```bash
# Check service status
sudo systemctl status napland-bot

# View logs
sudo journalctl -u napland-bot -f

# Health check
curl https://your-domain.com:8443/health
```

## Next Actions

1. **Review** the three documentation files:
   - `DEPLOYMENT_GUIDE.md` - Overview
   - `self-host-code-plan.md` - Code changes
   - `plan.md` - Deployment steps

2. **Implement** code changes from `self-host-code-plan.md`:
   - Create `app/server.py`
   - Update `requirements.txt`
   - Set environment variables

3. **Deploy** using `plan.md`:
   - For self-hosted: Follow all steps
   - For Lambda: No additional steps needed

## Key Benefits

- ✅ **Flexibility**: Choose deployment platform anytime
- ✅ **No Duplication**: Single codebase for both platforms
- ✅ **Backward Compatible**: Existing Lambda works unchanged
- ✅ **Easy Switching**: Just change `PLATFORM` variable
- ✅ **Scalable**: Grow from self-hosted to Lambda or vice versa
- ✅ **Future-Proof**: Easy to add new platforms

## Support

For issues or questions:
- Self-hosted: See `self-host-code-plan.md` troubleshooting
- Lambda: See `self-host-code-plan.md` Lambda section
- General: See `DEPLOYMENT_GUIDE.md`
