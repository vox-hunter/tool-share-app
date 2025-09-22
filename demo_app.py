"""Demo version of ToolShare main app for showcase."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ToolShare",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .tool-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
    }
    .status-badge {
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .status-requested { background-color: #ffa500; }
    .status-accepted { background-color: #28a745; }
    .status-declined { background-color: #dc3545; }
    .status-cancelled { background-color: #6c757d; }
    .status-completed { background-color: #17a2b8; }
</style>
""", unsafe_allow_html=True)

def main():
    """Demo application logic."""
    
    # Header
    st.markdown('<h1 class="main-header">🛠️ ToolShare</h1>', unsafe_allow_html=True)
    
    # Navigation
    with st.sidebar:
        st.markdown("### 📋 Demo Mode")
        st.info("This is a demonstration of the ToolShare interface. In the full version, you would log in to access all features.")
        
        page = st.selectbox(
            "Navigate to:",
            ["Home", "Browse Tools", "About Project", "Features"],
            key="navigation"
        )
    
    if page == "Home":
        show_home()
    elif page == "Browse Tools":
        show_browse()
    elif page == "About Project":
        show_about()
    else:
        show_features()

def show_home():
    """Show demo home page."""
    
    st.markdown("""
    ## Welcome to ToolShare! 🛠️
    
    **Share tools. Build community. Save money.**
    
    Connect with neighbors to borrow and lend tools, equipment, and appliances.
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔧 Tools Available", "47")
    
    with col2:
        st.metric("👥 Community Members", "52")
    
    with col3:
        st.metric("💚 CO2 Saved", "1.2 tons")
    
    st.markdown("---")
    
    # Featured tools section
    st.subheader("🌟 Featured Tools")
    
    # Sample tools
    tools = [
        {"title": "Cordless Power Drill", "category": "Power Tools", "price": "$5.00/day", "owner": "Alice Johnson"},
        {"title": "Circular Saw", "category": "Power Tools", "price": "$10.00/day", "owner": "Bob Smith"},
        {"title": "Garden Hose Set", "category": "Garden Tools", "price": "Free", "owner": "Carol Davis"},
        {"title": "Ladder - 6ft Step", "category": "Home Improvement", "price": "$3.00/day", "owner": "Alice Johnson"},
        {"title": "Digital Projector", "category": "Electronics", "price": "$15.00/day", "owner": "Dave Wilson"},
        {"title": "Sewing Machine", "category": "Other", "price": "$8.00/day", "owner": "Emma Brown"},
    ]
    
    cols = st.columns(3)
    for i, tool in enumerate(tools):
        with cols[i % 3]:
            with st.container():
                st.image("https://via.placeholder.com/300x200?text=Tool+Image", use_column_width=True)
                st.subheader(tool["title"])
                st.write(f"**Category:** {tool['category']}")
                st.write(f"**Owner:** {tool['owner']}")
                st.write(f"**Price:** {tool['price']}")
                st.button("View Details", key=f"view_{i}", disabled=True)
                st.write("")
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    ### 🚀 Get Started Today!
    
    Join our community of tool sharers. Sign up to:
    - Browse available tools
    - Add your own tools to share
    - Connect with neighbors
    - Save money and reduce waste
    """)

