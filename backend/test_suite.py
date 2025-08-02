
"""
TrustGraphed Test Suite
Automated testing for all core modules
"""

import unittest
import sys
import os
import json
from io import BytesIO

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import app
from utils.sdg import SourceDataGrappler
from utils.aie import AssertionIntegrityEngine
from utils.cce import ConfidenceComputationEngine
from utils.zfp import ZeroFabricationProtocol
from utils.score_engine import TrustScoreEngine

class TestTrustGraphedModules(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Test content samples
        self.high_trust_content = """
        According to the World Health Organization (2023), vaccines have prevented 
        millions of deaths globally. The CDC reports that vaccination rates have 
        increased by 15% since 2020, with measles vaccination reaching 95% coverage 
        in developed nations.
        """
        
        self.low_trust_content = """
        Studies show that 87.3% of people believe in conspiracy theories. 
        Many experts agree that the government might be hiding information. 
        It's possible that aliens have visited Earth multiple times.
        """
    
    def test_health_endpoint(self):
        """Test backend health check."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'TrustGraphed backend is live')
    
    def test_sdg_module(self):
        """Test Source Data Grappler."""
        sdg = SourceDataGrappler()
        result = sdg.process(self.high_trust_content)
        
        self.assertIn('assertions_count', result)
        self.assertIn('citations_count', result)
        self.assertIn('extraction_confidence', result)
        self.assertGreaterEqual(result['extraction_confidence'], 0)
        self.assertLessEqual(result['extraction_confidence'], 1)
    
    def test_aie_module(self):
        """Test Assertion Integrity Engine."""
        aie = AssertionIntegrityEngine()
        result = aie.process(self.high_trust_content, ["Test assertion"])
        
        self.assertIn('integrity_score', result)
        self.assertIn('issues_found', result)
        self.assertGreaterEqual(result['integrity_score'], 0)
        self.assertLessEqual(result['integrity_score'], 1)
    
    def test_cce_module(self):
        """Test Confidence Computation Engine."""
        cce = ConfidenceComputationEngine()
        result = cce.process(self.high_trust_content, ["Test assertion"], [])
        
        self.assertIn('overall_confidence', result)
        self.assertGreaterEqual(result['overall_confidence'], 0)
        self.assertLessEqual(result['overall_confidence'], 1)
    
    def test_zfp_module(self):
        """Test Zero-Fabrication Protocol."""
        zfp = ZeroFabricationProtocol()
        result = zfp.process(self.low_trust_content)
        
        self.assertIn('authenticity_score', result)
        self.assertIn('fabrication_risk', result)
        self.assertGreaterEqual(result['authenticity_score'], 0)
        self.assertLessEqual(result['authenticity_score'], 1)
    
    def test_score_engine(self):
        """Test TrustScore Engine integration."""
        # Run through full pipeline
        sdg = SourceDataGrappler()
        aie = AssertionIntegrityEngine()
        cce = ConfidenceComputationEngine()
        zfp = ZeroFabricationProtocol()
        score_engine = TrustScoreEngine()
        
        # Process test content
        sdg_result = sdg.process(self.high_trust_content)
        aie_result = aie.process(self.high_trust_content, sdg_result.get('assertions', []))
        cce_result = cce.process(self.high_trust_content, sdg_result.get('assertions', []), [])
        zfp_result = zfp.process(self.high_trust_content)
        
        results = {
            'sdg_result': sdg_result,
            'aie_result': aie_result,
            'cce_result': cce_result,
            'zfp_result': zfp_result
        }
        
        score_result = score_engine.process(results)
        
        self.assertIn('trust_score', score_result)
        self.assertIn('trust_level', score_result)
        self.assertGreaterEqual(score_result['trust_score'], 0)
        self.assertLessEqual(score_result['trust_score'], 1)
    
    def test_evaluate_endpoint_text(self):
        """Test text evaluation endpoint."""
        response = self.app.post('/evaluate',
                               json={'content': self.high_trust_content},
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('trust_evaluation', data)
        self.assertIn('certificate_id', data)
    
    def test_evaluate_endpoint_file(self):
        """Test file evaluation endpoint."""
        # Create a test text file
        test_file = BytesIO(self.high_trust_content.encode('utf-8'))
        test_file.name = 'test.txt'
        
        response = self.app.post('/evaluate',
                               data={'file': (test_file, 'test.txt')})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')

if __name__ == '__main__':
    unittest.main()
