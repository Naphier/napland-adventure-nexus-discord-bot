# Code Update Plan: Platform-Agnostic Discord Bot (Lambda + Self-Hosted)

This document outlines the code changes needed to make your Discord bot compatible with both AWS Lambda and self-hosted deployments. The same codebase can now run on either platform via a simple environment variable configuration.

## Overview

Your current `main.py` is designed for AWS Lambda. We'll refactor it to be platform-agnostic by:

1. Creating a platform abstraction layer that detects the runtime environment
2. Using Flask web server for self-hosted deployments
3. Maintaining full Lambda compatibility for AWS deployments
4. Handling HTTPS/SSL certificates for self-hosted setups
5. Updating dependencies to include Flask and MySQL support
6. Using environment variables to control platform selection

## Step 1: Create the Platform-Agnostic Server File

Create a new file: `app/server.py`

This file automatically detects the deployment platform and runs accordingly.

```python
from flask import Flask, request, jsonify
from main import lambda_handler
import os
import ssl
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get configuration from environment variables
PLATFORM = os.getenv('PLATFORM', 'self-hosted').lower()
BOT_PORT = int(os.getenv('BOT_PORT', '8443'))
CERT_PATH = os.getenv('CERT_PATH', '/etc/letsencrypt/live/your-domain.com')

@app.route('/interactions', methods=['POST'])
def interactions():
    """Handle Discord bot interactions"""
    try:
        logger.info("Received interaction request")
        
        # Convert Flask request to Lambda-like event format
        event = {
            'body': request.get_data(as_text=True),
            'headers': {
                'x-signature-ed25519': request.headers.get('x-signature-ed25519'),
                'x-signature-timestamp': request.headers.get('x-signature-timestamp')
            }
        }
        
        # Call the existing Lambda handler
        response = lambda_handler(event, None)
        
        logger.info(f"Response status: {response.get('statusCode', 200)}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing interaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'platform': PLATFORM,
        'port': BOT_PORT
    }), 200

def run_self_hosted():
    """Run as self-hosted HTTPS server"""
    try:
        # Create SSL context
        logger.info(f"Loading SSL certificates from {CERT_PATH}")
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(
            f'{CERT_PATH}/fullchain.pem',
            f'{CERT_PATH}/privkey.pem'
        )
        
        # Start Flask server with HTTPS
        logger.info(f"Starting bot as SELF-HOSTED on 0.0.0.0:{BOT_PORT}")
        app.run(
            host='0.0.0.0',
            port=BOT_PORT,
            ssl_context=ssl_context,
            debug=False,
            use_reloader=False
        )
    except FileNotFoundError as e:
        logger.error(f"SSL certificate files not found: {e}")
        logger.error(f"Expected path: {CERT_PATH}")
        exit(1)
    except Exception as e:
        logger.error(f"Failed to start self-hosted server: {e}")
        exit(1)

def run_lambda():
    """Run as AWS Lambda - returns lambda_handler function"""
    logger.info("Initializing for AWS LAMBDA deployment")
    logger.info("This server.py should not be executed in Lambda environment")
    logger.info("Use the lambda_handler from main.py instead")
    return lambda_handler

def main():
    """Entry point - platform selection"""
    if PLATFORM == 'lambda':
        logger.warning("Lambda mode detected but running via server.py")
        logger.warning("For Lambda, use the lambda_handler from main.py directly")
        sys.exit(1)
    elif PLATFORM in ['self-hosted', 'selfhosted', 'localhost']:
        run_self_hosted()
    else:
        logger.error(f"Unknown PLATFORM: {PLATFORM}")
        logger.error(f"Valid options: 'lambda', 'self-hosted'")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Step 1b: Update main.py (Minimal Changes for Platform Awareness)

Update `app/main.py` to be aware of the platform but maintain backward compatibility:

```python
# Add these imports at the top
import os

# ... existing imports ...

# Add platform detection (optional, for logging/debugging)
PLATFORM = os.getenv('PLATFORM', 'lambda')

def lambda_handler(event, context):
    """
    Main handler function - works on both Lambda and Self-Hosted
    
    Args:
        event: Dict with 'body' (JSON string) and 'headers' dict
        context: Lambda context (None when called from self-hosted)
    
    Returns:
        Dict with 'statusCode' and 'body' keys
    """
    if _is_eventbridge_event(event):
        return handle_display_event(event)

    if "body" not in event:
        LOG.error("Discord interaction payload missing body")
        return _error_response("Invalid request payload")

    # ... rest of existing lambda_handler code remains unchanged ...
```

This change is minimal - the existing `lambda_handler` remains the same and works on both platforms.

## Step 2: Update requirements.txt

Add the following dependencies to `app/requirements.txt`:

```
flask>=2.3.0
pyopenssl>=23.0.0
pymysql>=1.1.0
sqlalchemy>=2.0.0
```

**Note:** Keep all existing dependencies that are already listed. These new packages are lightweight and won't affect Lambda deployments (they'll just be packaged but not necessarily used in Lambda mode).

## Step 3: Update Environment Variables

Update your `.env` file (or create it if it doesn't exist) with:

```bash
# Platform Selection (REQUIRED)
# Options: 'lambda' or 'self-hosted'
# Lambda users: Keep as 'lambda' (don't deploy via server.py)
# Self-hosted users: Set to 'self-hosted'
PLATFORM=self-hosted

