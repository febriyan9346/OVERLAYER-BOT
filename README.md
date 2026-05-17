# 🌐 OVERLAYER BOT

> Automated bot for interacting with the [Overlayer Testnet](https://testnet.overlayer.fi/early-user) — automates daily on-chain tasks including minting, staking, bridging, swapping, and cycling transactions on Ethereum Sepolia and Base Sepolia.

---

## 🔗 Important Links

| Resource | Link |
|---|---|
| 🌐 Overlayer Testnet (Early User) | [https://testnet.overlayer.fi/early-user](https://testnet.overlayer.fi/early-user) |
| 🚰 GHO Faucet (USDT/USDC) | [https://gho.aave.com/faucet/](https://gho.aave.com/faucet/) |

---

## ✨ Features

- ✅ Multi-account support (`accounts.txt`)
- ✅ Proxy support (`proxy.txt`)
- ✅ Auto faucet — claims USDT & USDC testnet tokens
- ✅ Auto mint — wraps USDT → T+ and USDC → C+
- ✅ Auto stake — deposits T+ → sT+ and C+ → sC+
- ✅ Auto redeem — unstakes and unwraps tokens
- ✅ Auto bridge — cross-chain via LayerZero OFT (ETH Sepolia ↔ Base Sepolia)
- ✅ Auto bridge-back — returns bridged tokens from Base Sepolia
- ✅ Auto send — transfers ETH to target addresses
- ✅ Auto receive — receives ETH from other accounts
- ✅ Auto swap — simulates token swap interactions
- ✅ Auto liquidity add/remove
- ✅ Auto transaction cycling — hits daily TX targets
- ✅ Points/leaderboard tracking via Overlayer API
- ✅ Colored terminal output with full log file (`overlayer_bot.log`)
- ✅ 24-hour cycle loop with countdown timer
- ✅ Random delays between actions to avoid detection

---

## 📋 Requirements

- Python 3.8+
- pip packages:
  - `web3`
  - `eth-account`
  - `requests`
  - `colorama`
  - `pytz`

Install all dependencies:

```bash
pip install web3 eth-account requests colorama pytz
```

---

## 🚀 Setup & Usage

### 1. Clone the repository

```bash
git clone https://github.com/febriyan9346/OVERLAYER-BOT.git
cd OVERLAYER-BOT
```

### 2. Prepare your files

**`accounts.txt`** — one private key per line:
```
0xYOUR_PRIVATE_KEY_1
0xYOUR_PRIVATE_KEY_2
```

**`address.txt`** *(optional)* — target addresses for the "send" task:
```
0xRECIPIENT_ADDRESS_1
0xRECIPIENT_ADDRESS_2
```

**`proxy.txt`** *(optional)* — one proxy per line in `http://user:pass@host:port` format:
```
http://user:pass@host:port
http://user2:pass2@host2:port2
```

### 3. Run the bot

```bash
python bot.py
```

You will be prompted to choose:
```
1. Run with proxy
2. Run without proxy
```

---

## 🌐 Supported Networks

| Network | Chain ID | Role |
|---|---|---|
| Ethereum Sepolia | `11155111` | Primary — all main tasks run here |
| Base Sepolia | `84532` | Bridge destination via LayerZero |

### LayerZero EIDs

| Network | EID |
|---|---|
| ETH Mainnet | `30101` |
| Base Mainnet | `30184` |
| ETH Sepolia | `40161` |
| Base Sepolia | `40245` |

---

## 📦 Contract Addresses

### ETH Sepolia

| Token / Contract | Address |
|---|---|
| USDT | `0xaA8E23Fb1079EA71e0a56F48a2aA51851D8433D0` |
| USDC | `0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8` |
| aUSDT (Aave) | `0xAF0F6e8b0Dc5c913bbF4d14c22B4E78Dd14310B6` |
| aUSDC (Aave) | `0x16dA4541aD1807f4443d92D26044C1147406EB80` |
| T+ (Wrap USDT) | `0xe20534a32f9162488a90026F268a74fBE28d272D` |
| sT+ (Stake T+) | `0x079a4Bf1Cbd0E4ce15391340cB46efA6396aBc82` |
| C+ (Wrap USDC) | `0xE815718D44694ec4637CB775C468d87f6e15B538` |
| sC+ (Stake C+) | `0x753937137Eb92871A6F3517514d4f1Ee860e3FDF` |
| Backing USDT | `0xC6110c7Ba33a20dEfAA834B6fE0f3A1e801BC75A` |
| Backing USDC | `0xe1D1CFab6341567E8Ae367eb3D63003f045467BE` |
| POINTS / pOVA | `0xeD8f198Ad99468f351D2eaf93DDb6B2E1565Ceeb` |
| LP Token | `0x1Ac7E198685e53cCc3599e1656E48Dd7E278EbbE` |
| OVA OG NFT | `0x89e2f66E0F79B725321bCD457EB3640ae2e639E6` |
| Galxe NFT | `0x28ACC9a8D03d46a3497e22C8754EF0F4B71F9931` |
| Faucet | `0xC959483DBa39aa9E78757139af0e9a2EDEb3f42D` |
| Multicall3 | `0xca11bde05977b3631167028862be2a173976ca11` |

### Base Sepolia

| Token | Address |
|---|---|
| T+ | `0xdE287B4a0918102511b027d53688c169fb308762` |
| sT+ | `0x5BBc62c58C3b23566488fdFa78455ea00C31a76C` |
| C+ | `0x92f36E427a9579fe1356f19c74eb5d64bEae8930` |
| sC+ | `0x5BBc62c58C3b23566488fdFa78455ea00C31a76C` |

---

## ⚙️ How It Works

1. **Bot starts** and connects to Ethereum Sepolia RPC.
2. **Loads accounts** from `accounts.txt` and proxies from `proxy.txt`.
3. **For each account**, the bot fetches daily on-chain tasks from the Overlayer API.
4. **Executes tasks** in order: faucet → mint → stake → bridge → swap → liquidity → cycling, etc.
5. **Waits 24 hours** then repeats the cycle automatically.
6. All activity is logged to `overlayer_bot.log`.

---

## 📁 File Structure

```
OVERLAYER-BOT/
├── bot.py           # Main bot script
├── accounts.txt     # Private keys (one per line) — create this yourself
├── address.txt      # Send target addresses (optional) — create this yourself
├── proxy.txt        # Proxy list (optional) — create this yourself
├── overlayer_bot.log  # Auto-generated log file
└── README.md
```

---

## ⚠️ Disclaimer

This bot is built for **testnet use only**. Never use real mainnet funds. Always keep your private keys secure — never share them or commit them to any repository.

---

## 💰 Support Us with Cryptocurrency

You can make a contribution using any of the following blockchain networks:

| Network | Wallet Address |
|---|---|
| EVM | `0x216e9b3a5428543c31e659eb8fea3b4bf770bdfd` |
| TON | `UQCEzXLDalfKKySAHuCtBZBARCYnMc0QsTYwN4qda3fE6tto` |
| SOL | `9XgbPg8fndBquuYXkGpNYKHHhymdmVhmF6nMkPxhXTki` |
| SUI | `0x8c3632ddd46c984571bf28f784f7c7aeca3b8371f146c4024f01add025f993bf` |
