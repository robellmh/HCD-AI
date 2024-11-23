#!/bin/bash
MODEL_NAME=${LLM_MODEL:-"llama3.2:1b"}

echo "Using model: $MODEL_NAME"

ollama serve &
# Record Process ID.
pid=$!
sleep 5

echo "🔴 Retrieving model $MODEL_NAME..."
ollama pull $MODEL_NAME
echo "🟢 Done!"

# Wait for Ollama process to finish.
wait $pid
