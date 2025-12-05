import os
import re
import json
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_blockchain_info(chain_name: str) -> dict:
    """
    Get basic information about a specific blockchain network.
    
    Args:
        chain_name: The name of the blockchain (e.g., 'ethereum', 'bitcoin', 'solana', 'polygon')
    
    Returns:
        A dictionary containing blockchain information
    """
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
            "description": "The first and most well-known cryptocurrency, designed as a peer-to-peer electronic cash system."
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
            "description": "A high-performance blockchain supporting fast transactions and low fees."
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
            "description": "An Ethereum Layer 2 scaling solution for faster and cheaper transactions."
        },
        "binance": {
            "name": "BNB Chain (Binance Smart Chain)",
            "symbol": "BNB",
            "consensus": "Proof of Staked Authority (PoSA)",
            "avg_block_time": "~3 seconds",
            "smart_contracts": True,
            "launched": "2020",
            "founder": "Changpeng Zhao (CZ)",
            "website": "https://www.bnbchain.org",
            "description": "A blockchain focusing on fast and low-cost transactions, EVM compatible."
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
            "description": "A highly scalable blockchain platform for decentralized applications."
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
            "description": "A research-driven blockchain platform focused on security and sustainability."
        }
    }
    
    chain_key = chain_name.lower().strip()
    
    if chain_key in blockchain_data:
        return {"status": "success", "data": blockchain_data[chain_key]}
    else:
        available_chains = list(blockchain_data.keys())
        return {
            "status": "not_found",
            "message": f"Blockchain '{chain_name}' not found in database.",
            "available_chains": available_chains
        }


def validate_wallet_address(address: str, chain: str = "ethereum") -> dict:
    """
    Validate a wallet address format for a given blockchain.
    
    Args:
        address: The wallet address to validate
        chain: The blockchain network (default: 'ethereum')
    
    Returns:
        A dictionary with validation results
    """
    validations = {
        "ethereum": {
            "pattern": r"^0x[a-fA-F0-9]{40}$",
            "description": "Ethereum addresses start with '0x' followed by 40 hexadecimal characters"
        },
        "bitcoin": {
            "pattern": r"^(1|3|bc1)[a-zA-HJ-NP-Z0-9]{25,62}$",
            "description": "Bitcoin addresses start with '1', '3', or 'bc1'"
        },
        "solana": {
            "pattern": r"^[1-9A-HJ-NP-Za-km-z]{32,44}$",
            "description": "Solana addresses are base58 encoded, typically 32-44 characters"
        }
    }
    
    chain_lower = chain.lower()
    
    if chain_lower not in validations:
        return {
            "status": "error",
            "message": f"Validation not supported for chain: {chain}",
            "supported_chains": list(validations.keys())
        }
    
    pattern = validations[chain_lower]["pattern"]
    is_valid = bool(re.match(pattern, address))
    
    return {
        "status": "success",
        "address": address,
        "chain": chain,
        "is_valid": is_valid,
        "format_description": validations[chain_lower]["description"],
        "message": "Address format is valid!" if is_valid else "Invalid address format."
    }


