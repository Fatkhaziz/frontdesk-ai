"""Sanitized replay of the November 26 real response; no provider calls."""
import copy
import unittest
from backend.shopping import Preferences, ShoppingQuestion, source_list, validate_answer
from backend.ai_rejection import Rejection
from scripts.sample_inventory import example_vehicles


class SourceResolution(unittest.TestCase):
    def setUp(self):
        cars=example_vehicles()
        self.data={'listings':[{'id':'hatch','revision':1,'facts':cars[2]},
                               {'id':'city','revision':1,'facts':cars[0]}],
                   'knowledge':[{'id':'fictional','question':'Are these real offers?',
                                 'answer':'Both are fictional examples.','status':'approved'}],
                   'knowledge_revision':2,'profile':None,'profile_revision':None}
        self.refs=['listing:city:r1:price','listing:hatch:r1:price',
                   'listing:city:r1:seats','listing:hatch:r1:seats',
                   'comparison:hatch:r1:city:r1:price_difference',
                   'comparison:hatch:r1:city:r1:mpg_combined_difference','knowledge:fictional:r2']
        self.answer=('Both selected vehicles meet your $25k vehicle budget and 5-seat commuting need '
            '(sources: listing:city:r1:price, listing:hatch:r1:price, listing:city:r1:seats, listing:hatch:r1:seats). '
            'The 2022 City Hybrid ($23,500, 44 MPG, 42k miles, 15 cu ft cargo) offers superior fuel economy vs '
            'the 2020 Compact Hatch ($18,900, 34 MPG, 58k miles, 22 cu ft cargo), a $4,600 and 10 MPG difference '
            '(comparison:hatch:r1:city:r1:price_difference, comparison:hatch:r1:city:r1:mpg_combined_difference). '
            'Hybrid has lower mileage but less cargo; both are fictional examples (knowledge:fictional:r2). '
            'Missing: ownership costs, reliability, safety ratings, taxes/fees (not established in listings).')
        self.body=ShoppingQuestion(message='My vehicle-price budget is $25,000. I need five seats for commuting and prefer fuel economy.',selected_ids=['hatch','city'])

    def replay(self, answer=None, data=None, refs=None):
        result={'preferences':{**Preferences().model_dump(),'budget_cents':2500000,'budget_kind':'vehicle',
                               'min_seats':5,'priorities':['fuel_economy']},
                'answer':answer or self.answer,'follow_up':'Do you prioritize cargo space, lower mileage, or required features?',
                'recommended_ids':[],'source_ids':self.refs if refs is None else refs}
        data=data or self.data
        return validate_answer(result,data,self.body,source_list(data))

    def test_recorded_valid_specs_resolve_to_exact_published_fields(self):
        result=self.replay()
        for identity in ['city','hatch']:
            for field in ['mpg_combined','mileage','cargo_cubic_feet']:
                self.assertIn(f'listing:{identity}:r1:{field}',result['source_ids'])
        self.assertEqual(result['answer'],self.answer)

    def test_other_vehicles_value_cannot_be_borrowed(self):
        for old,new in [('44 MPG','34 MPG'),('15 cu ft','22 cu ft'),('$23,500','$18,900'),('42k miles','58k miles')]:
            with self.subTest(new=new),self.assertRaises(Rejection):self.replay(self.answer.replace(old,new))

    def test_missing_or_unpublished_spec_remains_unknown(self):
        data=copy.deepcopy(self.data);data['listings'][1]['facts']['cargo_cubic_feet']=None
        with self.assertRaises(Rejection):self.replay(data=data)

    def test_uncited_vehicle_cannot_gain_implicit_evidence(self):
        refs=[x for x in self.refs if not x.startswith('listing:city:')]
        answer='City Hybrid (44 MPG, 42k miles, 15 cu ft cargo).'
        with self.assertRaises(Rejection):self.replay(answer=answer,refs=refs)

    def test_unknown_values_and_foreign_inline_sources_still_rejected(self):
        for answer in [self.answer+' A $999 fee applies.',self.answer+' [listing:foreign:r1:price]']:
            with self.assertRaises(Rejection):self.replay(answer)
