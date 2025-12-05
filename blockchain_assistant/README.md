# 🔗 BlockchainBuddy API

A powerful blockchain and cryptocurrency assistant API powered by Google Gemini.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/blockchain-buddy-api&env=GEMINI_API_KEY)

## 🚀 Deploy to Vercel (Recommended)

### Option 1: One-Click Deploy
1. Click the "Deploy with Vercel" button above
2. Connect your GitHub account
3. Add your `GEMINI_API_KEY` environment variable
4. Deploy!

### Option 2: CLI Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variable
vercel env add GEMINI_API_KEY
```

### Option 3: GitHub Integration
1. Push this repo to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Add environment variable: `GEMINI_API_KEY`
5. Deploy!

## 💻 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the API
python api.py
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Chat with Assistant (Main Endpoint)
```bash
POST /chat
Content-Type: application/json

{
    "message": "What is Ethereum?",
    "session_id": "optional-session-id"
}
```

### Health Check
```bash
GET /
GET /health
```

### Direct Tool Endpoints
```bash
# Get blockchain info
GET /tools/blockchain/ethereum

# Validate wallet address
GET /tools/validate-address?address=0x742d35Cc...&chain=ethereum

# Get gas fee info
GET /tools/gas-fees/ethereum

# Get smart contract template
GET /tools/contract-template/erc20

# Convert crypto units
GET /tools/convert?amount=1&from_unit=eth&to_unit=gwei
```

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ Yes |

Get your API key: [Google AI Studio](https://aistudio.google.com/apikey)

## 📦 Project Structure

```
blockchain-buddy-api/
├── app.py              # FastAPI application (Vercel entry point)
├── pyproject.toml      # Python project config
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment file
└── README.md           # This file
```

## 🔒 Security Notes

1. **API Key**: Never commit your `.env` file
2. **CORS**: Configure `allow_origins` in production
3. **Rate Limiting**: Consider adding rate limiting

## 📄 License

MIT License
