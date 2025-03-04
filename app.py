from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import random, string
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# FastAPI app
app = FastAPI()

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# PostgreSQL connection
db_conn = psycopg2.connect(
    dbname='urlshortener', user='shortener_user', password='password', host='localhost', cursor_factory=RealDictCursor
)
db_cursor = db_conn.cursor()

def generate_short_code(length=6):
    """Generates a random short URL identifier."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class URLRequest(BaseModel):
    long_url: HttpUrl

@app.post("/shorten")
def shorten_url(request: URLRequest):
    """Shortens a given URL."""
    short_code = generate_short_code()
    
    # Convert HttpUrl to string before storing in DB
    long_url_str = str(request.long_url)
    
    db_cursor.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (%s, %s) RETURNING short_code", 
        (short_code, long_url_str)
    )
    db_conn.commit()
    
    # Store in Redis cache
    redis_client.set(short_code, long_url_str)
    
    return {"short_url": f"http://localhost:8000/{short_code}"}

@app.get("/{short_code}")
def redirect_url(short_code: str):
    """Redirects a short URL to the original long URL."""
    long_url = redis_client.get(short_code)
    
    if not long_url:
        db_cursor.execute("SELECT long_url FROM urls WHERE short_code = %s", (short_code,))
        result = db_cursor.fetchone()
        
        if result:
            long_url = result['long_url']
            redis_client.set(short_code, long_url)  # Cache the result in Redis
        else:
            raise HTTPException(status_code=404, detail="Short URL not found")
    
    return {"long_url": long_url}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
