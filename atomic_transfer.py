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

########## Function to Create Account ##########


def create_account():
    # Generate a new account
    private_key, address = account.generate_account()

    # Output the address and private key for the account
    print("Your new account address:", address)
    print("Your private key:", private_key)

    return private_key, address

########## Function to Create UCTZAR ##########


def create_asa(creator_private_key, creator_address, algod_client):

    # Get the suggested transaction parameters from the network
    params = algod_client.suggested_params()

    # UCTZAR creation transaction
    txn = transaction.AssetConfigTxn(

        # The address creating the UCTZAR and responsible for signing the transaction.
        sender=creator_address,
        sp=params,
        total=10,  # Total supply of UCTZAR
        decimals=2,
        default_frozen=False,  # Asset should not be frozen
        unit_name="UCTZAR",
        asset_name="UCTZAR",
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
    print(f"Sent UCTZAR creation transaction with txID: {txid}")

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
        sender=account_address,  # This is the account opting in
        sp=params,
        receiver=account_address,  # This is the account opting in
        amt=0,
        index=asset_id  # The ID of the ASA to opt in to
    )

    # Sign the transaction
    signed_txn = txn.sign(account_private_key)

    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)
    print(
        f"Sent opt-in transaction for UCTZAR (Asset ID: {asset_id}) with txID: {txid}")

    # Wait for confirmation
    try:
        txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print(f"Opt-in to ASA (Asset ID: {asset_id}) successful.")
    except Exception as e:
        print(
            f"An error occurred while confirming the opt-in transaction for ASA (Asset ID: {asset_id}).")
        print(e)

    return txid

########## Function to list UCTZAR and Algo balances for a specific account ##########


def list_assets_and_balances(account_address, specific_asset_id, algod_client):
    try:
        # Fetch account information
        account_info = algod_client.account_info(account_address)

        # Get Algos balance
        algos_balance = account_info.get('amount', 0)
        print(f" - ALGO: Balance {algos_balance / 1e6} ")

        # Check if account has the specific asset (UZTZAR)
        assets = account_info.get('assets', [])
        asset_found = False
        for asset in assets:
            if asset['asset-id'] == specific_asset_id:
                asset_balance = asset['amount']
                print(
                    f" - UCTZAR: Balance {asset_balance}")
                asset_found = True
                break

        if not asset_found:
            print(
                f"No balance for Asset ID {specific_asset_id} held by this account.")

    except Exception as e:
        print("An error occurred while fetching account information.")
        print(e)

########## Function to Perform atomic transfer between the two accounts ##########


def atomic_transfer(algod_client, sender_a_private_key, sender_a_address, sender_b_private_key, sender_b_address, asa_id):
    # Create an Atomic Transaction Composer
    atc = AtomicTransactionComposer()

    # Set up transaction signers for each sender
    signer_a = AccountTransactionSigner(sender_a_private_key)
    signer_b = AccountTransactionSigner(sender_b_private_key)

    # Fetch the suggested transaction parameters
    params = algod_client.suggested_params()

    # Transaction1 : 5 Algos send from account A to account B
    tx1 = transaction.PaymentTxn(
        sender=sender_a_address,
        sp=params,
        receiver=sender_b_address,
        amt=5000000  # 5 Algos = 5000000 MicoAlgos
    )

    # Transaction1 : 2 UCTZAR send from account B to account A
    tx2 = transaction.AssetTransferTxn(
        sender=sender_b_address,
        sp=params,
        receiver=sender_a_address,
        amt=2,
        index=asa_id
    )

    # Wrap transactions with signers
    tws1 = TransactionWithSigner(tx1, signer_a)
    tws2 = TransactionWithSigner(tx2, signer_b)

    # Add transactions to the composer
    atc.add_transaction(tws1)
    atc.add_transaction(tws2)

    try:
        # Execute the atomic group of transactions
        result = atc.execute(algod_client, 4)
        print("Atomic transaction successful. Transaction IDs:")
        for tx_id in result.tx_ids:
            print(tx_id)
        return result.tx_ids
    except Exception as e:
        print("An error occurred during the atomic transfer:", e)
        return None
########################################################################################################################


############################## Execution of functions ##############################

# Note: Use create_account() function to generate the two accounts
#       The first account must be funded with test Algos using an Algorand Faucet to allow for the Algo transfer and cover associated transaction fees
#       The second account must be funded with test Algos using an Algorand Faucet to ensure it can cover the transaction fee to to create the ASA and other assocaited transaction fees

# Account A: Sender of Algos and Reciever of UCTZAR
private_key1 = "wS7Wqa6WB61A4cVC6TrLXoemInJ/6RszmU5byuum65flRlHOTaFpkMiVPDiYeofj9hn30O8mnIjpq0rrh8SzKA=="
address1 = "4VDFDTSNUFUZBSEVHQ4JQ6UH4P3BT56Q54TJZCHJVNFOXB6EWMUBDCCVQY"

# Account B: Creator and sender of UCTZAR; Reciever of Algos
private_key2 = "PVSo4eVFkkRhV3ZAOiWvIOOOIp6zDICje55xG92U4+ECLiPkcOw4wXlOpU2XAKiyzaAC8u2FvuBFU+BcyltTHg=="
address2 = "AIXCHZDQ5Q4MC6KOUVGZOAFIWLG2AAXS5WC35YCFKPQFZSS3KMPDQZTPYU"

# Connect to testnet
algod_client = connect_to_algorand()

# create UCTZAR and extract asset ID
asset_id_asa = create_asa(private_key2, address2, algod_client)

# opt-in to UCTZAR referncing the asset by asset ID
opt_in_to_asa(private_key1, address1, asset_id_asa, algod_client)

# List ALGOs and UCTZAR assocaited balances of each account prior to the atomic transfer
list_assets_and_balances(address1, asset_id_asa, algod_client)
list_assets_and_balances(address2, asset_id_asa, algod_client)

# Perform atomic transfer
atomic_transfer(algod_client, private_key1, address1,
                private_key2, address2, asset_id_asa)

# List ALGOs and UCTZAR assocaited balances of each account prior to the atomic transfer
list_assets_and_balances(address1, asset_id_asa, algod_client)
list_assets_and_balances(address2, asset_id_asa, algod_client)

############################## End ##############################
