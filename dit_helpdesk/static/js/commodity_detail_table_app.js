

//const Modal = {
//  name: 'modal',
//  template: '#measure-conditions-modal',
//  methods: {
//    close(event) {
//      this.$emit('close');
//    },
//  },
//};


Vue.component('conditions-modal', {
    template: '#measure-conditions-modal',
    methods: {
        close(event) {
            this.$emit('close');
        },
    },
})


Vue.component('demo-grid', {
  template: '#grid-template',
  props: {
    data: Array,
    columns: Array,
    filterKey: String
  },
  data: function () {
    var sortOrders = {}
    this.columns.forEach(function (key) {
      sortOrders[key] = 1
    })
    return {
      sortKey: '',
      sortOrders: sortOrders
    }
  },
  computed: {
    filteredData: function () {
      var sortKey = this.sortKey
      var filterKey = this.filterKey && this.filterKey.toLowerCase()
      var order = this.sortOrders[sortKey] || 1
      var data = this.data
      if (filterKey) {
        data = data.filter(function (row) {
          return Object.keys(row).some(function (key) {
            return String(row[key]).toLowerCase().indexOf(filterKey) > -1
          })
        })
      }
      if (sortKey) {
        data = data.slice().sort(function (a, b) {
          a = a[sortKey]
          b = b[sortKey]
          return (a === b ? 0 : a > b ? 1 : -1) * order
        })
      }
      return data
    }
  },
  filters: {
    capitalize: function (str) {
      return str.charAt(0).toUpperCase() + str.slice(1)
    }
  },
  methods: {
    sortBy: function (key) {
      this.sortKey = key
      this.sortOrders[key] = this.sortOrders[key] * -1
    }
  }
})


var demo = new Vue({
  el: '#demo',
  data: {
    //isModalVisible: false,
    searchQuery: "",
    gridColumns: [
        'country', 'measure_description',  'measure_value', 'conditions_html',
        'excluded_countries', 'legal_base_html', 'start_end_date', 'footnotes_html'
    ],
    gridData: []
  },
  methods: {
  },
  mounted: function () {

     axios.get("commodity_measures_table/"+commodityCode+"/"+originCountry)
      .then(response => {
        this.gridData = response.data.gridData;
      })
      .catch(error => {
        console.log(error)
      })
  }
})
