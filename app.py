import os
import uuid
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Load environment variables
load_dotenv()

# ============== Agent Definition ==============
def get_blockchain_info(chain_name: str) -> dict:
    """Get basic information about a specific blockchain network."""
    blockchain_data = {
        "ethereum": {
            "name": "Ethereum",
            "symbol": "ETH",
            "consensus": "Proof of Stake (PoS)",
            "avg_block_time": "~12 seconds",
            "smart_contracts": True,
            "launched": "2015",
            "founder": "Vitalik Buterin",
            "website": "https://ethereum.org",
            "description": "A decentralized platform for building dApps and smart contracts."
        },
        "bitcoin": {
            "name": "Bitcoin",
            "symbol": "BTC",
            "consensus": "Proof of Work (PoW)",
            "avg_block_time": "~10 minutes",
            "smart_contracts": False,
            "launched": "2009",
            "founder": "Satoshi Nakamoto",
            "website": "https://bitcoin.org",
            "description": "The first and most well-known cryptocurrency."
        },
        "solana": {
            "name": "Solana",
            "symbol": "SOL",
            "consensus": "Proof of History (PoH) + Proof of Stake",
            "avg_block_time": "~400 milliseconds",
            "smart_contracts": True,
            "launched": "2020",
            "founder": "Anatoly Yakovenko",
            "website": "https://solana.com",
            "description": "A high-performance blockchain with fast transactions and low fees."
        },
        "polygon": {
            "name": "Polygon",
            "symbol": "MATIC",
            "consensus": "Proof of Stake (PoS)",
            "avg_block_time": "~2 seconds",
            "smart_contracts": True,
            "launched": "2017",
            "founder": "Jaynti Kanani, Sandeep Nailwal, Anurag Arjun",
            "website": "https://polygon.technology",
            "description": "An Ethereum Layer 2 scaling solution."
        },
        "avalanche": {
            "name": "Avalanche",
            "symbol": "AVAX",
            "consensus": "Avalanche Consensus (PoS variant)",
            "avg_block_time": "~2 seconds",
            "smart_contracts": True,
            "launched": "2020",
            "founder": "Emin Gün Sirer",
            "website": "https://www.avax.network",
            "description": "A highly scalable blockchain platform for dApps."
        },
        "cardano": {
            "name": "Cardano",
            "symbol": "ADA",
            "consensus": "Ouroboros Proof of Stake",
            "avg_block_time": "~20 seconds",
            "smart_contracts": True,
            "launched": "2017",
            "founder": "Charles Hoskinson",
            "website": "https://cardano.org",
            "description": "A research-driven blockchain focused on security."
        }
    }
    
    chain_key = chain_name.lower().strip()
    if chain_key in blockchain_data:
        return {"status": "success", "data": blockchain_data[chain_key]}
    return {
        "status": "not_found",
        "message": f"Blockchain '{chain_name}' not found.",
        "available_chains": list(blockchain_data.keys())
    }


def validate_wallet_address(address: str, chain: str = "ethereum") -> dict:
    """Validate a wallet address format for a given blockchain."""
    import re
    
    validations = {
        "ethereum": {
            "pattern": r"^0x[a-fA-F0-9]{40}$",
            "description": "Ethereum addresses start with '0x' followed by 40 hex characters"
        },
        "bitcoin": {
            "pattern": r"^(1|3|bc1)[a-zA-HJ-NP-Z0-9]{25,62}$",
            "description": "Bitcoin addresses start with '1', '3', or 'bc1'"
        },
        "solana": {
            "pattern": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
            "description": "Solana addresses are base58 encoded, 32-44 characters"
        }
    }
    
    chain_lower = chain.lower()
    if chain_lower not in validations:
        return {
            "status": "error",
            "message": f"Validation not supported for chain: {chain}",
            "supported_chains": list(validations.keys())
        }
    
    is_valid = bool(re.match(validations[chain_lower]["pattern"], address))
    return {
        "status": "success",
        "address": address,
        "chain": chain,
        "is_valid": is_valid,
        "format_description": validations[chain_lower]["description"],
        "message": "Address format is valid!" if is_valid else "Invalid address format."
    }


