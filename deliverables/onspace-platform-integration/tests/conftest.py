"""Test fixtures — make `onspace` importable without installing the package."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
