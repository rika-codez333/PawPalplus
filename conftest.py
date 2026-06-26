import sys
import os

# Automatically append project root to sys.path during testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
