# Architecture & Flow Diagrams

## System Architecture: Multi-Platform Support

```
┌──────────────────────────────────────────────────────────────────┐
│                   DISCORD BOT CODEBASE (SINGLE)                  │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              app/main.py (Core Logic)                      │ │
│  │  - Discord interaction handling                            │ │
│  │  - Command processing                                      │ │
│  │  - Database operations                                     │ │
│  │  - lambda_handler function (unchanged)                     │ │
│  └────────────┬─────────────────────────────────────────────┘ │
│               │                                                 │
│  ┌────────────▼────────────────────────────────────────────┐   │
│  │         app/server.py (Platform Abstraction)            │   │
│  │  - Detects PLATFORM environment variable               │   │
│  │  - Routes to appropriate execution mode                 │   │
│  │  - Flask wrapper for self-hosted                        │   │
│  │  - Health check endpoint                                │   │
│  └────────────┬─────────────────────────────────────────┬──┘   │
│               │                                         │        │
│         PLATFORM env var                          No PLATFORM   │
│               │                                         │        │
└───────────────┼─────────────────────────────────────────┼────────┘
                │                                         │
    ┌───────────▼─────────────┐        ┌────────────────▼─────┐
    │   Lambda Deployment     │        │  Self-Hosted on      │
    │  ✓ PLATFORM=lambda      │        │  CentOS 7.9          │
    │  ✓ main.lambda_handler  │        │  ✓ PLATFORM=         │
    │  ✓ No server.py         │        │    self-hosted        │
    │  ✓ API Gateway HTTPS    │        │  ✓ app/server.py     │
    │  ✓ AWS-managed scaling  │        │  ✓ Direct HTTPS 8443 │
    │  ✓ Pay-per-execution    │        │  ✓ systemd service   │
    │                         │        │  ✓ Let's Encrypt      │
    └─────────────────────────┘        │  ✓ Full control       │
                                       │  ✓ Fixed costs        │
                                       └───────────────────────┘
```

## Request Flow: Self-Hosted Mode

```
┌──────────────────────────────────────────────────────────────────┐
│                        Discord Servers                           │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         │ HTTPS POST
                         │ /interactions
                         │
                         ▼
            ┌────────────────────────────┐
            │  your-domain.com:8443      │
            │  (Let's Encrypt SSL)       │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │  app/server.py             │
            │  (Flask HTTPS Server)      │
            ├────────────────────────────┤
            │ PLATFORM=self-hosted       │
            │ BOT_PORT=8443              │
            │ CERT_PATH=/etc/letsen...   │
            └────────────┬───────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │ Verify Discord Signature   │
            │ (PUBLIC_KEY)               │
            └────────────┬───────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        ┌──────────┐          ┌──────────┐
        │Type = 1? │          │Type = 2? │
        │(Challenge)          │(Interact)
        └──────┬───┘          └────┬─────┘
               │                   │
               ▼                   ▼
        Return Challenge   app/main.py
        Response {         lambda_handler
          type: 1            - Log hours
        }                     - Display data
                            - Other commands
                              │
                              ▼
                          MySQL Database
                          (operations)
                              │
                              ▼
                          app/server.py
                          (format response)
                              │
                              ▼
                          Discord API
                          (webhook reply)
```

## Request Flow: Lambda Mode

```
┌──────────────────────────────────────────────────────────────────┐
│                        Discord Servers                           │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         │ HTTPS POST
                         │ /interactions
                         │
                         ▼
         ┌───────────────────────────────┐
         │  AWS API Gateway              │
         │  (HTTPS, certificate managed) │
         └────────────┬──────────────────┘
                      │
                      ▼
         ┌──────────────────────────────┐
         │  AWS Lambda Function          │
         │  Handler: main.lambda_handler │
         ├──────────────────────────────┤
         │ PLATFORM=lambda (ignored)     │
         │ PUBLIC_KEY                    │
         │ DISCORD_TOKEN                 │
         │ DATABASE_URL                  │
         └────────────┬──────────────────┘
                      │
                      ▼
         Verify Discord Signature
         (PUBLIC_KEY)
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      ┌────────┐           ┌──────────┐
      │Type 1? │           │Type 2?   │
      │Challenge           │Interact  │
      └────┬───┘           └────┬─────┘
           │                    │
           ▼                    ▼
    Return Challenge    Handle Command
    {type: 1}           - Log hours
                        - Display data
                          │
                          ▼
                      MySQL Database
                          │
                          ▼
                      Return Response
                      (format as Lambda response)
                          │
                          ▼
                      API Gateway
                          │
                          ▼
                      Discord API
```

## Deployment Timeline

