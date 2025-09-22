"""Home page for ToolShare."""

import streamlit as st

from lib.services import ToolService
from lib.supabase_client import get_current_user


def main():
    current_user = get_current_user()

    # Hero section
    st.markdown(
        """
    ## Welcome to ToolShare! 🛠️

    **Share tools. Build community. Save money.**

    Connect with neighbors to borrow and lend tools, equipment, and appliances.
    """
    )

    # Quick stats and call-to-action
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🔧 Tools Available", get_tool_count())

    with col2:
        st.metric("👥 Community Members", "50+")  # Placeholder

    with col3:
        st.metric("💚 CO2 Saved", "1.2 tons")  # Placeholder

    st.markdown("---")

    # Featured tools section
    st.subheader("🌟 Featured Tools")

    try:
        # Get recent tools
        featured_tools = ToolService.get_tools()[:6]  # Get 6 most recent

        if featured_tools:
            # Display in grid
            cols = st.columns(3)
            for i, tool in enumerate(featured_tools):
                with cols[i % 3]:
                    with st.container():
                        # Tool image placeholder
                        if tool.images:
                            st.image(tool.images[0], use_column_width=True)
                        else:
                            st.image(
                                "https://via.placeholder.com/300x200?text=No+Image",
                                use_column_width=True,
                            )

                        st.subheader(tool.title)
                        st.write(f"**Category:** {tool.category}")

                        if tool.description:
                            description = tool.description[:100]
                            if len(tool.description) > 100:
                                description += "..."
                            st.write(description)

                        st.write(
                            f"**Owner:** {tool.owner.full_name if tool.owner and tool.owner.full_name else 'Anonymous'}"
                        )

                        if tool.daily_price > 0:
                            st.write(f"**Price:** ${tool.daily_price:.2f}/day")
                        else:
                            st.write("**Price:** Free")

                        # Add some spacing
                        st.write("")
        else:
            st.info("No tools available yet. Be the first to add a tool!")

    except Exception as e:
        st.error(f"Error loading featured tools: {str(e)}")

    st.markdown("---")

    # Call to action
    if current_user:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
            ### 🔍 Browse Tools
            Find the perfect tool for your next project.
            """
            )
            if st.button("Browse All Tools", key="browse_tools"):
                st.session_state.navigation = "Browse Tools"
                st.rerun()

        with col2:
            st.markdown(
                """
            ### ➕ Add Your Tool
            Share your tools with the community.
            """
            )
            if st.button("Add a Tool", key="add_tool"):
                st.session_state.navigation = "Add Tool"
                st.rerun()
    else:
        st.markdown(
            """
        ### 🚀 Get Started Today!

        Join our community of tool sharers. Sign up to:
        - Browse available tools
        - Add your own tools to share
        - Connect with neighbors
        - Save money and reduce waste
        """
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sign Up Now", key="signup_cta"):
                st.session_state.auth_option = "Sign Up"
                st.rerun()

        with col2:
            if st.button("Login", key="login_cta"):
                st.session_state.auth_option = "Login"
                st.rerun()

    # About section
    st.markdown("---")
    st.markdown(
        """
    ### 🌍 Why ToolShare?

    **For the Environment** 🌱
    Reduce manufacturing demand and waste by sharing resources.

    **For Your Wallet** 💰
    Save money by borrowing instead of buying expensive tools you'll rarely use.

    **For Community** 🤝
    Build connections with neighbors and strengthen local relationships.

    **For Convenience** ⚡
    Access tools when you need them without storage hassles.
    """
    )


def get_tool_count():
    """Get total number of active tools."""
    try:
        tools = ToolService.get_tools()
        return len(tools)
    except Exception:
        return "0"


if __name__ == "__main__":
    main()
