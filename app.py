from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# From Meta Developer Dashboard
WHATSAPP_TOKEN = "PASTE_YOUR_META_TEMP_ACCESS_TOKEN_HERE"
PHONE_NUMBER_ID = "PASTE_YOUR_PHONE_NUMBER_ID_HERE"
VERIFY_TOKEN = "my_super_secret_password" # You set this yourself, remember it for Step 5

# From Hugging Face
HF_TOKEN = "PASTE_YOUR_HUGGING_FACE_TOKEN_HERE"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

# --- HELPER FUNCTIONS ---
def query_huggingface(payload):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()

def send_whatsapp_message(to_number, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, headers=headers, json=data)
    return response

# --- ROUTES ---

# 1. Verification Route (Meta calls this to ensure you own the server)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Forbidden', 403
    return 'Bad Request', 400

# 2. Message Handler (Meta sends messages here)
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.json
    
    # Check if it's a valid message (not a status update)
    if 'object' in data and 'entry' in data:
        for entry in data['entry']:
            for change in entry['changes']:
                if 'messages' in change['value']:
                    # Extract message details
                    msg_body = change['value']['messages'][0]
                    from_number = msg_body['from']
                    msg_text = msg_body['text']['body']
                    
                    print(f"Received: {msg_text} from {from_number}")

                    # 1. Ask Hugging Face
                    # We format input slightly to make the bot act like a chat assistant
                    prompt = f"[INST] {msg_text} [/INST]"
                    ai_response = query_huggingface({"inputs": prompt})
                    
                    # Hugging Face returns a list, we need the generated text
                    try:
                        reply_text = ai_response[0]['generated_text']
                        # Clean up the response (remove the prompt echo)
                        if "[/INST]" in reply_text:
                            reply_text = reply_text.split("[/INST]")[1].strip()
                    except:
                        reply_text = "Sorry, I'm loading... try again in a second."

                    # 2. Send reply to WhatsApp
                    send_whatsapp_message(from_number, reply_text)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)