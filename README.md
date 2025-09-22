# 🛠️ ToolShare

**A Community Tool-Sharing Platform**

ToolShare is a full-stack web application that enables communities to share tools and equipment with their neighbors. Built with Streamlit and Supabase, it promotes sustainability, saves money, and builds stronger local connections.

[![CI/CD Pipeline](https://github.com/vox-hunter/tool-share-app/actions/workflows/ci.yml/badge.svg)](https://github.com/vox-hunter/tool-share-app/actions/workflows/ci.yml)

## 🌟 Features

### Core Functionality
- 🔐 **User Authentication** - Email/password signup and login via Supabase Auth
- 🔍 **Browse & Search Tools** - Filter by category, availability, and search terms
- ➕ **Add/Manage Tools** - Full CRUD operations for tool listings with image uploads
- 📅 **Reservation System** - Request, approve/decline, and manage tool borrowing
- ⭐ **Reviews & Ratings** - Rate completed borrowing experiences
- 👤 **User Profiles** - Manage personal information and view borrowing history
- 🛡️ **Admin Panel** - Platform management and monitoring

### Advanced Features
- 📸 **Image Upload** - Tool photos via Supabase Storage
- 🔒 **Row Level Security** - Database-level authorization
- 🚫 **Conflict Prevention** - Prevents double-booking with database constraints
- 📊 **Analytics** - Tool popularity and user statistics
- 🔔 **Audit Logging** - Track all platform activities
- 📱 **Responsive Design** - Mobile-friendly interface

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Streamlit (Python 3.11)
- **Backend/Database**: Supabase (PostgreSQL + Auth + Storage)
- **Authentication**: Supabase Auth
- **File Storage**: Supabase Storage
- **Testing**: pytest
- **Linting**: black, ruff
- **CI/CD**: GitHub Actions
- **Deployment**: Docker-ready

### Project Structure
```
toolshare/
├── app/                    # Streamlit page modules
│   ├── home.py            # Home page
│   ├── browse.py          # Tool browsing and search
│   ├── add_tool.py        # Tool creation/editing
│   ├── my_tools.py        # User's tool management
│   ├── reservations.py    # Reservation management
│   ├── profile.py         # User profile management
│   ├── admin.py           # Admin panel
│   ├── login.py           # Authentication
│   └── signup.py          # User registration
├── lib/                   # Core business logic
│   ├── supabase_client.py # Database connection
│   ├── models.py          # Data models
│   └── services.py        # Business logic layer
├── migrations/            # Database schema
│   └── 001_initial_schema.sql
├── tests/                 # Unit tests
│   └── test_services.py
├── main.py               # Main Streamlit app
├── seed_data.py          # Development data seeding
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Supabase account
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/vox-hunter/tool-share-app.git
cd tool-share-app
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Supabase

#### Create a Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your Project URL and anon public API key

#### Set Up Database Schema
1. In your Supabase dashboard, go to SQL Editor
2. Copy and run the contents of `migrations/001_initial_schema.sql`
3. This creates all tables, indexes, and Row Level Security policies

#### Configure Storage
1. In Supabase dashboard, go to Storage
2. Create a new bucket called `tool-images`
3. Set bucket to public if you want direct image access

#### Environment Configuration
Create `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### 4. Seed Development Data (Optional)
```bash
python seed_data.py
```

### 5. Run the Application
```bash
streamlit run main.py
```

Visit `http://localhost:8501` to access the application.

## 📊 Database Schema

### Core Tables

**users**
- User profiles and authentication data
- Links to Supabase Auth

**tools** 
- Tool listings with metadata
- Owned by users, supports categories and pricing

**reservations**
- Borrowing requests and approvals
- Prevents double-booking via constraints

**reviews**
- Post-rental feedback and ratings
- Linked to completed reservations

**tool_images**
- Image metadata for tool photos
- References Supabase Storage paths

**audit_logs**
- Platform activity tracking
- JSON payload for flexible logging

### Security Features
- **Row Level Security (RLS)** on all tables
- **JWT-based authentication** via Supabase
- **Parameterized queries** prevent SQL injection
- **Input validation** on all user data

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lib

# Run specific test file
pytest tests/test_services.py -v
```

### Test Coverage
- Unit tests for business logic
- Reservation conflict detection
- Date validation
- Authentication guards

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t toolshare .

# Run container
docker run -p 8501:8501 toolshare
```

### Streamlit Cloud
1. Fork this repository
2. Connect to Streamlit Cloud
3. Add your Supabase credentials to secrets
4. Deploy automatically

### Environment Variables
For production deployment, set these environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon public key

## 🔧 Development

### Code Quality
```bash
# Lint code
ruff check .

# Format code  
black .

# Type checking (if using mypy)
mypy lib/
```

### Development Workflow
1. Create feature branch
2. Write tests for new functionality
3. Implement features
4. Ensure all tests pass
5. Format and lint code
6. Submit pull request

### Adding New Features
1. **Database Changes**: Add migrations to `migrations/`
2. **Models**: Update `lib/models.py` for new data structures
3. **Services**: Add business logic to `lib/services.py`
4. **UI**: Create/update pages in `app/`
5. **Tests**: Add tests in `tests/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure CI passes

## 📋 API Reference

### Reservation Business Logic

**Conflict Detection**
```python
ReservationService.has_conflict(tool_id, start_date, end_date)
```

**Create Reservation**
```python
ReservationService.create_reservation(
    tool_id="uuid",
    borrower_id="uuid", 
    start_date=date(2024, 3, 15),
    end_date=date(2024, 3, 17)
)
```

**Update Status**
```python
ReservationService.update_reservation_status(
    reservation_id="uuid",
    status=ReservationStatus.ACCEPTED,
    actor_id="uuid"
)
```

## 🐛 Known Issues & Limitations

### Current Limitations
- Image upload limited to basic file types
- Location features are basic (lat/lng only)
- Email notifications are simulated
- Admin features are demonstration-level
- No payment processing integration

### Planned Improvements
- [ ] Real-time notifications
- [ ] Advanced search with geolocation
- [ ] Payment integration
- [ ] Mobile app
- [ ] Advanced admin analytics
- [ ] Messaging between users
- [ ] Tool availability calendar widget

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Supabase** for providing an excellent backend-as-a-service
- **Streamlit** for making Python web apps accessible
- **Connected Worlds Hackathon 2025** for the inspiration

## 📞 Support

For support, email support@toolshare.example.com or create an issue in this repository.

---

**Built with ❤️ for community sharing**