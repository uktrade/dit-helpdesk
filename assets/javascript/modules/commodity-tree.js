require('govuk-frontend/govuk/vendor/polyfills/Function/prototype/bind')
require('govuk-frontend/govuk/vendor/polyfills/Event')
require('../vendor/polyfills/array-filter')

// enable collapsing on commodity tree
var commodityTree = {
  init: function ($module) {
    $module.addEventListener('click', commodityTree.toggleSections.bind(this))
    this.scrollToElement(window.location.pathname)
  },
  toggleSections: function (event) {
    var $target = event.target
    if ($target.tagName !== 'A') {
      return false
    }

    var $parentNode = $target.parentNode

    if ($parentNode.className.indexOf('app-hierarchy-tree__parent--open') !== -1) {
      event.preventDefault()
      $parentNode.className = $parentNode.className.replace(/app-hierarchy-tree__parent--open/, 'app-hierarchy-tree__parent--closed js-closed')
      var childList = Array.prototype.filter.call($parentNode.childNodes, function (el) {
        return el.className === 'app-hierarchy-tree--child'
      })

      childList[0].style.display = 'none'
    } else if ($parentNode.className.indexOf('js-closed') !== -1) {
      event.preventDefault()
      $parentNode.className = $parentNode.className.replace(/app-hierarchy-tree__parent--closed js-closed/, 'app-hierarchy-tree__parent--open')
      var childList = Array.prototype.filter.call($parentNode.childNodes, function (el) {
        return el.className === 'app-hierarchy-tree--child'
      })

      childList[0].style.display = 'block'
    }
  },
  scrollToElement: function (url) {
    // only run when the search has found a valid code
    if (window.location.pathname.indexOf('hierarchy') === -1) {
      return false
    }

    var element = document.getElementById(this.getFragmentFromUrl(url))
    // element.scrollIntoView() - UH-313 this causes jarring browser movement after navigate
    // focus on the link
    element.childNodes[0].focus({ preventScroll: false })

  },
  getFragmentFromUrl: function(url){
    if (url.indexOf('#') === -1) {
      return url.substring(url.lastIndexOf('/') + 1, url.length)
    } else {
      return url.substring(url.lastIndexOf('#') + 1, url.length)
    }
  }
}
module.exports = commodityTree