```
Timeline: Self-Hosted Deployment

Day 1: Code Preparation (30 minutes)
├─ Create app/server.py
├─ Update requirements.txt
└─ Commit to git

Day 1: Infrastructure Setup (30 minutes)
├─ Update CentOS packages
├─ Install Python 3, pip, Git
├─ Obtain SSL certificate (Let's Encrypt)
├─ Configure firewall (port 8443)
└─ Update Discord Developer Portal

Day 1-2: Deployment (30 minutes active)
├─ Clone repository
├─ Create virtual environment
├─ Install dependencies
├─ Create .env configuration
├─ Create systemd service
└─ Start and verify service
    └─ Total wall-clock time: ~2 hours
       (includes certificate generation wait)

Day 2+: Ongoing
├─ Monitor logs
├─ Verify Discord interactions
└─ Certbot auto-renewal (automatic)
```

## Environment Variable Flow

```
Configuration Sources (Priority Order)

Self-Hosted:
1. .env file (loaded by systemd)
   ├─ PLATFORM=self-hosted
   ├─ PUBLIC_KEY
   ├─ DISCORD_TOKEN
   ├─ DATABASE_URL
   ├─ BOT_PORT
   └─ CERT_PATH

2. System environment (if .env not set)
   └─ (can override .env values)
         │
         ▼
    app/server.py reads PLATFORM
         │
    ┌────┴────┐
    │          │
    ▼          ▼
self-hosted  lambda
(Flask)      (ignored)


AWS Lambda:
1. Lambda environment variables
   ├─ PLATFORM=lambda (or undefined)
   ├─ PUBLIC_KEY
   ├─ DISCORD_TOKEN
   └─ DATABASE_URL

2. Systems Manager Parameter Store
   └─ (optional, for secrets)
         │
         ▼
    main.lambda_handler
    (executes, app/server.py ignored)
```

## Port and Network Configuration

```
Self-Hosted Architecture:

Internet
   │
   │ HTTPS (443)
   │ your-domain.com
   │
   ▼
┌─────────────────────────┐
│  Firewall               │
│  - Port 443: Allowed    │
│  - Port 8443: Allowed   │
│  - Other: Blocked       │
└────────┬────────────────┘
         │
    ┌────┴─────────────────────┐
    │                          │
    ▼                          ▼
┌──────────────┐      ┌──────────────────┐
│ Existing Web │      │ Discord Bot      │
│ Server       │      │ HTTPS Server     │
│ Port 443     │      │ Port 8443        │
│              │      │                  │
│ Handles      │      │ Handles          │
│ your web     │      │ Discord          │
│ traffic      │      │ interactions     │
└──────────────┘      └──────────────────┘

DNS:
- your-domain.com → Your server IP
- Bot endpoint: https://your-domain.com:8443/interactions
  (Discord connects directly to bot port)
```

## Security Layers

```
Self-Hosted Security:

Discord
   │
   ├─ 1. HTTPS/TLS
   │     └─ Let's Encrypt certificate
   │        verified by Discord
   │
   ▼
Server Firewall
   │
   ├─ 2. Port Filtering
   │     └─ Only 8443 accessible
   │        from internet
   │
   ▼
Flask Application
   │
   ├─ 3. Discord Signature Verification
   │     └─ PUBLIC_KEY used to verify
   │        Discord sent the request
   │
   ├─ 4. User Permission Checks
   │     └─ App-level authorization
   │
   ▼
Database
   │
   └─ 5. Credentials in .env
        └─ File permissions: 600
           User: discordbot (non-root)


Lambda Security:

Discord
   │
   ├─ 1. HTTPS/TLS
   │     └─ API Gateway certificate
   │        AWS-managed
   │
   ▼
AWS API Gateway
   │
   ├─ 2. AWS Authentication
   │     └─ IAM roles and policies
   │
   ▼
Lambda Function
   │
   ├─ 3. Discord Signature Verification
   │     └─ PUBLIC_KEY verification
   │
   ├─ 4. Execution Environment
   │     └─ Isolated per-request
   │
   ▼
Database
   │
   └─ 5. Secrets Manager / Parameter Store
        └─ AWS-managed credentials
```

## Scaling Comparison

```
AWS Lambda:
┌──────────────────┐
│ Discord Request  │
└────────┬─────────┘
         │
    ┌────▼────┐
    │ Auto    │  (< 1 second)
    │ Scale   │  (handles surge)
    │ +1000   │
    └────┬────┘
         │
    Lambda executes
    (concurrent requests)
         │
    ┌────▼─────────┐
    │ Automatically │
    │ scale down    │
    │ (no traffic)  │
    └───────────────┘

Cost: Pay per execution + data transfer


Self-Hosted (CentOS):
┌──────────────────┐
│ Discord Request  │
└────────┬─────────┘
         │
    Fixed resources
    (1 process per port)
         │
    ┌────▼─────────────┐
    │ Queues requests   │
    │ if traffic spike  │
    └────┬─────────────┘
         │
    Server bottleneck
    (single machine limit)

Cost: Fixed (server monthly fee)
Solution: Manual vertical scaling
         (upgrade server)
         or horizontal
         (add load balancer)
```

---

**Diagram Key:**
- ✓ = Supported/Enabled
- ├─ = Configuration option
- ▼ = Process flow
- ┌─ = System boundary

**Last Updated:** November 10, 2025
