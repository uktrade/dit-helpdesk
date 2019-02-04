
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
})


// define the item component
Vue.component('item', {
  template: '#item-template',
  props: {
    model: {
        type: Object,
        default: function () {
          return { href: false, children: []}
        }
    },
    store: Object,
    parent_node_id: String,
  },
  data: function () {
    return {
      open: true
    }
  },
  computed: {
    isFolder: function () {
      if (typeof this.model == 'undefined'){
        return false
      }
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
    this.open = true
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


var demo = new Vue({
  el: '#demo',
  store,
  data: {
    store: this.$store,
    treeData: {"node_id": "root", "children": [], "href": false},
    selectedCommodity: null,
  },
  mounted: function () {
     axios.get('/heading_data/'+heading_code_4)
      .then(response => {
        this.treeData = response.data.treeData;
      })
      .catch(error => {
        console.log(error)
        this.errored = true
      })
      .finally(() => this.loading = false)
  },
})