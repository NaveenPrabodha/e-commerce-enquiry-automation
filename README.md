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