# Discord Bot Configuration
PUBLIC_KEY=your_discord_public_key_here
DISCORD_TOKEN=your_discord_bot_token_here

# Server Configuration (Only needed for self-hosted platform)
BOT_PORT=8443
CERT_PATH=/etc/letsencrypt/live/your-domain.com

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/napland_bot
```

### Environment Variable Reference:

| Variable | Platform | Required | Example | Purpose |
|----------|----------|----------|---------|---------|
| `PLATFORM` | Both | Yes | `self-hosted` | Selects deployment mode (`lambda` or `self-hosted`) |
| `PUBLIC_KEY` | Both | Yes | From Discord Portal | Discord bot verification |
| `DISCORD_TOKEN` | Both | Yes | From Discord Portal | Discord API authentication |
| `BOT_PORT` | Self-hosted | Yes | `8443` | HTTPS listening port |
| `CERT_PATH` | Self-hosted | Yes | `/etc/letsencrypt/live/domain.com` | SSL certificate directory |
| `DATABASE_URL` | Both | Depends | `mysql+pymysql://user:pass@host/db` | Database connection string |

### How to get these values:

- **PUBLIC_KEY**: From [Discord Developer Portal](https://discord.com/developers/applications) > Your App > General Information > Public Key
- **DISCORD_TOKEN**: From Discord Developer Portal > Your App > Bot > TOKEN
- **PLATFORM**: 
  - For Lambda deployment: `lambda`
  - For self-hosted: `self-hosted`
- **BOT_PORT**: The custom HTTPS port (default: 8443, can be 9443, 9999, etc.)
  - Only needed for self-hosted deployments
- **CERT_PATH**: Path to your Let's Encrypt certificates
  - If using Let's Encrypt: `/etc/letsencrypt/live/your-domain.com`
  - Replace `your-domain.com` with your actual domain
  - Only needed for self-hosted deployments
- **DATABASE_URL**: Your MySQL connection string
  - Format: `mysql+pymysql://username:password@host:port/database`
  - Example: `mysql+pymysql://napland_user:secure_password@localhost:3306/napland_bot`

## Step 4: Obtain SSL Certificates

Before running the server, you need SSL certificates. Use Let's Encrypt:

```bash
sudo yum install -y certbot

# Obtain certificate (choose one method)

# Method 1: Standalone (requires port 80/443 temporarily)
sudo certbot certonly --standalone -d your-domain.com

# Method 2: If you have an existing webserver, use webroot
sudo certbot certonly --webroot -w /path/to/webroot -d your-domain.com
```

Certificate will be located at: `/etc/letsencrypt/live/your-domain.com/`

**Make sure the `discordbot` user can read these certificates:**

```bash
sudo chgrp -R discordbot /etc/letsencrypt/live/
sudo chmod -R g+rx /etc/letsencrypt/live/
```

## Step 5: Configure Discord Developer Portal

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Navigate to **General Information**
4. Scroll to "Interactions Endpoint URL"
5. Enter: `https://your-domain.com:8443/interactions`
6. Click Save
7. Discord will send a validation request to verify the endpoint
8. Your bot should respond with the verification challenge (type 1)

**Note:** This is done by the existing lambda_handler, so it should work automatically once the server is running.

## Step 6: Update Database Connection (if needed)

If you're using a MySQL database that requires special connection handling, update `app/database_handler_sql.py` or relevant files to use the `DATABASE_URL` environment variable:

```python
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
```

Verify that your existing database handler can work with this URL format.

## Step 7: Test the Server Locally (Optional)

Before deploying, you can test the server on your local machine:

```bash
cd /path/to/napland-bot
source venv/bin/activate
export PLATFORM=self-hosted
export PUBLIC_KEY=your_key
export DISCORD_TOKEN=your_token
export DATABASE_URL=mysql+pymysql://user:pass@localhost/napland_bot
export BOT_PORT=8443
export CERT_PATH=/path/to/certs

# Run directly (for testing)
python3 app/server.py
```

### Testing with HTTP (for development only):

If you want to test without SSL certificates, you can temporarily modify `server.py` to use HTTP:

```python
# In run_self_hosted(), replace the SSL section with:
logger.info(f"Starting bot on http://0.0.0.0:{BOT_PORT} (DEVELOPMENT ONLY)")
app.run(
    host='0.0.0.0',
    port=BOT_PORT,
    debug=False,
    use_reloader=False
)
```

**Note:** This is development-only. Discord requires HTTPS for production deployments.

## Step 8: Verify Directory Structure

After all changes, your `app/` directory should contain:

```
app/
├── __init__.py
├── main.py (existing, unchanged)
├── server.py (NEW - platform-agnostic server for self-hosted)
├── database_handler_sql.py (existing)
├── database_connector.py (existing)
├── [other existing files...]
└── requirements.txt (updated with new dependencies)
```

**Lambda Deployment:** Lambda will continue to use `main.py` with the `lambda_handler` function directly. The `server.py` file will be included in the package but not used.

**Self-Hosted Deployment:** Self-hosted will use `server.py` which internally calls `lambda_handler` from `main.py`.

## Step 9: Install Dependencies

When you deploy to the server:

```bash
cd /opt/napland-bot
source venv/bin/activate
pip install -r requirements.txt
```

## Summary of Changes

| File | Change | Type | Lambda | Self-Hosted |
|------|--------|------|--------|-------------|
| `app/main.py` | Add PLATFORM awareness (minimal changes) | Updated | Used | Used |
| `app/server.py` | Create platform-agnostic server | New File | Ignored | Used |
| `requirements.txt` | Add Flask, PyOpenSSL, PyMySQL, SQLAlchemy | Updated | Packaged* | Used |
| `.env` | Add PLATFORM, BOT_PORT, CERT_PATH | Updated | Minimal | Required |
| Discord Portal | Set Interactions Endpoint URL | Configuration | N/A | Required |
| SSL Certificates | Obtain from Let's Encrypt | One-time Setup | N/A | Required |

*Lambda packaging includes the dependencies but they're not actively used since Lambda uses the `lambda_handler` directly.

## Deployment Guide by Platform

### For Lambda Deployments

**No changes needed!** Lambda will continue to work exactly as before:

1. Set `PLATFORM=lambda` (or leave it undefined, as Lambda is the default)
2. Deploy your Lambda function as usual, pointing to `main.lambda_handler` as the handler
3. The new `server.py` file will be included in the deployment package but won't be executed
4. Environment variables are still used the same way in Lambda
5. No SSL certificates needed for Lambda

```bash
# Lambda deployment (using SAM or Serverless Framework)
# Handler: main.lambda_handler
# No server.py execution needed
```

### For Self-Hosted Deployments

1. Set `PLATFORM=self-hosted` in `.env`
2. Deploy using `app/server.py` as the entry point
3. Systemd service file should execute: `python3 app/server.py`
4. SSL certificates are required (obtained from Let's Encrypt)
5. All environment variables must be set in `.env`

See `plan.md` for complete self-hosted deployment instructions.

## Troubleshooting

### For Lambda Deployments

If you're still using Lambda and encounter issues:

**Lambda continues to work unchanged:** The new code is fully backward compatible. Just ensure:
- Your Lambda function still points to `main.lambda_handler`
- Environment variables (`PUBLIC_KEY`, `DISCORD_TOKEN`, etc.) are set in Lambda environment
- No `server.py` execution in Lambda environment
- The `server.py` file is just ignored by Lambda

### For Self-Hosted Deployments

If PLATFORM is set to `self-hosted`, the following issues may occur:

#### Certificate Loading Error
```
SSL certificate files not found: [Errno 2] No such file or directory
```
**Solution:** Verify certificate path and ensure `discordbot` user can read the files:
```bash
ls -la /etc/letsencrypt/live/your-domain.com/
sudo chgrp -R discordbot /etc/letsencrypt/live/
sudo chmod -R g+rx /etc/letsencrypt/live/
```

#### Port Already in Use
```
Address already in use
```
**Solution:** Either change `BOT_PORT` in `.env` or kill the existing process:
```bash
sudo lsof -i :8443  # find what's using the port
sudo kill -9 <PID>
```

#### Flask Import Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** Ensure you've installed requirements:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### PLATFORM Environment Variable Not Set
If you see the bot starting in self-hosted mode but you expected Lambda:

**Solution:** Explicitly set `PLATFORM=lambda` in your Lambda environment variables or in local `.env` for testing.

#### Discord Endpoint Verification Fails
- Ensure server is running on the correct port
- Verify certificate is valid for your domain
- Check firewall allows inbound connections on the port
- Check bot logs: `sudo journalctl -u napland-bot -f`
- Verify `PLATFORM=self-hosted` in `.env`

## Next Steps

1. Make the code changes described in Steps 1-6
2. Obtain SSL certificates (Step 4) - **self-hosted only**
3. Configure Discord Developer Portal (Step 5) - **self-hosted only**
4. For self-hosted: Follow the Deployment Plan in `plan.md` to deploy to your server
5. For Lambda: Deploy using your normal Lambda workflow

## Choosing Your Platform

### Choose **Lambda** if:
- You want AWS to manage infrastructure and scaling
- You prefer pay-as-you-go pricing
- You don't want to manage servers or certificates
- Your bot has bursty, unpredictable traffic patterns
- Set `PLATFORM=lambda` (or leave undefined)

### Choose **Self-Hosted** if:
- You want full control over your infrastructure
- You already have a CentOS server
- You prefer fixed monthly costs
- You need direct access to logs and system resources
- Set `PLATFORM=self-hosted`

### The Code Supports Both
Your single codebase now supports both platforms seamlessly. You can even switch between them by just changing the `PLATFORM` environment variable!
