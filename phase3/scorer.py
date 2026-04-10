# scorer.py
def compute_confidence(regex_match, action_match, conditions_match):
    # Perfect match
    if regex_match and action_match and conditions_match:
        return 1.0
    
    # Strong match
    if regex_match and action_match:
        return 0.7
    
    # Weak match
    if regex_match:
        return 0.5
    
    # Very weak (root matched but not regex)
    if not regex_match and not action_match and not conditions_match:
        return 0.0