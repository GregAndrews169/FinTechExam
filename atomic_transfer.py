from algosdk import account
from algosdk.v2client import algod
from algosdk import transaction
from algosdk.atomic_transaction_composer import AtomicTransactionComposer, TransactionWithSigner, AccountTransactionSigner


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

    # Output the address, private key, and mnemonic for the account
    print("Your new account address:", address)
    print("Your private key:", private_key)

    return private_key, address

########## Function to Send Algos from One Account to Another ##########


def send_transaction(sender_private_key, sender_address, receiver_address, amount, algod_client):
    # Get the suggested transaction parameters
    params = algod_client.suggested_params()

    # Create a payment transaction
    txn = transaction.PaymentTxn(
        sender=sender_address,
        sp=params,
        receiver=receiver_address,
        amt=amount
    )

    # Sign the transaction
    signed_txn = txn.sign(sender_private_key)

    # Send the transaction
    txid = algod_client.send_transaction(signed_txn)
    print(f"Sent transaction with txID: {txid}")

    # Wait for confirmation
    try:
        txn_result = transaction.wait_for_confirmation(algod_client, txid, 4)
        print("Transaction successful.")
    except Exception as e:
        print("An error occurred while confirming the transaction.")
        print(e)

    return txid, txn_result

########## Function to Check Account Balance ##########


def check_account_balance(address, algod_client):
    # Get account information
    account_info = algod_client.account_info(address)

    # Get the amount of Algos in the account
    balance = account_info.get('amount')
    print(f"Account balance of {address}: {balance} microAlgos")

    return balance

########## Function to Create ASA ##########


def create_asa(creator_private_key, creator_address, algod_client):

    # Get the suggested transaction parameters from the network
    params = algod_client.suggested_params()

    # Construct the ASA creation transaction with the parameters provided
    txn = transaction.AssetConfigTxn(
        # The address creating the UCTZAR and responsible for signing the transaction.
        sender=creator_address,
        sp=params,
        total=15,
        decimals=2,
        default_frozen=False,
        unit_name="UCTZAR",  # Example unit name, change as needed
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

    # Send the transaction
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

########## Function to List all assets ##########


def list_assets_and_balances(account_address, algod_client):
    try:
        # Fetch account information
        account_info = algod_client.account_info(account_address)

        # Get Algos balance
        algos_balance = account_info.get('amount')
        # Convert microAlgos to Algos
        print(f"Algos balance: {algos_balance / 1e6} Algos")

        # Check if account has other assets
        if 'assets' in account_info:
            assets = account_info['assets']
            if assets:
                print(f"Assets held by {account_address}:")
                for asset in assets:
                    asset_id = asset['asset-id']
                    asset_balance = asset['amount']
                    print(f" - Asset ID {asset_id}: Balance {asset_balance}")
            else:
                print("No other assets held by this account.")
        else:
            print("No assets information available for this account.")

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

    # Transaction A -> B: Algos
    tx1 = transaction.PaymentTxn(
        sender=sender_a_address,
        sp=params,
        receiver=sender_b_address,
        amt=5000000
    )

    # Transaction B -> A: UCTZAR ASA
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

    # Execute the atomic group of transactions
    result = atc.execute(algod_client, 4)

    # Return transaction IDs
    return result.tx_ids  # If result.tx_ids is a list of txid strings
########################################################################################################################


############################## Execution of functions ##############################
# Connect to testnet
algod_client = connect_to_algorand()

# Create first account and store keys
private_key1 = "D5EQEWcJRSagWewKAae37ij1nnwGJYEzT2DNglGjKs/aVpbQm1DbSByGKmoA0vyJ2PkMaDJRnsPHVeYgOo7g/w=="
address1 = "3JLJNUE3KDNUQHEGFJVABUX4RHMPSDDIGJIZ5Q6HKXTCAOUO4D73HBZSQ4"

# Create second account and store keys
private_key2 = "l0P1ZO9Z/fSScQ5kjJAcU4vDPABOIfAJfm3aS5LeSlaFqQdAc24JFKtwMqMMi3ENpqpntFoEXnPzoDRXqqqOrA=="
address2 = "QWUQOQDTNYERJK3QGKRQZC3RBWTKUZ5ULICF447TUA2FPKVKR2WDGHITZM"

# Send from account 1 to account two
# send_transaction(private_key1, address1, address2, 1000000, algod_client)

# Check blance on account1
# check_account_balance(address1, algod_client)

# Check blance on account2
# check_account_balance(address2, algod_client)

# create ASA and extract asset ID
# asset_id_asa = create_asa(private_key2, address2, algod_client)
asset_id_asa = "480159984"

# opt-in to ASA
# opt_in_to_asa(private_key1, address1, asset_id_asa, algod_client)

list_assets_and_balances(address1, algod_client)

list_assets_and_balances(address2, algod_client)

atomic_transfer(algod_client, private_key1, address1,
                private_key2, address2, asset_id_asa)

list_assets_and_balances(address1, algod_client)

list_assets_and_balances(address2, algod_client)
