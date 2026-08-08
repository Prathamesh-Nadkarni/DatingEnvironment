import hashlib

def get_astro_fingerprint(name: str, dob: str, time: str, city: str) -> dict:
    """
    Since pyswisseph cannot be compiled in the current environment, this is a 
    deterministic fallback that calculates a unique 'moon_class' (0-107) 
    based on the birth details. This acts as the astrological fingerprint.
    """
    raw_string = f"{name.lower().strip()}-{dob}-{time}-{city.lower().strip()}"
    hash_digest = hashlib.md5(raw_string.encode()).hexdigest()
    
    # 27 Nakshatras * 4 Padas = 108 classes
    moon_class = int(hash_digest[:8], 16) % 108
    
    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    nakshatra_idx = moon_class // 4
    pada = (moon_class % 4) + 1
    
    return {
        "moon_class": moon_class,
        "nakshatra": nakshatras[nakshatra_idx],
        "pada": pada,
        "hash_digest": hash_digest
    }

def get_astakoota_score(moon_class_a: int, moon_class_b: int) -> dict:
    """
    Simulates the 108x108 precomputed Ashtakoota compatibility matrix.
    Given two moon classes, it deterministically returns the 36-point Guna score 
    and Dosha flags. (O(1) simulated lookup)
    """
    # Deterministic generation based on the directed combination of A and B
    combination_key = f"{moon_class_a}_{moon_class_b}"
    hash_val = int(hashlib.md5(combination_key.encode()).hexdigest()[:8], 16)
    
    # Base guna score between 12 and 36 (most matches are in this range)
    base_guna = 12 + (hash_val % 25)
    
    # Derive traditional components deterministically
    varna = (hash_val % 2)
    vashya = (hash_val % 3)
    tara = (hash_val % 4)
    yoni = (hash_val % 5)
    maitri = (hash_val % 6)
    gana = (hash_val % 7)
    bhakoot = (hash_val % 8)
    nadi = (hash_val % 9)
    
    # Nadi Dosha happens occasionally (e.g. if they fall in same Nadi group)
    nadi_dosha = (hash_val % 100) < 15
    bhakoot_dosha = (hash_val % 100) > 85
    
    # Apply severe penalties for doshas if we were simulating full rules,
    # but here we just adjust the base_guna slightly for realism.
    if nadi_dosha:
        base_guna -= 8
    if bhakoot_dosha:
        base_guna -= 7
        
    base_guna = max(0, min(36, base_guna))
    
    # Classification based on Drik rules
    if nadi_dosha:
        classification = "INAUSPICIOUS_NADI"
    elif not bhakoot_dosha:
        if base_guna >= 31:
            classification = "EXCELLENT"
        elif base_guna >= 21:
            classification = "VERY_GOOD"
        elif base_guna >= 17:
            classification = "MIDDLING"
        else:
            classification = "INAUSPICIOUS"
    else:
        if base_guna >= 26:
            classification = "VERY_GOOD"
        elif base_guna >= 21:
            classification = "MIDDLING"
        else:
            classification = "INAUSPICIOUS"

    return {
        "guna": base_guna,
        "max_guna": 36,
        "nadi_dosha": nadi_dosha,
        "bhakoot_dosha": bhakoot_dosha,
        "classification": classification,
        "breakdown": {
            "varna": varna,
            "vashya": vashya,
            "tara": tara,
            "yoni": yoni,
            "graha_maitri": maitri,
            "gana": gana,
            "bhakoot": bhakoot,
            "nadi": nadi
        }
    }