def explain_gas_fees(chain: str = "ethereum") -> dict:
    """
    Explain how gas fees work on a specific blockchain.
    
    Args:
        chain: The blockchain network to explain gas fees for
    
    Returns:
        A dictionary with gas fee explanation
    """
    gas_info = {
        "ethereum": {
            "fee_name": "Gas",
            "unit": "Gwei (1 Gwei = 0.000000001 ETH)",
            "components": ["Base Fee", "Priority Fee (Tip)"],
            "explanation": """
Ethereum gas fees consist of:
1. **Base Fee**: Automatically determined by network demand. This is burned (destroyed).
2. **Priority Fee (Tip)**: Optional fee to incentivize validators to include your transaction faster.

**Formula**: Total Fee = Gas Units × (Base Fee + Priority Fee)

**Tips to save on gas**:
- Transact during low-activity periods (weekends, late nights)
- Use Layer 2 solutions like Polygon, Arbitrum, or Optimism
- Set a max fee limit to avoid overpaying
            """,
            "typical_costs": {
                "simple_transfer": "21,000 gas units",
                "token_transfer": "~65,000 gas units",
                "uniswap_swap": "~150,000 gas units",
                "nft_mint": "~100,000-200,000 gas units"
            }
        },
        "solana": {
            "fee_name": "Transaction Fee",
            "unit": "Lamports (1 SOL = 1,000,000,000 Lamports)",
            "components": ["Base Fee", "Priority Fee"],
            "explanation": """
Solana has extremely low transaction fees:
1. **Base Fee**: Fixed at 5,000 lamports (0.000005 SOL) per signature
2. **Priority Fee**: Optional additional fee for faster processing

Solana's fees are among the lowest in the industry, typically costing a fraction of a cent.
            """,
            "typical_costs": {
                "simple_transfer": "~0.000005 SOL",
                "token_transfer": "~0.00001 SOL",
                "nft_mint": "~0.01-0.02 SOL"
            }
        },
        "polygon": {
            "fee_name": "Gas (MATIC)",
            "unit": "Gwei (paid in MATIC)",
            "components": ["Base Fee", "Priority Fee"],
            "explanation": """
Polygon uses a similar gas model to Ethereum but with much lower costs:
- Uses MATIC token for gas payments
- Significantly cheaper than Ethereum mainnet
- Fast transaction finality (~2 seconds)

Typical transaction costs are pennies compared to Ethereum's dollars.
            """,
            "typical_costs": {
                "simple_transfer": "~$0.001-0.01",
                "token_transfer": "~$0.01-0.05",
                "swap": "~$0.05-0.20"
            }
        }
    }
    
    chain_lower = chain.lower()
    
    if chain_lower in gas_info:
        return {"status": "success", "chain": chain, "gas_info": gas_info[chain_lower]}
    else:
        return {
            "status": "not_found",
            "message": f"Gas fee information not available for {chain}",
            "available_chains": list(gas_info.keys())
        }


