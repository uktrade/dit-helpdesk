var Details = require('govuk-frontend/components/details/details.js')
var Button = require('govuk-frontend/components/button/button.js')
var Accordion = require('govuk-frontend/components/accordion/accordion.js')
var ErrorSummary = require('govuk-frontend/components/error-summary/error-summary.js')
var common = require('govuk-frontend/common')
var commodityTree = require('./modules/commodity-tree')
var nodeListForEach = common.nodeListForEach

/*
  Cookie methods
  ==============
  Usage:
    Setting a cookie:
    CookieBanner.init('hobnob', 'tasty', { days: 30 });
    Reading a cookie:
    CookieBanner.init('hobnob');
    Deleting a cookie:
    CookieBanner.init('hobnob', null);
*/
var CookieBanner = {
  init: function (name, value, options) {
    if (typeof value !== 'undefined') {
      if (value === false || value === null) {
        return CookieBanner.setCookie(name, '', { days: -1 })
      } else {
        return CookieBanner.setCookie(name, value, options)
      }
    } else {
      return CookieBanner.getCookie(name)
    }
  },
  setCookie: function (name, value, options) {
    if (typeof options === 'undefined') {
      options = {}
    }
    var cookieString = name + '=' + value + '; path=/'
    if (options.days) {
      var date = new Date()
      date.setTime(date.getTime() + (options.days * 24 * 60 * 60 * 1000))
      cookieString = cookieString + '; expires=' + date.toGMTString()
    }
    if (document.location.protocol === 'https:') {
      cookieString = cookieString + '; Secure'
    }
    document.cookie = cookieString
  },
  getCookie: function (name) {
    var nameEQ = name + '='
    var cookies = document.cookie.split(';')
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i]
      while (cookie.charAt(0) === ' ') {
        cookie = cookie.substring(1, cookie.length)
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length))
      }
    }
    return null
  },
  addCookieMessage: function () {
    var message = document.querySelector('.js--cookie-banner')
    var hasCookieMessage = (message && CookieBanner.init('cookie_seen') === null)

    var isCookiesPage = document.URL.indexOf('cookies') !== -1

    // we only want to dismiss the cookie banner once they've visited the cookie page
    if (isCookiesPage) {
      CookieBanner.init('cookie_seen', 'true', { days: 28 })
    }

    // show the cookies banner until the cookie has been set
    if (hasCookieMessage) {
      message.className = message.className.replace(/js--cookie-banner/, 'app-cookie-banner--show')
    }
  }
}

CookieBanner.addCookieMessage()

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

 
