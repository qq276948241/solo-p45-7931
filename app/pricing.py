PRICING = {
    "standard": 80,
    "luxury": 150,
}


def calculate_fee(cage_type: str, days: int) -> float:
    rate = PRICING.get(cage_type, PRICING["standard"])
    return rate * days
