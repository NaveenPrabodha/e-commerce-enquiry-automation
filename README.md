# 📦 Real-Time Internal Order Alerts (WhatsApp)

A backend system that sends **instant WhatsApp notifications to business owners/admins** whenever a new order is placed on an e-commerce website.

This project focuses on **operational efficiency**, ensuring admins never miss an order due to delayed emails or dashboard checks.

---

## 🚀 Features

- ✅ Real-time WhatsApp alerts for new orders  
- ✅ Admin-only notifications (not customer-facing)  
- ✅ Secure webhook-based architecture  
- ✅ Cloud-native & scalable (Google Cloud Run)  
- ✅ Minimal operational cost  
- ✅ No impact on website performance  

---

## 🧠 How It Works

1. A customer places an order on the website  
2. The website triggers a **webhook** with order details  
3. A **FastAPI backend** processes and formats the data  
4. A structured WhatsApp message is sent to the admin via **WhatsApp Cloud API**

---

## 📲 Sample WhatsApp Alert

📦 New Order Received!
Order ID: #1245
Amount: LKR 15,000
Customer: Kamal Perera
Items: 2× Blue Shirt, 1× Chinos


---

## 🏗️ Tech Stack

- **Backend:** Python, FastAPI  
- **Messaging:** WhatsApp Cloud API (Meta)  
- **Deployment:** Google Cloud Run  
- **Integration:** Webhooks (E-commerce platform)

---

## 🔐 Architecture Highlights

- External processing (no website slowdown)
- Secure webhook validation
- Internal/admin-only messaging
- Designed for reliability and scalability

---

## 📋 Requirements

- Meta Business Manager account  
- WhatsApp Cloud API access  
- Admin phone number(s)  
- Google Cloud account  

---

## ⚙️ Environment Variables

Create a `.env` file:

`.env`

WHATSAPP_TOKEN=your_whatsapp_cloud_api_token
PHONE_NUMBER_ID=your_phone_number_id
ADMIN_PHONE=admin_phone_number_with_country_code
VERIFY_TOKEN=your_webhook_verify_token

## ▶️ Run Locally

`bash`

pip install -r requirements.txt
uvicorn main:app --reload

## ☁️ Deployment (Google Cloud Run)

1. Build the Docker image  
2. Deploy the image to Google Cloud Run  
3. Configure required environment variables  
4. Set the webhook URL in your e-commerce platform  

---

## 🔮 Future Enhancements

- Multiple admin routing  
- Priority alerts for high-value orders  
- Order status notifications  
- Analytics dashboard  
- Multi-channel alerts (Slack, Email)  

---

## 📌 Use Cases

- E-commerce stores  
- Restaurants & delivery services  
- Dropshipping businesses  
- Small & medium online retailers  


