"""Exercise the shell startup contract with synthetic process stubs, no network."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


class Launcher(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'scripts').mkdir();(self.root/'.venv/bin').mkdir(parents=True)
        (self.root/'bin').mkdir();(self.root/'.env').write_text('TEST_CONFIGURATION=1\n')
        for name in ['run-local.sh','launch-showcase.sh']:
            shutil.copyfile(Path('scripts')/name,self.root/'scripts'/name)
        python=self.root/'.venv/bin/python'
        python.write_text('#!/bin/sh\necho "$*" >> "$STARTUP_EVENTS"\nif [ "$2" = "scripts.acceptance_live" ]; then exit 1; fi\n')
        python.chmod(0o700)
        npm=self.root/'bin/npm';npm.write_text('#!/bin/sh\necho "frontend-build" >> "$STARTUP_EVENTS"\n');npm.chmod(0o700)
        self.log=self.root/'events'
        self.env={**os.environ,'PATH':str(self.root/'bin')+os.pathsep+os.environ['PATH'],'STARTUP_EVENTS':str(self.log)}

    def tearDown(self):self.tmp.cleanup()

    def launch(self, script, *args):
        return subprocess.run(['bash',str(self.root/'scripts'/script),*args],env=self.env,capture_output=True,text=True)

    def test_failed_optional_ai_check_still_serves_new_frontend(self):
        result=self.launch('launch-showcase.sh','--practice','--verify-live')
        self.assertEqual(result.returncode,0,result.stderr)
        events=self.log.read_text().splitlines()
        self.assertLess(events.index('frontend-build'),events.index('-m scripts.acceptance_live'))
        self.assertEqual(events[-1],'-m backend.local')
        self.assertIn('did not pass',result.stderr)
        self.assertEqual(events.count('-m scripts.acceptance_live'),1)

    def test_old_entry_point_builds_current_source_without_inference(self):
        result=self.launch('run-local.sh')
        self.assertEqual(result.returncode,0,result.stderr)
        events=self.log.read_text().splitlines()
        self.assertIn('frontend-build',events)
        self.assertEqual(events[-1],'-m backend.local')
        self.assertNotIn('-m scripts.acceptance_live',events)
