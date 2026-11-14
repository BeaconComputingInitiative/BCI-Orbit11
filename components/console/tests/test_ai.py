# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# File SHA-256: SHA256SUMS
# Verify model-grounded answers IF AND ONLY IF pinned provenance gates are met.
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import orbital_ai as ai


class NativeAiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.home=Path(self.temp.name)
        self.live={'current_context':'ctx-other','states':{'host':'active','packet':'active','neural':'active'},
                   'journal':{'valid':True,'count':9},'neural_window_count':9,'hours':1,'days':0.1}
    def tearDown(self):self.temp.cleanup()

    def test_baselines_intent_returns_real_layers(self):
        live={**self.live,
          'host_status':{'reference_classification':'curated_generic_reference_not_host_trained',
                         'context':'ctx-old','profile':{'approved':False,'n':17,'hours':2,
                                                    'categories':{'listener':44,'exe':47}}},
          'host_baseline_status':{'context':'ctx-old','ready_for_review':False,
                     'stats':{'approved':False,'n':17,'hours':2,'categories':{'listener':44,'exe':47}}}}
        for question in ('what are your baselines','tell me about your baseline',
                         'which behavioral profiles do you use','what is normal behavior?'):
            with self.subTest(question=question):
                answer=ai.respond(question,live,self.home)
                self.assertIn('Host behavioral profile',answer)
                self.assertIn('operator approved: NO',answer)
                self.assertIn('observations: 17',answer)
                self.assertIn('curated reference rules',answer)
                self.assertIn('experimental only',answer)
                self.assertIn('not installed or not verified',answer)
    def test_baseline_missing_data_not_invented(self):
        result=ai.respond('what are my baselines?',self.live,self.home)
        self.assertIn('operator approved: NOT VERIFIED',result)
        self.assertIn('observations: not reported',result)
        self.assertIn('journal integrity: PASS',result)
        self.assertNotIn('operator approved: YES',result)
    def test_baseline_never_promotes_or_executes(self):
        for question in ('approve my baseline','baselines', 'baseline training'):
            text=ai.respond(question,self.live,self.home)
            self.assertIn('No cross-context trust promotion',text)
            self.assertIn('not retrievable',text)
    def test_baseline_report_machine_readable(self):
        report=ai.baseline_report(self.live,self.home)
        self.assertEqual(report['header'],'BEACON COMPUTING INITIATIVE')
        self.assertIsNone(report['host_baseline_approved'])
        self.assertFalse(report['live_inference_enabled'])
        self.assertFalse(report['containment_authorized'])

    def test_no_model_never_invents_anomalies(self):
        answer=ai.respond('show anomalies',self.live,self.home)
        self.assertIn('not accessible',answer)
    def test_health_facts_are_not_model_inference(self):
        answer=ai.respond('system status',self.live,self.home)
        self.assertIn('Host monitor: active',answer)
        self.assertIn('live neural inference: DISABLED',answer)
    def test_training_not_silently_approved(self):
        answer=ai.respond('training readiness',self.live,self.home)
        self.assertIn('HOLD',answer)
        self.assertIn('explicit approval',answer)
    def test_context_cannot_be_assumed_equal(self):
        answer=ai.respond('network context',self.live,self.home)
        self.assertIn('ctx-other',answer)
        self.assertIn('No equivalence has been approved',answer)
    def test_unsupported_instruction_cannot_execute(self):
        answer=ai.respond('execute rm -rf /home/bci',self.live,self.home)
        self.assertIn('not guess',answer)
    def test_no_attribution_from_anomaly(self):
        answer=ai.respond('who attacked me',self.live,self.home)
        self.assertIn('Neither the anomaly model',answer)
    def test_pinned_model_context_gate(self):
        path=ai.ai_root(self.home)/'artifacts';path.mkdir(parents=True)
        (path/'legacy-model.json').write_text('{"developer_seal":"CJB-DEV-2026"}')
        with self.assertRaisesRegex(ValueError,'SHA-256'):
            ai.original_model(self.home)
    def test_matched_model_can_explain_original_scores(self):
        model={'architecture':[12,8,3,8,12],'context':ai.CONTEXT,'model_state':'candidate_unpromoted',
               'features':['x']*12,'layers':[{}]*4,'anomaly_threshold':1.86,'validation_mse':.082}
        item={'ts':'2026-11-10T05:40:00+00:00','context':ai.CONTEXT,'trust':'untrusted_legacy',
              'candidate_anomaly':True,'anomaly_score_mse':5.29,'threshold':1.86,
              'top_contributors':[{'feature':'inbound_count','squared_reconstruction_error':61.84}]}
        with patch.object(ai,'original_model',return_value=model), patch.object(ai,'original_scores',return_value=[item]):
            answer=ai.respond('explain anomaly 1',self.live,self.home)
        self.assertIn('inbound_count',answer)
        self.assertIn('not evidence of malicious intent',answer)
    def test_scoring_requires_hashed_input(self):
        with patch.object(ai,'original_model',return_value={'context':ai.CONTEXT}):
            with self.assertRaisesRegex(ValueError,'SHA-256 sidecar'):
                ai.score_argv(str(self.home/'not-there.jsonl'),self.home)
    def test_scoring_invokes_same_native_core(self):
        (ai.ai_root(self.home)/'artifacts').mkdir(parents=True)
        (ai.ai_root(self.home)/'artifacts/legacy-model.json.sha256').write_text('test\n')
        (self.home/'.local/bin').mkdir(parents=True)
        native=self.home/'.local/bin/bci-orbital-neural'
        native.write_text('#!/bin/sh\nexit 0\n');native.chmod(0o700)
        file=self.home/'data.jsonl';file.write_text('{}\n');(self.home/'data.jsonl.sha256').write_text('x\n')
        with patch.object(ai,'original_model',return_value={'context':ai.CONTEXT}):
            argv=ai.score_argv(str(file),self.home)
        self.assertEqual(argv[1],'score')
        self.assertIn('legacy-model.json',argv[3])
        self.assertEqual(argv[5],str(file))
        self.assertTrue(argv[7].endswith('.json'))

if __name__=='__main__':unittest.main()
