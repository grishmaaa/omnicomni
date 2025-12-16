# Groq API Test with curl
# Use this to test your API key directly (as Groq support suggested)

# Replace YOUR_API_KEY_HERE with your actual key from the developer account

curl https://api.groq.com/openai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [
      {
        "role": "user",
        "content": "Say this is a test"
      }
    ],
    "max_tokens": 10
  }'

# Expected output if key works:
# {
#   "choices": [
#     {
#       "message": {
#         "content": "This is a test"
#       }
#     }
#   ]
# }

# If you see "organization_restricted" error, the key is from the wrong account
