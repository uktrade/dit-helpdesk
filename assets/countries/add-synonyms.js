const fs = require('fs')

const countriesToAddSynonymsTo = [
  {
    // This is the country code of that all of the synonyms will redirect to.
    countryCode: 'EU',
    // An array of strings containing all of the synonyms.
    synonyms: [
      'Austria',
      'Belgium',
      'Bulgaria',
      'Croatia',
      'Cyprus',
      'Czechia',
      'Denmark',
      'Estonia',
      'Finland',
      'France',
      'Germany',
      'Greece',
      'Hungary',
      'Ireland',
      'Italy',
      'Latvia',
      'Lithuania',
      'Luxembourg',
      'Malta',
      'Netherlands',
      'Poland',
      'Portugal',
      'Romania',
      'Slovakia',
      'Slovenia',
      'Spain',
      'Sweden'
    ]
  }
]

const countriesToRemove = [
  'AT',
  'BE',
  'BG',
  'HR',
  'CY',
  'CZ',
  'DK',
  'EE',
  'FI',
  'FR',
  'DE',
  'GR',
  'HU',
  'IE',
  'IT',
  'LV',
  'LT',
  'LU',
  'MT',
  'NL',
  'PL',
  'PT',
  'RO',
  'SK',
  'SI',
  'ES',
  'SE'
]

const countriesData = require('./countries-data.json')

const removed = []

countriesData.forEach((country, i) => {
  let addCountry = true

  countriesToRemove.forEach((code, i) => {
    if (country.fields.country_code === code) {
      addCountry = false
    }
  })

  if (addCountry === true) {
    removed.push(country)
  }
})

fs.writeFileSync('./dit_helpdesk/countries/fixtures/countries_data.json', JSON.stringify(removed))

let graph = {}

removed.forEach((countryObject) => {
  const code = countryObject.fields.country_code.toLowerCase()
  const name = countryObject.fields.name

  graph[code] = {
    'names': {
      'en-GB': name
    },
    'meta': {
      'canonical': true,
      'canonical-mask': 1,
      'stable-name': true
    },
    'edges': {
      'from': []
    }
  }
})

countriesToAddSynonymsTo.forEach((countryToSynonymise) => {
  const country = countryToSynonymise.countryCode.toLowerCase()

  countryToSynonymise.synonyms.forEach((synonym) => {
    graph['nym:' + synonym.toLowerCase()] = {
      'names': {
        'en-GB': synonym
      },
      'meta': {
        'canonical': false,
        'canonical-mask': 1,
        'stable-name': true
      },
      'edges': {
        'from': [ country ]
      }
    }
  })
})

fs.writeFileSync('./dit_helpdesk/static_collected/js/location-autocomplete-graph.json', JSON.stringify(graph))
