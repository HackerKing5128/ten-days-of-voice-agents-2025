"""FAQ Search and Matching Utilities for Razorpay SDR Agent"""

import json
import os
from typing import List, Dict, Any
from pathlib import Path


def load_faq_data() -> Dict[str, Any]:
    """Load Razorpay FAQ data from JSON file.
    
    Returns:
        Dict containing company info, products, FAQs, and pricing details
    """
    faq_path = Path(__file__).parent.parent.parent / "shared-data" / "razorpay_faq.json"
    
    try:
        with open(faq_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"FAQ data not found at {faq_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in FAQ file: {e}")


def search_faqs(query: str, faq_data: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
    """Search FAQs using keyword matching.
    
    Args:
        query: User's question or search query
        faq_data: Complete FAQ data dictionary
        max_results: Maximum number of results to return
        
    Returns:
        List of relevant FAQ entries sorted by relevance
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    faqs = faq_data.get('faqs', [])
    scored_faqs = []
    
    for faq in faqs:
        score = 0
        
        # Check keywords (highest weight)
        keywords = faq.get('keywords', [])
        matching_keywords = sum(1 for keyword in keywords if keyword in query_lower)
        score += matching_keywords * 10
        
        # Check question match
        question_lower = faq.get('question', '').lower()
        question_words = set(question_lower.split())
        common_words = query_words & question_words
        score += len(common_words) * 5
        
        # Check if full query is in question or answer
        if query_lower in question_lower:
            score += 20
        if query_lower in faq.get('answer', '').lower():
            score += 15
        
        # Category bonus for specific searches
        category = faq.get('category', '')
        if any(cat_word in query_lower for cat_word in ['price', 'pricing', 'cost', 'fee']) and 'pricing' in category:
            score += 8
        if any(cat_word in query_lower for cat_word in ['integrate', 'integration', 'setup']) and 'integration' in category:
            score += 8
        
        if score > 0:
            scored_faqs.append({
                'faq': faq,
                'score': score
            })
    
    # Sort by score descending
    scored_faqs.sort(key=lambda x: x['score'], reverse=True)
    
    # Return top results
    return [item['faq'] for item in scored_faqs[:max_results]]


def format_faq_response(faqs: List[Dict[str, Any]], include_category: bool = False) -> str:
    """Format FAQ results into a natural response.
    
    Args:
        faqs: List of FAQ entries
        include_category: Whether to include category information
        
    Returns:
        Formatted string response
    """
    if not faqs:
        return "I don't have specific information about that in my knowledge base. Let me connect you with someone who can help with those details."
    
    # For single FAQ, return just the answer
    if len(faqs) == 1:
        return faqs[0]['answer']
    
    # For multiple FAQs, format with brief separators
    responses = []
    for i, faq in enumerate(faqs, 1):
        if include_category:
            category = faq.get('category', '').replace('_', ' ').title()
            responses.append(f"{category}: {faq['answer']}")
        else:
            responses.append(faq['answer'])
    
    return " Also, ".join(responses)


def get_product_info(product_name: str, faq_data: Dict[str, Any]) -> str:
    """Get information about a specific Razorpay product.
    
    Args:
        product_name: Name of the product (e.g., "Payment Gateway", "Subscriptions")
        faq_data: Complete FAQ data dictionary
        
    Returns:
        Product description and key features
    """
    products = faq_data.get('products', [])
    
    for product in products:
        if product_name.lower() in product.get('name', '').lower():
            name = product['name']
            desc = product['description']
            features = product.get('key_features', [])
            
            if features:
                features_str = ", ".join(features[:3])  # Top 3 features
                return f"{name}: {desc}. Key features include {features_str}."
            return f"{name}: {desc}"
    
    return None


def get_pricing_summary(faq_data: Dict[str, Any]) -> str:
    """Get a concise pricing summary.
    
    Args:
        faq_data: Complete FAQ data dictionary
        
    Returns:
        Formatted pricing summary
    """
    pricing = faq_data.get('pricing_details', {}).get('payment_gateway', {}).get('standard', {})
    
    transaction_fee = pricing.get('transaction_fee', '2%')
    setup_fee = pricing.get('setup_fee', '₹0')
    
    return f"Our standard pricing is {transaction_fee} per transaction with {setup_fee} setup fee. UPI transactions have zero platform fee. We also offer custom enterprise pricing for high-volume businesses."


def get_company_overview(faq_data: Dict[str, Any]) -> str:
    """Get company overview summary.
    
    Args:
        faq_data: Complete FAQ data dictionary
        
    Returns:
        Brief company overview
    """
    company = faq_data.get('company', {})
    name = company.get('name', 'Razorpay')
    tagline = company.get('tagline', '')
    description = company.get('description', '')
    customers = company.get('customers', '10+ million')
    
    return f"{name} - {tagline}. {description} We serve {customers} businesses across India."
