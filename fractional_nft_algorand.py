########## Module imports ##########
from algosdk import account
from algosdk.v2client import algod
from algosdk import transaction
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner, AccountTransactionSigner
##########


############################## Required Functions ############################################################

########## Function to connect to testnet ##########


def connect_to_algorand():
    # Algorand Testnet connection parameters
    ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
    ALGOD_TOKEN = ""  # No token is needed for the public Algorand Testnet

    # Establishing connection to the Algorand Testnet
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

########## Function to Create ASA ##########


def create_asa(creator_private_key, creator_address, algod_client):

    # Get the suggested transaction parameters from the network
    params = algod_client.suggested_params()

    # Construct the ASA creation transaction with the parameters provided
    txn = transaction.AssetConfigTxn(
        # The address creating the UCTZAR and responsible for signing the transaction.
        sender=creator_address,
        sp=params,
        total=100,  # The single NFT can be divided into 100 shares
        # Should be equal to the logarithm (base 10) of the total number of units as per algorand fractional NFT standards
        decimals=2,
        default_frozen=False,
        unit_name="FNFT",
        asset_name="FNFT",
        manager=creator_address,
        reserve=None,  # No reserve address
        freeze=None,   # No freeze address
        clawback=None,  # No clawback address
        # Allow empty addresses for reserve, freeze, and clawback
        strict_empty_address_check=False
    )

    # Sign the transaction with the creator's private key
    signed_txn = txn.sign(creator_private_key)

    # Send the transaction to the Algorand network
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent NFT creation transaction with txID: {txid}")

    # Wait for the transaction to be confirmed by the network
    try:
        confirmed_txn = transaction.wait_for_confirmation(
            algod_client, txid, 4)
        print("Asset-Creation creation successful.")
        print(f"Asset ID: {confirmed_txn['asset-index']}")
        return confirmed_txn['asset-index']
    except Exception as e:
        print("An error occurred while confirming the NFT creation transaction.")
        print(e)
        return None

########## Function to Opt in to ASA ##########


def opt_in_to_asa(account_private_key, account_address, asset_id, algod_client):
    # Get the suggested transaction parameters
    params = algod_client.suggested_params()

    # Create an asset transfer transaction with amount 0 - this is the opt-in transaction
    txn = transaction.AssetTransferTxn(
        sender=account_address,
        sp=params,
        receiver=account_address,
        amt=0,
        index=asset_id  # The ID of the ASA to opt in to
    )

    # Sign the transaction
    signed_txn = txn.sign(account_private_key)

    # Submit the transaction
    txid = algod_client.send_transaction(signed_txn)
    print(
        f"Sent opt-in transaction for ASA (Asset ID: {asset_id}) with txID: {txid}")

    # Wait for confirmation
    try:
        txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Opt-in to ASA (Asset ID: {asset_id}) successful.")
    except Exception as e:
        print(
            f"An error occurred while confirming the opt-in transaction for ASA (Asset ID: {asset_id}).")
        print(e)

    return txid

########## Function to send ASA ##########


def send_nft(sender_private_key, sender_address, receiver_address, asset_id, algod_client):

    # Get the suggested transaction parameters
    params = algod_client.suggested_params()

    # Create an asset transfer transaction
    txn = transaction.AssetTransferTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        # Since the decimals are 1, this is the smallest unit of the asset thus the 1 here actually represents a fraction of 0.1
        amt=10,  # Send 10 out of the 100 shares which represents a 0.1 fraction
        index=asset_id  # The ID of the ASA (NFT) to send
    )

    # Sign the transaction
    signed_txn = txn.sign(sender_private_key)

    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent NFT transfer transaction with txID: {txid}")

    # Wait for confirmation
    try:
        txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(
            f"Transfer of NFT (Asset ID: {asset_id}) to {receiver_address} successful.")
    except Exception as e:
        print(
            f"An error occurred while confirming the NFT transfer transaction for ASA (Asset ID: {asset_id}).")
        print(e)
        return None

    return txid

########## Function to Check accounts for fractional NFT and list balances if present ##########


