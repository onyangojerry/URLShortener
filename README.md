
### **README.md**

```md
# 🔗 URL Shortener API

A **high-performance URL shortener** built with **FastAPI**, **PostgreSQL**, and **Redis**. This API allows users to shorten long URLs and retrieve the original URLs using a generated short code.

---

## 🚀 Features

✅ **Shorten long URLs**  
✅ **Retrieve original URLs from short codes**  
✅ **Caching with Redis for faster lookups**  
✅ **PostgreSQL for persistent storage**  
✅ **FastAPI for a lightweight, high-performance backend**

---

## 🛠️ Installation & Setup

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/url-shortener.git
cd url-shortener
```

### **2. Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**
Create a `.env` file in the project root with the following:
```env
DB_NAME=urlshortener
DB_USER=shortener_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
REDIS_HOST=localhost
REDIS_PORT=6379
APP_HOST=0.0.0.0
APP_PORT=8000
```

### **5. Set Up the Database**
Ensure **PostgreSQL** is running and create the database:
```sql
CREATE DATABASE urlshortener;
CREATE USER shortener_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE urlshortener TO shortener_user;
```
Run the database schema:
```bash
psql -U shortener_user -d urlshortener -f database.sql
```

### **6. Start Redis**
```bash
redis-server
```

### **7. Run the FastAPI Server**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📌 API Endpoints

### **1️⃣ Shorten a URL**
- **Endpoint:** `POST /shorten`
- **Request Body (JSON):**
  ```json
  {
    "long_url": "https://example.com"
  }
  ```
- **Response (JSON):**
  ```json
  {
    "short_url": "http://localhost:8000/abc123"
  }
  ```

### **2️⃣ Retrieve Original URL**
- **Endpoint:** `GET /{short_code}`
- **Example Request:**
  ```bash
  curl -X 'GET' 'http://localhost:8000/abc123'
  ```
- **Response (JSON):**
  ```json
  {
    "long_url": "https://example.com"
  }
  ```

---

## 📊 Future Enhancements
🔹 **Custom short URLs** (allow users to define their own short codes)  
🔹 **Analytics tracking** (track the number of visits per short URL)  
🔹 **Expiration dates** (optional expiration for shortened URLs)  
🔹 **User authentication** (allow registered users to manage their links)  
🔹 **Deploy on cloud** (AWS, GCP, or Heroku)  

---

## 🛠️ Tech Stack
- **Backend:** FastAPI 🚀
- **Database:** PostgreSQL 🐘
- **Cache:** Redis 🔥
- **ORM:** psycopg2
- **Hosting:** Localhost (for now)

---

## 🤝 Contributing
Contributions are welcome!  
- Fork the repo  
- Create a feature branch  
- Submit a PR  

---

## 📜 License
This project is licensed under the **MIT License**.

---

🚀 **Happy Coding!**  
📩 **Have a feature request? Open an issue!**
```

---

### **📌 Next Steps**
- **Push to GitHub**
  ```bash
  git init
  git add .
  git commit -m "Initial commit: URL Shortener API"
  git branch -M main
  git remote add origin https://github.com/your-username/url-shortener.git
  git push -u origin main
  ```

Once you've pushed it to GitHub, let me know if you need help setting up **GitHub Actions for automated testing** or **deployment to the cloud!** 🚀🔥
