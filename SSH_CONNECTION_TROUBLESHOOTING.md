# 🔧 SSH Connection Troubleshooting Guide

**Error:** `Read from remote host: Can't assign requested address` / `Connection closed` / `Broken pipe`

---

## 🎯 What This Error Means

Your computer **cannot maintain** a stable SSH connection to your AWS EC2 instance (IP: 13.204.63.208).

**This is NOT a Docker error** - it's a connection problem between your computer and AWS.

---

## 🔍 Common Causes & Solutions

### 1. **Check if EC2 Instance is Running** ⚠️

**Most Common Issue!**

```bash
# From AWS Console:
1. Go to: https://console.aws.amazon.com/ec2/
2. Click "Instances" in left sidebar
3. Find your instance
4. Check "Instance State"
```

**Should say:** ✅ `Running` (green dot)

**If it says:** ❌ `Stopped` or `Terminated`
- **Solution:** Start the instance
- Click instance → Actions → Instance State → Start

---

### 2. **Verify Public IP Address**

Your instance IP might have changed!

```bash
# In AWS Console:
EC2 → Instances → Select your instance
Look for: "Public IPv4 address"
```

**If IP changed:**
- ❌ Old IP: 13.204.63.208
- ✅ New IP: (use the new one shown in console)

**Solution:** Use an **Elastic IP** to prevent IP changes

#### How to Attach Elastic IP:
```bash
# In AWS Console:
1. EC2 → Elastic IPs (left sidebar)
2. Click "Allocate Elastic IP address"
3. Click "Allocate"
4. Select the new Elastic IP
5. Actions → Associate Elastic IP address
6. Select your EC2 instance
7. Click "Associate"
```

✅ Now your IP won't change when instance restarts!

---

### 3. **Check Security Group Rules**

Your Security Group might be blocking SSH.

```bash
# In AWS Console:
1. EC2 → Instances → Select instance
2. Click "Security" tab
3. Click the security group link
4. Check "Inbound rules"
```

**Required Rule for SSH:**

| Type | Port | Source | Description |
|------|------|--------|-------------|
| SSH | 22 | Your IP / 0.0.0.0/0 | Allow SSH |

**If missing or wrong:**
```bash
1. Click "Edit inbound rules"
2. Add rule:
   - Type: SSH
   - Port: 22
   - Source: "My IP" (or 0.0.0.0/0 for any IP)
3. Save rules
```

---

### 4. **Verify SSH Key Permissions**

Your SSH key file might have wrong permissions.

```bash
# Check current permissions
ls -la ~/path/to/your-key.pem

# Should show: -r-------- or -rw-------
# If not, fix it:
chmod 400 ~/path/to/your-key.pem
```

---

### 5. **Test Basic Connectivity**

```bash
# Test if instance is reachable
ping 13.204.63.208

# Test if SSH port is open
telnet 13.204.63.208 22

# Or use nc (netcat)
nc -zv 13.204.63.208 22
```

**Expected output:**
```
Connection to 13.204.63.208 22 port [tcp/ssh] succeeded!
```

**If fails:** Security Group or instance is down.

---

### 6. **Try Different SSH Connection Options**

```bash
# Verbose mode (see what's happening)
ssh -vvv -i your-key.pem ubuntu@13.204.63.208

# With keep-alive (prevents timeout)
ssh -i your-key.pem \
    -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=3 \
    ubuntu@13.204.63.208

# Different user (if ubuntu doesn't work)
ssh -i your-key.pem ec2-user@13.204.63.208
```

---

### 7. **Check AWS Region**

Make sure you're looking at the **correct AWS region**!

```bash
# In AWS Console (top-right corner):
Check region: Asia Pacific (Mumbai) ap-south-1
             or US East (N. Virginia) us-east-1
             or whichever region you used
```

Your instance might be in a different region!

---

### 8. **Connection Timeout Issues**

If connection drops frequently:

```bash
# Add to your ~/.ssh/config file:
cat << 'EOF' >> ~/.ssh/config

Host aws-hybridrag
    HostName 13.204.63.208
    User ubuntu
    IdentityFile ~/path/to/your-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
EOF

# Then connect using:
ssh aws-hybridrag
```

---

