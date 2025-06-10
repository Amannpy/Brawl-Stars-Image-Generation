# Brawl Stars AI Image Generator

An AI-powered image generation platform that creates Brawl Stars themed artwork using natural language prompts enhanced with game-specific knowledge.

## Features

- AI Image Generation with Brawl Stars context
- Knowledge-Enhanced Prompts
- Character Database
- Theme Templates
- Community Gallery
- Prompt Suggestions

## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- Celery
- OpenAI API / Stability AI
- Transformers/Sentence-Transformers
- BeautifulSoup4/Scrapy

## Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- OpenAI API Key
- Stability AI API Key

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/brawl-stars-ai-generator.git
cd brawl-stars-ai-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/development.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=brawl_stars_ai
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key
STABILITY_API_KEY=your_stability_key
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Project Structure

```
brawl-stars-ai-generator/
├── app/                    # Application code
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── tests/                 # Test files
├── alembic/               # Database migrations
└── requirements/          # Python dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 