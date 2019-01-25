//import Vue from 'vue'
//import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    items: {},
    expanded: [],
  },
  mutations: {
    addItem(state, di) {
      state.items[di["node_id"]] = di["component"]
    },
    addExpanded(state, node_id) {
      state.expanded.push(node_id)
    },
  },
  getters: {
      getItem: (state, getters) => (id) => {
        return state.items[id]
      },
      expanded: state => state.expanded
  }
//  getItem: (state) => (id) => {
//    return state.items[id]
//  }
//  getters: {
//    items: state => state.items
//  }
})


//var data = {
//  name: 'My Tree',
//  children: [
//    { name: 'hello' },
//    { name: 'wat' },
//    {
//      name: 'child folder',
//      children: [
//        {
//          name: 'child folder',
//          children: [
//            { name: 'hello' },
//            { name: 'wat' }
//          ]
//        },
//        { name: 'hello' },
//        { name: 'wat' },
//        {
//          name: 'child folder',
//          children: [
//            { name: 'hello' },
//            { name: 'wat' }
//          ]
//        }
//      ]
//    }
//  ]
//}

// define the item component
Vue.component('item', {
  template: '#item-template',
  props: {
    model: Object,
    store: Object,
    parent_node_id: String,
  },
  data: function () {
    return {
      open: false
    }
  },
  computed: {
    isFolder: function () {
      return this.model.children && this.model.children.length
    }
  },
  mounted: function () {

    if (typeof this.model['node_id'] == 'undefined'){
        console.log("cannot mount: ")
        console.log(this.model)
        return
    }

    di = {"node_id": this.model['node_id'], "component": this}
    this.$store.commit('addItem', di)
  },
  methods: {
    toggle: function () {
      if (this.isFolder) {
        this.open = !this.open
      }
      if (this.open) {
        this.$store.commit('addExpanded', this.model['node_id'])
      }
    },
    collapse: function() {
        this.open = false
    },
    expandParent: function() {
        this.expand()
        if(this.model['node_id'] != 'root'){
            this.$store.getters.getItem(this.parent_node_id).expandParent()
        }
    },
    expand: function() {
        this.open = true
        this.$store.commit('addExpanded', this.model['node_id'])
    },
    changeType: function () {
      if (!this.isFolder) {
        Vue.set(this.model, 'children', [])
        this.addChild()
        this.open = true
      }
    },
    addChild: function () {
      this.model.children.push({
        name: 'new stuff'
      })
    }
  }
})


//Vue.component('commodity_summary', {
//  props: ['selectedCommodity'],
//})


// boot up the demo
var demo = new Vue({
  el: '#demo',
  store,
  data: {
    store: this.$store,
    treeData: {"node_id": "root", "children": []},
    selectedCommodity: null,
  },
  mounted: function () {
     axios.get('/hierarchy_data/')
      .then(response => {
        this.treeData = response.data.treeData;
      })
      .catch(error => {
        console.log(error)
        this.errored = true
      })
      .finally(() => this.loading = false)
  },
  methods: {
    expandCommodity: function(commodityCode){
        nodeId = 'commodity:' + commodityCode
        this.$store.getters.getItem(nodeId).expandParent()
    },
    expandNode: function(nodeId) {
        this.$store.getters.getItem(nodeId).toggle()
    },
    collapseAll: function() {
        var expanded = this.$store.getters.expanded
        for (var i=expanded.length-1; i >= 0; i--) {
            var id = expanded[i]
            this.$store.getters.getItem(id).collapse()
        }
    }
  }
})