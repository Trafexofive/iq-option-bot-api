#!/usr/bin/env python3
"""
Setup script for IQ Option integration.
This script helps configure the IQ Option API connection.
"""

import os
import getpass
from pathlib import Path


def setup_iq_option():
    """Interactive setup for IQ Option credentials"""
    
    print("IQ Option API Setup")
    print("=" * 30)
    
    # Get credentials
    email = input("Enter your IQ Option email: ")
    password = getpass.getpass("Enter your IQ Option password: ")
    demo_mode = input("Use demo mode? (y/n, default: y): ").lower()
    demo_mode = demo_mode != 'n'
    
    # LLM provider setup
    print("\nLLM Provider Setup")
    print("-" * 20)
    
    llm_provider = input("Choose LLM provider (openai/gemini/groq/ollama, default: ollama): ").lower()
    if not llm_provider:
        llm_provider = "ollama"
    
    api_key = ""
    if llm_provider in ["openai", "gemini", "groq"]:
        api_key = getpass.getpass(f"Enter your {llm_provider.upper()} API key: ")
    
    # Create .env file
    env_content = f"""# IQ Option Configuration
IQ_OPTION_EMAIL={email}
IQ_OPTION_PASSWORD={password}
IQ_OPTION_DEMO_MODE={'true' if demo_mode else 'false'}

# LLM Configuration
LLM_PROVIDER={llm_provider}
"""
    
    if llm_provider == "openai" and api_key:
        env_content += f"OPENAI_API_KEY={api_key}\n"
    elif llm_provider == "gemini" and api_key:
        env_content += f"GEMINI_API_KEY={api_key}\n"
    elif llm_provider == "groq" and api_key:
        env_content += f"GROQ_API_KEY={api_key}\n"
    elif llm_provider == "ollama":
        env_content += "OLLAMA_BASE_URL=http://ollama:11434\n"
    
    env_content += f"""
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/trading_bot

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Configuration
LOG_LEVEL=INFO
DEBUG=false
"""
    
    # Write to .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to {env_path}")
    print("\n📋 Next steps:")
    print("1. Review your .env file")
    print("2. Start the services: make up")
    print("3. Run the basic trading example: python examples/basic_trading.py")
    
    if demo_mode:
        print("\n⚠️  Remember: You're in DEMO mode - no real money will be used!")
    else:
        print("\n⚠️  WARNING: You're in LIVE mode - real money will be used!")


if __name__ == "__main__":
    setup_iq_option()