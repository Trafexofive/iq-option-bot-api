#!/bin/bash

# Setup the smallest possible Ollama model for testing
echo "🦙 Setting up TinyLlama - smallest model (~637MB)"

# Wait for Ollama to be ready
echo "Waiting for Ollama service..."
sleep 5

# Pull the smallest model
echo "📥 Pulling TinyLlama model..."
docker exec iq-ollama ollama pull tinyllama

echo "✅ TinyLlama setup complete!"
echo "Model size: ~637MB"
echo "Perfect for laptop testing 💻"