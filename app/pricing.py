PRICING = {
    "standard": 80,
    "luxury": 150,
}

CAGE_CAPACITY = {
    "standard": 2,
    "luxury": 1,
}


def calculate_fee(cage_type: str, days: int) -> float:
    rate = PRICING.get(cage_type, PRICING["standard"])
    return rate * days


def get_cage_capacity(cage_type: str) -> int:
    return CAGE_CAPACITY.get(cage_type, CAGE_CAPACITY["standard"])
