# 🤖 No-Code Federated Learning Platform

A full-stack web application that enables users to upload datasets, automatically generate machine learning pipelines, and train models collaboratively - all without writing code.

## ✨ Features

### 🔐 User Authentication
- Secure signup/login with JWT tokens
- Password hashing with bcrypt

### 👥 Federated Learning
- Create projects with unique shareable codes
- Multiple users can join projects
- Each user uploads their own dataset
- Independent model training per user
- Separate results and insights

### 📊 Smart Dataset Processing
- Upload CSV or Excel files (<1 MB)
- Automatic preprocessing and cleaning
- Column analysis and type detection
- Handles missing values, duplicates, and outliers
- Robust parsing for various file formats

### 🧠 Intelligent Pipeline Generation
- **Code-based AI engine** (not LLM-dependent)
- Analyzes dataset characteristics
- Automatically selects appropriate models
- Configures preprocessing steps
- Minimal Gemini API usage (only for explanations)

### 🎯 Model Training
- Automatic model selection (Linear Regression, Random Forest, etc.)
- Hyperparameter optimization
- Cross-validation
- **Feature Importance Analysis** - Shows which features influence predictions most
- Normalized importance scores (0-100%)

### 📈 Results & Insights
- Model performance metrics
- Feature importance visualization data
- AI-generated data stories (Gemini-powered)
- Non-technical explanations
- Actionable recommendations

### ☁️ Cloud-Ready
- **Files stored in Neon PostgreSQL** (no local storage)
- Ready for Vercel deployment
- Fully serverless architecture
- Scales automatically

## 🏗️ Architecture

```
Frontend (Next.js/React)
    ↓ REST API
Backend (Flask/Python)
    ↓ SQLAlchemy ORM
Neon PostgreSQL
    ├── Users & Auth
    ├── Projects & Members
    ├── Datasets (stored as binary)
    └── Training Results & Feature Importance
```

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Neon PostgreSQL account (free tier works)

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/nocode-federated-learning.git
cd nocode-federated-learning
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Flask backend
python app.py
```

Backend will run on `http://localhost:5000`

### 3. Frontend Setup
```bash
# Install Node dependencies
npm install

# Run Next.js frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### 4. Access Application
Open http://localhost:3000 in your browser

## 🌐 Deploy to Production

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for complete deployment guide to Vercel.

**Quick Deploy:**
1. Push code to GitHub
2. Import to Vercel
3. Add environment variables
4. Deploy!

**Cost:** $0/month with free tiers

## 🔧 Configuration

### Environment Variables

Create `.env` file (or set in deployment platform):

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# Security
SECRET_KEY=your-secret-key-here

# API Keys
GEMINI_API_KEY=your-gemini-api-key
```

## 📦 Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Neon PostgreSQL** - Database (serverless)
- **Pandas & NumPy** - Data processing
- **Scikit-learn** - Machine learning
- **Google Gemini API** - Natural language explanations

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Fetch API** - Backend communication

## 📊 Model Training Pipeline

1. **Data Upload** → Stored in Neon PostgreSQL as binary
2. **Preprocessing** → Automatic cleaning and feature engineering
3. **Pipeline Generation** → Code-based smart engine
4. **Model Training** → Multiple algorithms tested
5. **Feature Importance** → Identifies key predictors
6. **Results** → AI-generated insights + visualizations

## 🎯 Use Cases

- **Healthcare:** Predict patient outcomes collaboratively
- **Finance:** Analyze customer data across branches
- **Education:** Grade prediction models per school
- **Real Estate:** House price prediction
- **HR:** Employee retention analysis

## 🔒 Security Features

- JWT-based authentication
- Password hashing (bcrypt)
- Environment variable configuration
- SQL injection protection (ORM)
- CORS configuration
- SSL/TLS for database connections

## 📈 Scalability

- **Database:** Neon auto-scales (0.5GB → 10GB)
- **Backend:** Serverless functions (Vercel/Railway)
- **Frontend:** Global CDN (Vercel)
- **Storage:** Files in database (persistent)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- Neon for serverless PostgreSQL
- Google for Gemini API
- Vercel for hosting platform
- Scikit-learn for ML algorithms

## 📞 Support

- **Issues:** GitHub Issues
- **Docs:** See DEPLOYMENT.md
- **Questions:** Open a discussion

---

Built with ❤️ for making machine learning accessible to everyone.
