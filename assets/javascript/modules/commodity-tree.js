require('govuk-frontend/vendor/polyfills/Function/prototype/bind')
require('govuk-frontend/vendor/polyfills/Element/prototype/classList')
require('govuk-frontend/vendor/polyfills/Event')
// enable collapsing on commodity tree
var commodityTree = {
    init: function ($module) {
        console.log($module)
        /$module.addEventListener('click', commodityTree.handleClick.bind(this))
        // commodityTree.handleClick()
    },
    collapseSection: function() {
    },
    handleClick: function(event) {
        console.log('yes')
    }
}
module.exports = commodityTree