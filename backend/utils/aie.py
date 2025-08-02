
"""
Assertion Integrity Engine (AIE)
Detects contradictions, redundancies, or unsupported claims.
"""

from typing import List, Dict, Any
import difflib
import re

class AssertionIntegrityEngine:
    def __init__(self):
        self.name = "Assertion Integrity Engine"
        self.version = "1.0.0"
        self.contradiction_patterns = [
            (r'\bnot\b', r'\bis\b'),
            (r'\bfalse\b', r'\btrue\b'),
            (r'\bimpossible\b', r'\bpossible\b'),
            (r'\bnever\b', r'\balways\b'),
        ]
    
    def detect_contradictions(self, assertions: List[str]) -> List[Dict[str, Any]]:
        """Detect potential contradictions between assertions."""
        contradictions = []
        
        for i, assertion1 in enumerate(assertions):
            for j, assertion2 in enumerate(assertions[i+1:], i+1):
                similarity = difflib.SequenceMatcher(None, assertion1.lower(), assertion2.lower()).ratio()
                
                # Check for high similarity with opposing words
                if similarity > 0.6:
                    for neg_pattern, pos_pattern in self.contradiction_patterns:
                        if (re.search(neg_pattern, assertion1.lower()) and re.search(pos_pattern, assertion2.lower())) or \
                           (re.search(pos_pattern, assertion1.lower()) and re.search(neg_pattern, assertion2.lower())):
                            contradictions.append({
                                "type": "contradiction",
                                "assertion1": assertion1[:100] + "..." if len(assertion1) > 100 else assertion1,
                                "assertion2": assertion2[:100] + "..." if len(assertion2) > 100 else assertion2,
                                "similarity": round(similarity, 3),
                                "severity": "high"
                            })
        
        return contradictions
    
    def detect_redundancies(self, assertions: List[str]) -> List[Dict[str, Any]]:
        """Detect redundant or highly similar assertions."""
        redundancies = []
        
        for i, assertion1 in enumerate(assertions):
            for j, assertion2 in enumerate(assertions[i+1:], i+1):
                similarity = difflib.SequenceMatcher(None, assertion1.lower(), assertion2.lower()).ratio()
                
                if similarity > 0.85:  # High similarity threshold
                    redundancies.append({
                        "type": "redundancy",
                        "assertion1": assertion1[:100] + "..." if len(assertion1) > 100 else assertion1,
                        "assertion2": assertion2[:100] + "..." if len(assertion2) > 100 else assertion2,
                        "similarity": round(similarity, 3),
                        "severity": "medium"
                    })
        
        return redundancies
    
    def detect_unsupported_claims(self, content: str, assertions: List[str]) -> List[Dict[str, Any]]:
        """Detect assertions that might be unsupported claims."""
        unsupported = []
        
        unsupported_patterns = [
            r'\bit is well known\b',
            r'\beveryone knows\b',
            r'\bobviously\b',
            r'\bclearly\b',
            r'\bof course\b',
        ]
        
        for assertion in assertions:
            for pattern in unsupported_patterns:
                if re.search(pattern, assertion.lower()):
                    unsupported.append({
                        "type": "unsupported_claim",
                        "assertion": assertion[:100] + "..." if len(assertion) > 100 else assertion,
                        "pattern": pattern,
                        "severity": "medium",
                        "description": "Assertion uses language that may indicate unsupported claims"
                    })
        
        return unsupported
    
    def calculate_integrity_score(self, issues: List[Dict[str, Any]], total_assertions: int) -> float:
        """Calculate overall integrity score based on detected issues."""
        if total_assertions == 0:
            return 1.0
        
        severity_weights = {"high": 0.3, "medium": 0.15, "low": 0.05}
        
        total_penalty = 0
        for issue in issues:
            severity = issue.get("severity", "low")
            total_penalty += severity_weights.get(severity, 0.05)
        
        # Normalize by number of assertions
        penalty_per_assertion = total_penalty / total_assertions
        
        # Score from 0 to 1 (higher is better)
        integrity_score = max(0.0, 1.0 - penalty_per_assertion)
        return integrity_score
    
    def process(self, content: str, assertions: List[str]) -> Dict[str, Any]:
        """Main processing function."""
        if not assertions:
            return {
                "module": self.name,
                "integrity_score": 1.0,
                "issues_found": 0,
                "contradictions": [],
                "redundancies": [],
                "unsupported_claims": [],
                "status": "processed"
            }
        
        contradictions = self.detect_contradictions(assertions)
        redundancies = self.detect_redundancies(assertions)
        unsupported_claims = self.detect_unsupported_claims(content, assertions)
        
        all_issues = contradictions + redundancies + unsupported_claims
        integrity_score = self.calculate_integrity_score(all_issues, len(assertions))
        
        return {
            "module": self.name,
            "integrity_score": round(integrity_score, 3),
            "issues_found": len(all_issues),
            "contradictions": contradictions[:3],  # Limit for demo
            "redundancies": redundancies[:3],
            "unsupported_claims": unsupported_claims[:3],
            "total_assertions_analyzed": len(assertions),
            "status": "processed"
        }
