from typing import List
from datetime import datetime

def get_component_value(components, target_key):
    """Rekurzívne hľadá hodnotu podľa kľúča (napr. BT-21-Procedure)"""
    for comp in components:
        if comp.get("key") == target_key:
            return comp.get("value")
        if "components" in comp:
            res = get_component_value(comp["components"], target_key)
            if res: return res
    return None


def analyze_red_flags(tender_data, components) -> List[dict]:
    """Automatické vyhodnotenie rizikových ukazovateľov"""
    flags = []

    # 1. Jediná ponuka
    bids = tender_data.get("bids_count")
    if bids == 1:
        flags.append({"type": "SINGLE_BID", "description": "Bola prijatá len jedna ponuka."})

    # 2. Námietkové konanie v texte
    description = get_component_value(components, "BT-24-Procedure") or ""
    if "námietkové konanie" in description.lower():
        flags.append({"type": "OBJECTION", "description": "V texte sa spomína prebiehajúce námietkové konanie."})

    # 3. Príliš krátka lehota (príklad: menej ako 15 dní od zverejnenia)
    if tender_data.get("deadline"):
        delta = (tender_data["deadline"] - datetime.now()).days
        if 0 < delta < 15:
            flags.append(
                {"type": "SHORT_DEADLINE", "description": f"Lehota končí o {delta} dní, čo je podozrivo málo."})

    return flags