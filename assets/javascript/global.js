var Details = require('govuk-frontend/components/details/details.js')
var Button = require('govuk-frontend/components/button/button.js')
var Accordion = require('govuk-frontend/components/accordion/accordion.js')
var ErrorSummary = require('govuk-frontend/components/error-summary/error-summary.js')
var common = require('govuk-frontend/common')
var commodityTree = require('./modules/commodity-tree')
// var showHideHeadings = require('./modules/showhide-headings')
var Modal = require('./modules/modal')
var CookiePolicy = require('./modules/cookie-policy');
var nodeListForEach = common.nodeListForEach

var cookiePolicy = new CookiePolicy(document, console);
cookiePolicy.initBanner('.app-cookie-banner', '.js-accept-cookie', 'cookies');

// accessibility feature
new Button(document).init()

// details polyfill for MS browsers
var $details = document.querySelectorAll('details')
if ($details) {
  nodeListForEach($details, function ($detail) {
    new Details($detail).init()
  })
}

// Find all global accordion components to enhance.
var $accordions = document.querySelectorAll('[data-module="accordion"]')
nodeListForEach($accordions, function ($accordion) {
  new Accordion($accordion).init()
})

var $commodityTree = document.querySelector('.app-hierarchy-tree')
if ($commodityTree) {
  commodityTree.init($commodityTree)
}

// error summary focus on page load
var $errorSummary = document.querySelector('[data-module="error-summary"]')
if ($errorSummary) {
  new ErrorSummary($errorSummary).init()
}

var $modals = document.querySelectorAll('[data-module="modal-dialogue"]')
if ($modals) {
  nodeListForEach($modals, function ($modal) {
    new Modal($modal).start()
  })
}

var CommoditySearchForm = {
  init: function (target, event, form) {
    this.target = target
    this.searchForm = form
    for (var i = 0; i < target.length; i++) {
      this.addListener(target[i], event)
    }
  },
  addListener: function (target, event) {
    var theForm = this.searchForm
    if (target.attachEvent) {
      target.attachEvent('on' + event, function () {
        theForm.submit()
      })
    } else {
      target.addEventListener(event, function () {
        theForm.submit()
      }, false)
    }
  }
}

var $searchForm = document.getElementById('commodity-search')
var $radioToggleElems = document.querySelectorAll('#toggle_headings .govuk-radios__input')
if ($radioToggleElems) {
  CommoditySearchForm.init($radioToggleElems, 'click', $searchForm)
}

var $selectSortBy = document.querySelectorAll('#select-sortby select')
if ($selectSortBy) {
  CommoditySearchForm.init($selectSortBy, 'change', $searchForm)
}

module.exports = {
  bindCookiePolicyForm: cookiePolicy.bindForm,

}
