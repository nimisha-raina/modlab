"""Keep the two spoken lessons equivalent and their prediction pauses safe."""
import json
from pathlib import Path
import unittest
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from render_coil_bilingual import frame_indices


class CoilLanguageTests(unittest.TestCase):
    def test_language_retiming_keeps_pictures_in_the_matching_explanation(self):
        master=dict(duration=8,segments=[dict(id='first',target_start=0,target_end=4),
                                       dict(id='second',target_start=4,target_end=8)])
        shorter=dict(duration=6,segments=[dict(id='first',target_start=0,target_end=2),
                                        dict(id='second',target_start=2,target_end=6)])
        mapping=frame_indices(shorter,master,6)
        self.assertEqual(len(mapping),36)
        self.assertEqual(mapping,sorted(mapping))
        self.assertTrue(all(i<24 for i in mapping[:12]))
        self.assertEqual(mapping[12],24)
        self.assertTrue(all(24<=i<48 for i in mapping[12:]))
        self.assertEqual(frame_indices(master,master,6),list(range(48)))

    def test_approved_speakers_and_matching_story_sections(self):
        scripts=[json.loads((ROOT/f'docs/coil-narration-{lang}.json').read_text(encoding='utf-8')) for lang in ('english','hinglish')]
        self.assertEqual(scripts[0]['speaker'],'en-IN-PrabhatNeural')
        self.assertEqual(scripts[1]['speaker'],'hi-IN-SwaraNeural')
        for a,b in zip(scripts[0]['segments'],scripts[1]['segments'],strict=True):
            self.assertEqual((a['id'],a['start'],a['end']),(b['id'],b['start'],b['end']))
            self.assertTrue(a['text'] and b['text'])
        self.assertEqual(scripts[0]['segments'][-1]['end']-scripts[0]['segments'][-1]['start'],11)

    def test_four_equivalent_predictions_in_both_languages(self):
        questions=[json.loads((ROOT/f'student-lesson/content/coil/{lang}.json').read_text(encoding='utf-8')) for lang in ('english','hinglish')]
        self.assertEqual(len(questions[0]),4)
        for a,b in zip(*questions,strict=True):
            self.assertEqual((a['id'],a['after_id'],a['correct']),(b['id'],b['after_id'],b['correct']))
            for q in (a,b):
                self.assertEqual(len(q['answers']),3)
                self.assertTrue(q['hint'] and q['success'])
