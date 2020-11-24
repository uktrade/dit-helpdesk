from typing import List, Dict, Optional
import os

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


def _get_text_from_rule(rule: Optional[Element]) -> str:
    if rule:
        rule = rule.find('rule').text

    return rule


def _process_subpositions(subpositions: List[Element]) -> List[Dict]:
    subposition_list = []

    for subposition in subpositions:
        description = subposition.find('description')
        rule1 = subposition.find('rule1')
        rule2 = subposition.find('rule2')

        subposition_list.append({
            'description': description.text,
            'rule1': _get_text_from_rule(rule1),
            'rule2': _get_text_from_rule(rule2),
        })

    return subposition_list


def _process_positions(positions: Element) -> List[Dict]:
    positions_list = []

    for position in positions:
        description = position.find('description').text

        rule1 = position.find('rule1')
        rule1 = _get_text_from_rule(rule1)
        rule2 = position.find('rule2')
        rule2 = _get_text_from_rule(rule2)

        inclusions = position.find('positionCodeXml').find('inclusions')

        subpositions = position.findall('subPosition')
        subpositions_list = _process_subpositions(subpositions)

        positions_list.append({
            'code': position.attrib['positionCode'],
            'description': description,
            'rule1': rule1,
            'rule2': rule2,
            'subpositions': subpositions_list,
            'inclusions': inclusions.attrib,
        })

    return positions_list


def _process_notes(notes: Element) -> List[Dict]:
    notes_list = []

    for note in notes:
        identifier = note.attrib['identifier']
        content = note.text

        notes_list.append({
            'identifier': identifier,
            'content': content,
        })

    return notes_list


def parse_file(f):

    tree = ET.parse(f)
    root = tree.getroot()

    meta = root.find('meta')
    positions = root.find('positions')
    notes = root.find('notes')

    agreement_partners = meta.findall('agreementPartner')
    non_gb_partners = [ap for ap in agreement_partners if ap.attrib['code'] != 'GB']
    non_gb_partners_labels = [ap.find('label').text for ap in non_gb_partners]
    fta_name = f"FTA {', '.join(non_gb_partners_labels)}"
    countries_with_dates = [
        country_element.attrib
        for ap in non_gb_partners
        for country_element in ap.findall('country')
    ]

    positions_list = _process_positions(positions)

    notes_list = _process_notes(notes)

    output = {
        'name': fta_name,
        'countries_with_dates': countries_with_dates,
        'positions': positions_list,
        'notes': notes_list,
    }

    return output


if __name__ == '__main__':
    output = parse_file('PSRO_UK_EN-UK-CL-FTA.xml')
    import json
    json.dump(output, open('output.json', 'w'), indent=4)
