"""Self-learning support for governed contract knowledge."""
from .contract_database import (
    ContractDatabase,
    ContractRecord,
    build_contract_database,
    write_contract_database,
)

__all__ = [
    "ContractDatabase",
    "ContractRecord",
    "build_contract_database",
    "write_contract_database",
]
