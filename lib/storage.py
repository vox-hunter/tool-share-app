"""
Local file storage utilities for ToolShare.
"""
import os
import uuid
from typing import List, Optional
from PIL import Image
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# Configuration
UPLOADS_DIR = "uploads"
AVATARS_DIR = "avatars"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
IMAGE_QUALITY = 85
MAX_IMAGE_SIZE = (1024, 1024)  # Max width, height

def ensure_directories():
    """Ensure upload directories exist."""
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(AVATARS_DIR, exist_ok=True)

def validate_image(uploaded_file) -> bool:
    """Validate uploaded image file."""
    if uploaded_file is None:
        return False
        
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        st.error(f"File size too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.")
        return False
    
    # Check file extension
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        return False
    
    return True

def save_image(uploaded_file, directory: str = UPLOADS_DIR) -> Optional[str]:
    """
    Save uploaded image file to local storage.
    Returns the relative path to the saved file, or None if failed.
    """
    if not validate_image(uploaded_file):
        return None
    
    ensure_directories()
    
    try:
        # Generate unique filename
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(directory, filename)
        
        # Open and process image
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Save image
        image.save(filepath, quality=IMAGE_QUALITY, optimize=True)
        
        logger.info(f"Image saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving image: {e}")
        st.error("Failed to save image. Please try again.")
        return None

def save_tool_images(uploaded_files) -> List[str]:
    """Save multiple tool images and return list of paths."""
    image_paths = []
    
    for uploaded_file in uploaded_files:
        path = save_image(uploaded_file, UPLOADS_DIR)
        if path:
            image_paths.append(path)
    
    return image_paths

def save_avatar(uploaded_file) -> Optional[str]:
    """Save user avatar image."""
    return save_image(uploaded_file, AVATARS_DIR)

def delete_image(filepath: str) -> bool:
    """Delete an image file safely."""
    if not filepath:
        return True
        
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Image deleted: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting image: {e}")
        return False

def delete_images(filepaths: List[str]) -> bool:
    """Delete multiple image files."""
    success = True
    for filepath in filepaths:
        if not delete_image(filepath):
            success = False
    return success

def get_image_url(filepath: str) -> str:
    """Get URL for serving image (for Streamlit display)."""
    if not filepath or not os.path.exists(filepath):
        return ""
    return filepath

def display_image(filepath: str, caption: str = "", width: Optional[int] = None):
    """Display image in Streamlit with error handling."""
    if filepath and os.path.exists(filepath):
        try:
            st.image(filepath, caption=caption, width=width)
        except Exception as e:
            logger.error(f"Error displaying image {filepath}: {e}")
            st.error("Failed to display image")
    else:
        st.write("No image available")

def display_image_gallery(image_paths: List[str], max_columns: int = 3):
    """Display a gallery of images in columns."""
    if not image_paths:
        st.write("No images available")
        return
    
    # Filter out invalid paths
    valid_paths = [path for path in image_paths if path and os.path.exists(path)]
    
    if not valid_paths:
        st.write("No valid images found")
        return
    
    # Display images in columns
    cols = st.columns(min(len(valid_paths), max_columns))
    
    for i, image_path in enumerate(valid_paths):
        with cols[i % len(cols)]:
            display_image(image_path, width=200)

def cleanup_orphaned_files():
    """Clean up files that are no longer referenced in the database."""
    # This would require database queries to find referenced files
    # and remove any files not in the database
    # Implementation would be more complex and is optional for MVP
    pass