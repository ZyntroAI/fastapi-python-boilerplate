---
name: Coding Standards
description: Rules for writing code in this project
---

# Coding Standards

## Python Style
- Use **snake_case** for functions and variables
- Use **PascalCase** for classes
- Use type hints everywhere
- Max line length: 100 characters

## Imports Order
1. Standard library
2. Third-party packages
3. Local modules

## FastAPI Patterns
- Define response models in the same route file or separate schemas/ folder
- Use `HTTPException` for error handling
- Add docstrings to all public endpoints
- Pydantic models go in `api/schemas/`
