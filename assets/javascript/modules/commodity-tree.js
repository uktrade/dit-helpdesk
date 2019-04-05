require('govuk-frontend/vendor/polyfills/Function/prototype/bind')
require('govuk-frontend/vendor/polyfills/Event')
require('../vendor/polyfills/array-filter')
// enable collapsing on commodity tree
var commodityTree = {
    init: function ($module) {
        $module.addEventListener('click', commodityTree.toggleSections.bind(this))
    },
    toggleSections: function(event) {
        var $target = event.target
        if ($target.tagName !== 'A') {
            return false
        }
        
        var $parentNode = $target.parentNode
        if ($parentNode.className.indexOf('app-hierarchy-tree__parent--open') !== -1) {
            event.preventDefault()
            $parentNode.className = $parentNode.className.replace(/app-hierarchy-tree__parent--open/, 'app-hierarchy-tree__parent--closed js-closed')
            var childList = Array.prototype.filter.call($parentNode.childNodes, function(el){
                return el.className === 'app-hierarchy-tree--child';
            });
            childList[0].style.display = 'none';
        } else if ($parentNode.className.indexOf('js-closed') !== -1) {
            event.preventDefault()
            $parentNode.className = $parentNode.className.replace(/app-hierarchy-tree__parent--closed js-closed/, 'app-hierarchy-tree__parent--open')
            var childList = Array.prototype.filter.call($parentNode.childNodes, function(el){
                return el.className === 'app-hierarchy-tree--child';
            });
            childList[0].style.display = 'block';
        }
    }
}
module.exports = commodityTree