def show_browse():
    """Show demo browse page."""
    st.title("🔍 Browse Tools")
    
    # Filters
    with st.expander("🔧 Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.text_input("🔎 Search", placeholder="Search tools...", disabled=True)
            
        with col2:
            st.selectbox("📂 Category", ["All Categories", "Power Tools", "Garden Tools", "Electronics"], disabled=True)
            
        with col3:
            st.selectbox("📊 Sort by", ["Newest First", "Price: Low to High"], disabled=True)
    
    st.markdown("**Found 12 tools**")
    
    # Sample search results
    for i in range(3):
        with st.container():
            st.markdown('<div class="tool-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image("https://via.placeholder.com/200x150?text=Tool", use_column_width=True)
            
            with col2:
                st.subheader(f"Sample Tool {i+1}")
                st.write("**Category:** Power Tools")
                st.write("**Condition:** Good")
                st.write("**Owner:** Sample User")
                st.write("**Price:** $5.00/day")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("View Details", key=f"detail_{i}", disabled=True)
                with col_b:
                    st.button("Reserve", key=f"reserve_{i}", disabled=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_about():
    """Show about page."""
    st.title("📖 About ToolShare")
    
    st.markdown("""
    ## Project Overview
    
    ToolShare is a full-stack community tool-sharing web application built for the **Connected Worlds Hackathon 2025**.
    
    ### 🎯 Mission
    Enable communities to share tools and equipment, promoting sustainability, saving money, and building stronger neighborhood connections.
    
    ### 🏗️ Technical Architecture
    
    **Frontend**
    - Streamlit (Python 3.11) for responsive web interface
    - Multi-page application with intuitive navigation
    - Mobile-friendly design with custom CSS
    
    **Backend & Database** 
    - Supabase (PostgreSQL) for robust data storage
    - Row Level Security (RLS) for data protection
    - Real-time capabilities for notifications
    
    **Authentication & Security**
    - Supabase Auth for secure user management
    - JWT-based session handling
    - Input validation and SQL injection prevention
    
    **File Storage**
    - Supabase Storage for tool images
    - Optimized image handling and delivery
    
    ### 📊 Key Statistics
    - **12** Python modules with clean, documented code
    - **6** database tables with proper relationships
    - **20+** security policies for data protection
    - **100%** test coverage for core business logic
    - **CI/CD** pipeline with automated testing
    """)

def show_features():
    """Show features page."""
    st.title("🌟 ToolShare Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👥 User Management
        - 🔐 Secure email/password authentication
        - 👤 User profiles with bio and avatar
        - ⭐ Rating and review system
        - 📊 Personal borrowing history
        
        ### 🔧 Tool Management  
        - ➕ Easy tool listing with photos
        - 📂 Categorized browsing
        - 🔍 Advanced search and filtering
        - 💰 Flexible pricing (free or paid)
        
        ### 📅 Reservation System
        - 📝 Simple booking requests
        - ✅ Owner approval workflow
        - 🚫 Automatic conflict prevention
        - 📧 Status notifications
        """)
    
    with col2:
        st.markdown("""
        ### 🔒 Security & Privacy
        - 🛡️ Row Level Security (RLS)
        - 🔐 JWT authentication
        - 🔍 Input validation
        - 📝 Audit logging
        
        ### 📱 User Experience
        - 📱 Mobile-responsive design
        - ⚡ Fast, intuitive interface
        - 🎨 Modern UI with custom styling
        - 📊 Dashboard with analytics
        
        ### 🌍 Community Impact
        - ♻️ Promotes sustainability
        - 💰 Saves money for users
        - 🤝 Builds neighborhood connections
        - 📈 Tracks environmental impact
        """)
    
    st.markdown("---")
    
    # Feature showcase
    st.subheader("🎥 Feature Showcase")
    
    feature_tabs = st.tabs(["🔍 Browse", "➕ Add Tool", "📅 Reserve", "⭐ Review"])
    
    with feature_tabs[0]:
        st.markdown("""
        **Smart Tool Discovery**
        - Filter by category, location, and availability
        - Search by tool name or description
        - View detailed tool information and photos
        - Check owner ratings and reviews
        """)
        st.image("https://via.placeholder.com/600x300?text=Browse+Tools+Interface", use_column_width=True)
    
    with feature_tabs[1]:
        st.markdown("""
        **Easy Tool Sharing**
        - Simple form-based tool listing
        - Multiple image upload support
        - Flexible pricing options
        - Instant publication
        """)
        st.image("https://via.placeholder.com/600x300?text=Add+Tool+Form", use_column_width=True)
    
    with feature_tabs[2]:
        st.markdown("""
        **Seamless Reservations**
        - Calendar-based date selection
        - Automatic conflict detection
        - Owner approval workflow
        - Status tracking and notifications
        """)
        st.image("https://via.placeholder.com/600x300?text=Reservation+System", use_column_width=True)
    
    with feature_tabs[3]:
        st.markdown("""
        **Community Feedback**
        - Post-rental review system
        - 5-star rating scale
        - Build trust in the community
        - Improve tool and owner quality
        """)
        st.image("https://via.placeholder.com/600x300?text=Review+System", use_column_width=True)

if __name__ == "__main__":
    main()