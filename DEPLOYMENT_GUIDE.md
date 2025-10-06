# Production Deployment Guide

## 🎯 Overview
Your application is **95% ready** for deployment. Here's what needs to be fixed and how to deploy it.

---

## 🔴 CRITICAL FIXES NEEDED

### 1. File Storage Fix (REQUIRED)

**Problem:** Uploaded datasets and trained models are stored locally. Cloud platforms delete these on restart.

**Solution A: Use AWS S3 (Recommended)**

#### Install boto3:
```bash
pip install boto3
```

#### Update `config.py`:
```python
# Add S3 configuration
USE_S3 = os.getenv('USE_S3', 'False') == 'True'
S3_BUCKET = os.getenv('S3_BUCKET', '')
S3_REGION = os.getenv('S3_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
```

#### Create `s3_storage.py`:
```python
import boto3
import os
from config import Config

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.S3_REGION
        )
        self.bucket = Config.S3_BUCKET
    
    def upload_file(self, local_path, s3_path):
        """Upload file to S3"""
        self.s3.upload_file(local_path, self.bucket, s3_path)
        return f"https://{self.bucket}.s3.amazonaws.com/{s3_path}"
    
    def download_file(self, s3_path, local_path):
        """Download file from S3"""
        self.s3.download_file(self.bucket, s3_path, local_path)
    
    def delete_file(self, s3_path):
        """Delete file from S3"""
        self.s3.delete_object(Bucket=self.bucket, Key=s3_path)
```

#### Update file upload in `app.py`:
```python
from s3_storage import S3Storage

if Config.USE_S3:
    storage = S3Storage()
else:
    storage = None

# In upload route:
if storage:
    s3_path = f"datasets/{dataset_id}/{filename}"
    storage.upload_file(filepath, s3_path)
    dataset.file_path = s3_path  # Store S3 path
else:
    dataset.file_path = filepath  # Store local path
```

**Alternative: Cloudflare R2 (Cheaper than S3)**
- Compatible with S3 API
- Much cheaper bandwidth
- Same code as above

### 2. Environment Variables (REQUIRED)

#### Create `.env` file (DO NOT COMMIT TO GIT):
```bash
# Database
DATABASE_URL=postgresql://neondb_owner:npg_bHR7VTgl5eKv@ep-broad-brook-a13kxylc-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

# Security
SECRET_KEY=your-super-secret-random-string-here-generate-new-one

# Gemini API
GEMINI_API_KEY=AIzaSyAUsSQuwbnlOxyj7kXCF8AgaIYi36H5X0g

# File Storage (if using S3)
USE_S3=True
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Upload limits
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=./uploads
```

#### Update `.gitignore`:
```
.env
uploads/
models/
*.pyc
__pycache__/
```

### 3. Frontend Environment Variables

#### Create `.env.local` in frontend:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

#### Update `src/lib/api.ts`:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const api = {
  baseURL: API_BASE_URL,
  // ... rest of your API calls
};
```

---

## 🚀 Deployment Steps

### Backend Deployment (Flask)

#### Option 1: Railway (Recommended - Free Tier)

1. **Go to:** https://railway.app/
2. **Click:** "Start a New Project"
3. **Select:** "Deploy from GitHub repo"
4. **Connect** your GitHub repository
5. **Set Environment Variables:**
   ```
   DATABASE_URL=your-neon-connection-string
   SECRET_KEY=generate-new-secret
   GEMINI_API_KEY=your-key
   USE_S3=True (if using S3)
   ... (other S3 vars if needed)
   ```
6. **Add Procfile** to root:
   ```
   web: python app.py
   ```
7. **Railway will auto-deploy!**

#### Option 2: Render (Free Tier)

1. **Go to:** https://render.com/
2. **New Web Service**
3. **Connect GitHub** repo
4. **Settings:**
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. **Add Environment Variables** (same as above)
6. **Create Web Service**

#### Option 3: Heroku

1. **Install Heroku CLI**
2. **Login:**
   ```bash
   heroku login
   ```
3. **Create app:**
   ```bash
   heroku create your-app-name
   ```
4. **Set env vars:**
   ```bash
   heroku config:set DATABASE_URL=your-neon-url
   heroku config:set SECRET_KEY=your-secret
   heroku config:set GEMINI_API_KEY=your-key
   ```
5. **Create Procfile:**
   ```
   web: python app.py
   ```
6. **Deploy:**
   ```bash
   git push heroku main
   ```

### Frontend Deployment (Next.js)

#### Option 1: Vercel (Recommended)

1. **Go to:** https://vercel.com/
2. **Import Project** from GitHub
3. **Framework:** Next.js (auto-detected)
4. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
   ```
5. **Deploy!**
6. **Custom Domain** (optional): Add your own domain

#### Option 2: Netlify

1. **Go to:** https://netlify.com/
2. **New site from Git**
3. **Build settings:**
   - Build command: `npm run build`
   - Publish directory: `.next`
4. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=your-backend-url
   ```
5. **Deploy!**

---

## 📋 Pre-Deployment Checklist

### Security
- [ ] Move all secrets to environment variables
- [ ] Generate new `SECRET_KEY` for production
- [ ] Enable CORS only for your frontend domain
- [ ] Add rate limiting (optional but recommended)
- [ ] Review and rotate API keys

### Database
- [ ] Neon connection string in environment variables
- [ ] Test connection from deployment platform
- [ ] Check Neon usage limits (0.5GB storage on free tier)
- [ ] Set up automatic backups (Neon console)

### File Storage
- [ ] Decide: S3, R2, or persistent volume
- [ ] Set up storage bucket/volume
- [ ] Update code to use remote storage
- [ ] Test file upload/download

### Frontend
- [ ] Update API URL to production backend
- [ ] Test CORS from frontend domain
- [ ] Optimize build size
- [ ] Test all routes and features

### Testing
- [ ] Test signup/login flow
- [ ] Test project creation and joining
- [ ] Test dataset upload (check storage)
- [ ] Test model training (check results persist)
- [ ] Test federated learning (multiple users)

---

## 🔒 Security Hardening for Production

### 1. Update `config.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database (from environment only!)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required!")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security (MUST be set in production)
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required!")
    
    # File Storage
    USE_S3 = os.getenv('USE_S3', 'False') == 'True'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MODEL_FOLDER = './models'
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # S3 Configuration (if enabled)
    if USE_S3:
        S3_BUCKET = os.getenv('S3_BUCKET')
        S3_REGION = os.getenv('S3_REGION', 'us-east-1')
        AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required!")
    
    # JWT
    JWT_EXPIRATION_HOURS = 24
```

### 2. Update CORS in `app.py`:
```python
# Production CORS (restrict to your frontend domain)
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)
```

### 3. Add Rate Limiting:
```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply to auth routes
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # ... existing code
```

---

## 💰 Cost Estimates (Free Tiers)

### Current Setup (100% Free)
- **Neon PostgreSQL:** Free (0.5GB storage, 1GB RAM)
- **Railway Backend:** Free (500 hours/month, $5 credit)
- **Vercel Frontend:** Free (unlimited static, 100GB bandwidth)
- **Gemini API:** Free (15 requests/minute)

**Total Cost:** $0/month for small usage!

### With S3 Storage (Paid but Minimal)
- **AWS S3:** ~$0.023/GB storage + $0.09/GB transfer
- **Example:** 10GB data + 100GB transfer = ~$9.23/month

### With Cloudflare R2 (Cheaper Alternative)
- **Storage:** $0.015/GB (~35% cheaper than S3)
- **Egress:** FREE (0 bandwidth costs!)
- **Example:** 10GB data = ~$0.15/month 💰

---

## 🎯 Recommended Stack (Best Free Option)

1. **Backend:** Railway (free tier)
2. **Frontend:** Vercel (free tier)
3. **Database:** Neon (already set up)
4. **File Storage:** Cloudflare R2 (cheapest)
5. **Domain:** Namecheap/Cloudflare (~$10/year)

**Total monthly cost:** ~$0-1/month (excluding domain)

---

## 📊 Scaling Considerations

### When You Outgrow Free Tier:

#### Neon Limits (Free)
- 0.5GB storage
- 1GB RAM
- If exceeded: Upgrade to $19/month (10GB + 2GB RAM)

#### Railway Limits (Free)
- $5 credit/month
- ~500 hours runtime
- If exceeded: $0.01/hour after credit

#### Scaling Options:
1. **Small Scale (100-1000 users):**
   - Railway: $10-20/month
   - Neon: $19/month
   - R2: $1-5/month
   - **Total: $30-44/month**

2. **Medium Scale (1000-10000 users):**
   - AWS EC2/ECS: $50-100/month
   - Neon Scale plan: $69/month
   - R2: $10-20/month
   - CDN: $10/month
   - **Total: $139-199/month**

---

## ✅ Quick Start Deployment (30 Minutes)

### Step 1: Prepare Code (5 min)
```bash
# 1. Create .env file (don't commit!)
echo "DATABASE_URL=your-neon-url" > .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "GEMINI_API_KEY=your-key" >> .env

# 2. Update .gitignore
echo ".env" >> .gitignore

# 3. Commit changes
git add .
git commit -m "Prepare for production deployment"
git push
```

### Step 2: Deploy Backend (10 min)
1. Go to Railway.app
2. New Project → Deploy from GitHub
3. Add environment variables
4. Done! Get your backend URL

### Step 3: Deploy Frontend (10 min)
1. Go to Vercel.com
2. Import from GitHub
3. Add `NEXT_PUBLIC_API_URL=your-railway-url`
4. Deploy!

### Step 4: Test (5 min)
1. Visit your Vercel URL
2. Create account
3. Upload dataset
4. Train model
5. ✅ If it works, you're live!

---

## 🐛 Common Deployment Issues

### Issue 1: "Database connection failed"
**Fix:** Check Neon allows connections from your deployment platform's IP

### Issue 2: "CORS error" in browser
**Fix:** Add your frontend domain to `ALLOWED_ORIGINS`

### Issue 3: "Module not found" error
**Fix:** Ensure all dependencies are in `requirements.txt`

### Issue 4: Files disappear after upload
**Fix:** Implement S3/R2 storage (don't use local files)

### Issue 5: Gemini API rate limit
**Fix:** Free tier is 15 req/min. Add error handling and retry logic.

---

## 📞 Support Resources

- **Railway Docs:** https://docs.railway.app/
- **Vercel Docs:** https://vercel.com/docs
- **Neon Docs:** https://neon.tech/docs
- **Cloudflare R2:** https://developers.cloudflare.com/r2/

---

## 🎉 You're Ready!

Your application is **ready to deploy** after:
1. Moving secrets to environment variables ✅
2. Setting up file storage (S3/R2) ✅
3. Updating frontend API URL ✅

The database (Neon) is already production-ready!

Good luck with your deployment! 🚀

