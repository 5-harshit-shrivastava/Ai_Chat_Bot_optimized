# 🌾 Agricultural RAG Chatbot

A production-ready **Retrieval-Augmented Generation (RAG) chatbot** specialized in agricultural fertilizer advice. Built with Python, PostgreSQL, and advanced AI models.

## 🚀 Features

- **🤖 Advanced AI**: Uses BAAI/bge-large-en-v1.5 embeddings (1024 dimensions) + Google Gemini 1.5 Flash
- **🔍 Smart Retrieval**: Vector similarity search with optimized HNSW indexing
- **🌱 Agricultural Expert**: Specialized knowledge base for fertilizer management
- **⚡ Fast Performance**: ~5-6 second response times with database optimization
- **🛡️ Production Ready**: Clean architecture, error handling, and deployment configs

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   RAG Pipeline   │───▶│   AI Response   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ HuggingFace API │    │ Vector Database  │    │   Gemini API    │
│ (Embeddings)    │    │ (PostgreSQL +    │    │ (Generation)    │
│                 │    │  pgvector)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
rag-chatbot/
├── backend/
│   ├── api/
│   │   └── index.py          # Main RAG API
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Python dependencies
│   ├── setup_data.py         # Database initialization
│   └── vercel.json          # Deployment config
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.12+
- PostgreSQL with pgvector extension
- HuggingFace API token
- Google Gemini API key

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment
Create `backend/.env` file:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# HuggingFace API
HUGGINGFACE_API_TOKEN=hf_your_token_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=development
PORT=8000
```

### 5. Initialize Database
```bash
python setup_data.py
```

### 6. Run Server
```bash
python api/index.py
```

Server runs at: `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "RAG Chatbot API is running"
}
```

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What is the best NPK ratio for wheat?"
}
```

**Response:**
```json
{
  "response": "For wheat, aim for a 120:60:40 kg/ha NPK ratio...",
  "context": [
    "NPK Fertilizers for Wheat",
    "Rice Fertilizer Management", 
    "Potassium for Disease Resistance"
  ],
  "context_used": 3
}
```

### Database Setup
```http
POST /api/setup
```

## 🧪 Testing

### Sample Questions
- "What is the best NPK ratio for wheat?"
- "How to manage nitrogen deficiency in crops?"
- "What are the benefits of organic fertilizers?"
- "How should I apply phosphorus for root development?"

### Expected Performance
- **Response Time**: 5-6 seconds
- **Accuracy**: High for agricultural topics
- **Fallback**: Returns "I don't have enough information" for non-agricultural queries

## 🚀 Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Manual Deployment
```bash
# Build and deploy as needed for your platform
```

## 🛡️ Security

- ✅ Environment variables for API keys
- ✅ Input validation and sanitization
- ✅ Error handling and logging
- ✅ No sensitive data in repository

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ for farmers and agricultural professionals** 🌾

r