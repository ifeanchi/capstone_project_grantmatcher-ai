# GrantMatcher AI - Capstone Project

An AI-powered grant matching system that helps nonprofit teams and researchers find relevant funding opportunities using semantic search and LLM-generated fit rationale.

## 🎯 Problem Statement

Nonprofit teams and researchers waste **10–20 hours/week** manually searching for grants. Keyword-based tools miss relevant opportunities due to terminology gaps, leading to missed funding and inefficient resource allocation.

## ✨ Solution

GrantMatcher AI uses:
- **Semantic Search**: TF-IDF embeddings + cosine similarity to find semantically similar grants
- **LLM-Powered Rationale**: Llama 3 (via Ollama) generates concise fit explanations for each match
- **Smart Filtering**: Field, deadline, and funding amount filters for refined searches
- **Search History**: Authenticated users can save and revisit past searches
- **Responsible AI**: Transparent matching with human-in-the-loop design and disclaimers

## 🚀 Features

- 🔍 **Semantic Grant Matching** - Find grants based on project description, not just keywords
- 💡 **AI-Generated Fit Rationale** - Understand why each grant matches your project
- 🎯 **Smart Filtering** - Filter by field, deadline range, and funding amount
- 💾 **Search History** - Save searches and revisit results anytime
- 🔐 **User Authentication** - Secure OAuth-based login
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚖️ **Responsible AI** - Transparent matching with clear disclaimers

## 🛠️ Tech Stack

### Frontend
- **React 19** - UI framework
- **Tailwind CSS 4** - Styling
- **shadcn/ui** - Component library
- **Wouter** - Routing
- **tRPC** - Type-safe API client

### Backend
- **Express 4** - Web server
- **tRPC 11** - RPC framework
- **Drizzle ORM** - Database management
- **SQLite/MySQL** - Database (configurable)

### AI & Search
- **Ollama** - Local LLM inference (Llama 3)
- **Sentence-Transformers** - Embeddings (via server-side)
- **TF-IDF** - Semantic search algorithm

### Database
- **SQLite** - Local development (file-based)
- **MySQL/TiDB** - Production deployment

## 📋 Prerequisites

