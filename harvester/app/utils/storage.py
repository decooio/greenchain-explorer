from scalecodec.types import GenericMetadataVersioned, GenericPalletMetadata, GenericStorageEntryMetadata
from scalecodec.base import ScaleBytes, RuntimeConfiguration
from substrateinterface import SubstrateInterface
from app.models.data import RuntimeStorage


def query(substrate: SubstrateInterface, pallet_name: str, storage_name: str, param_types: list, param_hashers: list,
          params: list, value_type: str, block_hash):
    # Encode parameters
    for idx, param in enumerate(params):
        # param = substrate.convert_storage_parameter(param_types[idx], param)
        if type(param) is bytes:
            param = f'0x{param.hex()}'
        param_obj = substrate.runtime_config.create_scale_object(type_string=param_types[idx])
        params[idx] = param_obj.encode(param)

    storage_hash = substrate.generate_storage_hash(
        storage_module=pallet_name,
        storage_function=storage_name,
        params=params,
        hashers=param_hashers
    )
    query_value = substrate.get_storage_by_key(block_hash, storage_hash)
    if query_value is None:
        return None
    scale_class = substrate.runtime_config.create_scale_object(value_type,
                                                               data=ScaleBytes(query_value))
    scale_class.decode()
    return scale_class


def query_storage(pallet_name: str, storage_name: str, substrate: SubstrateInterface, block_hash,
                  params: list = None):
    if params is None:
        params = []

    if substrate.metadata_decoder is None:
        metadata: GenericMetadataVersioned = substrate.get_block_metadata(block_hash)
    else:
        metadata: GenericMetadataVersioned = substrate.metadata_decoder

    module: GenericPalletMetadata = metadata.get_metadata_pallet(pallet_name)
    storage_func: GenericStorageEntryMetadata = module.get_storage_function(storage_name)
    param_types = storage_func.get_params_type_string()
    value_type = storage_func.get_value_type_string()

    return query(substrate=substrate, pallet_name=module.value['storage']['prefix'], storage_name=storage_name, param_types=param_types,
                 param_hashers=storage_func.get_param_hashers(), params=params, value_type=value_type,
                 block_hash=block_hash)


def query_storage_by_db(storage_obj: RuntimeStorage, substrate: SubstrateInterface, block_hash, params: list = None):
    if params is None:
        params = []
    param_types = storage_obj.get_types()
    return query(substrate=substrate, pallet_name=storage_obj.module_id, storage_name=storage_obj.name,
                 param_types=param_types,
                 param_hashers=storage_obj.get_hashers(), params=params, value_type=storage_obj.type_value,
                 block_hash=block_hash)
