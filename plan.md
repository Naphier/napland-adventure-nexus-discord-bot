# Deployment Plan for Napland Adventure Nexus Discord Bot

## System Requirements
- CentOS 7.9.2009
- Python 3.6+ (CentOS 7 default is Python 2.7, so we'll need to install Python 3)
- pip (Python package manager)
- Git (for cloning the repository)
- Systemd (for running the bot as a service)

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

3. Create a dedicated user for the bot
```bash
sudo useradd -r -s /bin/false discordbot
```

4. Create application directory
```bash
sudo mkdir -p /opt/napland-bot
sudo chown discordbot:discordbot /opt/napland-bot
```

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
Create a `.env` file in the application directory with necessary configurations:
```bash
sudo -u discordbot touch /opt/napland-bot/.env
```

Required environment variables:
- DISCORD_TOKEN
- DATABASE_URL (if using external database)
- Other configuration variables as needed

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
ExecStart=/opt/napland-bot/venv/bin/python3 app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

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

1. Database Backups (if using SQLite or local database)
- Set up regular backups of the database file
- Store backups in a secure location

2. Configuration Backups
- Regularly backup the .env file and any other configuration files
- Document any custom changes or configurations

## Security Considerations

1. Firewall Configuration
```bash
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

2. SELinux Configuration (if enabled)
```bash
sudo semanage fcontext -a -t bin_t "/opt/napland-bot/venv/bin(/.*)?"
sudo restorecon -Rv /opt/napland-bot/venv/bin
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

## Additional Notes

- Keep Python packages updated regularly
- Monitor system resources (CPU, memory, disk usage)
- Set up monitoring alerts for service disruptions
- Maintain regular backups of critical data
- Document any custom modifications or configurations