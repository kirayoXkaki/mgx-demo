# MGX Demo - AI-Powered Software Development Platform

A complete web application that transforms project ideas into fully functional applications through multi-agent collaboration. Built with React, FastAPI, and powered by OpenAI.

## 🎯 Features

- **Multi-Agent Collaboration**: Three AI agents (Product Manager, Architect, Engineer) work together to generate complete software projects
- **Real-time Progress**: WebSocket-based live updates showing each agent's work
- **Interactive UI**: Modern interface with chat, progress tracking, and file explorer
- **Cost Tracking**: Monitor API usage and costs in real-time
- **File Management**: Browse and view generated files in real-time
- **Project Download**: Download complete projects as ZIP files
- **GitHub Integration**: Automatically push generated projects to GitHub with version control
- **Conversation History**: Save and load previous conversations

## 🏗️ Architecture

```
Frontend (React) ←→ WebSocket ←→ Backend (FastAPI) ←→ Agent System
                                    ↓
                               Supabase (Database + Storage)
```

### Core Components

- **Environment**: Message bus managing all agent communications
- **Role**: Base class for agents using Observe-Think-Act pattern
- **Team**: Manages multiple roles and controls workflow

### Workflow

```
User Input (e.g., "Write a Pac-Man game") → ProductManager writes PRD → 
Architect writes Design → Engineer writes Code → Complete
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Supabase account (for database and storage)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mgx-demo.git
cd mgx-demo/workspace
```

2. **Backend Setup**
```bash
cd mgx_backend
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd ../mgx_frontend
npm install
```

4. **Environment Variables**

Create `.env` file in `mgx_backend/`:
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_supabase_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
JWT_SECRET=your_jwt_secret
```

Create `.env` file in `mgx_frontend/`:
```env
VITE_API_URL=http://localhost:8000
```

5. **Initialize Database**
```bash
cd mgx_backend
python init_db.py
```

6. **Start the Application**

Terminal 1 - Backend:
```bash
cd mgx_backend
python -m uvicorn api:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd mgx_frontend
npm run dev
```

7. **Open in Browser**
```
http://localhost:3000
```

## 📁 Project Structure

```
workspace/
├── mgx_backend/          # Python backend
│   ├── api.py            # FastAPI application
│   ├── software_company.py  # Core generation logic
│   ├── team.py           # Team management
│   ├── role.py           # Agent base class
│   ├── roles/            # Agent implementations
│   ├── actions/          # Action implementations
│   └── requirements.txt  # Python dependencies
│
├── mgx_frontend/         # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── lib/         # Utilities
│   └── package.json      # Node dependencies
│
└── IMPLEMENTATION_GUIDE.md  # Detailed implementation guide
```

## 🛠️ Technology Stack

### Frontend
- **React 18** + **TypeScript**: Modern UI framework
- **Vite**: Fast build tool
- **Tailwind CSS**: Styling
- **WebSocket**: Real-time communication

### Backend
- **FastAPI**: High-performance async web framework
- **WebSocket**: Real-time updates
- **SQLAlchemy**: ORM for database operations
- **OpenAI API**: LLM integration

### Database & Storage
- **Supabase PostgreSQL**: Database
- **Supabase Storage**: File storage

## 💡 Usage

1. **Start a New Project**
   - Enter your project idea in the chat input (e.g., "Write a Pac-Man game")
   - Set your budget (default: $5)
   - Click "Generate"

2. **Watch the Agents Work**
   - Product Manager writes the PRD
   - Architect designs the system
   - Engineer implements the code
   - All progress is shown in real-time

3. **View Generated Files**
   - Files appear in the file explorer as they're generated
   - Click any file to view its content
   - Syntax highlighting for code files

4. **Download Project**
   - Click "Download Project" to get a ZIP file
   - Or push directly to GitHub using the GitHub integration

## 🔧 Development

### Backend Development
```bash
cd mgx_backend
python -m uvicorn api:app --reload
```

### Frontend Development
```bash
cd mgx_frontend
npm run dev
```

### Running Tests
```bash
cd mgx_backend
python -m pytest
```

## 📦 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository
2. Set build command: `cd mgx_frontend && npm install && npm run build`
3. Set output directory: `mgx_frontend/dist`
4. Add environment variable: `VITE_API_URL`

### Backend (Railway)
1. Connect your GitHub repository
2. Set root directory: `workspace/mgx_backend`
3. Add all environment variables
4. Railway will auto-detect Python and install dependencies

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## 🎨 Key Features Explained

### Multi-Agent System
Three specialized agents collaborate:
- **Product Manager**: Analyzes requirements and writes PRD
- **Architect**: Designs system architecture
- **Engineer**: Implements code

### Real-time Updates
WebSocket connection provides live updates:
- Agent thinking status
- Progress percentage
- File generation
- Cost tracking

### GitHub Integration
Automatically:
- Initializes Git repository
- Creates `.gitignore` based on project type
- Pushes to GitHub
- Sets up CI/CD templates

## 📚 Documentation

- [Implementation Guide](./IMPLEMENTATION_GUIDE.md) - Detailed development process
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Deployment instructions
- [Supabase Setup](./SUPABASE_SETUP.md) - Database configuration
- [Supabase Storage Setup](./SUPABASE_STORAGE_SETUP.md) - File storage setup

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🙏 Acknowledgments

- Built on top of MetaGPT concepts
- Powered by OpenAI
- UI inspired by modern design systems

---

**Made with ❤️ using AI-assisted development**

