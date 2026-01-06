"""
Company and location name normalization
"""
import re
from typing import Tuple


def normalize_company_name(name: str) -> str:
    """
    Normalize company name for deduplication
    
    Examples:
        "Google Inc." -> "google"
        "Google LLC" -> "google"
        "Microsoft Corporation" -> "microsoft"
    """
    if not name:
        return ""
    
    # Convert to lowercase
    normalized = name.lower().strip()
    
    # Remove common suffixes
    suffixes = [
        r'\s+inc\.?$',
        r'\s+llc\.?$',
        r'\s+ltd\.?$',
        r'\s+corp\.?$',
        r'\s+corporation$',
        r'\s+limited$',
        r'\s+company$',
        r'\s+co\.?$',
    ]
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized, flags=re.IGNORECASE)
    
    # Remove special characters
    normalized = re.sub(r'[.,\-&]', ' ', normalized)
    
    # Replace "&" with "and"
    normalized = normalized.replace('&', 'and')
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized


def normalize_location(location: str) -> str:
    """
    Normalize location for deduplication
    
    Examples:
        "Remote" -> "remote"
        "Work from Home" -> "remote"
        "WFH" -> "remote"
        "San Francisco" -> "san francisco"
    """
    if not location:
        return ""
    
    normalized = location.lower().strip()
    
    # Normalize remote variations
    remote_variations = [
        'work from home',
        'wfh',
        'work remotely',
        'remote work',
        'fully remote',
        '100% remote',
    ]
    
    if any(variation in normalized for variation in remote_variations):
        return 'remote'
    
    # Normalize city name variations
    city_mappings = {
        'sf': 'san francisco',
        'san fran': 'san francisco',
        'nyc': 'new york',
        'ny': 'new york',
        'la': 'los angeles',
    }
    
    for abbrev, full_name in city_mappings.items():
        if abbrev in normalized:
            normalized = normalized.replace(abbrev, full_name)
    
    # Normalize country variations
    country_mappings = {
        'united states': 'usa',
        'us': 'usa',
        'u.s.': 'usa',
        'u.s.a.': 'usa',
    }
    
    for variation, standard in country_mappings.items():
        if variation in normalized:
            normalized = normalized.replace(variation, standard)
    
    # Remove extra whitespace
    normalized = ' '.join(normalized.split())
    
    return normalized


def calculate_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two normalized names using Levenshtein distance
    
    Returns a value between 0.0 (completely different) and 1.0 (identical)
    """
    try:
        from Levenshtein import ratio
        return ratio(name1, name2)
    except ImportError:
        # Fallback to simple comparison if python-Levenshtein is not available
        if name1 == name2:
            return 1.0
        # Simple character-based similarity
        if not name1 or not name2:
            return 0.0
        
        # Count common characters
        set1 = set(name1)
        set2 = set(name2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


def match_company(
    company_name: str,
    location: str,
    existing_companies: list[dict]
) -> Tuple[str | None, bool]:
    """
    Match a company name and location against existing companies
    
    Args:
        company_name: Company name to match
        location: Location to match
        existing_companies: List of dicts with 'normalized_name' and 'normalized_location'
    
    Returns:
        Tuple of (company_id, matched) where matched is True if found
    """
    normalized_name = normalize_company_name(company_name)
    normalized_location = normalize_location(location)
    
    if not normalized_name:
        return None, False
    
    # First try exact match
    for company in existing_companies:
        if (company.get('normalized_name') == normalized_name and
            company.get('normalized_location') == normalized_location):
            return company.get('company_id'), True
    
    # Then try fuzzy match on name (similarity > 0.85)
    for company in existing_companies:
        if company.get('normalized_location') == normalized_location:
            similarity = calculate_similarity(
                normalized_name,
                company.get('normalized_name', '')
            )
            if similarity > 0.85:
                return company.get('company_id'), True
    
    return None, False

