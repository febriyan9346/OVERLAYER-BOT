import os
import sys
import time
import random
import logging
import requests
from datetime import datetime
from pathlib import Path

import pytz
from colorama import Fore, Style, init
from web3 import Web3
from eth_account import Account

os.system('clear' if os.name == 'posix' else 'cls')

import warnings
warnings.filterwarnings('ignore')

if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

init(autoreset=True)

_flog = logging.getLogger("bot_file")
_flog.setLevel(logging.DEBUG)
_fh = logging.FileHandler("overlayer_bot.log", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s  %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
_flog.addHandler(_fh)
_flog.propagate = False

# ════════════════════════════════════════════════════════════════════════════
# ─── CHAIN CONFIG ────────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

# ── ETH Sepolia ───────────────────────────────────────────────────────────────
CHAIN_ID_ETH_SEP      = 11155111
RPC_URLS_ETH_SEP = [
    "https://ethereum-sepolia-rpc.publicnode.com",
    "https://rpc.sepolia.org",
    "https://sepolia.drpc.org",
    "https://1rpc.io/sepolia",
]

# ── Base Sepolia ──────────────────────────────────────────────────────────────
CHAIN_ID_BASE_SEP     = 84532
RPC_URLS_BASE_SEP = [
    "https://sepolia.base.org",
    "https://base-sepolia-rpc.publicnode.com",
    "https://base-sepolia.drpc.org",
]

# Default chain (tasks berjalan di ETH Sepolia)
CHAIN_ID = CHAIN_ID_ETH_SEP
RPC_URLS = RPC_URLS_ETH_SEP

# ── LayerZero EIDs ────────────────────────────────────────────────────────────
# Source: bundle Qut={mainnet:30101,sepolia:40161}, Zut={mainnet:30184,sepolia:40245}
LZ_EID_ETH_MAINNET  = 30101   # ETH Mainnet
LZ_EID_BASE_MAINNET = 30184   # Base Mainnet
LZ_EID_ETH_SEPOLIA  = 40161   # ETH Sepolia  (testnet)
LZ_EID_BASE_SEPOLIA = 40245   # Base Sepolia (testnet)

# ════════════════════════════════════════════════════════════════════════════
# ─── API ─────────────────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════
API_BASE = "https://api.overlayer.fi"

# ── API Endpoints (lengkap dari bundle) ──────────────────────────────────────
# GET  /api-s/socials/onchain-tasks?address={addr}       → task list harian
# GET  /api-s/socials/onchain-tasks/points/{addr}        → total points
# GET  /api-s/socials/leaderboard                        → leaderboard
# GET  /api-s/socials/{addr}                             → profile sosial
# GET  /api-s/socials/{addr}/discord-verify              → verif discord
# GET  /api-s/socials/{addr}/telegram-check              → cek telegram
# POST /api-s/socials/og/mint/{addr}                     → mint OVA OG NFT
# GET  /api-s/earlyuser/status/{addr}                    → status early user
# GET  /api-s/gdpr-consent/{addr}                        → GDPR consent

# ════════════════════════════════════════════════════════════════════════════
# ─── CONTRACT ADDRESSES — ETH SEPOLIA (chain 11155111) ───────────────────────
# ════════════════════════════════════════════════════════════════════════════

# ── Collateral tokens (bawahan Aave / USDT / USDC asli) ──────────────────────
USDT_CONTRACT    = Web3.to_checksum_address("0xaA8E23Fb1079EA71e0a56F48a2aA51851D8433D0")  # USDT  (dec=6)
USDC_CONTRACT    = Web3.to_checksum_address("0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8")  # USDC  (dec=6)
AUSDT_CONTRACT   = Web3.to_checksum_address("0xAF0F6e8b0Dc5c913bbF4d14c22B4E78Dd14310B6")  # aUSDT Aave (dec=6)
AUSDC_CONTRACT   = Web3.to_checksum_address("0x16dA4541aD1807f4443d92D26044C1147406EB80")  # aUSDC Aave (dec=6)

# ── Wrap tokens (Overlayer wrap) ──────────────────────────────────────────────
T_PLUS_CONTRACT  = Web3.to_checksum_address("0xe20534a32f9162488a90026F268a74fBE28d272D")  # T+    (dec=18)
ST_PLUS_CONTRACT = Web3.to_checksum_address("0x079a4Bf1Cbd0E4ce15391340cB46efA6396aBc82")  # sT+   (dec=18)
C_PLUS_CONTRACT  = Web3.to_checksum_address("0xE815718D44694ec4637CB775C468d87f6e15B538")  # C+    (dec=18)
SC_PLUS_CONTRACT = Web3.to_checksum_address("0x753937137Eb92871A6F3517514d4f1Ee860e3FDF")  # sC+   (dec=18)

# ── Backing / MintRedeemManager contracts ────────────────────────────────────
BACKING_USDT_CONTRACT = Web3.to_checksum_address("0xC6110c7Ba33a20dEfAA834B6fE0f3A1e801BC75A")  # MintRedeem USDT
BACKING_USDC_CONTRACT = Web3.to_checksum_address("0xe1D1CFab6341567E8Ae367eb3D63003f045467BE")  # MintRedeem USDC
MINT_REDEEM_MANAGER   = Web3.to_checksum_address("0xD0Bc2335fa66714EdFe0b766092808f3D08Dd543")  # MintRedeemManager (APR)

# ── Reward / Governance tokens ────────────────────────────────────────────────
POINTS_CONTRACT  = Web3.to_checksum_address("0xeD8f198Ad99468f351D2eaf93DDb6B2E1565Ceeb")  # POINTS / pOVA (dec=18)
LP_CONTRACT      = Web3.to_checksum_address("0x1Ac7E198685e53cCc3599e1656E48Dd7E278EbbE")  # LP token (dec=18)

# ── NFT / OG contracts ────────────────────────────────────────────────────────
OVA_NFT_CONTRACT = Web3.to_checksum_address("0x89e2f66E0F79B725321bCD457EB3640ae2e639E6")  # OVA OG NFT
GALXE_NFT_CONTRACT = Web3.to_checksum_address("0x28ACC9a8D03d46a3497e22C8754EF0F4B71F9931")  # Galxe Gated NFT

# ── Faucet contract (PUBLIC — siapa saja bisa call) ───────────────────────────
FAUCET_CONTRACT  = Web3.to_checksum_address("0xC959483DBa39aa9E78757139af0e9a2EDEb3f42D")
# mint(address token, address to, uint256 amount)

# ── Multicall3 (untuk batch read balances) ────────────────────────────────────
MULTICALL3_CONTRACT = Web3.to_checksum_address("0xca11bde05977b3631167028862be2a173976ca11")  # standard multicall3

# ════════════════════════════════════════════════════════════════════════════
# ─── CONTRACT ADDRESSES — BASE SEPOLIA (chain 84532) ─────────────────────────
# ════════════════════════════════════════════════════════════════════════════

# ── T+ & sT+ on Base Sepolia (bridge destination) ────────────────────────────
T_PLUS_BASE_CONTRACT  = Web3.to_checksum_address("0xdE287B4a0918102511b027d53688c169fb308762")  # T+  Base Sep
ST_PLUS_BASE_CONTRACT = Web3.to_checksum_address("0x5BBc62c58C3b23566488fdFa78455ea00C31a76C")  # sT+ Base Sep

# ── C+ & sC+ on Base Sepolia ──────────────────────────────────────────────────
C_PLUS_BASE_CONTRACT  = Web3.to_checksum_address("0x92f36E427a9579fe1356f19c74eb5d64bEae8930")  # C+  Base Sep
SC_PLUS_BASE_CONTRACT = Web3.to_checksum_address("0x5BBc62c58C3b23566488fdFa78455ea00C31a76C")  # sC+ Base Sep

# ════════════════════════════════════════════════════════════════════════════
# ─── DECIMALS & CONSTANTS ────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

USDT_DECIMALS  = 6
USDC_DECIMALS  = 6
TOKEN_DECIMALS = 18   # T+, sT+, C+, sC+, POINTS, LP
NFT_DECIMALS   = 0    # NFT (ERC-721)
MAX_UINT256    = 2**256 - 1

# Cycling params
MINT_USDT_RAW  = 100_000    # 0.1 USDT  (untuk cycling)
MINT_TPLUS_RAW = 10**17     # 0.1 T+

# Faucet config
FAUCET_BUFFER_MULTIPLIER = 1.3
FAUCET_MAX_PER_CALL_USDT = 10_000 * 10**USDT_DECIMALS
FAUCET_MAX_PER_CALL_USDC = 10_000 * 10**USDC_DECIMALS

# ════════════════════════════════════════════════════════════════════════════
# ─── PRODUCT MAP — lengkap semua token per produk ────────────────────────────
# ════════════════════════════════════════════════════════════════════════════
PRODUCT_MAP = {
    "usdt": {
        "wrap":                 T_PLUS_CONTRACT,
        "stake":                ST_PLUS_CONTRACT,
        "collateral":           USDT_CONTRACT,
        "collateral_dec":       USDT_DECIMALS,
        "a_collateral":         AUSDT_CONTRACT,       # NEW: aToken Aave
        "backing":              BACKING_USDT_CONTRACT, # NEW: MintRedeemManager USDT
        "wrap_base":            T_PLUS_BASE_CONTRACT,  # NEW: T+ on Base Sepolia
        "stake_base":           ST_PLUS_BASE_CONTRACT, # NEW: sT+ on Base Sepolia
        "wrap_symbol":          "T+",
        "stake_symbol":         "sT+",
        "collateral_symbol":    "USDT",
        "a_collateral_symbol":  "aUSDT",
        "lz_eid_dst":           LZ_EID_BASE_SEPOLIA,
    },
    "usdc": {
        "wrap":                 C_PLUS_CONTRACT,
        "stake":                SC_PLUS_CONTRACT,
        "collateral":           USDC_CONTRACT,
        "collateral_dec":       USDC_DECIMALS,
        "a_collateral":         AUSDC_CONTRACT,        # NEW
        "backing":              BACKING_USDC_CONTRACT,  # NEW
        "wrap_base":            C_PLUS_BASE_CONTRACT,   # NEW: C+ on Base Sepolia
        "stake_base":           SC_PLUS_BASE_CONTRACT,  # NEW: sC+ on Base Sepolia
        "wrap_symbol":          "C+",
        "stake_symbol":         "sC+",
        "collateral_symbol":    "USDC",
        "a_collateral_symbol":  "aUSDC",
        "lz_eid_dst":           LZ_EID_BASE_SEPOLIA,
    },
}

# ════════════════════════════════════════════════════════════════════════════
# ─── ABIs ─────────────────────────────────────────────────────────────────────
# ════════════════════════════════════════════════════════════════════════════

ERC20_ABI = [
    {"inputs": [{"name": "owner",   "type": "address"},
                {"name": "spender", "type": "address"}],
     "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "spender", "type": "address"},
                {"name": "amount",  "type": "uint256"}],
     "name": "approve", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to",     "type": "address"},
                {"name": "amount", "type": "uint256"}],
     "name": "transfer", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [],
     "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [],
     "name": "decimals", "outputs": [{"name": "", "type": "uint8"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [],
     "name": "symbol", "outputs": [{"name": "", "type": "string"}],
     "stateMutability": "view", "type": "function"},
]

ERC721_ABI = [
    {"inputs": [{"name": "owner", "type": "address"}],
     "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}],
     "name": "ownerOf", "outputs": [{"name": "", "type": "address"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}],
     "name": "safeTransferFrom", "outputs": [],
     "stateMutability": "nonpayable", "type": "function"},
]

_ORDER = [
    {"internalType": "address", "name": "benefactor",          "type": "address"},
    {"internalType": "address", "name": "beneficiary",         "type": "address"},
    {"internalType": "address", "name": "collateral",          "type": "address"},
    {"internalType": "uint256", "name": "collateralAmount",    "type": "uint256"},
    {"internalType": "uint256", "name": "overlayerWrapAmount", "type": "uint256"},
]

WRAP_ABI = ERC20_ABI + [
    {"inputs": [{"components": _ORDER, "internalType": "struct MintRedeemManagerTypes.Order",
                 "name": "order", "type": "tuple"}],
     "name": "mint",   "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"components": _ORDER, "internalType": "struct MintRedeemManagerTypes.Order",
                 "name": "order", "type": "tuple"}],
     "name": "redeem", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
]

