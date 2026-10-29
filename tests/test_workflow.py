"""Isolated API tests: SQLite and injected Auth/AI are NOT integration evidence."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app, identity
from backend.db import connect, execute

class Workflow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  os.environ.update(TESTING='1',DATABASE_URL='sqlite:///'+self.tmp.name+'/test.sqlite')
  with connect() as c:
   sql=Path('migrations/001_demo.sql').read_text().split('-- Application data')[0]+'COMMIT;'
   c.executescript(sql)
   for b in ['a','b']: execute(c,'INSERT INTO businesses VALUES(%s,%s)',(b,b))
  self.member={'subject':'owner-a','business_id':'a','role':'owner'}
  app.dependency_overrides[identity]=lambda:self.member
  self.client=TestClient(app)
  self.facts={'make':'Toyota','model':'Camry','year':2022,'price':2300000,'mileage':32000}
 def tearDown(self):
  app.dependency_overrides.clear(); self.tmp.cleanup()
 def create(self):
  r=self.client.post('/api/listings',json={'facts':self.facts,'description':'Reviewed Toyota listing'})
  self.assertEqual(r.status_code,201);return r.json()['id']
 def publish(self,lid,revision=1):
  return self.client.post(f'/api/listings/{lid}/publish',json={'expected_revision':revision,'confirm_approval':True})
 def test_persistence_and_private_draft(self):
  lid=self.create(); self.assertEqual(self.client.get('/api/listings/'+lid).json()['facts']['price'],2300000)
  self.assertEqual(self.client.get('/api/public/'+lid).status_code,404)
  self.assertEqual(self.publish(lid).status_code,200)
  self.facts['price']=2400000
  r=self.client.patch('/api/listings/'+lid,json={'facts':self.facts,'description':'New review','expected_revision':1})
  self.assertEqual(r.status_code,200)
  self.assertIsNone(r.json()['approved_revision'])
  self.assertEqual(self.publish(lid).status_code,409)
  self.assertEqual(self.client.get('/api/public/'+lid).json()['facts']['price'],2300000)
  self.assertEqual(self.publish(lid,2).status_code,200)
  with patch('backend.main.call_ai',return_value={'intent':'facts','fields':['price','mileage']}):
   answer=self.client.post('/api/public/'+lid+'/questions',json={'question':'Price and mileage?'}).json()
  self.assertIn('24,000.00',answer['answer']);self.assertIn('32,000',answer['answer']);self.assertEqual(answer['revision'],2)
 def test_ownership_and_role(self):
  lid=self.create();self.member={'subject':'other','business_id':'b','role':'owner'}
  self.assertEqual(self.client.get('/api/listings/'+lid).status_code,404)
  self.assertEqual(self.publish(lid).status_code,404)
  self.member={'subject':'staff','business_id':'a','role':'staff'}
  self.assertEqual(self.publish(lid).status_code,403)
  self.assertEqual(self.client.get('/api/diagnostics').status_code,403)
 def test_inquiry_storage_and_isolation(self):
  lid=self.create();self.publish(lid)
  import uuid
  body={'request_key':str(uuid.uuid4()),'contact':'test@example.com','message':'Accident history?'}
  r=self.client.post('/api/public/'+lid+'/inquiries',json=body);self.assertEqual(r.status_code,201)
  self.assertEqual(self.client.post('/api/public/'+lid+'/inquiries',json=body).json()['id'],r.json()['id'])
  self.assertEqual(len(self.client.get('/api/inquiries').json()),1)
  self.member={'subject':'b','business_id':'b','role':'owner'}
  self.assertEqual(self.client.get('/api/inquiries').json(),[])
  self.assertEqual(self.client.patch('/api/inquiries/'+r.json()['id'],json={'status':'resolved'}).status_code,404)
 def test_invalid_ai_and_failure_handoff(self):
  lid=self.create();self.publish(lid)
  for result in [{'intent':'facts','fields':['secret']},{'intent':'handoff','fields':[]},{'intent':'facts','fields':['price'],'answer':'invented'}]:
   with patch('backend.main.call_ai',return_value=result):
    self.assertTrue(self.client.post('/api/public/'+lid+'/questions',json={'question':'anything'}).json()['handoff'])
  with patch('backend.main.call_ai',side_effect=RuntimeError()):
   self.assertTrue(self.client.post('/api/public/'+lid+'/questions',json={'question':'price?'}).json()['handoff'])
   self.assertEqual(self.client.post('/api/listings/'+lid+'/draft',json={'expected_revision':1}).status_code,503)
 def test_late_ai_draft_and_repeated_publication(self):
  lid=self.create()
  def concurrent(*args):
   self.client.patch('/api/listings/'+lid,json={'facts':self.facts,'description':'Concurrent edit','expected_revision':1})
   return {'description':'Late AI'}
  with patch('backend.main.call_ai',side_effect=concurrent):
   self.assertEqual(self.client.post('/api/listings/'+lid+'/draft',json={'expected_revision':1}).status_code,409)
  for _ in range(10):self.assertEqual(self.publish(lid,2).status_code,200)
  self.assertEqual(self.client.get('/api/listings/'+lid).json()['description'],'Concurrent edit')
 def test_anonymous_protection(self):
  app.dependency_overrides.clear()
  self.assertEqual(self.client.get('/api/listings').status_code,401)
  self.assertEqual(self.client.get('/api/diagnostics').status_code,401)

if __name__=='__main__': unittest.main()