def get_smart_contract_template(contract_type: str) -> dict:
    """
    Get a basic smart contract template for common use cases.
    
    Args:
        contract_type: The type of contract ('erc20', 'erc721', 'simple_storage')
    
    Returns:
        A dictionary with the contract template and explanation
    """
    templates = {
        "erc20": {
            "name": "ERC-20 Token",
            "description": "Standard fungible token contract",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, Ownable {
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply
    ) ERC20(name, symbol) Ownable(msg.sender) {
        _mint(msg.sender, initialSupply * 10 ** decimals());
    }

    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}''',
            "explanation": "This creates a basic ERC-20 token with minting capability. Uses OpenZeppelin for security."
        },
        "erc721": {
            "name": "ERC-721 NFT",
            "description": "Standard non-fungible token (NFT) contract",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    function safeMint(address to, string memory uri) public onlyOwner {
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}''',
            "explanation": "A basic NFT contract with metadata URI storage. Each token is unique and can have its own metadata."
        },
        "simple_storage": {
            "name": "Simple Storage",
            "description": "A basic contract for learning Solidity",
            "code": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SimpleStorage {
    uint256 private storedValue;
    
    event ValueChanged(uint256 newValue, address changedBy);

    function set(uint256 value) public {
        storedValue = value;
        emit ValueChanged(value, msg.sender);
    }

    function get() public view returns (uint256) {
        return storedValue;
    }
}''',
            "explanation": "A beginner-friendly contract that stores a single number. Great for learning Solidity basics."
        }
    }
    
    contract_key = contract_type.lower().strip()
    
    if contract_key in templates:
        return {"status": "success", "template": templates[contract_key]}
    else:
        return {
            "status": "not_found",
            "message": f"Template '{contract_type}' not found.",
            "available_templates": list(templates.keys())
        }


def convert_crypto_units(amount: float, from_unit: str, to_unit: str) -> dict:
    """
    Convert between different cryptocurrency unit denominations.
    
    Args:
        amount: The amount to convert
        from_unit: The source unit (e.g., 'eth', 'gwei', 'wei', 'btc', 'satoshi')
        to_unit: The target unit
    
    Returns:
        A dictionary with the conversion result
    """
    # Conversion factors (to base unit)
    conversions = {
        # Ethereum units (to Wei)
        "wei": 1,
        "gwei": 1e9,
        "eth": 1e18,
        "ether": 1e18,
        # Bitcoin units (to Satoshi)
        "satoshi": 1,
        "sat": 1,
        "btc": 1e8,
        "bitcoin": 1e8,
        # Solana units (to Lamports)
        "lamport": 1,
        "lamports": 1,
        "sol": 1e9,
        "solana": 1e9,
    }
    
    eth_units = ["wei", "gwei", "eth", "ether"]
    btc_units = ["satoshi", "sat", "btc", "bitcoin"]
    sol_units = ["lamport", "lamports", "sol", "solana"]
    
    from_lower = from_unit.lower()
    to_lower = to_unit.lower()
    
    if from_lower not in conversions or to_lower not in conversions:
        return {
            "status": "error",
            "message": "Invalid unit specified",
            "available_units": list(conversions.keys())
        }
    
    # Check if units are from the same blockchain
    def get_chain(unit):
        if unit in eth_units:
            return "ethereum"
        elif unit in btc_units:
            return "bitcoin"
        elif unit in sol_units:
            return "solana"
        return None
    
    from_chain = get_chain(from_lower)
    to_chain = get_chain(to_lower)
    
    if from_chain != to_chain:
        return {
            "status": "error",
            "message": f"Cannot convert between different blockchains ({from_chain} to {to_chain})"
        }
    
    # Convert
    base_amount = amount * conversions[from_lower]
    result = base_amount / conversions[to_lower]
    
    return {
        "status": "success",
        "input": {"amount": amount, "unit": from_unit},
        "output": {"amount": result, "unit": to_unit},
        "blockchain": from_chain
    }


# Create the blockchain assistant agent
root_agent = Agent(
    model='gemini-2.0-flash',
    name='blockchain_assistant',
    description="A helpful blockchain and cryptocurrency assistant that provides information about various blockchain networks, validates wallet addresses, explains concepts, and helps with smart contract development.",
    instruction="""You are BlockchainBuddy, an expert blockchain and cryptocurrency assistant. You help users with:

1. **Blockchain Information**: Explain different blockchain networks, their features, consensus mechanisms, and use cases.

2. **Wallet Address Validation**: Verify if wallet addresses are in the correct format for different chains.

3. **Gas Fee Explanations**: Help users understand gas fees, how they work, and tips to save on transaction costs.

4. **Smart Contract Development**: Provide templates and guidance for creating smart contracts (ERC-20, ERC-721, etc.).

5. **Unit Conversions**: Convert between crypto units (ETH/Gwei/Wei, BTC/Satoshi, SOL/Lamports).

6. **General Crypto Knowledge**: Answer questions about DeFi, NFTs, DAOs, Layer 2 solutions, and more.

**Guidelines**:
- Always be accurate and up-to-date with blockchain information
- Warn users about security best practices (never share private keys, verify contracts, etc.)
- Use the available tools to provide concrete data when possible
- Explain complex concepts in simple terms
- If you're unsure about something, say so rather than guessing

**Available Tools**:
- `get_blockchain_info`: Get details about specific blockchains
- `validate_wallet_address`: Check if a wallet address format is valid
- `explain_gas_fees`: Explain gas/transaction fees for different chains
- `get_smart_contract_template`: Get starter templates for smart contracts
- `convert_crypto_units`: Convert between crypto unit denominations
""",
    tools=[
        get_blockchain_info,
        validate_wallet_address,
        explain_gas_fees,
        get_smart_contract_template,
        convert_crypto_units,
    ],
)