def explain_gas_fees(chain: str = "ethereum") -> dict:
    """Explain how gas fees work on a specific blockchain."""
    gas_info = {
        "ethereum": {
            "fee_name": "Gas",
            "unit": "Gwei (1 Gwei = 0.000000001 ETH)",
            "components": ["Base Fee", "Priority Fee (Tip)"],
            "explanation": "Ethereum gas fees consist of Base Fee (burned) and Priority Fee (tip to validators).",
            "typical_costs": {
                "simple_transfer": "21,000 gas units",
                "token_transfer": "~65,000 gas units",
                "swap": "~150,000 gas units"
            }
        },
        "solana": {
            "fee_name": "Transaction Fee",
            "unit": "Lamports (1 SOL = 1B Lamports)",
            "components": ["Base Fee", "Priority Fee"],
            "explanation": "Solana has extremely low fees, typically a fraction of a cent.",
            "typical_costs": {
                "simple_transfer": "~0.000005 SOL",
                "token_transfer": "~0.00001 SOL"
            }
        },
        "polygon": {
            "fee_name": "Gas (MATIC)",
            "unit": "Gwei (paid in MATIC)",
            "components": ["Base Fee", "Priority Fee"],
            "explanation": "Polygon uses a similar gas model to Ethereum but much cheaper.",
            "typical_costs": {
                "simple_transfer": "~$0.001-0.01",
                "swap": "~$0.05-0.20"
            }
        }
    }
    
    chain_lower = chain.lower()
    if chain_lower in gas_info:
        return {"status": "success", "chain": chain, "gas_info": gas_info[chain_lower]}
    return {
        "status": "not_found",
        "message": f"Gas info not available for {chain}",
        "available_chains": list(gas_info.keys())
    }


