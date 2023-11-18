# ECO5037S - Fintech and Cryptocurrencies Final Exam Code Implementation 

This repository contains the Python scripts developed by Gregory Raymond Andrews for the coding component of the ECO5037S exam 2023 with the University of Cape Town. It showcases practical implementations of atomic transfers and fractional NFT management on the Algorand blockchain.

## Overview

The repository includes two primary scripts:

- `atomic_transfer.py`
- `fractional_nft_algorand.py`

These scripts demonstrate intricate functionalities of the Algorand blockchain, including asset creation, opt-in transactions, atomic transfers, and the handling of fractional non-fungible tokens (NFTs).

## Scripts Description

### atomic_transfer.py

This script illustrates an atomic transfer involving two accounts (Account A and Account B) with the following key actions:

- **ASA Creation**: Account B initiates an Algorand Standard Asset (ASA) creation for the asset named 'UCTZAR'.
- **Opt-in Transaction**: Account A opts into the UCTZAR asset.
- **Atomic Transfer**: Executes a simultaneous transaction where Account A sends 5 Algos to Account B, and in return, Account B sends 2 UCTZAR to Account A.
- **Balance Verification**: Checks the balances of the assets before and after the transaction to confirm the proper execution and settlement.

### fractional_nft_algorand.py

This script focuses on the creation and distribution of a fractional NFT. The process involves four accounts, with one being the creator and the others as recipients:

- **Fractional NFT Creation**: The NFT creator account establishes a fractional NFT divided into 100 units, thus if the full NFT is 1, the smallest fraction that can be sent is 0.01.
- **Opt-in Transactions**: Three recipient accounts opt into the fractional NFT asset.
- **NFT Distribution**: Each account receives 10 units, equating to a 0.1 fraction of the entire NFT.
- **Balance Assessment**: Conducts pre- and post-transfer checks for each account. If an account holds a fraction of the NFT, it prints the account address and the fractional balance. If not, it prints the account address and displays a message indicating the absence of the fractional NFT.

## Installation

Before executing the scripts, install the required Algorand Python SDK:

```bash
pip3 install py-algorand-sdk
```

## Usage

To run the scripts, use the following commands in your terminal within the repository's directory:

For `atomic_transfer.py`:

```bash
python3 atomic_transfer.py
For fractional_nft_algorand.py:
```

For `fractional_nft_algorand.py`:

```bash
python3 fractional_nft_algorand.py
```
