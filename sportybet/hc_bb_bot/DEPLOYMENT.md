# Deployment Guide

## 🚀 Deployment Options

### Option 1: Local Machine (Development)

```bash
# 1. Clone/download the bot
cd basketball_bot

# 2. Run installation
./install.sh

# 3. Configure environment
nano .env

# 4. Start the bot
./run.sh
```

---

### Option 2: VPS/Cloud Server (Production)

#### Step 1: Provision Server

Recommended providers:
- DigitalOcean ($5/month droplet)
- AWS EC2 (t2.micro - free tier)
- Google Cloud (e2-micro - free tier)
- Vultr ($5/month instance)

Requirements:
- Ubuntu 20.04+ / Debian 10+
- 1GB RAM minimum
- 10GB storage

#### Step 2: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Create user
sudo useradd -m -s /bin/bash basketballbot
sudo usermod -aG sudo basketballbot
su - basketballbot

# Clone repository
git clone <your-repo-url> basketball_bot
cd basketball_bot

# Run installation
./install.sh
```

#### Step 3: Configure Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/basketball-bot.service
```

Add content:
```ini
[Unit]
Description=Basketball Betting Bot
After=network.target

[Service]
Type=simple
User=basketballbot
WorkingDirectory=/home/basketballbot/basketball_bot
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/basketballbot/basketball_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable basketball-bot
sudo systemctl start basketball-bot

# Check status
sudo systemctl status basketball-bot

# View logs
sudo journalctl -u basketball-bot -f
```

---

### Option 3: Docker Deployment

#### Using Docker Compose

```bash
# 1. Clone repository
git clone <your-repo-url> basketball_bot
cd basketball_bot

# 2. Create .env file
cp .env.example .env
nano .env

# 3. Build and run
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Stop
docker-compose down
```

#### Using Docker Run

```bash
# Build image
docker build -t basketball-bot .

# Run container
docker run -d \
  --name basketball-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  basketball-bot

# View logs
docker logs -f basketball-bot
```

---

### Option 4: Heroku Deployment

```bash
# 1. Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create your-basketball-bot

# 4. Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set API_BASKETBALL_KEY=your_key

# 5. Deploy
git push heroku main

# 6. Scale worker
heroku ps:scale worker=1

# 7. View logs
heroku logs --tail
```

**Required files for Heroku:**

`Procfile`:
```
worker: python bot.py
```

`runtime.txt`:
```
python-3.11.0
```

---

### Option 5: Railway/Render

#### Railway

1. Connect GitHub repo to Railway
2. Add environment variables in dashboard
3. Deploy automatically

#### Render

1. Create new Web Service
2. Connect GitHub repo
3. Set environment variables
4. Deploy

---

## 🔒 Security Checklist

- [ ] Use strong API keys
- [ ] Rotate keys regularly
- [ ] Don't commit .env file
- [ ] Use firewall (ufw)
- [ ] Enable automatic updates
- [ ] Monitor logs for errors
- [ ] Set up alerts for downtime

---

## 📊 Monitoring

### Log Rotation

```bash
# Install logrotate
sudo apt install logrotate

# Create config
sudo nano /etc/logrotate.d/basketball-bot
```

Add:
```
/home/basketballbot/basketball_bot/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 basketballbot basketballbot
}
```

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

if ! pgrep -f "python bot.py"; then
    echo "Bot is down! Restarting..."
    sudo systemctl restart basketball-bot
    echo "Restarted at $(date)" >> /var/log/bot-restarts.log
fi
```

Add to crontab:
```bash
*/5 * * * * /home/basketballbot/basketball_bot/health_check.sh
```

---

## 🔄 Updates

```bash
# Pull latest code
cd basketball_bot
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart basketball-bot
```

---

## 💾 Backup

```bash
# Backup database and configs
tar -czf backup-$(date +%Y%m%d).tar.gz \
  basketball_bot.db \
  .env \
  data/ \
  logs/

# Upload to cloud storage (optional)
aws s3 cp backup-*.tar.gz s3://your-bucket/backups/
```

---

## 📈 Scaling

If you need more API requests:

1. **Upgrade API-Basketball plan**
   - Pro: $10/month (1,000 requests/day)
   - Ultra: $25/month (5,000 requests/day)

2. **Use multiple API keys**
   - Rotate between keys
   - Distribute load

3. **Implement caching**
   - Redis for response caching
   - Reduce API calls

4. **Optimize requests**
   - Batch when possible
   - Cache fixtures longer
