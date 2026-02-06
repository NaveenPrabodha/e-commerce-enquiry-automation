from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Print configuration on startup (for debugging)
logger.info("=" * 60)
logger.info("🤖 WhatsApp Bot Configuration")
logger.info("=" * 60)
logger.info(f"VERIFY_TOKEN set: {'✅' if VERIFY_TOKEN else '❌'}")
logger.info(f"VERIFY_TOKEN value: {VERIFY_TOKEN}")
logger.info(f"WHATSAPP_TOKEN set: {'✅' if WHATSAPP_TOKEN else '❌'}")
logger.info(f"WHATSAPP_PHONE_ID set: {'✅' if WHATSAPP_PHONE_ID else '❌'}")
logger.info(f"HUGGINGFACE_API_KEY set: {'✅' if HUGGINGFACE_API_KEY else '❌'}")
logger.info("=" * 60)

# Hugging Face API endpoint
# Using a more reliable model
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# WhatsApp API endpoint
WHATSAPP_API_URL = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_ID}/messages"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "Bot is running!", 
        "message": "WhatsApp AI Bot is active",
        "verify_token_configured": bool(VERIFY_TOKEN)
    }


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
    
    logger.info("=" * 60)
    logger.info("📞 WEBHOOK VERIFICATION REQUEST RECEIVED")
    logger.info("=" * 60)
    logger.info(f"Mode received: '{mode}'")
    logger.info(f"Token received: '{token}'")
    logger.info(f"Challenge received: '{challenge}'")
    logger.info(f"Expected token: '{VERIFY_TOKEN}'")
    logger.info(f"Tokens match: {token == VERIFY_TOKEN}")
    logger.info("=" * 60)
    
    # Check if mode and token are valid
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("✅ ✅ ✅ WEBHOOK VERIFIED SUCCESSFULLY! ✅ ✅ ✅")
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        logger.error("❌ ❌ ❌ WEBHOOK VERIFICATION FAILED! ❌ ❌ ❌")
        if mode != "subscribe":
            logger.error(f"Wrong mode: expected 'subscribe', got '{mode}'")
        if token != VERIFY_TOKEN:
            logger.error(f"Wrong token: expected '{VERIFY_TOKEN}', got '{token}'")
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
            "parameters": {
                "max_length": 100,
                "temperature": 0.7
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=30)
        
        # # Handle model loading
        # if response.status_code == 503:
        #     logger.warning("⏳ Model is loading...")
        #     return "The AI is waking up! Please try again in 20 seconds. 😴"
        
        # # Handle model errors
        # if response.status_code == 410:
        #     logger.error("❌ Model no longer available")
        #     return "Sorry, I'm having technical difficulties. The AI model is unavailable. 🔧"
        
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"Raw API response: {result}")
        
        # Extract the response text - DialoGPT format
        if isinstance(result, list) and len(result) > 0:
            if "generated_text" in result[0]:
                ai_text = result[0]["generated_text"]
                # Clean up the response (remove the input prompt if it's included)
                if user_message in ai_text:
                    ai_text = ai_text.replace(user_message, "").strip()
                logger.info(f"✅ AI response: {ai_text}")
                return ai_text if ai_text else "Hello! How can I help you today? 😊"
        elif isinstance(result, dict) and "generated_text" in result:
            ai_text = result["generated_text"]
            if user_message in ai_text:
                ai_text = ai_text.replace(user_message, "").strip()
            logger.info(f"✅ AI response: {ai_text}")
            return ai_text if ai_text else "Hello! How can I help you today? 😊"
        
        # Fallback response
        logger.warning("⚠️ Unexpected response format from Hugging Face")
        return "Hello! I'm here to help. How can I assist you? 😊"
        
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
        
        # Add timeout to prevent hanging
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f"✅ Message sent to {to}")
        
    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout sending message to {to}")
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting WhatsApp Bot Server...")
    logger.info("📝 Make sure to update your webhook URL in Meta dashboard!")
    logger.info("🔗 Your webhook endpoint will be: https://YOUR_NGROK_URL/webhook")
    uvicorn.run(app, host="0.0.0.0", port=8000)