curl -X POST https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill \
-H "Authorization: Bearer hf-token" \
-H "Content-Type: application/json" \
-d '{"inputs":"Hello"}'