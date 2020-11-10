# Generated by Django 2.2.13 on 2020-10-21 09:41
from django.db import migrations

import logging


trade_data = [
    {'Country code': 'CO',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-andean-countries-trade-agreement',
     'Mendel agreement label': 'ANDEAN-COUNTRIES',
     'TWUK content template label': 'ANDEAN-COUNTRIES'},
    {'Country code': 'EC',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-andean-countries-trade-agreement',
     'Mendel agreement label': 'ANDEAN-COUNTRIES',
     'TWUK content template label': 'ANDEAN-COUNTRIES'},
    {'Country code': 'PE',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-andean-countries-trade-agreement',
     'Mendel agreement label': 'ANDEAN-COUNTRIES',
     'TWUK content template label': 'ANDEAN-COUNTRIES'},
    {'Country code': 'AG',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'BB',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'BZ',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'DM',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'DO',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'GD',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'GY',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'JM',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'KN',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'LC',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'VC',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'SR',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'BS',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'TT',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/cariforum-uk-economic-partnership-agreement',
     'Mendel agreement label': 'CARIFORUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'CR',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'SV',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'GT',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'HN',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'NI',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'PA',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-central-america-association-agreement',
     'Mendel agreement label': 'CENTRAL-AMERICA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'CL',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-chile-association-agreement',
     'Mendel agreement label': 'CHILE',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'MG',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/esa-uk-economic-partnership-agreement-epa--2',
     'Mendel agreement label': 'ESA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'MU',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/esa-uk-economic-partnership-agreement-epa--2',
     'Mendel agreement label': 'ESA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'SC',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/esa-uk-economic-partnership-agreement-epa--2',
     'Mendel agreement label': 'ESA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'ZW',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/esa-uk-economic-partnership-agreement-epa--2',
     'Mendel agreement label': 'ESA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'CI',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-AGR-SIGNED-NO-LINK',
     'TWUK content template label': 'EU-AGR-SIGNED-NO-LINK'},
    {'Country code': 'UA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-AGR-SIGNED-NO-LINK',
     'TWUK content template label': 'EU-AGR-SIGNED-NO-LINK'},
    {'Country code': 'AT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'BE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'BG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'HR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'CY',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'CZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'DK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'EE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'FI',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'FR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'DE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'GR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'HU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'IE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'IT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'LV',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'LT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'LU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'MT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'NL',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'PL',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'PT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'RO',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'SK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'SI',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'ES',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'SE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-MEMBER',
     'TWUK content template label': 'EU-MEMBER'},
    {'Country code': 'DZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'AD',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'BA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'SZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'MK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'SM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'XS',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-NON-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-NON-WTO'},
    {'Country code': 'AL',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'CM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'CA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'EG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'GH',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'KE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'MX',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'MD',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'ME',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'SG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'EU-NOAGR-FOR-EXIT-WTO',
     'TWUK content template label': 'EU-NOAGR-FOR-EXIT-WTO'},
    {'Country code': 'FO',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-faroe-islands-free-trade-agreement-fta',
     'Mendel agreement label': 'FAROE-ISLANDS',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'GE',
     'GOVUK FTA URL': 'https://www.gov.uk/government/publications/ukgeorgia-strategic-partnership-and-cooperation-agreement-cs-georgia-no12019',
     'Mendel agreement label': 'GEORGIA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'IS',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'ICELAND-NORWAY',
     'TWUK content template label': 'ICELAND-NORWAY'},
    {'Country code': 'NO',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'ICELAND-NORWAY',
     'TWUK content template label': 'ICELAND-NORWAY'},
    {'Country code': 'IL',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-israel-trade-and-partnership-agreement',
     'Mendel agreement label': 'ISRAEL',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'JP',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'JAPAN',
     'TWUK content template label': 'JAPAN'},
    {'Country code': 'JO',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-jordan-association-agreement',
     'Mendel agreement label': 'JORDAN',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'XK',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-kosovopartnership-trade-and-cooperationagreement',
     'Mendel agreement label': 'KOSOVO',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'LB',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-lebanon-association-agreement',
     'Mendel agreement label': 'LEBANON',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'LI',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-switzerland-liechtenstein-trade-agreement',
     'Mendel agreement label': 'LIECHTENSTEIN',
     'TWUK content template label': 'CH-LI'},
    {'Country code': 'MA',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-morocco-association-agreement',
     'Mendel agreement label': 'MOROCCO',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'FJ',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-pacific-economic-partnership-agreement',
     'Mendel agreement label': 'PACIFIC-STATES',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'PG',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-pacific-economic-partnership-agreement',
     'Mendel agreement label': 'PACIFIC-STATES',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'PS',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-palestinian-authority-political-trade-and-partnership-agreement',
     'Mendel agreement label': 'PALESTINIAN-AUTHORITY',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'BW',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/sacum-uk-economic-partnership-agreement-epa',
     'Mendel agreement label': 'SACUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'LS',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/sacum-uk-economic-partnership-agreement-epa',
     'Mendel agreement label': 'SACUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'MZ',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/sacum-uk-economic-partnership-agreement-epa',
     'Mendel agreement label': 'SACUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'NA',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/sacum-uk-economic-partnership-agreement-epa',
     'Mendel agreement label': 'SACUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'ZA',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/sacum-uk-economic-partnership-agreement-epa',
     'Mendel agreement label': 'SACUM',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'KR',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-south-korea-trade-agreement',
     'Mendel agreement label': 'SOUTH-KOREA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'CH',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-switzerland-trade-agreement',
     'Mendel agreement label': 'SWITZERLAND',
     'TWUK content template label': 'CH-LI'},
    {'Country code': 'TN',
     'GOVUK FTA URL': 'https://www.gov.uk/government/collections/uk-tunisia-association-agreement',
     'Mendel agreement label': 'TUNISIA',
     'TWUK content template label': 'EU-AGR-SIGNED-LINK'},
    {'Country code': 'TR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'TURKEY',
     'TWUK content template label': 'TURKEY'},
    {'Country code': 'VN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'VN',
     'TWUK content template label': 'VN'},
    {'Country code': 'AF',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'AO',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'AR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'AM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'AU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BH',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BD',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BJ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BO',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BF',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'BI',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'KH',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CV',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CF',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'TD',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CD',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'CU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'DJ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'GA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'GN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'GW',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'HT',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'IN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'KZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'KW',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'KG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'LA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'LR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MW',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MY',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MV',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'ML',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MR',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'MM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'NP',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'NZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'NE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'NG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'OM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'PK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'PY',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'PH',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'QA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'RU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'RW',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'WS',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'SA',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'SN',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'SL',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'SB',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'LK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'TJ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'TZ',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'TH',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'GM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'TG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'UG',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'AE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'US',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'UY',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'VU',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'VE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'YE',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'ZM',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'},
    {'Country code': 'HK',
     'GOVUK FTA URL': '',
     'Mendel agreement label': 'WTO',
     'TWUK content template label': 'WTO'}
]


def populate_trade_scenarios(apps, schema_editor):
    Country = apps.get_model('countries', 'Country')

    for item in trade_data:
        country_code = item['Country code']
        trade_scenario = item['TWUK content template label']
        content_url = item['GOVUK FTA URL']

        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            logging.error("Could not find country with country_code=%s", country_code)
        else:
            country.scenario = trade_scenario
            country.content_url = content_url
            country.save()


def unpopulate_trade_scenarios(apps, schema_editor):
    Country = apps.get_model('countries', 'Country')

    Country.objects.all().update(scenario='WTO')


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0003_auto_20201021_1041'),
    ]

    operations = [
        migrations.RunPython(populate_trade_scenarios, unpopulate_trade_scenarios)
    ]
