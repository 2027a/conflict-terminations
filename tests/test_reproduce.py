"""End-to-end checks against the published, pinned UCDP snapshot."""
import csv
from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]

class ReproductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='conflict-terminations-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.output = Path(cls.temp.name) / 'output'
        subprocess.run([sys.executable, str(PROJECT / 'reproduce.py'),
                        '--output-dir', str(cls.output)],
                       cwd=cls.temp.name, check=True, capture_output=True, text=True)

    def read_csv(self, name):
        with (self.output / name).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f, delimiter=';'))

    def test_episode_totals_and_keys(self):
        rows = self.read_csv('fins-conflits-ucdp-1946-2023.csv')
        self.assertEqual(len(rows), 507)
        self.assertEqual(len({(r['id_conflit_ucdp'], r['derniere_annee_active'])
                              for r in rows}), 507)
        self.assertEqual(Counter(r['issue_code_ucdp'] for r in rows),
                         {'1':60, '2':67, '3':107, '4':44, '5':209, '6':20})

    def test_periods_and_denominators(self):
        rows = self.read_csv('fins-conflits-par-periode.csv')
        self.assertEqual([int(r['n']) for r in rows], [23,40,49,47,61,116,62,80,29])
        for r in rows:
            self.assertAlmostEqual(sum(float(v) for k,v in r.items()
                                       if k.endswith('_pourcent')), 100, places=3)
            self.assertEqual(sum(int(v) for k,v in r.items()
                                 if k.endswith('_nombre')), int(r['n']))
        self.assertEqual((rows[0]['debut'],rows[-1]['fin']), ('1946','2023'))

    def test_csv_outputs_match_committed_results(self):
        for name in ['fins-conflits-ucdp-1946-2023.csv','fins-conflits-par-periode.csv']:
            self.assertEqual((self.output/name).read_bytes(),
                             (PROJECT/'output'/name).read_bytes())

    def test_wars_only(self):
        # Same directory: the second view must not overwrite the first one.
        before = {f.name:f.read_bytes() for f in self.output.iterdir()}
        subprocess.run([sys.executable, str(PROJECT/'reproduce.py'), '--wars-only',
                        '--output-dir', str(self.output)],
                       cwd=self.temp.name, check=True, capture_output=True, text=True)
        for name, content in before.items():
            self.assertEqual((self.output/name).read_bytes(), content)
        rows = self.read_csv('fins-guerres-ucdp-1946-2023.csv')
        self.assertEqual(len(rows), 131)
        self.assertEqual(Counter(r['issue_code_ucdp'] for r in rows),
                         {'1':24, '2':22, '3':25, '4':17, '5':33, '6':10})
        with (PROJECT/'data/source.csv').open(encoding='utf-8-sig', newline='') as f:
            source = list(csv.DictReader(f))
        # Independent oracle: inspect the whole time interval of each episode.
        expected = {(r['conflict_id'], r['year']) for r in source
                    if r['c_epterm'] == '1' and any(
                        y['conflict_id'] == r['conflict_id']
                        and int(r['c_ep_startyear']) <= int(y['year']) <= int(r['year'])
                        and y['intensity_level'] == '2' for y in source)}
        self.assertEqual({(r['id_conflit_ucdp'], r['derniere_annee_active']) for r in rows},
                         expected)
        # 50 retained episodes had fallen below war intensity in their final year.
        self.assertEqual(sum(r['intensity_level'] == '1' for r in source
                             if (r['conflict_id'],r['year']) in expected), 50)
        periods = self.read_csv('fins-guerres-par-periode.csv')
        self.assertEqual([int(r['n']) for r in periods], [13,18,14,18,17,23,14,10,4])
        for r in periods:
            self.assertAlmostEqual(sum(float(v) for k,v in r.items()
                                       if k.endswith('_pourcent')), 100, places=3)
        for name in ['fins-guerres-ucdp-1946-2023.csv','fins-guerres-par-periode.csv']:
            self.assertEqual((self.output/name).read_bytes(),
                             (PROJECT/'output'/name).read_bytes())
        with Image.open(self.output/'fins-guerres-evolution-1946-2023.png') as image:
            self.assertEqual(image.size, (2340,1620))
            image.verify()

    def test_png_is_valid(self):
        with Image.open(self.output/'fins-conflits-evolution-1946-2023.png') as image:
            self.assertEqual(image.size, (2340,1620))
            self.assertEqual(image.format, 'PNG')
            image.verify()

if __name__ == '__main__':
    unittest.main()
