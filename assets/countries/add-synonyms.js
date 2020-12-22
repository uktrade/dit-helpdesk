const fs = require('fs')

const countriesToAddSynonymsTo = []

const countriesToRemove = [
  'XC', // Ceuta
  'XL'  // Melilla
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

fs.writeFileSync(
    './dit_helpdesk/countries/fixtures/countries_data.json',
    JSON.stringify(removed, null, 4))

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

fs.writeFileSync(
    './dit_helpdesk/static_collected/js/location-autocomplete-graph.json',
    JSON.stringify(graph, null, 4))