STAKE_ABI = ERC20_ABI + [
    {"inputs": [{"internalType": "uint256", "name": "assets",   "type": "uint256"},
                {"internalType": "address", "name": "receiver", "type": "address"}],
     "name": "deposit", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "shares",   "type": "uint256"},
                {"internalType": "address", "name": "receiver", "type": "address"},
                {"internalType": "address", "name": "_owner",   "type": "address"}],
     "name": "redeem", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "assets",   "type": "uint256"},
                {"internalType": "address", "name": "receiver", "type": "address"},
                {"internalType": "address", "name": "_owner",   "type": "address"}],
     "name": "withdraw", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}],
     "name": "maxDeposit", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}],
     "name": "maxRedeem", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}],
     "name": "maxWithdraw", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "shares", "type": "uint256"}],
     "name": "convertToAssets", "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]

_SEND_PARAM = [
    {"internalType": "uint32",  "name": "dstEid",       "type": "uint32"},
    {"internalType": "bytes32", "name": "to",           "type": "bytes32"},
    {"internalType": "uint256", "name": "amountLD",     "type": "uint256"},
    {"internalType": "uint256", "name": "minAmountLD",  "type": "uint256"},
    {"internalType": "bytes",   "name": "extraOptions", "type": "bytes"},
    {"internalType": "bytes",   "name": "composeMsg",   "type": "bytes"},
    {"internalType": "bytes",   "name": "oftCmd",       "type": "bytes"},
]
_MESSAGING_FEE = [
    {"internalType": "uint256", "name": "nativeFee",  "type": "uint256"},
    {"internalType": "uint256", "name": "lzTokenFee", "type": "uint256"},
]

