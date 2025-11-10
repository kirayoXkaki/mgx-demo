# MGX Demo - AI Software Development Platform

A complete web application demonstrating AI-powered software development using multi-agent collaboration.

## 🎯 Features

- **AI-Powered Generation**: Three AI agents (ProductManager, Architect, Engineer) work together to generate complete software projects
- **Real-time Progress**: WebSocket-based live updates showing each agent's work
- **Interactive UI**: Modern interface with chat, progress tracking, and file explorer
- **Cost Tracking**: Monitor API usage and costs in real-time
- **File Management**: Browse and view generated files
- **Project Download**: Download complete projects as ZIP files

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Chat Interface                                        │
│  - Progress Visualization                                │
│  - File Explorer                                         │
│  - Cost Display                                          │
└────────────────┬────────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────▼────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  - REST Endpoints                                        │
│  - WebSocket for real-time updates                      │
│  - Task management                                       │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│           MGX Backend (Multi-Agent System)               │
│  - ProductManager → Writes PRD                           │
│  - Architect → Designs System                            │
│  - Engineer → Implements Code                            │
└──────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
/workspace/
├── mgx_backend/          # Python backend
│   ├── api.py           # FastAPI wrapper
│   ├── software_company.py
│   ├── roles/           # AI agents
│   ├── actions/         # Agent actions
│   └── .env            # Configuration
├── mgx_frontend/        # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   ├── hooks/       # React hooks
│   │   └── types/       # TypeScript types
│   └── package.json
└── start_mgx_demo.sh   # Launch script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- OpenAI API Key

### Step 1: Configure Backend

```bash
cd /workspace/mgx_backend

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
# Set: OPENAI_API_KEY=sk-your-api-key-here
```

### Step 2: Start the Application

**Option A: Start Everything (Recommended)**
```bash
cd /workspace
chmod +x start_mgx_demo.sh
./start_mgx_demo.sh
```

**Option B: Start Separately**

Terminal 1 - Backend:
```bash
cd /workspace/mgx_backend
chmod +x start_api.sh
./start_api.sh
```

Terminal 2 - Frontend:
```bash
cd /workspace/mgx_frontend
chmod +x start_frontend.sh
./start_frontend.sh
```

### Step 3: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 💻 Usage

1. **Enter Project Idea**: Type your project description in the chat panel
   - Example: "Create a 2048 game"
   - Example: "Build a todo list app with React"

2. **Set Budget**: Adjust the investment slider (default: $5.00)

3. **Generate**: Click "Generate Project" button

4. **Watch Progress**: See real-time updates as AI agents work:
   - ProductManager writes PRD
   - Architect designs system
   - Engineer implements code

5. **View Results**: Browse generated files in the file explorer

6. **Download**: Click "Download Project" to get a ZIP file

## 🔌 API Endpoints

### REST API

```
POST   /api/generate          # Start new generation
GET    /api/status/{task_id}  # Get task status
GET    /api/files/{task_id}   # Get generated files
GET    /api/download/{task_id} # Download project ZIP
GET    /api/tasks             # List all tasks
DELETE /api/tasks/{task_id}   # Delete a task
```

### WebSocket

```
WS /api/ws/{task_id}  # Real-time progress updates
```

## 📊 API Usage Example

### Start Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Create a calculator app",
    "investment": 5.0,
    "n_round": 5
  }'
```

Response:
```json
{
  "task_id": "abc-123-def",
  "status": "pending"
}
```

### Check Status

```bash
curl http://localhost:8000/api/status/abc-123-def
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/abc-123-def')

ws.onmessage = (event) => {
  const update = JSON.parse(event.data)
  console.log('Progress:', update.progress, '%')
  console.log('Stage:', update.stage)
}
```

## 🎨 Frontend Components

- **Header**: Logo, cost display, download button
- **ChatPanel**: User input and conversation history
- **ProgressPanel**: Real-time agent progress visualization
- **FileExplorer**: File tree and code viewer

## 🔧 Configuration

### Backend (.env)

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo
MGX_WORKSPACE=./workspace
```

### Frontend (vite.config.ts)

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 📝 Development

### Backend Development

```bash
cd mgx_backend

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn websockets

# Run API server
python api.py

# Run tests
python -m pytest tests/
```

### Frontend Development

```bash
cd mgx_frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: API key not found
```bash
# Solution: Check .env file
cat mgx_backend/.env
# Make sure OPENAI_API_KEY is set
```

**Problem**: Port 8000 already in use
```bash
# Solution: Kill existing process
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**Problem**: Cannot connect to backend
```bash
# Solution: Check if backend is running
curl http://localhost:8000/
```

**Problem**: Dependencies not installed
```bash
# Solution: Reinstall
cd mgx_frontend
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Deployment

### Deploy Backend

```bash
# Using Docker
cd mgx_backend
docker build -t mgx-backend .
docker run -p 8000:8000 --env-file .env mgx-backend
```

### Deploy Frontend

```bash
# Build for production
cd mgx_frontend
npm run build

# Deploy to Vercel/Netlify
# Upload the dist/ folder
```

### Environment Variables for Production

```bash
# Backend
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4-turbo
CORS_ORIGINS=https://your-frontend-domain.com

# Frontend
VITE_API_URL=https://your-backend-domain.com
```

## 📊 Cost Estimation

Typical costs per project generation:

- **Simple Project** (Calculator, Todo): $0.50 - $2.00
- **Medium Project** (Game, Dashboard): $2.00 - $5.00
- **Complex Project** (Full App): $5.00 - $15.00

Factors affecting cost:
- Project complexity
- Number of rounds (n_round)
- Model used (gpt-4 vs gpt-3.5-turbo)
- Code length and detail

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Based on MetaGPT architecture
- Built with React, FastAPI, and shadcn/ui
- Powered by OpenAI GPT models

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub

---

**Happy Building! 🚀**