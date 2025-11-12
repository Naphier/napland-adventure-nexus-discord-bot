# Deployment Plan for Napland Adventure Nexus Discord Bot

## System Requirements
- CentOS 7.9.2009
- Python 3.6+ (CentOS 7 default is Python 2.7, so we'll need to install Python 3)
- pip (Python package manager)
- Git (for cloning the repository)
- Systemd (for running the bot as a service)
- MySQL (already running on your system)

## Pre-deployment Steps

1. Update the system
```bash
sudo yum update -y
sudo yum upgrade -y
```

2. Install required system packages
```bash
sudo yum install -y epel-release
sudo yum install -y git python3 python3-pip
```

3. Verify MySQL is running and accessible
```bash
mysql -u root -p -e "SHOW DATABASES;"
```

4. Create a dedicated user for the bot
```bash
sudo useradd -r -s /bin/false discordbot
```

5. Create application directory
```bash
sudo mkdir -p /opt/napland-bot
sudo chown discordbot:discordbot /opt/napland-bot
```

## Discord Bot Setup (Before Deployment)

**Important:** You need to configure your Discord bot application BEFORE deployment.

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)

2. Create a new application or open your existing bot application

3. Under **General Information**, note your:
   - Application ID
   - Public Key (needed for request signature verification)

4. Under **Bot**, create or reveal your bot token and copy it

5. **Set the Interactions Endpoint URL** (This is crucial for self-hosted servers):
   - You'll need your server's public IP/domain and port
   - Set the endpoint to: `https://your-server-domain.com/interactions`
   - Discord will send a POST request to verify the endpoint
   - Your application must respond to the verification challenge (type 1)

6. Under **OAuth2** > **URL Generator**:
   - Select scopes: `bot`
   - Select permissions: `applications.commands`, `chat:write` (adjust based on your needs)
   - Copy the generated URL and authorize your bot to your server

### Network Requirements for Self-Hosted Bot

- Your bot needs a **public IP address** or **domain name**
- An **HTTPS port** must be open and accessible from the internet
- Options for port configuration:
  - **Option 1**: Use a custom HTTPS port (e.g., 8443, 9443) - Discord accepts non-standard ports
  - **Option 2**: Use a subdomain (e.g., bot.your-domain.com) on port 443 with your existing webserver
  - **Option 3**: Run alongside your existing port 443 webserver using a reverse proxy (more complex)
- Consider using Let's Encrypt for free SSL certificates

### Setting Up HTTPS with Self-Hosted Bot

**Option 1: Custom HTTPS Port (Recommended if port 443 is taken)**

1. Choose a custom port (e.g., 8443)
2. Obtain SSL certificate for your domain
```bash
sudo yum install -y certbot
sudo certbot certonly --standalone -d your-domain.com
```

3. Run your bot directly on the custom HTTPS port with SSL
4. Set Discord Interactions Endpoint URL to: `https://your-domain.com:8443/interactions`
5. Make sure the port is open in your firewall:
```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --reload
```

**Option 2: Use a Subdomain on Port 443**

If you want to keep using port 443, you can use a subdomain (bot.your-domain.com) alongside your existing webserver. Your existing webserver would need to be configured to route `bot.your-domain.com` requests to your bot application.

**Option 3: Nginx Reverse Proxy (If you want to use port 443)**

1. Install and configure nginx
```bash
sudo yum install -y nginx
```

2. Configure nginx to proxy requests on port 443 to your internal bot port. See the Nginx Configuration section below.

## Deployment Steps

1. Clone the repository
```bash
cd /opt/napland-bot
sudo -u discordbot git clone https://github.com/Naphier/napland-adventure-nexus-discord-bot.git .
```

2. Set up Python virtual environment
```bash
sudo -u discordbot python3 -m venv venv
sudo -u discordbot source venv/bin/activate
```