OFT_ABI = [
    {"inputs": [
        {"components": _SEND_PARAM,    "internalType": "struct SendParam",    "name": "_sendParam",  "type": "tuple"},
        {"internalType": "bool",       "name": "_payInLzToken",               "type": "bool"},
     ],
     "name": "quoteSend",
     "outputs": [{"components": _MESSAGING_FEE, "internalType": "struct MessagingFee", "name": "", "type": "tuple"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [
        {"components": _SEND_PARAM,    "internalType": "struct SendParam",    "name": "_sendParam",  "type": "tuple"},
        {"components": _MESSAGING_FEE, "internalType": "struct MessagingFee", "name": "_fee",        "type": "tuple"},
        {"internalType": "address",    "name": "_refundAddress",              "type": "address"},
     ],
     "name": "send",
     "outputs": [
         {"components": [{"internalType": "bytes32", "name": "guid",  "type": "bytes32"},
                         {"internalType": "uint64",  "name": "nonce", "type": "uint64"}],
          "internalType": "struct MessagingReceipt", "name": "", "type": "tuple"},
         {"components": [{"internalType": "uint256", "name": "amountSentLD",     "type": "uint256"},
                         {"internalType": "uint256", "name": "amountReceivedLD", "type": "uint256"}],
          "internalType": "struct OFTReceipt", "name": "", "type": "tuple"},
     ],
     "stateMutability": "payable", "type": "function"},
    {"inputs": [], "name": "approvalRequired",
     "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
]

FAUCET_ABI = [
    {"inputs": [{"name": "token",  "type": "address"},
                {"name": "to",     "type": "address"},
                {"name": "amount", "type": "uint256"}],
     "name": "mint", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "token", "type": "address"}],
     "name": "isMintable", "outputs": [{"name": "", "type": "bool"}],
     "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "MAX_MINT_AMOUNT",
     "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]

# ── Multicall3 ABI (untuk batch read) ─────────────────────────────────────────
MULTICALL3_ABI = [
    {"inputs": [{"components": [
        {"name": "target",   "type": "address"},
        {"name": "callData", "type": "bytes"},
    ], "name": "calls", "type": "tuple[]"}],
     "name": "aggregate",
     "outputs": [{"name": "blockNumber", "type": "uint256"},
                 {"name": "returnData",  "type": "bytes[]"}],
     "stateMutability": "view", "type": "function"},
]

# ── APY/backing ABI (MintRedeemManager / j5e) ─────────────────────────────────
MINT_REDEEM_MANAGER_ABI = [
    {"inputs": [{"name": "token",      "type": "address"},
                {"name": "decimals",   "type": "uint256"},
                {"name": "backingAddr","type": "address"}],
     "name": "getCollateralBalance",
     "outputs": [{"name": "", "type": "uint256"}],
     "stateMutability": "view", "type": "function"},
]


# ════════════════════════════════════════════════════════════════════════════
class OverlayerBot:
    def __init__(self):
        self.wib = pytz.timezone("Asia/Jakarta")
        self._session_cache = {}   # {address_lower: {"token": str, "expires_at": float}}

    def get_wib_time(self):
        return datetime.now(self.wib).strftime("%H:%M:%S")

    def print_banner(self):
        banner = f"""
{Fore.CYAN}OVERLAYER BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
        print(banner)

    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        if level == "INFO":
            color  = Fore.CYAN;    symbol = "[INFO]"
        elif level == "SUCCESS":
            color  = Fore.GREEN;   symbol = "[SUCCESS]"
        elif level == "ERROR":
            color  = Fore.RED;     symbol = "[ERROR]"
        elif level == "WARNING":
            color  = Fore.YELLOW;  symbol = "[WARNING]"
        elif level == "CYCLE":
            color  = Fore.MAGENTA; symbol = "[CYCLE]"
        else:
            color  = Fore.WHITE;   symbol = "[LOG]"
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")
        _flog.info(f"{level} {message}")

    def random_delay(self, lo=3, hi=10):
        delay = random.randint(lo, hi)
        self.log(f"Delay {delay} seconds...", "INFO")
        time.sleep(delay)

    def show_menu(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run with proxy")
        print(f"2. Run without proxy{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                if choice in ["1", "2"]:
                    return choice
                print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
                sys.exit(0)

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            h = i // 3600; m = (i % 3600) // 60; s = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {Fore.YELLOW}{h:02d}:{m:02d}:{s:02d}{Style.RESET_ALL} ",
                  end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    # ── Web3 helpers ──────────────────────────────────────────────────────────
    def get_web3(self, proxy=None, rpc_list=None):
        if rpc_list is None:
            rpc_list = RPC_URLS
        for url in rpc_list:
            try:
                req_kwargs = {"timeout": 30}
                if proxy:
                    req_kwargs["proxies"] = {"http": proxy, "https": proxy}
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs=req_kwargs))
                if w3.is_connected():
                    return w3
            except Exception:
                pass
        raise ConnectionError(f"All RPC endpoints failed: {rpc_list}")

    def get_web3_base(self, proxy=None):
        """Koneksi ke Base Sepolia (untuk cek balance pasca bridge)."""
        return self.get_web3(proxy=proxy, rpc_list=RPC_URLS_BASE_SEP)

    # ── TX helpers ────────────────────────────────────────────────────────────
    def build_tx(self, w3, fn, sender, default_gas=300_000, value=0, chain_id=None):
        if chain_id is None:
            chain_id = CHAIN_ID
        nonce = w3.eth.get_transaction_count(sender)
        gp    = int(w3.eth.gas_price * 1.2)
        tx    = fn.build_transaction({"from": sender, "nonce": nonce,
                                      "gasPrice": gp, "chainId": chain_id,
                                      "value": value})
        try:
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = default_gas
        return tx

    def send_tx(self, w3, tx, pk):
        signed  = Account.from_key(pk).sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        self.log(f"Waiting for confirmation  0x{tx_hash.hex()[:12]}...", "INFO")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=3)
        if receipt.status != 1:
            raise RuntimeError(f"REVERTED: {tx_hash.hex()}")
        return tx_hash.hex(), receipt.blockNumber, receipt.gasUsed

    def ensure_allowance(self, w3, token_addr, spender, owner, pk, required, chain_id=None):
        tok = w3.eth.contract(address=Web3.to_checksum_address(token_addr), abi=ERC20_ABI)
        if tok.functions.allowance(owner, spender).call() >= required:
            self.log(f"Allowance sufficient  {token_addr[:10]}...", "INFO")
            return
        self.log(f"Approving  {token_addr[:10]}...  ->  {spender[:10]}...", "INFO")
        h, blk, gas = self.send_tx(
            w3, self.build_tx(w3, tok.functions.approve(spender, MAX_UINT256), owner, 80_000,
                              chain_id=chain_id), pk)
        self.log(f"Approve success  Block: {blk}  Gas: {gas:,}  Tx: 0x{h[:12]}...", "SUCCESS")
        self.random_delay(2, 5)

    # ════════════════════════════════════════════════════════════════════════
    # ─── BALANCE READER ──────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def read_all_balances(self, w3, addr):
        """Baca semua token balance sekaligus."""
        def bal(contract_addr, dec=18):
            try:
                c = w3.eth.contract(address=Web3.to_checksum_address(contract_addr), abi=ERC20_ABI)
                raw = c.functions.balanceOf(addr).call()
                return raw, raw / 10**dec
            except Exception:
                return 0, 0.0

        eth_wei = w3.eth.get_balance(addr)
        return {
            "ETH":    (eth_wei,                             float(w3.from_wei(eth_wei, "ether"))),
            "USDT":   bal(USDT_CONTRACT,    USDT_DECIMALS),
            "USDC":   bal(USDC_CONTRACT,    USDC_DECIMALS),
            "aUSDT":  bal(AUSDT_CONTRACT,   USDT_DECIMALS),
            "aUSDC":  bal(AUSDC_CONTRACT,   USDC_DECIMALS),
            "T+":     bal(T_PLUS_CONTRACT,  TOKEN_DECIMALS),
            "sT+":    bal(ST_PLUS_CONTRACT, TOKEN_DECIMALS),
            "C+":     bal(C_PLUS_CONTRACT,  TOKEN_DECIMALS),
            "sC+":    bal(SC_PLUS_CONTRACT, TOKEN_DECIMALS),
            "POINTS": bal(POINTS_CONTRACT,  TOKEN_DECIMALS),
            "LP":     bal(LP_CONTRACT,      TOKEN_DECIMALS),
        }

    def print_balances(self, balances):
        self.log("── Balance ────────────────────────────────", "INFO")
        for sym, (raw, human) in balances.items():
            if human > 0 or sym in ("ETH", "USDT", "USDC"):
                self.log(f"  {sym:<8}: {human:.6f}", "INFO")

    # ════════════════════════════════════════════════════════════════════════
    # ─── SIWE AUTH (Sign-In With Ethereum) ───────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def _get_cached_token(self, address):
        """Return cached JWT token jika masih valid (>60s sebelum expire)."""
        key  = address.lower()
        info = self._session_cache.get(key)
        if not info:
            return None
        if time.time() >= info["expires_at"] - 60:
            del self._session_cache[key]
            return None
        return info["token"]

    def _cache_token(self, address, token, expires_at_iso):
        """Simpan JWT token ke memory cache."""
        try:
            from datetime import timezone
            dt = datetime.fromisoformat(expires_at_iso.replace("Z", "+00:00"))
            self._session_cache[address.lower()] = {
                "token":      token,
                "expires_at": dt.timestamp(),
            }
        except Exception:
            pass

    def ensure_gdpr_consent(self, address, proxy=None):
        """POST GDPR consent kalau belum disetujui."""
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            r = requests.get(
                f"{API_BASE}/api-s/gdpr-consent/{address}",
                headers={"Origin": "https://testnet.overlayer.fi"},
                proxies=proxies, timeout=10,
            )
            if r.json().get("accepted"):
                return True  # sudah consent
            # Belum consent — POST untuk menyetujui
            r2 = requests.post(
                f"{API_BASE}/api-s/gdpr-consent/{address}",
                headers={"Origin": "https://testnet.overlayer.fi",
                         "Content-Type": "application/json"},
                proxies=proxies, timeout=10,
            )
            if r2.json().get("success"):
                self.log(f"GDPR consent accepted for {address[:10]}...", "INFO")
                return True
        except Exception as ex:
            self.log(f"GDPR consent error (non-fatal): {ex}", "WARNING")
        return False

    def authenticate(self, address, pk, proxy=None):
        """
        SIWE flow:
          1. (opsional) POST /api-s/gdpr-consent/{address}  → terima GDPR
          2. GET  /api-s/auth/nonce/{address}  → nonce
          3. sign message: "Request Overlayer social session\\n{addr}\\n{ts}\\n{nonce}"
          4. POST /api-s/auth/verify/{address} {message, signature} → JWT token
        Return JWT token string, or None on failure.
        """
        # Kembalikan token dari cache kalau masih valid
        cached = self._get_cached_token(address)
        if cached:
            return cached

        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            # Step 0: pastikan GDPR consent sudah di-accept
            self.ensure_gdpr_consent(address, proxy=proxy)

            # Step 1: ambil nonce
            r = requests.get(
                f"{API_BASE}/api-s/auth/nonce/{address}",
                headers={"Origin": "https://testnet.overlayer.fi",
                         "Referer": "https://testnet.overlayer.fi/"},
                proxies=proxies, timeout=15,
            )
            r.raise_for_status()
            nonce_data = r.json()
            if not nonce_data.get("success"):
                self.log(f"Auth nonce failed: {nonce_data}", "ERROR")
                return None
            nonce = nonce_data["nonce"]

            # Step 2: buat & sign message
            ts      = int(time.time()) + 5 * 60   # expire 5 menit ke depan
            message = f"Request Overlayer social session\n{address}\n{ts}\n{nonce}"
            from eth_account.messages import encode_defunct as _edf
            raw_sig = Account.from_key(pk).sign_message(_edf(text=message)).signature.hex()
            # API butuh hex dengan prefix "0x"
            sig     = raw_sig if raw_sig.startswith("0x") else "0x" + raw_sig

            # Step 3: verifikasi & dapat token
            r2 = requests.post(
                f"{API_BASE}/api-s/auth/verify/{address}",
                json={"message": message, "signature": sig},
                headers={"Origin": "https://testnet.overlayer.fi",
                         "Referer": "https://testnet.overlayer.fi/",
                         "Content-Type": "application/json"},
                proxies=proxies, timeout=15,
            )
            r2.raise_for_status()
            verify_data = r2.json()
            if not verify_data.get("success") or not verify_data.get("token"):
                self.log(f"Auth verify failed: {verify_data}", "ERROR")
                return None

            token      = verify_data["token"]
            expires_at = verify_data.get("expiresAt", "")
            self._cache_token(address, token, expires_at)
            self.log(f"Auth success for {address[:10]}...", "SUCCESS")
            return token

        except Exception as ex:
            self.log(f"Auth error: {ex}", "ERROR")
            return None

    def _auth_headers(self, token):
        """Return dict headers dengan Authorization Bearer."""
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    # ════════════════════════════════════════════════════════════════════════
    # ─── API: Fetch tasks ────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def fetch_tasks(self, address, pk, proxy=None):
        url     = f"{API_BASE}/api-s/socials/onchain-tasks"
        proxies = {"http": proxy, "https": proxy} if proxy else None

        # Autentikasi dulu
        token = self.authenticate(address, pk, proxy=proxy)
        if not token:
            self.log("Skipping task fetch — auth failed.", "WARNING")
            return []

        try:
            resp = requests.get(
                url,
                params={"address": address},
                headers=self._auth_headers(token),
                proxies=proxies, timeout=15,
            )
            resp.raise_for_status()
            data  = resp.json()
            tasks = data.get("tasks", [])
            # Filter hanya eth-sepolia, skip yang sudah selesai
            tasks = [t for t in tasks
                     if t.get("chain") == "eth-sepolia" and not t.get("completed", False)]
            # Urut: transaction (cycling) paling akhir
            tasks.sort(key=lambda t: 1 if t["type"] == "transaction" else 0)
            self.log(f"Fetched {len(tasks)} pending tasks for {address[:10]}...", "INFO")
            return tasks
        except Exception as ex:
            self.log(f"Failed to fetch tasks: {ex}", "WARNING")
            return []

    def fetch_points(self, address, pk, proxy=None):
        """Ambil total poin yang sudah dikumpulkan address ini."""
        url     = f"{API_BASE}/api-s/socials/onchain-tasks/points/{address}"
        proxies = {"http": proxy, "https": proxy} if proxy else None
        token   = self.authenticate(address, pk, proxy=proxy)
        try:
            resp = requests.get(
                url,
                headers=self._auth_headers(token),
                proxies=proxies, timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("totalPoints", 0) if isinstance(data, dict) else (data if isinstance(data, (int, float)) else 0)
        except Exception:
            return 0

    def fetch_earlyuser_status(self, address, proxy=None):
        """Cek status early user dan apakah sudah terdaftar."""
        url     = f"{API_BASE}/api-s/earlyuser/status/{address}"
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            resp = requests.get(url, proxies=proxies, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}

    def print_tasks(self, tasks):
        if not tasks:
            self.log("No pending tasks today.", "INFO")
            return
        self.log(f"Today's Tasks ({len(tasks)}):", "INFO")
        for i, t in enumerate(tasks, 1):
            p   = PRODUCT_MAP.get(t.get("product", ""), {})
            sym = p.get("wrap_symbol", t.get("product", "?").upper())
            print(f"  {Fore.CYAN}{i}. [{t['type'].upper():11}] {t['amount']:>6} {sym:<4} "
                  f"+{t.get('points',0):>4}pts  |  {t['description']}{Style.RESET_ALL}")
        print()

    # ════════════════════════════════════════════════════════════════════════
    # ─── AUTO TOPUP via FAUCET ───────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def faucet_mint(self, w3, addr, pk, token_addr, amount_raw, symbol):
        faucet     = w3.eth.contract(address=FAUCET_CONTRACT, abi=FAUCET_ABI)
        token_addr = Web3.to_checksum_address(token_addr)
        dec        = USDT_DECIMALS if symbol == "USDT" else USDC_DECIMALS
        max_call   = FAUCET_MAX_PER_CALL_USDT if symbol == "USDT" else FAUCET_MAX_PER_CALL_USDC

        remaining = amount_raw
        calls     = 0
        while remaining > 0:
            this_call = min(remaining, max_call)
            self.log(f"Faucet mint {this_call/10**dec:,.2f} {symbol}  ->  {addr[:10]}...", "INFO")
            nonce = w3.eth.get_transaction_count(addr)
            gp    = int(w3.eth.gas_price * 1.2)
            tx    = faucet.functions.mint(token_addr, addr, this_call).build_transaction({
                "from": addr, "nonce": nonce, "gasPrice": gp,
                "chainId": CHAIN_ID, "value": 0,
            })
            try:
                tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
            except Exception:
                tx["gas"] = 120_000
            h, blk, gas = self.send_tx(w3, tx, pk)
            self.log(f"Faucet {symbol} success!  +{this_call/10**dec:,.2f} {symbol}  "
                     f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
            remaining -= this_call
            calls += 1
            if remaining > 0:
                self.random_delay(2, 4)
        return calls

    def prepare_materials(self, w3, addr, pk, tasks):
        self.log("Checking material requirements...", "INFO")

        need_usdt_raw = 0
        need_usdc_raw = 0
        cycling_target = 43

        for t in tasks:
            t_type    = t["type"]
            t_product = t.get("product", "usdt")
            t_amount  = t["amount"]

            if t_type == "transaction":
                cycling_target = t_amount

            if t_type in ("mint", "stake", "send", "receive"):
                if t_product == "usdt":
                    need_usdt_raw += t_amount * 10**USDT_DECIMALS
                elif t_product == "usdc":
                    need_usdc_raw += t_amount * 10**USDC_DECIMALS

            elif t_type in ("bridge", "bridge_back"):
                if t_product == "usdc":
                    need_usdc_raw += t_amount * 10**USDC_DECIMALS
                elif t_product == "usdt":
                    need_usdt_raw += t_amount * 10**USDT_DECIMALS

            elif t_type in ("unstake", "redeem"):
                # tidak butuh topup, malah mendapat token kembali
                pass

        cycling_usdt   = int((cycling_target / 4 + 2) * MINT_USDT_RAW)
        need_usdt_raw += cycling_usdt
        need_usdt_raw  = int(need_usdt_raw * FAUCET_BUFFER_MULTIPLIER)
        need_usdc_raw  = int(need_usdc_raw * FAUCET_BUFFER_MULTIPLIER) if need_usdc_raw > 0 else 0

        usdt_c   = w3.eth.contract(address=USDT_CONTRACT, abi=ERC20_ABI)
        usdc_c   = w3.eth.contract(address=USDC_CONTRACT, abi=ERC20_ABI)
        usdt_bal = usdt_c.functions.balanceOf(addr).call()
        usdc_bal = usdc_c.functions.balanceOf(addr).call()

        self.log(f"Need  USDT: {need_usdt_raw/10**USDT_DECIMALS:,.2f}  "
                 f"USDC: {need_usdc_raw/10**USDC_DECIMALS:,.2f}", "INFO")
        self.log(f"Have  USDT: {usdt_bal/10**USDT_DECIMALS:,.2f}  "
                 f"USDC: {usdc_bal/10**USDC_DECIMALS:,.2f}", "INFO")

        if need_usdt_raw > 0 and usdt_bal < need_usdt_raw:
            topup = need_usdt_raw - usdt_bal
            self.log(f"USDT shortage +{topup/10**USDT_DECIMALS:,.2f}  → faucet...", "WARNING")
            try:
                self.faucet_mint(w3, addr, pk, USDT_CONTRACT, topup, "USDT")
                self.random_delay(2, 5)
            except Exception as ex:
                self.log(f"Faucet USDT failed: {ex}", "ERROR")

        if need_usdc_raw > 0 and usdc_bal < need_usdc_raw:
            topup = need_usdc_raw - usdc_bal
            self.log(f"USDC shortage +{topup/10**USDC_DECIMALS:,.2f}  → faucet...", "WARNING")
            try:
                self.faucet_mint(w3, addr, pk, USDC_CONTRACT, topup, "USDC")
                self.random_delay(2, 5)
            except Exception as ex:
                self.log(f"Faucet USDC failed: {ex}", "ERROR")

        uf = usdt_c.functions.balanceOf(addr).call()
        cf = usdc_c.functions.balanceOf(addr).call()
        self.log(f"Materials ready  USDT: {uf/10**USDT_DECIMALS:,.2f}  "
                 f"USDC: {cf/10**USDC_DECIMALS:,.2f}", "SUCCESS")

    # ════════════════════════════════════════════════════════════════════════
    # ─── TASK EXECUTORS ──────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def ensure_wrap_balance(self, w3, addr, pk, product, amount_wei):
        p         = PRODUCT_MAP[product]
        wrap_c    = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        wrap_bal  = wrap_c.functions.balanceOf(addr).call()
        sym       = p["wrap_symbol"]
        csym      = p["collateral_symbol"]

        if wrap_bal >= amount_wei:
            self.log(f"{sym} sufficient: {wrap_bal/10**TOKEN_DECIMALS:.4f}", "INFO")
            return True

        collateral_c    = w3.eth.contract(address=p["collateral"], abi=ERC20_ABI)
        collateral_bal  = collateral_c.functions.balanceOf(addr).call()
        collateral_need = int(amount_wei / 10**(TOKEN_DECIMALS - p["collateral_dec"]))

        self.log(f"{sym} insufficient ({wrap_bal/10**TOKEN_DECIMALS:.4f}), "
                 f"minting {amount_wei/10**TOKEN_DECIMALS:.4f} {sym} "
                 f"from {collateral_need/10**p['collateral_dec']:.4f} {csym}", "INFO")

        if collateral_bal < collateral_need:
            self.log(f"Insufficient {csym}. Trying faucet first...", "WARNING")
            try:
                token_contract = USDT_CONTRACT if product == "usdt" else USDC_CONTRACT
                self.faucet_mint(w3, addr, pk, token_contract,
                                 collateral_need - collateral_bal, csym.upper())
                self.random_delay(2, 4)
                collateral_bal = collateral_c.functions.balanceOf(addr).call()
            except Exception as ex:
                self.log(f"Faucet failed: {ex}. Skipped.", "ERROR")
                return False

        wrap_contract = w3.eth.contract(address=p["wrap"], abi=WRAP_ABI)
        self.ensure_allowance(w3, p["collateral"], p["wrap"], addr, pk, collateral_need)
        order = (addr, addr, p["collateral"], collateral_need, amount_wei)
        h, blk, gas = self.send_tx(w3, self.build_tx(w3, wrap_contract.functions.mint(order), addr), pk)
        self.log(f"Mint {amount_wei/10**TOKEN_DECIMALS:.4f} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        self.random_delay(3, 6)
        return True

    # ── type: mint ────────────────────────────────────────────────────────────
    def exec_mint(self, w3, addr, pk, task):
        product    = task.get("product", "usdt")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        csym       = p["collateral_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        collateral_c    = w3.eth.contract(address=p["collateral"], abi=ERC20_ABI)
        collateral_need = amount * (10 ** p["collateral_dec"])
        collateral_bal  = collateral_c.functions.balanceOf(addr).call()

        self.log(f"[Mint] {amount} {sym}  |  {csym} bal: {collateral_bal/10**p['collateral_dec']:.4f}", "INFO")

        if collateral_bal < collateral_need:
            self.log(f"[Mint] Not enough {csym}, trying faucet...", "WARNING")
            try:
                token_contract = USDT_CONTRACT if product == "usdt" else USDC_CONTRACT
                self.faucet_mint(w3, addr, pk, token_contract,
                                 collateral_need - collateral_bal, csym.upper())
                self.random_delay(2, 4)
                collateral_bal = collateral_c.functions.balanceOf(addr).call()
            except Exception as ex:
                self.log(f"[Mint] Faucet failed: {ex}. Skipped.", "ERROR")
                return None, None, None

        wrap_contract = w3.eth.contract(address=p["wrap"], abi=WRAP_ABI)
        self.ensure_allowance(w3, p["collateral"], p["wrap"], addr, pk, collateral_need)
        order = (addr, addr, p["collateral"], collateral_need, amount_wei)
        h, blk, gas = self.send_tx(w3, self.build_tx(w3, wrap_contract.functions.mint(order), addr), pk)
        self.log(f"[Mint] {amount} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: stake ───────────────────────────────────────────────────────────
    def exec_stake(self, w3, addr, pk, task):
        product    = task.get("product", "usdt")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        ssym       = p["stake_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        self.log(f"[Stake] {amount} {sym}  ->  {ssym}", "INFO")

        if not self.ensure_wrap_balance(w3, addr, pk, product, amount_wei):
            return None, None, None

        vault = w3.eth.contract(address=p["stake"], abi=STAKE_ABI)
        try:
            md = vault.functions.maxDeposit(addr).call()
            if amount_wei > md:
                amount_wei = md
        except Exception:
            pass

        self.ensure_allowance(w3, p["wrap"], p["stake"], addr, pk, amount_wei)
        h, blk, gas = self.send_tx(w3, self.build_tx(w3, vault.functions.deposit(amount_wei, addr), addr), pk)
        self.log(f"[Stake] {amount_wei/10**TOKEN_DECIMALS:.4f} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: unstake (NEW) ───────────────────────────────────────────────────
    def exec_unstake(self, w3, addr, pk, task):
        """
        Unstake sT+ / sC+ kembali ke T+ / C+.
        Bisa juga muncul sebagai task baru, jadi ditangani eksplisit.
        """
        product    = task.get("product", "usdt")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        ssym       = p["stake_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        vault = w3.eth.contract(address=p["stake"], abi=STAKE_ABI)
        try:
            max_redeem = vault.functions.maxRedeem(addr).call()
        except Exception:
            max_redeem = vault.functions.balanceOf(addr).call()

        if max_redeem == 0:
            self.log(f"[Unstake] No {ssym} to unstake. Skipped.", "WARNING")
            return None, None, None

        shares = min(amount_wei, max_redeem)
        self.log(f"[Unstake] {shares/10**TOKEN_DECIMALS:.4f} {ssym}  ->  {sym}", "INFO")

        h, blk, gas = self.send_tx(
            w3, self.build_tx(w3, vault.functions.redeem(shares, addr, addr), addr), pk)
        self.log(f"[Unstake] success!  Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: redeem (NEW) ────────────────────────────────────────────────────
    def exec_redeem(self, w3, addr, pk, task):
        """
        Redeem T+ / C+ kembali ke USDT / USDC.
        """
        product    = task.get("product", "usdt")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        csym       = p["collateral_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)
        collateral_amount = amount * (10 ** p["collateral_dec"])

        self.log(f"[Redeem] {amount} {sym}  ->  {csym}", "INFO")

        wrap_c   = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        wrap_bal = wrap_c.functions.balanceOf(addr).call()
        if wrap_bal < amount_wei:
            amount_wei       = wrap_bal
            collateral_amount = int(wrap_bal / 10**(TOKEN_DECIMALS - p["collateral_dec"]))

        if amount_wei == 0:
            self.log(f"[Redeem] No {sym} balance. Skipped.", "WARNING")
            return None, None, None

        wrap_contract = w3.eth.contract(address=p["wrap"], abi=WRAP_ABI)
        self.ensure_allowance(w3, p["wrap"], p["wrap"], addr, pk, amount_wei)
        order = (addr, addr, p["collateral"], collateral_amount, amount_wei)
        h, blk, gas = self.send_tx(
            w3, self.build_tx(w3, wrap_contract.functions.redeem(order), addr), pk)
        self.log(f"[Redeem] {amount_wei/10**TOKEN_DECIMALS:.4f} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: bridge ──────────────────────────────────────────────────────────
    def exec_bridge(self, w3, addr, pk, task):
        product    = task.get("product", "usdc")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        dst_eid    = p.get("lz_eid_dst", LZ_EID_BASE_SEPOLIA)
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        self.log(f"[Bridge] {amount} {sym}  ETH Sepolia  →  Base Sepolia  (EID {dst_eid})", "INFO")

        if not self.ensure_wrap_balance(w3, addr, pk, product, amount_wei):
            return None, None, None

        wrap_c   = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        wrap_bal = wrap_c.functions.balanceOf(addr).call()
        if wrap_bal < amount_wei:
            self.log(f"[Bridge] {sym} still insufficient. Skipped.", "WARNING")
            return None, None, None

        oft = w3.eth.contract(address=p["wrap"], abi=OFT_ABI)
        try:
            needs_approval = oft.functions.approvalRequired().call()
        except Exception:
            needs_approval = False
        if needs_approval:
            self.ensure_allowance(w3, p["wrap"], p["wrap"], addr, pk, amount_wei)

        to_bytes32    = "0x" + "00" * 12 + addr[2:].lower()
        min_amount    = int(amount_wei * 99 // 100)
        extra_options = bytes.fromhex("00030100110100000000000000000000000000030d40")

        send_param = {
            "dstEid":       dst_eid,
            "to":           to_bytes32,
            "amountLD":     amount_wei,
            "minAmountLD":  min_amount,
            "extraOptions": extra_options,
            "composeMsg":   b"",
            "oftCmd":       b"",
        }

        try:
            fee_result = oft.functions.quoteSend(send_param, False).call()
            native_fee = int(fee_result[0] * 1.1)
        except Exception as ex:
            self.log(f"[Bridge] quoteSend failed: {ex}  → Fallback 0.005 ETH", "WARNING")
            native_fee = int(5e15)

        self.log(f"[Bridge] LZ Native Fee: {native_fee/10**18:.6f} ETH", "INFO")

        messaging_fee = {"nativeFee": native_fee, "lzTokenFee": 0}
        nonce = w3.eth.get_transaction_count(addr)
        gp    = int(w3.eth.gas_price * 1.2)
        tx    = oft.functions.send(send_param, messaging_fee, addr).build_transaction({
            "from": addr, "nonce": nonce, "gasPrice": gp,
            "chainId": CHAIN_ID, "value": native_fee,
        })
        try:
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = 400_000

        h, blk, gas = self.send_tx(w3, tx, pk)
        self.log(f"[Bridge] {amount} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: bridge_back (NEW) ───────────────────────────────────────────────
    def exec_bridge_back(self, w3_base, addr, pk, task):
        """
        Bridge balik dari Base Sepolia ke ETH Sepolia.
        Gunakan T+/C+ yang ada di Base Sepolia.
        """
        product    = task.get("product", "usdc")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        wrap_base_addr = p.get("wrap_base")
        if not wrap_base_addr:
            self.log(f"[BridgeBack] No Base Sepolia wrap contract for {sym}. Skipped.", "WARNING")
            return None, None, None

        self.log(f"[BridgeBack] {amount} {sym}  Base Sepolia  →  ETH Sepolia", "INFO")

        oft = w3_base.eth.contract(address=wrap_base_addr, abi=OFT_ABI)
        to_bytes32    = "0x" + "00" * 12 + addr[2:].lower()
        min_amount    = int(amount_wei * 99 // 100)
        extra_options = bytes.fromhex("00030100110100000000000000000000000000030d40")

        send_param = {
            "dstEid":       LZ_EID_ETH_SEPOLIA,
            "to":           to_bytes32,
            "amountLD":     amount_wei,
            "minAmountLD":  min_amount,
            "extraOptions": extra_options,
            "composeMsg":   b"",
            "oftCmd":       b"",
        }

        try:
            fee_result = oft.functions.quoteSend(send_param, False).call()
            native_fee = int(fee_result[0] * 1.1)
        except Exception as ex:
            self.log(f"[BridgeBack] quoteSend failed: {ex}  → Fallback 0.005 ETH", "WARNING")
            native_fee = int(5e15)

        messaging_fee = {"nativeFee": native_fee, "lzTokenFee": 0}
        nonce = w3_base.eth.get_transaction_count(addr)
        gp    = int(w3_base.eth.gas_price * 1.2)
        tx    = oft.functions.send(send_param, messaging_fee, addr).build_transaction({
            "from": addr, "nonce": nonce, "gasPrice": gp,
            "chainId": CHAIN_ID_BASE_SEP, "value": native_fee,
        })
        try:
            tx["gas"] = int(w3_base.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = 400_000

        h, blk, gas = self.send_tx(w3_base, tx, pk)
        self.log(f"[BridgeBack] {amount} {sym} success!  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: send ────────────────────────────────────────────────────────────
    def exec_send(self, w3, addr, pk, task, to_address):
        product    = task.get("product", "usdt")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        self.log(f"[Send] {amount} {sym}  ->  {to_address[:10]}...", "INFO")

        if not self.ensure_wrap_balance(w3, addr, pk, product, amount_wei):
            return None, None, None

        wrap_c  = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        to_addr = Web3.to_checksum_address(to_address)
        h, blk, gas = self.send_tx(
            w3, self.build_tx(w3, wrap_c.functions.transfer(to_addr, amount_wei), addr, 80_000), pk)
        self.log(f"[Send] {amount} {sym} success!  "
                 f"To: {to_address[:10]}...  Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: receive ─────────────────────────────────────────────────────────
    def exec_receive(self, w3, addr, pk, task, all_accounts):
        product    = task.get("product", "usdc")
        amount     = task["amount"]
        p          = PRODUCT_MAP[product]
        sym        = p["wrap_symbol"]
        amount_wei = amount * (10 ** TOKEN_DECIMALS)

        self.log(f"[Receive] Need {amount} {sym} sent to {addr[:10]}...", "INFO")

        sender_pk   = None
        sender_addr = None
        for other_pk in all_accounts:
            if other_pk == pk:
                continue
            oa     = Account.from_key(other_pk).address
            wrap_c = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
            bal    = wrap_c.functions.balanceOf(oa).call()
            if bal >= amount_wei:
                sender_pk   = other_pk
                sender_addr = oa
                break

        # Jika tidak ada akun lain yang cukup → gunakan akun sendiri, kirim ke diri sendiri
        if not sender_pk:
            self.log(f"[Receive] No other account has {sym}. Will mint & self-send.", "WARNING")
            if self.ensure_wrap_balance(w3, addr, pk, product, amount_wei):
                sender_pk   = pk
                sender_addr = addr

        if not sender_pk:
            self.log(f"[Receive] Cannot fulfill. Skipped.", "ERROR")
            return None, None, None

        wrap_c  = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        to_addr = Web3.to_checksum_address(addr)
        h, blk, gas = self.send_tx(
            w3,
            self.build_tx(w3, wrap_c.functions.transfer(to_addr, amount_wei), sender_addr, 80_000),
            sender_pk,
        )
        self.log(f"[Receive] {amount} {sym} from {sender_addr[:10]}...  "
                 f"Block: {blk}  Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
        return h, blk, gas

    # ── type: swap (NEW — potensi task baru: swap T+ <-> C+) ─────────────────
    def exec_swap(self, w3, addr, pk, task):
        """
        Potensi task swap antar produk.
        Strategi: redeem wrap -> collateral -> mint ke wrap lain.
        """
        product_in  = task.get("product_in",  task.get("product", "usdt"))
        product_out = task.get("product_out", "usdc")
        amount      = task["amount"]
        p_in        = PRODUCT_MAP[product_in]
        p_out       = PRODUCT_MAP[product_out]
        amount_wei  = amount * (10 ** TOKEN_DECIMALS)

        self.log(f"[Swap] {amount} {p_in['wrap_symbol']}  →  {p_out['wrap_symbol']}", "INFO")

        # Step 1: Redeem wrap_in → collateral_in
        wrap_in_c = w3.eth.contract(address=p_in["wrap"], abi=WRAP_ABI)
        col_amount = amount * (10 ** p_in["collateral_dec"])
        self.ensure_allowance(w3, p_in["wrap"], p_in["wrap"], addr, pk, amount_wei)
        order_redeem = (addr, addr, p_in["collateral"], col_amount, amount_wei)
        h1, blk1, gas1 = self.send_tx(w3, self.build_tx(w3, wrap_in_c.functions.redeem(order_redeem), addr), pk)
        self.log(f"[Swap] Redeem {p_in['wrap_symbol']} → {p_in['collateral_symbol']}  Hash: 0x{h1[:16]}...", "SUCCESS")
        self.random_delay(3, 6)

        # Step 2: Mint wrap_out dari collateral_out (asumsi sama-sama USDT/USDC)
        h2, blk2, gas2 = self.send_tx(
            w3,
            self.build_tx(
                w3,
                w3.eth.contract(address=p_out["wrap"], abi=WRAP_ABI).functions.mint(
                    (addr, addr, p_out["collateral"],
                     amount * (10 ** p_out["collateral_dec"]),
                     amount_wei)
                ),
                addr
            ),
            pk
        )
        self.log(f"[Swap] Mint {p_out['wrap_symbol']}  Hash: 0x{h2[:16]}...", "SUCCESS")
        return h2, blk2, gas2

    # ── type: liquidity_add / liquidity_remove (NEW potential tasks) ──────────
    def exec_liquidity_add(self, w3, addr, pk, task):
        """
        Placeholder untuk task add liquidity (LP token).
        Akan diimplementasikan penuh saat task muncul di API.
        """
        self.log(f"[LP Add] Task detected but full LP ABI not yet available. Logged for review.", "WARNING")
        self.log(f"  LP Contract: {LP_CONTRACT}", "INFO")
        self.log(f"  Task details: {task}", "INFO")
        return None, None, None

    def exec_liquidity_remove(self, w3, addr, pk, task):
        self.log(f"[LP Remove] Task detected but full LP ABI not yet available. Logged for review.", "WARNING")
        return None, None, None

    # ════════════════════════════════════════════════════════════════════════
    # ─── CYCLING (type: transaction) ─────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def do_mint_cycle(self, w3, addr, pk):
        self.log("Cycle Mint  0.1 USDT  ->  0.1 T+", "INFO")
        self.ensure_allowance(w3, USDT_CONTRACT, T_PLUS_CONTRACT, addr, pk, MINT_USDT_RAW)
        self.random_delay(2, 5)
        c = w3.eth.contract(address=T_PLUS_CONTRACT, abi=WRAP_ABI)
        return self.send_tx(
            w3,
            self.build_tx(w3, c.functions.mint((addr, addr, USDT_CONTRACT,
                                                MINT_USDT_RAW, MINT_TPLUS_RAW)), addr),
            pk,
        )

    def do_stake_cycle(self, w3, addr, pk, assets_wei):
        vault = w3.eth.contract(address=ST_PLUS_CONTRACT, abi=STAKE_ABI)
        try:
            md = vault.functions.maxDeposit(addr).call()
            if assets_wei > md:
                assets_wei = md
        except Exception:
            pass
        self.log(f"Cycle Stake  {assets_wei/10**TOKEN_DECIMALS:.6f} T+  ->  sT+", "INFO")
        self.ensure_allowance(w3, T_PLUS_CONTRACT, ST_PLUS_CONTRACT, addr, pk, assets_wei)
        self.random_delay(2, 5)
        return self.send_tx(
            w3, self.build_tx(w3, vault.functions.deposit(assets_wei, addr), addr), pk)

    def do_unstake_cycle(self, w3, addr, pk):
        vault = w3.eth.contract(address=ST_PLUS_CONTRACT, abi=STAKE_ABI)
        try:
            shares = vault.functions.maxRedeem(addr).call()
        except Exception:
            shares = vault.functions.balanceOf(addr).call()
        if shares == 0:
            self.log("No sT+ to unstake, skipped.", "WARNING")
            return None, None, None
        self.log(f"Cycle Unstake  {shares/10**TOKEN_DECIMALS:.6f} sT+  ->  T+", "INFO")
        return self.send_tx(
            w3, self.build_tx(w3, vault.functions.redeem(shares, addr, addr), addr), pk)

    def do_redeem_cycle(self, w3, addr, pk, tplus_wei):
        redeem_tplus = min(tplus_wei, MINT_TPLUS_RAW)
        redeem_usdt  = min(int(redeem_tplus * MINT_USDT_RAW / MINT_TPLUS_RAW), MINT_USDT_RAW)
        self.log(f"Cycle Redeem  {redeem_tplus/10**TOKEN_DECIMALS:.6f} T+  ->  "
                 f"{redeem_usdt/10**USDT_DECIMALS:.4f} USDT", "INFO")
        self.ensure_allowance(w3, T_PLUS_CONTRACT, T_PLUS_CONTRACT, addr, pk, redeem_tplus)
        self.random_delay(2, 5)
        c = w3.eth.contract(address=T_PLUS_CONTRACT, abi=WRAP_ABI)
        return self.send_tx(
            w3,
            self.build_tx(w3, c.functions.redeem((addr, addr, USDT_CONTRACT,
                                                   redeem_usdt, redeem_tplus)), addr),
            pk,
        )

    def do_bridge_cycle(self, w3, addr, pk):
        """Bridge 0.1 T+ dari ETH Sepolia ke Base Sepolia. Dihitung website."""
        p          = PRODUCT_MAP["usdt"]
        amount_wei = MINT_TPLUS_RAW  # 0.1 T+
        wrap_c     = w3.eth.contract(address=p["wrap"], abi=ERC20_ABI)
        if wrap_c.functions.balanceOf(addr).call() < amount_wei:
            self.log("[BridgeCycle] T+ tidak cukup untuk bridge, skip.", "WARNING")
            return None, None, None

        self.log("Cycle Bridge  0.1 T+  ETH Sepolia → Base Sepolia", "INFO")
        oft = w3.eth.contract(address=p["wrap"], abi=OFT_ABI)
        try:
            needs_approval = oft.functions.approvalRequired().call()
        except Exception:
            needs_approval = False
        if needs_approval:
            self.ensure_allowance(w3, p["wrap"], p["wrap"], addr, pk, amount_wei)

        to_bytes32    = "0x" + "00" * 12 + addr[2:].lower()
        min_amount    = int(amount_wei * 99 // 100)
        extra_options = bytes.fromhex("00030100110100000000000000000000000000030d40")
        send_param = {
            "dstEid":       p["lz_eid_dst"],
            "to":           to_bytes32,
            "amountLD":     amount_wei,
            "minAmountLD":  min_amount,
            "extraOptions": extra_options,
            "composeMsg":   b"",
            "oftCmd":       b"",
        }
        try:
            fee_result = oft.functions.quoteSend(send_param, False).call()
            native_fee = int(fee_result[0] * 1.1)
        except Exception as ex:
            self.log(f"[BridgeCycle] quoteSend failed: {ex}  → Fallback 0.005 ETH", "WARNING")
            native_fee = int(5e15)

        nonce = w3.eth.get_transaction_count(addr)
        gp    = int(w3.eth.gas_price * 1.2)
        tx    = oft.functions.send(send_param, {"nativeFee": native_fee, "lzTokenFee": 0}, addr).build_transaction({
            "from": addr, "nonce": nonce, "gasPrice": gp,
            "chainId": CHAIN_ID, "value": native_fee,
        })
        try:
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = 400_000
        return self.send_tx(w3, tx, pk)

    def do_bridge_back_cycle(self, w3_base, addr, pk):
        """Bridge 0.1 T+ dari Base Sepolia kembali ke ETH Sepolia. Recycle."""
        p              = PRODUCT_MAP["usdt"]
        wrap_base_addr = p.get("wrap_base")
        if not wrap_base_addr:
            return None, None, None
        amount_wei = MINT_TPLUS_RAW  # 0.1 T+
        wrap_c     = w3_base.eth.contract(address=wrap_base_addr, abi=ERC20_ABI)
        bal        = wrap_c.functions.balanceOf(addr).call()
        if bal < amount_wei:
            self.log(f"[BridgeBackCycle] T+ di Base Sepolia tidak cukup ({bal/10**18:.4f}), skip.", "WARNING")
            return None, None, None

        self.log("Cycle BridgeBack  0.1 T+  Base Sepolia → ETH Sepolia", "INFO")
        oft        = w3_base.eth.contract(address=wrap_base_addr, abi=OFT_ABI)
        to_bytes32    = "0x" + "00" * 12 + addr[2:].lower()
        min_amount    = int(amount_wei * 99 // 100)
        extra_options = bytes.fromhex("00030100110100000000000000000000000000030d40")
        send_param = {
            "dstEid":       LZ_EID_ETH_SEPOLIA,
            "to":           to_bytes32,
            "amountLD":     amount_wei,
            "minAmountLD":  min_amount,
            "extraOptions": extra_options,
            "composeMsg":   b"",
            "oftCmd":       b"",
        }
        try:
            fee_result = oft.functions.quoteSend(send_param, False).call()
            native_fee = int(fee_result[0] * 1.1)
        except Exception as ex:
            self.log(f"[BridgeBackCycle] quoteSend failed: {ex}  → Fallback 0.005 ETH", "WARNING")
            native_fee = int(5e15)

        nonce = w3_base.eth.get_transaction_count(addr)
        gp    = int(w3_base.eth.gas_price * 1.2)
        tx    = oft.functions.send(send_param, {"nativeFee": native_fee, "lzTokenFee": 0}, addr).build_transaction({
            "from": addr, "nonce": nonce, "gasPrice": gp,
            "chainId": CHAIN_ID_BASE_SEP, "value": native_fee,
        })
        try:
            tx["gas"] = int(w3_base.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = 400_000
        return self.send_tx(w3_base, tx, pk)

    def run_cycling(self, w3, addr, pk, target, proxy=None):
        """
        Cycling untuk task: "Make at least N transactions (mint, stake, or bridge)"

        TX yang DIHITUNG website:
          - mint    (0.1 USDT → 0.1 T+)
          - stake   (0.1 T+   → sT+)
          - bridge  (0.1 T+   → Base Sepolia via OFT)

        TX untuk RECYCLE (tidak dihitung, tapi wajib biar cycle bisa lanjut):
          - unstake     (sT+ → T+)
          - redeem      (T+  → USDT)
          - bridge_back (T+ Base → ETH, opsional, butuh ETH di Base)

        Per cycle: hingga 3 tx valid (mint + stake + bridge).
        """
        usdt_c  = w3.eth.contract(address=USDT_CONTRACT,   abi=ERC20_ABI)
        tplus_c = w3.eth.contract(address=T_PLUS_CONTRACT, abi=ERC20_ABI)

        tx_count           = 0
        cycle              = 0
        errors             = 0
        bridged_this_cycle = False

        while tx_count < target:
            cycle    += 1
            usdt_bal  = usdt_c.functions.balanceOf(addr).call()
            tplus_bal = tplus_c.functions.balanceOf(addr).call()

            self.log(
                f"[Transaction] Cycle #{cycle}  |  Valid Tx: {tx_count}/{target}  |  "
                f"USDT: {usdt_bal/10**USDT_DECIMALS:.4f}  |  T+: {tplus_bal/10**TOKEN_DECIMALS:.6f}",
                "CYCLE",
            )

            if usdt_bal < MINT_USDT_RAW and tplus_bal < MINT_TPLUS_RAW:
                errors += 1
                self.log(f"Insufficient balance (need >= 0.1 USDT or >= 0.1 T+)  [{errors}/10]", "WARNING")
                if errors == 1:
                    try:
                        self.faucet_mint(w3, addr, pk, USDT_CONTRACT,
                                         MINT_USDT_RAW * 100, "USDT")
                        self.random_delay(3, 6)
                        continue
                    except Exception as ex:
                        self.log(f"Auto-faucet failed: {ex}", "ERROR")
                self.log("ETH Faucet  : https://cloud.google.com/application/web3/faucet/ethereum/sepolia", "WARNING")
                self.log("USDT Faucet : https://gho.aave.com/faucet/", "WARNING")
                if errors >= 10:
                    self.log("Max error limit reached.", "ERROR")
                    break
                time.sleep(60)
                continue

            bridged_this_cycle = False

            try:
                # ── Step 1: MINT 0.1 USDT → 0.1 T+  [DIHITUNG ✅] ──────────────────
                if usdt_bal >= MINT_USDT_RAW and tx_count < target:
                    h, blk, gas = self.do_mint_cycle(w3, addr, pk)
                    tx_count += 1; errors = 0
                    self.log(f"[MINT] Valid Tx: {tx_count}/{target}  Block: {blk}  "
                             f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
                    self.random_delay(5, 12)
                    tplus_bal = tplus_c.functions.balanceOf(addr).call()

                # ── Step 2: STAKE 0.1 T+ → sT+  [DIHITUNG ✅] ──────────────────────
                if tplus_bal >= MINT_TPLUS_RAW and tx_count < target:
                    h, blk, gas = self.do_stake_cycle(w3, addr, pk, MINT_TPLUS_RAW)
                    tx_count += 1; errors = 0
                    self.log(f"[STAKE] Valid Tx: {tx_count}/{target}  Block: {blk}  "
                             f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
                    self.random_delay(5, 12)
                    tplus_bal = tplus_c.functions.balanceOf(addr).call()

                # ── Step 3: BRIDGE 0.1 T+ → Base Sepolia  [DIHITUNG ✅] ─────────────
                if tplus_bal >= MINT_TPLUS_RAW and tx_count < target:
                    try:
                        h, blk, gas = self.do_bridge_cycle(w3, addr, pk)
                        if h:
                            tx_count += 1; errors = 0
                            bridged_this_cycle = True
                            self.log(f"[BRIDGE] Valid Tx: {tx_count}/{target}  Block: {blk}  "
                                     f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "SUCCESS")
                            self.random_delay(5, 12)
                            tplus_bal = tplus_c.functions.balanceOf(addr).call()
                    except Exception as ex:
                        self.log(f"[BRIDGE] Skipped: {ex}", "WARNING")

                # ── Step 4: UNSTAKE sT+ → T+  [recycle, tidak dihitung] ─────────────
                try:
                    h, blk, gas = self.do_unstake_cycle(w3, addr, pk)
                    if h:
                        errors = 0
                        self.log(f"[UNSTAKE] recycle  Block: {blk}  "
                                 f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "INFO")
                        self.random_delay(5, 12)
                        tplus_bal = tplus_c.functions.balanceOf(addr).call()
                except Exception as ex:
                    self.log(f"[UNSTAKE] Skipped: {ex}", "WARNING")

                # ── Step 5: REDEEM T+ → USDT  [recycle, tidak dihitung] ─────────────
                try:
                    tplus_bal = tplus_c.functions.balanceOf(addr).call()
                    if tplus_bal > 0:
                        h, blk, gas = self.do_redeem_cycle(w3, addr, pk, tplus_bal)
                        if h:
                            errors = 0
                            self.log(f"[REDEEM] recycle  Block: {blk}  "
                                     f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "INFO")
                            self.random_delay(5, 12)
                except Exception as ex:
                    self.log(f"[REDEEM] Skipped: {ex}", "WARNING")

                # ── Step 6: BRIDGE_BACK T+ Base → ETH  [recycle, tidak dihitung] ────
                if bridged_this_cycle:
                    try:
                        self.log("[BRIDGE_BACK] Tunggu 30s LayerZero delivery...", "INFO")
                        time.sleep(30)
                        w3_base = self.get_web3_base(proxy=proxy)
                        h, blk, gas = self.do_bridge_back_cycle(w3_base, addr, pk)
                        if h:
                            errors = 0
                            self.log(f"[BRIDGE_BACK] recycle  Block: {blk}  "
                                     f"Gas: {gas:,}  Hash: 0x{h[:16]}...", "INFO")
                            self.random_delay(10, 20)
                    except Exception as ex:
                        self.log(f"[BRIDGE_BACK] Skipped (belum tiba atau no ETH di Base): {ex}", "WARNING")

            except Exception as ex:
                errors += 1
                self.log(f"Cycle error: {ex}", "ERROR")
                if errors >= 10:
                    self.log("Too many errors.", "ERROR")
                    break
                wait = 30 * errors
                self.log(f"Retrying in {wait}s...", "WARNING")
                time.sleep(wait)
                try:
                    w3 = self.get_web3(proxy=None)
                except Exception:
                    pass

        return tx_count

    # ════════════════════════════════════════════════════════════════════════
    # ─── LOADERS ─────────────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def load_accounts(self, path="accounts.txt"):
        p = Path(path)
        if not p.exists():
            self.log(f"{path} not found!", "ERROR")
            sys.exit(1)
        keys = []
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith("0x"):
                line = "0x" + line
            try:
                Account.from_key(line)
                keys.append(line)
            except Exception as ex:
                self.log(f"Skipping invalid key {line[:10]}... : {ex}", "WARNING")
        if not keys:
            self.log("No valid private keys in accounts.txt", "ERROR")
            sys.exit(1)
        return keys

    def load_addresses(self, path="address.txt"):
        p = Path(path)
        if not p.exists():
            self.log(f"{path} not found. Create address.txt for send tasks.", "WARNING")
            return []
        addrs = []
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                addrs.append(Web3.to_checksum_address(line))
            except Exception:
                self.log(f"Skipping invalid address: {line[:20]}...", "WARNING")
        self.log(f"Loaded {len(addrs)} recipient addresses", "SUCCESS")
        return addrs

    def load_proxies(self, path="proxy.txt"):
        p = Path(path)
        if not p.exists():
            return []
        proxies = []
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith(("http://", "https://", "socks5://")):
                line = "http://" + line
            proxies.append(line)
        return proxies

    # ════════════════════════════════════════════════════════════════════════
    # ─── run_account ─────────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def run_account(self, pk, acc_idx, acc_total, all_accounts, send_addresses, proxy=None):
        w3      = self.get_web3(proxy=proxy)
        account = Account.from_key(pk)
        addr    = account.address

        proxy_display = (proxy[:40] + "...") if proxy and len(proxy) > 40 else (proxy or "No Proxy")
        self.log(f"Account #{acc_idx}/{acc_total}", "INFO")
        self.log(f"Proxy  : {proxy_display}", "INFO")
        self.log(f"Address: {addr}", "INFO")

        # Print semua balances
        balances = self.read_all_balances(w3, addr)
        self.print_balances(balances)

        if balances["ETH"][1] < 0.001:
            self.log("ETH balance very low! Gas may be insufficient.", "WARNING")
            self.log("Faucet: https://cloud.google.com/application/web3/faucet/ethereum/sepolia", "WARNING")

        # Tampilkan total poin dan status early user
        total_pts = self.fetch_points(addr, pk, proxy=proxy)
        self.log(f"Total Points  : {total_pts:,}", "INFO")

        eu_status = self.fetch_earlyuser_status(addr, proxy=proxy)
        if eu_status:
            self.log(f"Early User    : {eu_status}", "INFO")

        # Fetch & print tasks
        tasks = self.fetch_tasks(addr, pk, proxy=proxy)
        self.print_tasks(tasks)

        if not tasks:
            self.log("No tasks to execute today.", "INFO")
            return 0

        # Auto topup
        try:
            self.prepare_materials(w3, addr, pk, tasks)
        except Exception as ex:
            self.log(f"prepare_materials error: {ex}  (continuing)", "WARNING")
        self.random_delay(3, 6)

        # Execute tasks
        total_tx  = 0
        tx_target = 43

        for task in tasks:
            t_type    = task["type"]
            t_product = task.get("product", "usdt")
            t_amount  = task["amount"]
            t_desc    = task["description"]

            self.log(f"Executing: [{t_type.upper()}] {t_desc}", "INFO")

            try:
                if t_type == "mint":
                    h, blk, gas = self.exec_mint(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "stake":
                    h, blk, gas = self.exec_stake(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "unstake":
                    h, blk, gas = self.exec_unstake(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "redeem":
                    h, blk, gas = self.exec_redeem(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "bridge":
                    h, blk, gas = self.exec_bridge(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "bridge_back":
                    try:
                        w3_base = self.get_web3_base(proxy=proxy)
                        h, blk, gas = self.exec_bridge_back(w3_base, addr, pk, task)
                        if h: total_tx += 1
                    except Exception as ex:
                        self.log(f"[BridgeBack] Failed: {ex}", "ERROR")
                    self.random_delay(4, 8)

                elif t_type == "send":
                    if send_addresses:
                        to_addr = send_addresses[(acc_idx - 1) % len(send_addresses)]
                        h, blk, gas = self.exec_send(w3, addr, pk, task, to_addr)
                        if h: total_tx += 1
                    else:
                        self.log("[Send] No addresses in address.txt. Skipped.", "WARNING")
                    self.random_delay(4, 8)

                elif t_type == "receive":
                    h, blk, gas = self.exec_receive(w3, addr, pk, task, all_accounts)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "swap":
                    h, blk, gas = self.exec_swap(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type in ("liquidity_add", "add_liquidity"):
                    h, blk, gas = self.exec_liquidity_add(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type in ("liquidity_remove", "remove_liquidity"):
                    h, blk, gas = self.exec_liquidity_remove(w3, addr, pk, task)
                    if h: total_tx += 1
                    self.random_delay(4, 8)

                elif t_type == "transaction":
                    tx_target = t_amount
                    self.log(f"[Transaction] Daily cycling target: {tx_target} txs", "INFO")
                    n = self.run_cycling(w3, addr, pk, target=tx_target, proxy=proxy)
                    total_tx += n
                    if n >= tx_target:
                        self.log(f"[Transaction] Target {tx_target} txs reached! ({n} done)", "SUCCESS")
                    else:
                        self.log(f"[Transaction] {n}/{tx_target} txs completed.", "WARNING")

                else:
                    self.log(f"Unknown task type '{t_type}' — skipped. "
                             f"Report to developer for support.", "WARNING")
                    self.log(f"  Full task data: {task}", "WARNING")

            except Exception as ex:
                self.log(f"[{t_type.upper()}] Error: {ex}", "ERROR")
                self.random_delay(5, 10)

        self.log(f"Account done!  Total Tx: {total_tx}  |  {addr[:10]}...", "SUCCESS")
        return total_tx

    # ════════════════════════════════════════════════════════════════════════
    # ─── MAIN RUN ─────────────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════

    def run(self):
        self.print_banner()

        choice    = self.show_menu()
        use_proxy = choice == "1"
        self.log("Running with proxy" if use_proxy else "Running without proxy", "INFO")

        self.log("Connecting to Ethereum Sepolia...", "INFO")
        w3 = self.get_web3()
        self.log(
            f"Connected!  Chain ID: {w3.eth.chain_id}  |  "
            f"Block: #{w3.eth.block_number:,}  |  Gas: {w3.eth.gas_price/10**9:.3f} Gwei",
            "SUCCESS",
        )

        # Print semua contract yang digunakan
        self.log("── Contract Addresses ─────────────────────────────────────", "INFO")
        self.log(f"  [ETH Sepolia]", "INFO")
        self.log(f"  USDT          : {USDT_CONTRACT}", "INFO")
        self.log(f"  USDC          : {USDC_CONTRACT}", "INFO")
        self.log(f"  aUSDT (Aave)  : {AUSDT_CONTRACT}", "INFO")
        self.log(f"  aUSDC (Aave)  : {AUSDC_CONTRACT}", "INFO")
        self.log(f"  T+            : {T_PLUS_CONTRACT}", "INFO")
        self.log(f"  sT+           : {ST_PLUS_CONTRACT}", "INFO")
        self.log(f"  C+            : {C_PLUS_CONTRACT}", "INFO")
        self.log(f"  sC+           : {SC_PLUS_CONTRACT}", "INFO")
        self.log(f"  Backing USDT  : {BACKING_USDT_CONTRACT}", "INFO")
        self.log(f"  Backing USDC  : {BACKING_USDC_CONTRACT}", "INFO")
        self.log(f"  POINTS/pOVA   : {POINTS_CONTRACT}", "INFO")
        self.log(f"  LP Token      : {LP_CONTRACT}", "INFO")
        self.log(f"  OVA NFT       : {OVA_NFT_CONTRACT}", "INFO")
        self.log(f"  Galxe NFT     : {GALXE_NFT_CONTRACT}", "INFO")
        self.log(f"  Faucet        : {FAUCET_CONTRACT}", "INFO")
        self.log(f"  Multicall3    : {MULTICALL3_CONTRACT}", "INFO")
        self.log(f"  [Base Sepolia]", "INFO")
        self.log(f"  T+ Base       : {T_PLUS_BASE_CONTRACT}", "INFO")
        self.log(f"  sT+ Base      : {ST_PLUS_BASE_CONTRACT}", "INFO")
        self.log(f"  C+ Base       : {C_PLUS_BASE_CONTRACT}", "INFO")
        self.log(f"  sC+ Base      : {SC_PLUS_BASE_CONTRACT}", "INFO")
        self.log(f"  [LayerZero EIDs]", "INFO")
        self.log(f"  ETH Sepolia   : {LZ_EID_ETH_SEPOLIA}", "INFO")
        self.log(f"  Base Sepolia  : {LZ_EID_BASE_SEPOLIA}", "INFO")
        self.log(f"  [API] {API_BASE}", "INFO")

        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

        accounts       = self.load_accounts("accounts.txt")
        send_addresses = self.load_addresses("address.txt")
        proxies        = self.load_proxies("proxy.txt") if use_proxy else []

        self.log(f"Loaded {len(accounts)} accounts", "INFO")
        if use_proxy:
            self.log(f"Loaded {len(proxies)} proxies" if proxies else
                     "proxy.txt empty, running without proxy.", "INFO" if proxies else "WARNING")

        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

        loop = 1
        while True:
            self.log(f"Cycle #{loop} Started  |  {len(accounts)} Accounts", "CYCLE")
            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")

            success_count = 0
            total_tx      = 0

            for i, pk in enumerate(accounts):
                addr  = Account.from_key(pk).address
                proxy = proxies[i % len(proxies)] if proxies else None

                n = 0
                try:
                    n = self.run_account(
                        pk, i + 1, len(accounts),
                        all_accounts=accounts,
                        send_addresses=send_addresses,
                        proxy=proxy,
                    )
                    total_tx      += n
                    success_count += 1
                except Exception as ex:
                    self.log(f"Fatal error {addr[:10]}... : {ex}", "ERROR")

                if i < len(accounts) - 1:
                    print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                    delay = random.randint(10, 30)
                    self.log(f"Waiting {delay}s before next account...", "INFO")
                    time.sleep(delay)

            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
            self.log(
                f"Cycle #{loop} Complete  |  Accounts: {success_count}/{len(accounts)}  |  Total Tx: {total_tx}",
                "CYCLE",
            )
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

            loop += 1
            self.countdown(86400)


if __name__ == "__main__":
    try:
        bot = OverlayerBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[STOPPED] Bot stopped by user.{Style.RESET_ALL}\n")
