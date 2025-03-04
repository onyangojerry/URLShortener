import os
import time
import random
import string
from datetime import datetime, timedelta

import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

# FastAPI app
app = FastAPI()

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "db")  # Docker service name
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "urlshortener")
DB_USER = os.getenv("DB_USER", "shortener_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Redis Cache
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# PostgreSQL Connection with Retry Mechanism
MAX_RETRIES = 10
RETRY_DELAY = 5  # 5 seconds

db_conn = None
for attempt in range(MAX_RETRIES):
    try:
        db_conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,  
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        db_cursor = db_conn.cursor()
        print("✅ Successfully connected to PostgreSQL!")
        break
    except psycopg2.OperationalError as e:
        print(f"🚨 Database connection failed (Attempt {attempt + 1}/{MAX_RETRIES}): {e}")
        time.sleep(RETRY_DELAY)
else:
    print("❌ Could not connect to PostgreSQL after multiple attempts. Exiting...")
    exit(1)

# Ensure the `urls` table exists
def create_table():
    """Ensures the URLs table exists before the app starts."""
    db_cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            short_code VARCHAR(10) UNIQUE NOT NULL,
            long_url TEXT NOT NULL,
            expiry_date TIMESTAMP NOT NULL,
            click_count INTEGER DEFAULT 0
        );
    """)
    db_conn.commit()
    print("✅ Database table 'urls' ensured to exist.")

create_table()

# Base62 Encoding Characters
BASE62_ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length=6):
    """Generates a random short URL identifier using Base62."""
    return ''.join(random.choices(BASE62_ALPHABET, k=length))

class URLRequest(BaseModel):
    long_url: HttpUrl
    days_valid: int = 30  # Default expiration: 30 days

@app.post("/shorten")
def shorten_url(request: URLRequest):
    """Shortens a given URL with an optional expiration period."""
    long_url_str = str(request.long_url)
    short_code = generate_short_code()
    expiry_date = datetime.now() + timedelta(days=request.days_valid)

    print(f"🔗 Creating short URL for: {long_url_str}")

    # Check if URL already exists
    db_cursor.execute("SELECT short_code FROM urls WHERE long_url = %s", (long_url_str,))
    existing_url = db_cursor.fetchone()

    if existing_url:
        print(f"✅ Found existing short URL: {existing_url['short_code']}")
        return {"short_url": f"http://localhost:8000/{existing_url['short_code']}"}

    # Insert into database
    db_cursor.execute(
        "INSERT INTO urls (short_code, long_url, expiry_date, click_count) VALUES (%s, %s, %s, 0) RETURNING short_code",
        (short_code, long_url_str, expiry_date)
    )
    db_conn.commit()

    # Store in Redis cache
    redis_client.set(short_code, long_url_str, ex=request.days_valid * 86400)  # Cache with expiry

    print(f"✅ Short URL created: {short_code} -> {long_url_str}")

    return {"short_url": f"http://localhost:8000/{short_code}", "expires_at": expiry_date}

@app.get("/{short_code}")
def redirect_url(short_code: str):
    """Redirects a short URL to the original long URL, checking expiration."""
    print(f"🔍 Checking short code: {short_code}")
    long_url = redis_client.get(short_code)

    if not long_url:
        print(f"🔍 Not found in Redis, checking database for: {short_code}")
        db_cursor.execute("SELECT long_url, expiry_date, click_count FROM urls WHERE short_code = %s", (short_code,))
        result = db_cursor.fetchone()

        if not result:
            print(f"❌ Short URL not found: {short_code}")
            raise HTTPException(status_code=404, detail="Short URL not found")

        long_url = result['long_url']
        expiry_date = result['expiry_date']
        click_count = result['click_count']

        if expiry_date and expiry_date < datetime.now():
            print(f"⏰ Short URL expired: {short_code}")
            raise HTTPException(status_code=410, detail="Short URL has expired")

        # Update click count
        new_click_count = click_count + 1
        db_cursor.execute("UPDATE urls SET click_count = %s WHERE short_code = %s", (new_click_count, short_code))
        db_conn.commit()

        # Cache URL in Redis
        redis_client.set(short_code, long_url)

    else:
        db_cursor.execute("SELECT click_count FROM urls WHERE short_code = %s", (short_code,))
        result = db_cursor.fetchone()
        new_click_count = result['click_count'] + 1 if result else 1

        # Update click count in database
        db_cursor.execute("UPDATE urls SET click_count = %s WHERE short_code = %s", (new_click_count, short_code))
        db_conn.commit()

    print(f"✅ Redirecting to {long_url}")
    return {"long_url": long_url, "click_count": new_click_count}

@app.get("/stats/{short_code}")
def get_url_stats(short_code: str):
    """Fetches statistics for a short URL."""
    print(f"📊 Fetching stats for: {short_code}")
    db_cursor.execute("SELECT long_url, click_count, expiry_date FROM urls WHERE short_code = %s", (short_code,))
    result = db_cursor.fetchone()

    if not result:
        print(f"❌ No stats found for: {short_code}")
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {
        "long_url": result['long_url'],
        "click_count": result['click_count'],
        "expires_at": result['expiry_date']
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
