# Food Recommendation Bot

A Telegram bot powered by AI that helps users find optimal food choices based on their preferences and dietary restrictions.

## Overview

This project uses a serverless architecture on AWS to provide personalized food recommendations through a Telegram bot interface. The system integrates with Wolt's delivery platform to fetch restaurant and menu data, enriches it with AI-generated nutritional information, and allows users to search for food through natural language queries.

## Architecture

The system follows a serverless architecture on AWS:

- **Data Ingestion**: Fetches restaurant and menu data from Wolt API
- **Data Processing**: Enriches the data with OpenAI's vision and language models
- **Search**: Vector-based food search with OpenSearch
- **Recommendation**: AI consultant that matches user preferences with available food options
- **Interface**: Telegram bot for user interaction

## Tech Stack

### Backend
- Python 3.9
- AWS CDK for infrastructure as code
- AWS Lambda for serverless functions
- AWS Step Functions for workflow orchestration
- Amazon OpenSearch for vector search
- S3 for storing venue and user data
- API Gateway for REST API
- OpenAI API for content enrichment and recommendations
- Telegram Bot API for user interface

### Frontend (Planned)
- React 17 with TypeScript (configuration exists but implementation not started)
- Cloudscape Design components
- AWS CDK for infrastructure

## Project Structure

```
.
├── frontend/                 # React frontend scaffolding (not implemented)
│   ├── package.json          # Frontend dependencies
│   ├── tsconfig.json         # TypeScript configuration
│   └── cdk/                  # CDK code for frontend deployment
│
└── backend/                  # Python backend serverless application
    ├── app.py                # CDK application entry point
    ├── python/               # Backend code
    │   ├── python_stack.py   # Main stack definition
    │   ├── stacks/           # CDK stack modules
    │   └── lambdas/          # Lambda function code
    │       ├── dependency/   # Shared libraries
    │       │   ├── ai_client.py           # OpenAI API integration
    │       │   ├── consult_client.py      # Recommendation logic
    │       │   ├── search_client.py       # Vector search
    │       │   ├── storage_client.py      # S3 storage
    │       │   └── wolt_client.py         # Wolt API integration
    │       ├── ingestion/    # Data ingestion functions
    │       ├── search/       # Search functions
    │       └── telegram/     # Telegram bot functions
    └── tests/                # Test code
        ├── unit/             # Unit tests
        └── integ/            # Integration tests
```

## Features

- **AI-Powered Food Analysis**: Enriches food items with calorie count, nutritional information, and detailed descriptions using OpenAI
- **Personalized Recommendations**: Takes into account dietary preferences, previous orders, and budget
- **Conversational Interface**: Easy-to-use Telegram bot interface
- **Vector-Based Search**: Find food based on semantic similarity to natural language queries
- **Real-Time Data**: Integration with Wolt's delivery platform for up-to-date menu information

## Getting Started

### Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.9
- OpenAI API Key
- Telegram Bot Token

### Backend Setup

1. Clone the repository

```bash
git clone https://github.com/your-organization/food-recommendation-bot.git
cd food-recommendation-bot
```

2. Setup Python environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Deploy the backend infrastructure

```bash
cdk deploy --context OPENAI_API_KEY=your-openai-api-key --context TELEGRAM_TOKEN=your-telegram-token
```

## Deployment

The backend is deployed as a CDK stack:

```bash
cd backend
cdk deploy
```

## Usage

### Telegram Bot

Users can interact with the system via Telegram:

1. Search for the bot by its username
2. Start a conversation with the bot
3. Send food preferences or dietary restrictions
4. Get personalized recommendations with direct links to order

### Example Interactions

- "I want something healthy with chicken"
- "Looking for a vegetarian option under 20 GEL"
- "Recommend me a high protein meal"

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest
```

## How It Works

1. **Data Ingestion**: The system periodically fetches restaurant and menu data from Wolt's API.
2. **Enrichment**: AI models analyze each food item to extract nutritional information and create detailed descriptions.
3. **Vector Embedding**: Food descriptions are converted to vector embeddings for semantic search.
4. **User Interaction**: Users send natural language queries through Telegram.
5. **Recommendation**: The system matches user preferences against available options and provides personalized recommendations.

## Future Development

- Implement the planned React frontend for a web interface
- Add support for more delivery services
- Enhance recommendation algorithm with more personalization options