def get_smart_contract_template(contract_type: str) -> dict:
    """Get a basic smart contract template for common use cases."""
    templates = {
        "erc20": {
            "name": "ERC-20 Token",
            "description": "Standard fungible token contract",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor(string memory name, string memory symbol, uint256 initialSupply)
        ERC20(name, symbol) Ownable(msg.sender) {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}'''
        },
        "erc721": {
            "name": "ERC-721 NFT",
            "description": "Standard NFT contract",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    function safeMint(address to, string memory uri) public onlyOwner {
        uint256 tokenId = _tokenIdCounter++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage)
        returns (string memory) { return super.tokenURI(tokenId); }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage)
        returns (bool) { return super.supportsInterface(interfaceId); }
}'''
        },
        "simple_storage": {
            "name": "Simple Storage",
            "description": "Basic learning contract",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SimpleStorage {
    uint256 private storedValue;
    event ValueChanged(uint256 newValue, address changedBy);

    function set(uint256 value) public {
        storedValue = value;
        emit ValueChanged(value, msg.sender);
    }

    function get() public view returns (uint256) { return storedValue; }
}'''
        }
    }
    
    contract_key = contract_type.lower().strip()
    if contract_key in templates:
        return {"status": "success", "template": templates[contract_key]}
    return {
        "status": "not_found",
        "message": f"Template '{contract_type}' not found.",
        "available_templates": list(templates.keys())
    }


def convert_crypto_units(amount: float, from_unit: str, to_unit: str) -> dict:
    """Convert between different cryptocurrency unit denominations."""
    conversions = {
        "wei": 1, "gwei": 1e9, "eth": 1e18, "ether": 1e18,
        "satoshi": 1, "sat": 1, "btc": 1e8, "bitcoin": 1e8,
        "lamport": 1, "lamports": 1, "sol": 1e9, "solana": 1e9,
    }
    
    eth_units = ["wei", "gwei", "eth", "ether"]
    btc_units = ["satoshi", "sat", "btc", "bitcoin"]
    sol_units = ["lamport", "lamports", "sol", "solana"]
    
    from_lower, to_lower = from_unit.lower(), to_unit.lower()
    
    if from_lower not in conversions or to_lower not in conversions:
        return {"status": "error", "message": "Invalid unit", "available_units": list(conversions.keys())}
    
    def get_chain(unit):
        if unit in eth_units: return "ethereum"
        if unit in btc_units: return "bitcoin"
        if unit in sol_units: return "solana"
        return None
    
    from_chain, to_chain = get_chain(from_lower), get_chain(to_lower)
    if from_chain != to_chain:
        return {"status": "error", "message": f"Cannot convert between {from_chain} and {to_chain}"}
    
    result = (amount * conversions[from_lower]) / conversions[to_lower]
    return {
        "status": "success",
        "input": {"amount": amount, "unit": from_unit},
        "output": {"amount": result, "unit": to_unit},
        "blockchain": from_chain
    }


# Create the blockchain assistant agent
blockchain_agent = Agent(
    model='gemini-2.0-flash',
    name='blockchain_assistant',
    description="A blockchain and cryptocurrency assistant.",
    instruction="""You are BlockchainBuddy, an expert blockchain and cryptocurrency assistant. You help users with:

1. **Blockchain Information**: Explain different blockchain networks and their features.
2. **Wallet Address Validation**: Verify wallet address formats.
3. **Gas Fee Explanations**: Help users understand transaction fees.
4. **Smart Contract Development**: Provide templates and guidance.
5. **Unit Conversions**: Convert between crypto units.

Always be accurate, warn about security best practices, and explain concepts simply.
""",
    tools=[
        get_blockchain_info,
        validate_wallet_address,
        explain_gas_fees,
        get_smart_contract_template,
        convert_crypto_units,
    ],
)

# ============== Session & Runner Setup ==============
APP_NAME = "blockchain_assistant"
session_service = InMemorySessionService()

# Store active sessions
sessions: dict = {}


# ============== API Models ==============
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    agent_name: str
    timestamp: str


# ============== FastAPI App ==============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 BlockchainBuddy API is starting...")
    yield
    # Shutdown
    print("👋 BlockchainBuddy API is shutting down...")


app = FastAPI(
    title="BlockchainBuddy API",
    description="A powerful blockchain and cryptocurrency assistant API powered by Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="online",
        agent_name="BlockchainBuddy",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        agent_name="BlockchainBuddy",
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the blockchain assistant.
    
    - **message**: Your question or request
    - **session_id**: Optional session ID for conversation continuity
    """
    try:
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())
        user_id = f"user_{session_id[:8]}"
        
        # Try to get existing session, create if not exists
        try:
            session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
        except Exception:
            session = None
        
        if session is None:
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
        
        # Create runner
        runner = Runner(
            agent=blockchain_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        # Build message content
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=request.message)]
        )
        
        # Run agent and collect response
        response_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
        
        return ChatResponse(
            response=response_text or "I apologize, but I couldn't generate a response. Please try again.",
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session to clear conversation history."""
    return {"status": "deleted", "session_id": session_id}


# ============== Direct Tool Endpoints ==============
@app.get("/tools/blockchain/{chain_name}")
async def get_blockchain(chain_name: str):
    """Get information about a specific blockchain."""
    return get_blockchain_info(chain_name)


@app.get("/tools/validate-address")
async def validate_address(address: str, chain: str = "ethereum"):
    """Validate a wallet address format."""
    return validate_wallet_address(address, chain)


@app.get("/tools/gas-fees/{chain}")
async def get_gas_fees(chain: str):
    """Get gas fee information for a blockchain."""
    return explain_gas_fees(chain)


@app.get("/tools/contract-template/{contract_type}")
async def get_contract_template(contract_type: str):
    """Get a smart contract template."""
    return get_smart_contract_template(contract_type)


@app.get("/tools/convert")
async def convert_units(amount: float, from_unit: str, to_unit: str):
    """Convert between crypto units."""
    return convert_crypto_units(amount, from_unit, to_unit)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