def nft_existance_checker(account_address, fractional_nft_asset_id, algod_client):
    try:
        # Fetch account information
        account_info = algod_client.account_info(account_address)

        # Check if account has the specified fractional NFT
        assets = account_info.get('assets', [])
        nft_found = any(asset['asset-id'] ==
                        fractional_nft_asset_id for asset in assets)

        if nft_found:
            # Find the fractional NFT and get its balance
            nft_balance = next(
                asset['amount'] for asset in assets if asset['asset-id'] == fractional_nft_asset_id)
            print(
                f"{account_address} holds {nft_balance} units of the fractional NFT (Asset ID: {fractional_nft_asset_id}).")
        else:
            print(
                f"{account_address} does not hold any units of the fractional NFT (Asset ID: {fractional_nft_asset_id}).")

    except Exception as e:
        print(
            f"An error occurred while checking for fractional NFT holdings for {account_address}.")
        print(e)


########################################################################################################################

############################## Execution of functions ##############################

###### Required Accounts ######

# NFT creator account
NFT_Creator_address = "J4NQXH3IGGJGHNVMMF6DUJQSIQ5BBJXIEG7O7U4A5CADT4SUW2UJ3Y63AA"
NFT_Creator_private_key = "RmUJaC7bipx4vLP+p39qJJVTo+RytTq87Y5LzIFsJy5PGwufaDGSY7asYXw6JhJEOhCm6CG+79OA6IA58lS2qA=="

# NFT reciever account 1
NFT_reciever_address_1 = "VEEGL5IIFRY5MC6BJWBHF5ZPR2EIHECV42JJEVNLM6Z55AZK6QGKVKH4MM"
NFT_reciever_private_key_1 = "91Od0BoMe+93wqEnrCN5fbORyADjP6x8SLGpk2pf8W2pCGX1CCxx1gvBTYJy9y+OiIOQVeaSklWrZ7Pegyr0DA=="

# NFT reciever account 2
NFT_reciever_address_2 = "WQDGOPSBBSWGT7R3Z3XX7KGRRPEQR5SVJOHHBLMHYZLJJNJGWFMOB667SI"
NFT_reciever_private_key_2 = "HkIY8rQYG2jABRRZrElRjXcz3uhK0rhg2moZ3nfBU8e0Bmc+QQysaf47zu9/qNGLyQj2VUuOcK2HxlaUtSaxWA=="

# NFT reciever account 3
NFT_reciever_address_3 = "NPA72YU25AOFJSF4ZKLDQ3LINSFLZB662XZGW2PFUCM6BOLEQAXGMV4M2Y"
NFT_reciever_private_key_3 = "OrESkgDYJ0/OxntgY+we5WU6Hnd+V7sRy3GXXKthTUNrwf1imugcVMi8ypY4bWhsiryH3tXya2nloJnguWSALg=="
######


# Connect to testnet
algod_client = connect_to_algorand()

# create ASA and extract asset ID
asset_id_asa = create_asa(NFT_Creator_private_key,
                          NFT_Creator_address, algod_client)

# Check for existance of Fractional NFT and if present list amount
nft_existance_checker(NFT_reciever_address_1, asset_id_asa, algod_client)
nft_existance_checker(NFT_reciever_address_2, asset_id_asa, algod_client)
nft_existance_checker(NFT_reciever_address_3, asset_id_asa, algod_client)

# Reciever 1 opt-in to ASA referncing the asset by asset ID
opt_in_to_asa(NFT_reciever_private_key_1,
              NFT_reciever_address_1, asset_id_asa, algod_client)

# Reciever 2 opt-in to ASA referncing the asset by asset ID
opt_in_to_asa(NFT_reciever_private_key_2,
              NFT_reciever_address_2, asset_id_asa, algod_client)

# Reciever 3 opt-in to ASA referncing the asset by asset ID
opt_in_to_asa(NFT_reciever_private_key_3,
              NFT_reciever_address_3, asset_id_asa, algod_client)

# Send NFT fraction to reciever 1
send_nft(NFT_Creator_private_key, NFT_Creator_address,
         NFT_reciever_address_1, asset_id_asa, algod_client)

# Send NFT fraction to reciever 2
send_nft(NFT_Creator_private_key, NFT_Creator_address,
         NFT_reciever_address_2, asset_id_asa, algod_client)

# Send NFT fraction to reciever 3
send_nft(NFT_Creator_private_key, NFT_Creator_address,
         NFT_reciever_address_3, asset_id_asa, algod_client)


# Check for existance of Fractional NFT and if present list amount
nft_existance_checker(NFT_reciever_address_1, asset_id_asa, algod_client)
nft_existance_checker(NFT_reciever_address_2, asset_id_asa, algod_client)
nft_existance_checker(NFT_reciever_address_3, asset_id_asa, algod_client)
