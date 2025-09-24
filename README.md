# 🛠️ ToolShare

**Local-First Community Tool Sharing Platform**

ToolShare is a local-first, production-ready web application that helps neighbors share tools and equipment. Built with Streamlit and SQLite, it runs entirely locally without any external dependencies or cloud services.

> *Building sustainable communities through sharing and collaboration.*

## 🌟 Features

* 🔐 **Local User System** - Sign up and login with secure password hashing
* 🔍 **Browse & Search Tools** - Find tools by category, availability, and owner
* ➕ **Tool Management** - Add, edit, and manage your tool listings with image uploads
* 📅 **Reservation System** - Request tools, approve/decline requests, calendar management
* 👤 **User Profiles** - Customizable profiles with avatars and bios
* ⭐ **Reviews & Ratings** - Rate and review tools after completed rentals
* 🔔 **Notifications** - Console logging and activity tracking
* 🛡️ **Admin Panel** - Comprehensive system administration interface
* 🧪 **Tested & Reliable** - Full unit test coverage with automated CI
* 🌱 **Local-First** - No internet required, runs completely offline

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Python-based UI framework)
* **Database:** SQLite (single-file database with no external dependencies)
* **Authentication:** Local user system with bcrypt password hashing
* **Storage:** Local filesystem for images and avatars
* **Testing:** pytest with comprehensive unit tests
* **CI/CD:** GitHub Actions for automated testing and linting

## 📦 Quick Start

### Prerequisites

* Python 3.9 or higher
* pip (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/vox-hunter/tool-share-app.git
cd tool-share-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the Database and Seed Data

```bash
python seed_data.py
```

This creates the SQLite database and populates it with demo users, tools, and reservations.

### 4. Run the Application

```bash
streamlit run app/home.py
```

The application will open at [http://localhost:8501](http://localhost:8501).

## 👥 Demo Accounts

The seed data script creates several demo accounts you can use immediately:

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Admin | System administrator with full access |
| `alice_builder` | `password123` | User | DIY enthusiast with power tools |
| `bob_gardener` | `password123` | User | Gardener with outdoor equipment |
| `carol_chef` | `password123` | User | Chef with kitchen appliances |
| `david_mechanic` | `password123` | User | Mechanic with automotive tools |

## 📂 Project Structure

```
toolshare/
├── app/                    # Streamlit pages
│   ├── home.py            # Homepage with featured tools
│   ├── browse.py          # Browse and search tools
│   ├── tool_detail.py     # Individual tool details and reservation
│   ├── add_tool.py        # Add/edit tool form
│   ├── my_tools.py        # Manage user's tools and requests
│   ├── reservations.py    # View and manage reservations
│   ├── profile.py         # User profile management
│   ├── login.py           # User login
│   ├── signup.py          # User registration
│   └── admin.py           # Admin panel (admin users only)
├── lib/                   # Core business logic
│   ├── db.py             # Database connection and schema
│   ├── auth.py           # Authentication and user management
│   ├── services.py       # Tool, reservation, and review services
│   └── storage.py        # File upload and image handling
├── tests/                 # Unit tests
│   └── test_core.py      # Core functionality tests
├── uploads/              # Tool images (created at runtime)
├── avatars/              # User profile pictures (created at runtime)
├── .github/workflows/    # CI/CD configuration
├── seed_data.py          # Database seeding script
├── requirements.txt      # Python dependencies
├── toolshare.db         # SQLite database (created at runtime)
└── README.md            # This file
```

## 🧪 Testing

Run the unit tests to verify everything works correctly:

```bash
python -m pytest tests/ -v
```

Run linting and formatting:

```bash
ruff check .
black --check .
```

## 🔧 Development

### Adding New Features

1. Core business logic goes in `lib/`
2. UI components go in `app/`
3. Add tests for new functionality in `tests/`
4. Update database schema in `lib/db.py` if needed

### Database Schema

The application uses SQLite with the following main tables:

* **users** - User accounts and profiles
* **tools** - Tool listings with images and details
* **reservations** - Tool reservation requests and bookings
* **reviews** - User reviews and ratings
* **audit_logs** - System activity logging

### File Storage

* Tool images are stored in `uploads/`
* User avatars are stored in `avatars/`
* Images are automatically resized and optimized
* Only JPG, PNG, and GIF formats are supported

## 🚀 Deployment

### Local Deployment

The application is designed to run locally. Simply follow the Quick Start guide above.

### Docker Deployment (Optional)

```bash
# Build image
docker build -t toolshare .

# Run container
docker run -p 8501:8501 toolshare
```

### Production Considerations

* The SQLite database is stored as a single file (`toolshare.db`)
* Upload directories (`uploads/`, `avatars/`) need to be writable
* For multi-user production environments, consider regular database backups
* Admin panel provides system monitoring and user management

## 🔐 Security Features

* Passwords are hashed using bcrypt with salt
* Input validation on all forms
* File upload restrictions (type, size)
* SQL injection prevention with parameterized queries
* Session-based authentication
* Admin-only access controls

## 🌍 Hackathon Theme Alignment

**"Connected Worlds: Innovating Together"**

ToolShare embodies this theme by:

* **Building Local Communities** - Connects neighbors through tool sharing
* **Promoting Sustainability** - Reduces waste through equipment reuse
* **Fostering Collaboration** - Encourages mutual aid and resource sharing
* **Innovation in Simplicity** - Local-first approach requires no cloud infrastructure

## 📜 License

This project is open-sourced under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📧 Support

For questions or support, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for the Connected Worlds Hackathon 2025**