## 🚨 Emergency Checklist

Run through these in order:

```
□ Is EC2 instance "Running"? (Check AWS Console)
□ Is the IP address correct? (Might have changed)
□ Is Security Group allowing SSH on port 22?
□ Is your key file permissions set to 400?
□ Can you ping the instance?
□ Can you telnet to port 22?
□ Are you in the correct AWS region?
□ Is your internet connection stable?
```

---

## 🔧 Quick Fixes

### Fix 1: Restart EC2 Instance
```bash
# In AWS Console:
Instance → Actions → Instance State → Reboot
Wait 2 minutes, then try connecting again
```

### Fix 2: Use EC2 Instance Connect (Browser-based)
```bash
# In AWS Console:
1. Select your instance
2. Click "Connect" button (top-right)
3. Choose "EC2 Instance Connect"
4. Click "Connect"

# This opens a browser-based terminal!
# No SSH key needed!
```

### Fix 3: Use AWS Session Manager (No SSH needed)
```bash
# Install AWS CLI and Session Manager plugin
# Then:
aws ssm start-session --target i-YOUR_INSTANCE_ID
```

---

## 📞 Step-by-Step Recovery

### If Instance is Stopped:
```bash
1. AWS Console → EC2 → Instances
2. Select instance
3. Actions → Instance State → Start
4. Wait for "Status checks" to show 2/2 passed
5. Note the NEW public IP address
6. Try connecting with new IP
```

### If IP Changed:
```bash
1. Get current IP from AWS Console
2. Update your SSH command:
   ssh -i your-key.pem ubuntu@NEW_IP_ADDRESS
3. Update .env file with new IP:
   VITE_API_URL=http://NEW_IP_ADDRESS:8010
4. Rebuild frontend:
   docker compose build frontend --no-cache
   docker compose up -d
```

---

## 🎯 Best Practice: Use Elastic IP

**Why:** Your IP address changes every time you stop/start the instance

**Solution:**
1. Allocate Elastic IP (free when attached to running instance)
2. Associate with your EC2 instance
3. Use this IP forever (doesn't change)
4. Update Security Group if needed

**Cost:** FREE when attached to running instance, ~$0.005/hour if unattached

---

## 🧪 Test Connection

Once you think it's fixed, test:

```bash
# 1. Basic SSH
ssh -i your-key.pem ubuntu@YOUR_IP

# 2. Check Docker is running
docker ps

# 3. Check app is running
curl http://localhost:8010/health
curl http://localhost/

# 4. Check from outside
curl http://YOUR_PUBLIC_IP:8010/health
curl http://YOUR_PUBLIC_IP/
```

---

## 💡 Alternative: EC2 Instance Connect

If SSH keeps failing, use browser-based access:

```bash
# In AWS Console:
1. EC2 → Instances
2. Select your instance
3. Click "Connect" (top-right)
4. Tab: "EC2 Instance Connect"
5. Click "Connect"

# You now have a terminal in your browser!
# No SSH key issues!
```

---

## 🆘 Still Not Working?

### Check AWS Service Health
```
https://status.aws.amazon.com/
```

### Verify Instance Details
```bash
# In AWS Console:
Instance → Description tab
Check:
- Instance state: Running
- Status checks: 2/2 passed
- Public IPv4: Shows an IP
- Security groups: Has SSH rule
```

### Create New Instance
If all else fails:
```bash
1. Launch new EC2 instance
2. Use Elastic IP from start
3. Configure security group correctly
4. Deploy fresh
```

---

## 📝 Prevention for Future

Add to your `~/.ssh/config`:

```bash
Host aws-prod
    HostName YOUR_ELASTIC_IP
    User ubuntu
    IdentityFile ~/.ssh/your-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
    
# Then just use:
# ssh aws-prod
```

---

## 🎯 Most Likely Causes (in order)

1. ✅ **EC2 Instance is stopped** (90% of cases)
2. ✅ **IP address changed** (if no Elastic IP)
3. ✅ **Security Group blocks SSH** (port 22)
4. ✅ **Wrong AWS region selected**
5. ✅ **Network connectivity issues**

**Start with #1 - Check if instance is running!**

---

**Good luck! Once connected, your Docker containers should be running fine.** 🚀

