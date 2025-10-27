"""
CSS Loader Utility for Streamlit Dashboard

This module handles loading and injecting custom CSS styles into the Streamlit app.
It provides a centralized way to manage the dashboard's visual theme.
"""

import streamlit as st
import os
from pathlib import Path


def load_custom_css():
    """
    Load and inject custom CSS into the Streamlit app.
    
    This function reads the custom.css file and injects it into the app using
    st.markdown with unsafe_allow_html=True. It should be called early in the
    app initialization process.
    
    The CSS file is located at: styles/custom.css (relative to project root)
    
    Returns:
        None
    """
    # Get the project root directory (2 levels up from this file)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    css_file_path = project_root / "styles" / "custom.css"
    
    # Check if CSS file exists
    if not css_file_path.exists():
        st.warning(f"Custom CSS file not found at: {css_file_path}")
        return
    
    # Read the CSS file
    try:
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        # Inject CSS using st.markdown
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error loading custom CSS: {str(e)}")


def apply_custom_theme():
    """
    Apply the complete custom theme to the Streamlit dashboard.
    
    This is the main function that should be called to activate the custom styling.
    It loads the CSS and can be extended to include other theme-related configurations.
    
    Usage:
        Call this function at the beginning of your Streamlit app, typically in
        the setup() function or main() function.
        
        Example:
            from src.dashboard.styles_loader import apply_custom_theme
            
            def main():
                apply_custom_theme()
                # Rest of your app code...
    
    Returns:
        None
    """
    load_custom_css()