3. Install dependencies
```bash
sudo -u discordbot pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file in the application directory:
```bash
sudo -u discordbot touch /opt/napland-bot/.env
sudo chmod 600 /opt/napland-bot/.env
```

Required environment variables (add to .env):
```bash
PUBLIC_KEY=your_discord_public_key
DISCORD_TOKEN=your_discord_bot_token
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/napland_bot
```

To get these values:
- **PUBLIC_KEY**: From Discord Developer Portal > General Information > Public Key
- **DISCORD_TOKEN**: From Discord Developer Portal > Bot > Token
- **DATABASE_URL**: MySQL connection string (user, password, host, port, database name)

## Service Setup

1. Create a systemd service file
```bash
sudo nano /etc/systemd/system/napland-bot.service
```

Add the following content:
```ini
[Unit]
Description=Napland Adventure Nexus Discord Bot
After=network.target

[Service]
Type=simple
User=discordbot
Group=discordbot
WorkingDirectory=/opt/napland-bot
Environment=PATH=/opt/napland-bot/venv/bin
EnvironmentFile=/opt/napland-bot/.env
ExecStart=/opt/napland-bot/venv/bin/python3 app/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Note:** This service file runs `app/server.py` which automatically detects that `PLATFORM=self-hosted` and starts the HTTPS server accordingly.

2. Enable and start the service
```bash
sudo systemctl daemon-reload
sudo systemctl enable napland-bot
sudo systemctl start napland-bot
```

## Monitoring and Maintenance

1. Check service status
```bash
sudo systemctl status napland-bot
```

2. View logs
```bash
sudo journalctl -u napland-bot -f
```

3. Updating the bot
```bash
cd /opt/napland-bot
sudo -u discordbot git pull
sudo -u discordbot source venv/bin/activate
sudo -u discordbot pip install -r requirements.txt
sudo systemctl restart napland-bot
```

## Backup Considerations

1. Database Backups (MySQL)
- Set up regular MySQL backups of the napland_bot database
- Use mysqldump for automated backups:
```bash
mysqldump -u username -p napland_bot > /backup/napland_bot_$(date +\%Y\%m\%d).sql
```
- Store backups in a secure location, consider off-site backup storage
- Test backup restoration regularly to ensure integrity

2. Configuration Backups
- Regularly backup the .env file and any other configuration files
- Document any custom changes or configurations

## Security Considerations

1. Firewall Configuration
```bash
sudo firewall-cmd --permanent --add-port=8443/tcp
sudo firewall-cmd --reload
```

2. MySQL Connection Security
- Ensure MySQL is only accessible from localhost (or your bot server)
- Use strong passwords for database user
- Keep MySQL user privileges limited to the napland_bot database only
- Consider using SSL connections for MySQL if on remote server

3. SELinux Configuration (if enabled)
```bash
sudo semanage fcontext -a -t bin_t "/opt/napland-bot/venv/bin(/.*)?"
sudo restorecon -Rv /opt/napland-bot/venv/bin
sudo setsebool -P httpd_can_network_connect on
```

## Troubleshooting

Common issues and solutions:
1. Bot not starting
   - Check logs: `sudo journalctl -u napland-bot -f`
   - Verify permissions: `ls -la /opt/napland-bot`
   - Check Python version: `python3 --version`

2. Database connection issues
   - Verify database credentials in .env
   - Check database service status
   - Ensure proper network connectivity

3. Permission issues
   - Verify file ownership: `sudo chown -R discordbot:discordbot /opt/napland-bot`
   - Check SELinux contexts if enabled

## Code Adaptation

**Important:** Before deploying, you need to update the code for self-hosted execution. See `self-host-code-plan.md` for detailed instructions.

The code refactoring supports **both Lambda and self-hosted deployments** via the `PLATFORM` environment variable:
- **Lambda deployments** continue to work unchanged (set `PLATFORM=lambda` or leave undefined)
- **Self-hosted deployments** use the new `server.py` file (set `PLATFORM=self-hosted`)

## Additional Notes

- Keep Python packages updated regularly
- Monitor system resources (CPU, memory, disk usage)
- Set up monitoring alerts for service disruptions
- Maintain regular backups of critical data
- Document any custom modifications or configurations