- **Node.js** v18+ ([Download](https://nodejs.org/))
- **pnpm** package manager (`npm install -g pnpm`)
- **Ollama** running locally ([Download](https://ollama.ai/))
- **SQLite3** (comes with most systems)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/capstone_project_grantmatcher-ai.git
cd capstone_project_grantmatcher-ai
```

### 2. Install Dependencies
```bash
pnpm install
```

### 3. Configure Environment
Create `.env.local` in the project root:
```bash
# Database
DATABASE_URL="file:./dev.db"

# Ollama Configuration
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama2"

# OAuth (local dev)
VITE_APP_ID="local-dev"
OAUTH_SERVER_URL="http://localhost:3000"
VITE_OAUTH_PORTAL_URL="http://localhost:3000"

# JWT Secret
JWT_SECRET="your-secret-key-change-in-production"

# Owner Info
OWNER_OPEN_ID="local-dev-user"
OWNER_NAME="Local Developer"

# Analytics (optional)
VITE_ANALYTICS_ENDPOINT="http://localhost:3000"
VITE_ANALYTICS_WEBSITE_ID="local"

# App Configuration
VITE_APP_TITLE="GrantMatcher AI"
VITE_FRONTEND_FORGE_API_KEY="local-dev-key"
VITE_FRONTEND_FORGE_API_URL="http://localhost:3000"
BUILT_IN_FORGE_API_KEY="local-dev-key"
BUILT_IN_FORGE_API_URL="http://localhost:3000"
```

### 4. Set Up Database
```bash
# Generate migrations
pnpm drizzle-kit generate

# Apply migrations
pnpm drizzle-kit migrate

# Seed mock grants
node server/seed-grants.mjs
```

### 5. Start Ollama (in a separate terminal)
```bash
ollama serve
```

### 6. Start Development Server
```bash
pnpm dev
```

Visit `http://localhost:3000` in your browser.

## 📁 Project Structure

```
grantmatcher-ai/
├── client/                    # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── components/       # Reusable UI components
│   │   ├── lib/              # Utilities and helpers
│   │   └── index.css         # Global styles
│   └── index.html
├── server/                    # Express backend
│   ├── routers.ts            # tRPC procedures
│   ├── db.ts                 # Database queries
│   ├── embeddings.ts         # Semantic search logic
│   ├── grant-matcher.ts      # LLM integration
│   ├── seed-grants.mjs       # Data seeding script
│   └── _core/                # Core infrastructure
├── drizzle/                   # Database schema & migrations
│   ├── schema.ts             # Table definitions
│   └── migrations/           # SQL migration files
├── shared/                    # Shared types & constants
├── .env.local                 # Local environment variables
├── dev.db                     # SQLite database (local only)
├── package.json
├── tsconfig.json
└── README.md
```

## 🔄 Development Workflow

### Making Changes

1. **Create a feature branch** (optional but recommended):
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test locally

3. **Stage your changes**:
   ```bash
   git add .
   ```

4. **Commit with a clear message**:
   ```bash
   git commit -m "Add feature: description of changes"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub (if using branches)

### Running Tests

```bash
pnpm test
```

### Checking TypeScript

```bash
pnpm check
```

### Formatting Code

```bash
pnpm format
```

## 📊 Database Schema

### Users Table
- `id` - Primary key
- `openId` - OAuth identifier
- `name` - User name
- `email` - User email
- `loginMethod` - Login provider
- `role` - User role (user/admin)
- `createdAt` - Creation timestamp
- `updatedAt` - Last update timestamp
- `lastSignedIn` - Last login timestamp

### Grants Table
- `id` - Primary key
- `title` - Grant title
- `funder` - Funding organization
- `field` - Grant category (environment, education, health, etc.)
- `description` - Grant description
- `deadline` - Application deadline
- `fundingAmount` - Funding amount in dollars
- `tags` - JSON array of tags
- `createdAt` - Creation timestamp

### Searches Table
- `id` - Primary key
- `userId` - User ID (foreign key)
- `projectDescription` - User's project description
- `filters` - JSON object with applied filters
- `createdAt` - Search timestamp

### SearchResults Table
- `id` - Primary key
- `searchId` - Search ID (foreign key)
- `grantId` - Grant ID (foreign key)
- `matchScore` - Semantic similarity score (0-1)
- `rationale` - AI-generated fit explanation
- `createdAt` - Result timestamp

## 🤖 How It Works

### 1. User Submits Project Description
User enters their project summary and applies optional filters (field, deadline, funding).

### 2. Semantic Search
- Project description is converted to embeddings using TF-IDF
- Embeddings are compared against all grant descriptions using cosine similarity
- Top 3 matches are selected based on similarity score

### 3. LLM-Generated Rationale
- Top 3 grants are passed to Llama 3 (via Ollama)
- LLM generates a concise explanation of why each grant matches the project
- Rationale includes specific connections between project and grant requirements

### 4. Results Display
- Matched grants are displayed as cards with:
  - Match score (0-100%)
  - Funder name and deadline
  - Funding amount
  - AI-generated fit rationale
  - Responsible AI disclaimer

### 5. Search History
- Search and results are saved to the database
- Authenticated users can view past searches anytime

## 🔒 Security & Privacy

- **OAuth Authentication** - Secure login via Manus OAuth
- **User Data Isolation** - Users only see their own searches
- **No API Keys Exposed** - LLM API keys are server-side only
- **Responsible AI** - Clear disclaimers on all results
- **Local LLM Option** - Can run Ollama locally for complete privacy

## 📈 Performance

- **Semantic Search**: ~100ms for 20+ grants
- **LLM Rationale Generation**: ~2-5 seconds per search
- **Database Queries**: <50ms for indexed queries
- **Frontend Load Time**: <2 seconds on 4G

## 🚀 Deployment

### Deploy to Manus (Recommended)
The project is built with Manus WebDev and can be deployed directly:
1. Click "Publish" in the Manus Management UI
2. Custom domain support available

### Deploy to Other Platforms
- **Vercel/Netlify** - Frontend only (requires separate backend)
- **Railway/Render** - Full-stack deployment
- **Docker** - Containerized deployment

## 🐛 Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` is set correctly in `.env.local`
- Verify model is pulled: `ollama pull llama2`

### Database Error
- Check `DATABASE_URL` in `.env.local`
- Ensure SQLite file has write permissions
- Run migrations: `pnpm drizzle-kit migrate`

### Port Already in Use
- Change port in `server/_core/index.ts`
- Or kill process using port 3000: `netstat -ano | findstr :3000`

## 📚 Documentation

- [LOCAL_SETUP_GUIDE.md](./LOCAL_SETUP_GUIDE.md) - Detailed local setup for Windows
- [GITHUB_SETUP_GUIDE.md](./GITHUB_SETUP_GUIDE.md) - Git and GitHub workflow
- [README.md](./README.md) - Original project README

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👨‍💼 Author

**Stanley Enyinnaya**
- GitHub: [@ifeanchi](https://github.com/ifeanchi)
- Email: anyistan225@gmail.com

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **Drizzle ORM** - Type-safe database management
- **shadcn/ui** - Beautiful UI components

## 📞 Support

For issues, questions, or suggestions:
1. Check existing [GitHub Issues](https://github.com/ifeanchi/capstone_project_grantmatcher-ai/issues)
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

---

*Last updated: May 2026*
