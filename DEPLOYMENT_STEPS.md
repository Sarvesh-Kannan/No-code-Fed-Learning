# Deployment Guide for No-Code Federated Learning

## 🚀 Quick Deployment Steps

### Prerequisites
- GitHub account
- Vercel account (for frontend)
- Railway account (for backend)
- Neon PostgreSQL database (already configured)

---

## Step 1: Push to GitHub

Run these commands in your project directory:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - No-code federated learning application"

# Add remote repository
git remote add origin https://github.com/Sarvesh-Kannan/No-code-Fed-Learning.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project
1. Go to [Railway](https://railway.app/)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `No-code-Fed-Learning` repository
5. Railway will auto-detect it's a Python project

### 2.2 Configure Environment Variables
Add these in Railway's "Variables" section:

```
DATABASE_URL=postgresql://neondb_owner:npg_EBNGrL9gFSh8@ep-wandering-rice-a1g88vgs-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
GEMINI_API_KEY=AIzaSyAUsSQuwbnlOxyj7kXCF8AgaIYi36H5X0g
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
FLASK_ENV=production
```

### 2.3 Configure Build Settings
Railway should automatically detect:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app` (from Procfile)

### 2.4 Run Migration
After deployment, run this command in Railway's terminal:
```bash
python migrate_database.py
```

### 2.5 Note Your Backend URL
Railway will provide a URL like: `https://your-app.railway.app`
**Copy this URL - you'll need it for frontend deployment**

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Project
1. Go to [Vercel](https://vercel.com/)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect it's a Next.js project

### 3.2 Configure Environment Variables
Add this in Vercel's "Environment Variables" section:

```
NEXT_PUBLIC_API_URL=https://your-app.railway.app
```
**Replace `https://your-app.railway.app` with your actual Railway URL**

### 3.3 Configure Build Settings
Vercel should automatically use:
- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### 3.4 Deploy
Click "Deploy" and wait for Vercel to build your application.

---

## Step 4: Update Backend CORS

After getting your Vercel URL (e.g., `https://your-app.vercel.app`), you need to update the backend CORS settings:

1. Edit `app.py` line 29-30:
```python
CORS(app, resources={r"/api/*": {
    "origins": ["http://localhost:3000", "https://your-app.vercel.app"],  # Add your Vercel URL
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})
```

2. Commit and push:
```bash
git add app.py
git commit -m "Update CORS for production"
git push
```

Railway will automatically redeploy with the new settings.

---

## Step 5: Verify Deployment

### Test Backend
Visit: `https://your-app.railway.app/health`
Should return: `{"status": "healthy"}`

### Test Frontend
1. Visit your Vercel URL
2. Create an account
3. Create a project
4. Upload a dataset
5. Train a model

---

## 🔒 Security Checklist

- [ ] Change `JWT_SECRET_KEY` to a strong random string
- [ ] Verify DATABASE_URL has SSL enabled (`sslmode=require`)
- [ ] Check that GEMINI_API_KEY is working
- [ ] Update CORS origins to include only your production URLs
- [ ] Review Neon database connection limits (free tier has limits)

---

## 📊 Monitoring

### Railway Backend
- Check logs in Railway dashboard
- Monitor memory and CPU usage
- Set up alerts for downtime

### Vercel Frontend
- Check deployment logs
- Monitor function execution time
- Review analytics dashboard

---

## 🐛 Troubleshooting

### Backend Issues
**Database Connection Failed**
- Check DATABASE_URL is correct
- Verify Neon database is active
- Run migration script: `python migrate_database.py`

**Gemini API Errors**
- Verify API key is correct
- Check Gemini API quotas
- Review error logs for rate limits

### Frontend Issues
**API Connection Failed**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend health endpoint
- Review browser console for CORS errors

**Build Failures**
- Check Node.js version (should be 18+)
- Clear `.next` folder and rebuild
- Verify `package.json` dependencies

---

## 💰 Cost Estimates

### Free Tier Limits
- **Neon**: 3GB storage, 100 hours compute/month
- **Railway**: $5 free credit/month (~500 hours for small app)
- **Vercel**: 100GB bandwidth/month, unlimited deployments
- **Gemini API**: Free tier with rate limits

### Expected Usage (MVP)
- Backend: ~$0-5/month (Railway hobby plan)
- Frontend: $0/month (within Vercel free tier)
- Database: $0/month (within Neon free tier)
- **Total: ~$0-5/month**

---

## 🔄 Updates and Maintenance

### Updating Code
```bash
# Make changes
git add .
git commit -m "Your update message"
git push
```
Both Railway and Vercel will auto-deploy on push.

### Database Migrations
When changing database schema:
1. Update `database.py`
2. Create migration script (similar to `migrate_database.py`)
3. Run migration in Railway terminal
4. Commit and push changes

---

## 📞 Support Resources

- [Railway Docs](https://docs.railway.app/)
- [Vercel Docs](https://vercel.com/docs)
- [Neon Docs](https://neon.tech/docs)
- [Next.js Docs](https://nextjs.org/docs)
- [Flask Docs](https://flask.palletsprojects.com/)

---

## ✅ Post-Deployment Checklist

- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] User registration works
- [ ] Project creation works
- [ ] Dataset upload works
- [ ] Pipeline generation works
- [ ] Model training works
- [ ] Federated learning works (multiple users)
- [ ] File storage in Neon works
- [ ] Results display correctly

---

**Your application is now live! 🎉**

Share your Vercel URL with users to start using your no-code federated learning platform.

