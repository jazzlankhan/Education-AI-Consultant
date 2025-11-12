# Education Consultant AI Bot

## Setup

1. `cp .env.example .env`
2. Replace placeholders in `.env`
3. `pip install -r requirements.txt`
4. Start PostgreSQL:  
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=pass -e POSTGRES_USER=user -e POSTGRES_DB=leadbot postgres