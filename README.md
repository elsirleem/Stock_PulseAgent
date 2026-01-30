# 📈 StockPulse WhatsApp Agent

A personal AI financial agent that allows users to track their stock portfolios and watchlists via WhatsApp. Built with Python, FastAPI, and LangGraph.

## ✨ Features

- **Natural Language Queries**: Ask about stock prices, portfolio performance, and market trends
- **Portfolio Management**: Add, remove, and track your stock holdings
- **Watchlist**: Monitor stocks you're interested in
- **Daily Updates**: Receive automated morning portfolio summaries
- **Conversation Memory**: The agent remembers your previous interactions

## 🛠️ Tech Stack

| Layer | Technology | Role |
|-------|------------|------|
| Language | Python 3.11+ | Core programming language |
| Framework | FastAPI | Webhook handling and API management |
| Orchestration | LangGraph | Stateful agent logic, memory, and tool use |
| Communication | Twilio WhatsApp API | Messaging interface |
| Data Provider | yfinance | Real-time and historical stock data |
| Database | SQLite | Local storage for portfolios and watchlists |
| Memory | LangGraph SqliteSaver | Conversation state persistence |
| Automation | APScheduler | Daily morning updates |

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Twilio account with WhatsApp Sandbox
- OpenAI API key
- ngrok (for local development)

### Installation

1. **Clone the repository**
   ```bash
   cd Stock_PulseAgent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Expose with ngrok** (for Twilio webhook)
   ```bash
   ngrok http 8000
   ```

7. **Configure Twilio Webhook**
   - Go to Twilio Console > Messaging > Settings > WhatsApp Sandbox Settings
   - Set the webhook URL to: `https://your-ngrok-url.ngrok.io/whatsapp`

## 📱 Usage Examples

### Stock Prices
- "What is the price of Tesla?"
- "How is AAPL doing today?"
- "Get me the price of MSFT, GOOGL, and AMZN"

### Portfolio Management
- "I bought 5 shares of AAPL at $175"
- "Add 10 shares of NVDA at $450 to my portfolio"
- "Remove MSFT from my portfolio"
- "Show my portfolio"
- "How is my portfolio doing?"

### Watchlist
- "Add TSLA to my watchlist"
- "Watch NVDA for me"
- "Remove AAPL from my watchlist"
- "Show my watchlist"

### Portfolio Analysis
- "What's my total portfolio value?"
- "How much have I gained or lost?"
- "Give me a portfolio summary"

## 📁 Project Structure

```
Stock_PulseAgent/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI routes & WhatsApp webhook
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── state.py           # LangGraph state definition
│   │   └── graph.py           # LangGraph agent implementation
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py          # SQLite models
│   │   └── connection.py      # Database connection
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── stock_tools.py     # yfinance tools
│   │   └── portfolio_tools.py # Portfolio management tools
│   └── scheduler/
│       ├── __init__.py
│       └── daily_updates.py   # APScheduler for daily updates
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | Required |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | Required |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp number | `whatsapp:+14155238886` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DAILY_UPDATE_HOUR` | Hour for daily updates (24h) | `8` |
| `DAILY_UPDATE_MINUTE` | Minute for daily updates | `30` |

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| POST | `/whatsapp` | Twilio WhatsApp webhook |
| GET | `/whatsapp` | Webhook verification |

## 📊 Daily Updates

The agent sends automated portfolio summaries every day at the configured time (default: 8:30 AM). Updates include:

- Summary of all held stocks
- Current price vs. purchase price
- Daily and total percentage changes
- Total portfolio value
- Watchlist with current prices

## 🔒 Security Notes

- Never commit your `.env` file
- Use environment variables for all sensitive data
- Consider using Twilio request validation in production
- Implement rate limiting for production deployments

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues, please open a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
