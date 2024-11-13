from web3 import Web3
import time

# Koneksi ke node Taiko Mainnet menggunakan Ankr RPC
taiko_rpc_url = "https://rpc.ankr.com/taiko"
web3 = Web3(Web3.HTTPProvider(taiko_rpc_url))

# Verifikasi koneksi
if not web3.is_connected():
    print("Tidak dapat terhubung ke jaringan Taiko.")
    exit()

# Ambil private key dari variabel lingkungan
private_key = "PRIVATE"  # Ganti dengan private key Anda
my_address = Web3.to_checksum_address("ALAMAT")  # Alamat dompet Anda

# Alamat kontrak voting yang diberikan
vote_contract_address = Web3.to_checksum_address("0x4D1E2145082d0AB0fDa4a973dC4887C7295e21aB")  # Alamat kontrak voting

# ABI untuk fungsi vote
vote_abi = '''
[
    {
        "constant": false,
        "inputs": [],
        "name": "vote",
        "outputs": [],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
'''

# Inisialisasi kontrak voting
vote_contract = web3.eth.contract(address=vote_contract_address, abi=vote_abi)

# Fungsi untuk mendapatkan nonce berikutnya
def get_next_nonce():
    return web3.eth.get_transaction_count(my_address)

# Fungsi untuk memeriksa konfirmasi transaksi
def wait_for_confirmation(tx_hash, timeout=300):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt and receipt['status'] == 1:
                print(f"Status: Transaksi {web3.to_hex(tx_hash)} berhasil dikonfirmasi.")
                return True
            elif receipt and receipt['status'] == 0:
                print(f"Status: Transaksi {web3.to_hex(tx_hash)} gagal.")
                return False
        except Exception as e:
            pass  # Tidak mencetak error untuk status transaksi
        time.sleep(30)  # Tunggu 30 detik sebelum memeriksa lagi
    print(f"Status: Timeout menunggu konfirmasi untuk transaksi {web3.to_hex(tx_hash)}.")
    return False

# Fungsi untuk melakukan voting (EIP-1559)
def vote():
    nonce = get_next_nonce()

    # Estimasi gas
    gas_estimate = web3.eth.estimate_gas({
        'to': vote_contract_address,
        'data': '0x632a9a52'  # MethodID untuk fungsi vote()
    })

    # Tentukan gas price dalam Gwei
    gas_price_gwei = 0.2  # Tentukan gas price yang sesuai (dalam Gwei)
    max_priority_fee_per_gas = web3.to_wei(gas_price_gwei, 'gwei')
    max_fee_per_gas = web3.to_wei(gas_price_gwei, 'gwei')  # Set ke nilai maksimum yang sama dengan priority fee

    # Menyusun transaksi dengan EIP-1559
    transaction = {
        'to': vote_contract_address,
        'chainId': 167000,  # Chain ID Taiko Mainnet
        'gas': gas_estimate,
        'maxFeePerGas': max_fee_per_gas,
        'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'nonce': nonce,
        'data': '0x632a9a52',  # MethodID untuk fungsi vote
        'type': 2  # Jenis transaksi EIP-1559
    }

    # Tandatangani transaksi
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    try:
        # Kirim transaksi
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"\nStatus: Voting berhasil dikirim.")
        print(f"Tx Hash: {web3.to_hex(tx_hash)}")

        # Tunggu konfirmasi transaksi
        if wait_for_confirmation(tx_hash):
            print("Voting berhasil dikonfirmasi.")
            return True
    except Exception as e:
        print(f"Error saat mengirim transaksi voting: {e}")
    return False

# Panggil fungsi vote
if vote():
    print("Voting berhasil dilakukan!")
else:
    print("Voting gagal!")
