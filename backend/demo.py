"""Deterministic demo questions. No inference, credentials, or external requests."""
import re


def fields_for_question(question):
    text = re.sub(r"[?!.]+$", '', question.strip().lower()).strip()
    text = re.sub(r'\s+', ' ', text)
    price = {'price', 'what is the price', "what's the price", 'how much',
             'how much is it', 'how much does it cost'}
    mileage = {'mileage', 'what is the mileage', "what's the mileage",
               'how many miles', 'how many miles does it have'}
    both = {'price and mileage', 'price & mileage', 'what are the price and mileage',
            'mileage and price'}
    if text in price:
        return ['price']
    if text in mileage:
        return ['mileage']
    if text in both:
        return ['price', 'mileage']
    return []
