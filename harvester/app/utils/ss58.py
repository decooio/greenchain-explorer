#  Polkascan PRE Harvester
#
#  Copyright 2018-2020 openAware BV (NL).
#  This file is part of Polkascan.
#
#  Polkascan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Polkascan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Polkascan. If not, see <http://www.gnu.org/licenses/>.
#
#  ss58.py

""" SS58 is a simple address format designed for Substrate based chains.
    Encoding/decoding according to specification on https://wiki.parity.io/External-Address-Format-(SS58)

"""
import base58
from hashlib import blake2b
from typing import Optional, Union

from scalecodec import ScaleBytes
from scalecodec.types import U8, U16, U32, U64


def ss58_decode(address: str, valid_ss58_format: Optional[int] = None) -> str:
    """
    Decodes given SS58 encoded address to an account ID
    Parameters
    ----------
    address: e.g. EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk
    valid_ss58_format

    Returns
    -------
    Decoded string AccountId
    """

    # Check if address is already decoded
    if address.startswith('0x'):
        return address

    if address == '':
        raise ValueError("Empty address provided")

    checksum_prefix = b'SS58PRE'

    address_decoded = base58.b58decode(address)

    if address_decoded[0] & 0b0100_0000:
        ss58_format_length = 2
        ss58_format = ((address_decoded[0] & 0b0011_1111) << 2) | (address_decoded[1] >> 6) | \
                      ((address_decoded[1] & 0b0011_1111) << 8)
    else:
        ss58_format_length = 1
        ss58_format = address_decoded[0]

    if ss58_format in [46, 47]:
        raise ValueError(f"{ss58_format} is a reserved SS58 format")

    if valid_ss58_format is not None and ss58_format != valid_ss58_format:
        raise ValueError("Invalid SS58 format")

    # Determine checksum length according to length of address string
    if len(address_decoded) in [3, 4, 6, 10]:
        checksum_length = 1
    elif len(address_decoded) in [5, 7, 11, 34 + ss58_format_length, 35 + ss58_format_length]:
        checksum_length = 2
    elif len(address_decoded) in [8, 12]:
        checksum_length = 3
    elif len(address_decoded) in [9, 13]:
        checksum_length = 4
    elif len(address_decoded) in [14]:
        checksum_length = 5
    elif len(address_decoded) in [15]:
        checksum_length = 6
    elif len(address_decoded) in [16]:
        checksum_length = 7
    elif len(address_decoded) in [17]:
        checksum_length = 8
    else:
        raise ValueError("Invalid address length")

    checksum = blake2b(checksum_prefix + address_decoded[0:-checksum_length]).digest()

    if checksum[0:checksum_length] != address_decoded[-checksum_length:]:
        raise ValueError("Invalid checksum")

    return address_decoded[ss58_format_length:len(address_decoded)-checksum_length].hex()

def ss58_encode(address: Union[str, bytes], ss58_format: int = 42):
    """
    Encodes an account ID to an Substrate address according to provided address_type

    Parameters
    ----------
    address
    ss58_format

    Returns
    -------

    """
    checksum_prefix = b'SS58PRE'

    if ss58_format < 0 or ss58_format > 16383 or ss58_format in [46, 47]:
        raise ValueError("Invalid value for ss58_format")

    if type(address) is bytes or type(address) is bytearray:
        address_bytes = address
    else:
        address_bytes = bytes.fromhex(address.replace('0x', ''))

    if len(address_bytes) in [32, 33]:
        # Checksum size is 2 bytes for public key
        checksum_length = 2
    elif len(address_bytes) in [1, 2, 4, 8]:
        # Checksum size is 1 byte for account index
        checksum_length = 1
    else:
        raise ValueError("Invalid length for address")

    if ss58_format < 64:
        ss58_format_bytes = bytes([ss58_format])
    else:
        ss58_format_bytes = bytes([
            ((ss58_format & 0b0000_0000_1111_1100) >> 2) | 0b0100_0000,
            (ss58_format >> 8) | ((ss58_format & 0b0000_0000_0000_0011) << 6)
        ])

    input_bytes = ss58_format_bytes + address_bytes
    checksum = blake2b(checksum_prefix + input_bytes).digest()

    return base58.b58encode(input_bytes + checksum[:checksum_length]).decode()


def ss58_encode_account_index(account_index, address_type=42):

    if 0 <= account_index <= 2**8 - 1:
        account_idx_encoder = U8()
    elif 2**8 <= account_index <= 2**16 - 1:
        account_idx_encoder = U16()
    elif 2**16 <= account_index <= 2**32 - 1:
        account_idx_encoder = U32()
    elif 2**32 <= account_index <= 2**64 - 1:
        account_idx_encoder = U64()
    else:
        raise ValueError("Value too large for an account index")

    return ss58_encode(account_idx_encoder.encode(account_index).data, address_type)


def ss58_decode_account_index(address, valid_address_type=42):

    account_index_bytes = ss58_decode(address, valid_address_type)

    if len(account_index_bytes) == 2:
        return U8(ScaleBytes('0x{}'.format(account_index_bytes))).decode()
    if len(account_index_bytes) == 4:
        return U16(ScaleBytes('0x{}'.format(account_index_bytes))).decode()
    if len(account_index_bytes) == 8:
        return U32(ScaleBytes('0x{}'.format(account_index_bytes))).decode()
    if len(account_index_bytes) == 16:
        return U64(ScaleBytes('0x{}'.format(account_index_bytes))).decode()
    else:
        raise ValueError("Invalid account index length")

def is_valid_ss58_address(value: str, valid_ss58_format: Optional[int] = None) -> bool:
    """
    Checks if given value is a valid SS58 formatted address, optionally check if address is valid for specified
    ss58_format

    Parameters
    ----------
    value: value to checked
    valid_ss58_format: if valid_ss58_format is provided the address must be valid for specified ss58_format (network) as well

    Returns
    -------
    bool
    """

    # Return False in case a public key is provided
    if value.startswith('0x'):
        return False

    try:
        ss58_decode(value, valid_ss58_format=valid_ss58_format)
    except Exception:
        return False

    return True

def get_account_id_and_ss58_address(value: str, address_type: Optional[int] = None):
    if is_valid_ss58_address(value, address_type):
        ss58_address = value
        hex_account_id = ss58_decode(value)
    else:
        hex_account_id = value
        ss58_address = ss58_encode(value)
    return hex_account_id, ss58_address