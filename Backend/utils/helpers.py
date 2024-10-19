import logging
from typing import List
import re

def setup_logging():
    """Set up logging configuration for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def validate_user_input(area_of_interest: str, content_type: str, keywords: List[str], post_frequency: int) -> bool:
    """
    Validate user input for creating a content schedule.
    
    Args:
    area_of_interest (str): The main topic area.
    content_type (str): The type of content to be created.
    keywords (List[str]): List of relevant keywords.
    post_frequency (int): Number of posts per week.

    Returns:
    bool: True if input is valid, False otherwise.
    """
    if not area_of_interest or not content_type:
        return False
    if not keywords or len(keywords) == 0:
        return False
    if post_frequency < 1 or post_frequency > 7:
        return False
    return True

def format_content(content: str) -> str:
    """
    Format the generated content for better readability.
    
    Args:
    content (str): The raw generated content.

    Returns:
    str: Formatted content.
    """
    # Add line breaks after periods for better readability
    formatted = re.sub(r'\.(?=\s|$)', '.\n\n', content)
    
    # Capitalize the first letter of each sentence
    formatted = '. '.join(s.capitalize() for s in formatted.split('. '))
    
    return formatted.strip()