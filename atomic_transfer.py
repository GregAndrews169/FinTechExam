import json
from algosdk import account
from algosdk.v2client import algod
from algosdk import transaction


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


########################################################################################################################

############################## Create Account ##############################


# Connect to testnet
algod_client = connect_to_algorand()

# Create first account and store keys
private_key1 = "D5EQEWcJRSagWewKAae37ij1nnwGJYEzT2DNglGjKs/aVpbQm1DbSByGKmoA0vyJ2PkMaDJRnsPHVeYgOo7g/w=="
address1 = "3JLJNUE3KDNUQHEGFJVABUX4RHMPSDDIGJIZ5Q6HKXTCAOUO4D73HBZSQ4"

# Create second account and store keys
private_key2 = "5RKL4PVVI6HTPDFDQRCHIIE63YU7X4CS5MFAGIQI42YZZWY2TITOEFZLZI"
address2 = "5RKL4PVVI6HTPDFDQRCHIIE63YU7X4CS5MFAGIQI42YZZWY2TITOEFZLZI"

# Send from account 1 to account two
send_transaction(private_key1, address1, address2, 1000000, algod_client)

# Check blance on account1
check_account_balance(address1, algod_client)

# Check blance on account2
check_account_balance(address2, algod_client)
