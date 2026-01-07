"""Utility functions for .env file management."""
import os
import re
from typing import Dict

ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")


def read_env_file() -> Dict[str, str]:
    """Read .env file and return as dictionary."""
    env_vars = {}
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
    return env_vars


def write_env_file(env_vars: Dict[str, str]) -> bool:
    """Write dictionary to .env file."""
    try:
        with open(ENV_FILE_PATH, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        return True
    except Exception as e:
        print(f"Error writing .env file: {e}")
        return False


def update_env_variable(key: str, value: str) -> bool:
    """Update a single environment variable in .env file."""
    env_vars = read_env_file()
    env_vars[key] = value
    return write_env_file(env_vars)


def update_env_variables(updates: Dict[str, str]) -> bool:
    """Update multiple environment variables in .env file."""
    env_vars = read_env_file()
    env_vars.update(updates)
    return write_env_file(env_vars)
