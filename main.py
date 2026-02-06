from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Hugging Face API endpoint
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

# WhatsApp API endpoint
WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "Bot is running!", "message": "WhatsApp AI Bot is active"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint for WhatsApp
    This is called by Meta to verify your webhook URL
    """
    # Get query parameters
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.info(f"Webhook verification request received")
    logger.info(f"Mode: {mode}, Token matches: {token == VERIFY_TOKEN}")
    
    # Check if mode and token are valid
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ Webhook verified successfully!")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logger.warning("❌ Webhook verification failed!")
        return PlainTextResponse(content="Forbidden", status_code=403)


@app.post("/webhook")
async def receive_message(request: Request):
    """
    Main webhook endpoint that receives messages from WhatsApp
    """
    try:
        # Get the request body
        body = await request.json()
        logger.info(f"📥 Received webhook: {body}")
        
        # Check if this is a WhatsApp message
        if body.get("object"):
            # Extract message details
            if (body.get("entry") and 
                body["entry"][0].get("changes") and 
                body["entry"][0]["changes"][0].get("value") and 
                body["entry"][0]["changes"][0]["value"].get("messages")):
                
                # Get the message
                message = body["entry"][0]["changes"][0]["value"]["messages"][0]
                from_number = message.get("from")  # User's phone number
                message_body = message.get("text", {}).get("body", "")
                
                logger.info(f"📨 Message from {from_number}: {message_body}")
                
                # Get AI response
                ai_response = await get_ai_response(message_body)
                
                # Send response back to WhatsApp
                await send_whatsapp_message(from_number, ai_response)
                
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


async def get_ai_response(user_message: str) -> str:
    """
    Get AI response from Hugging Face API
    """
    try:
        logger.info(f"🤖 Getting AI response for: {user_message}")
        
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": user_message,
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        # Handle model loading
        if response.status_code == 503:
            logger.warning("⏳ Model is loading...")
            return "The AI is waking up! Please try again in 20 seconds. 😴"
        
        response.raise_for_status()
        result = response.json()
        
        # Extract the response text
        if isinstance(result, list) and len(result) > 0:
            if "generated_text" in result[0]:
                ai_text = result[0]["generated_text"]
                logger.info(f"✅ AI response: {ai_text}")
                return ai_text
        elif isinstance(result, dict) and "generated_text" in result:
            ai_text = result["generated_text"]
            logger.info(f"✅ AI response: {ai_text}")
            return ai_text
        
        # Fallback response
        logger.warning("⚠️ Unexpected response format from Hugging Face")
        return "I heard you! Let me think about that... 🤔"
        
    except requests.exceptions.Timeout:
        logger.error("⏱️ Request to Hugging Face timed out")
        return "Sorry, I'm thinking too hard! Can you try again?"
    except Exception as e:
        logger.error(f"❌ Error getting AI response: {str(e)}")
        return "Sorry, I had trouble understanding. Can you try again? 🤔"


async def send_whatsapp_message(to: str, message: str):
    """
    Send message back to WhatsApp user
    """
    try:
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "text": {"body": message}
        }
        
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        logger.info(f"✅ Message sent to {to}")
        
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting WhatsApp Bot Server...")
    logger.info("📝 Make sure to update your webhook URL in Meta dashboard!")
    uvicorn.run(app, host="0.0.0.0", port=8000)