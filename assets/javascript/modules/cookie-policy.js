'use strict'

function CookieBanner (document, console) {
  if (!console) {
    console = (function () {
      var nullf = function () {
      }

      return {
        log: nullf
      }
    })()
  }

  var cookiePreferencesName = 'cookie_preferences_set'
  var cookiePreferencesDurationDays = 31

  var cookiesPolicyName = 'cookies_policy'
  var cookiesPolicyDurationDays = 365

  function setCookie (name, value, options) {
    if (typeof options === 'undefined') {
      options = {}
    }
    var cookieString = name + '=' + value + '; path=/'
    if (options.days) {
      var date = new Date()
      date.setTime(date.getTime() + options.days * 24 * 60 * 60 * 1000)
      cookieString = cookieString + '; expires=' + date.toGMTString()
    }
    if (document.location.protocol === 'https:') {
      cookieString = cookieString + '; Secure'
    }
    document.cookie = cookieString
  }

  function getCookie (name) {
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
  }

  var gtmUsageEventFired = false

  function raiseGTMUsageEvent () {
    if (gtmUsageEventFired) return

    window.dataLayer = window.dataLayer || []
    window.dataLayer.push({
      event: 'dit-enable-usage'
    })

    console.log('event has been raised')
    gtmUsageEventFired = true
  }

  function getDefaultPolicy () {
    var policy = {
      essential: true,
      settings: true,
      usage: false,
      campaigns: false
    }

    return policy
  }

  /**
   * Tries to find policy settings from saved cookie json.
   * Returns default policy if the cookie isn't set
   * Any errors parsing the cookie also returns default
   * @returns {{settings: boolean, campaigns: boolean, usage: boolean, essential: boolean}}
   */
  function getPolicyOrDefault () {
    var cookie = getCookie(cookiesPolicyName)
    var policy = getDefaultPolicy()
    if (!cookie || cookie == null) return policy

    try {
      var parsed = JSON.parse(cookie)

      policy.campaigns = parsed.campaigns || false
      policy.usage = parsed.usage || false
      policy.settings = parsed.settings || false

    } catch (e) {
      return policy
    }

    return policy

  }

  function createPoliciesCookie (settings, usage, campaigns) {
    var policy = getDefaultPolicy()
    policy.settings = settings || false
    policy.usage = usage || false
    policy.campaigns = campaigns || false
    var json = JSON.stringify(policy)
    setCookie(cookiesPolicyName, json, { days: cookiesPolicyDurationDays })
  }

  function hideCookieBanner (className) {
    console.log('hide cookiebanner with classname ' + className)
    var banner = document.querySelector(className)
    banner.className = banner.className.replace(/app-cookie-banner--show/, '')
  }

  function displayCookieBanner (className) {
    console.log('displaying cookiebanner with classname ' + className)
    var banner = document.querySelector(className)

    banner.className = banner.className.replace(
      /js--cookie-banner/,
      'app-cookie-banner--show'
    )
  }

  function bindAcceptAllCookiesButton (className, onClickFunction) {
    var button = document.querySelector(className)
    if (button.attachEvent) {
      button.attachEvent('onclick', onClickFunction)
    } else {
      button.addEventListener('click', onClickFunction, false)
    }
  }

  function setPreferencesCookie () {
    setCookie(cookiePreferencesName, 'true', { days: cookiePreferencesDurationDays })
  }

  function enableCookieBanner (bannerClassName, acceptButtonClassName) {
    console.log('preferences have not been set - display cookie banner')
    displayCookieBanner(bannerClassName)
    bindAcceptAllCookiesButton(acceptButtonClassName, function () {
      console.log('clicked')

      createPoliciesCookie(true, true, true)

      //confirm that we've seen preferences
      setPreferencesCookie()

      hideCookieBanner(bannerClassName)
      raiseGTMUsageEvent()

      // return false in case button is a link
      return false
    })
    return
  }

  function init (bannerClassName, acceptButtonClassName, cookiesPolicyUrl) {
    if (!bannerClassName) {
      throw 'Expected bannerClassName'
    }

    //Has the cookie policy been set?
    var preferenceCookie = getCookie(cookiePreferencesName)
    console.log(preferenceCookie)
    console.log('init cookie banner')

    var isCookiesPage = document.URL.indexOf(cookiesPolicyUrl) !== -1
    console.log(isCookiesPage)

    if ((!preferenceCookie || preferenceCookie == null) && !isCookiesPage) {
      enableCookieBanner(bannerClassName, acceptButtonClassName)
    }

    var policy = getPolicyOrDefault()
    console.log(policy)
    if (policy.usage) {
      raiseGTMUsageEvent()
    }

  }

  /**
   *
   * @param formSelector
   * @param radioButtons
   * Object {
   *   usage: "name-of-form-field",
   *   campaign : "name-of-campaign-radio-button-field",
   *   settings: "etc"
   * }
   *
   *
   */
  function bindCookiePolicyForm (formSelector, confirmationSelector, radioButtons) {

    if (typeof radioButtons !== 'object') {
      throw 'expected an object with radio button selectors'
    }

    console.log(formSelector)
    var form = document.querySelector(formSelector)

    if (!form) {
      throw formSelector + ' was not found'
    }

    var confirmation = document.querySelector(confirmationSelector)
    if (!confirmation) {
      throw confirmationSelector + ' was not found'
    }

    // Get current cookies policy
    var policy = getPolicyOrDefault()

    form[radioButtons.usage].value = policy.usage ? 'on' : 'off'
    form[radioButtons.settings].value = policy.settings ? 'on' : 'off'
    form[radioButtons.campaigns].value = policy.campaigns ? 'on' : 'off'

    var attachEventMethod = form.attachEvent || form.addEventListener
    attachEventMethod('submit', function (e) {

      var settings = form[radioButtons.settings].value == 'on'
      var usage = form[radioButtons.usage].value == 'on'
      var campaigns = form[radioButtons.campaigns].value == 'on'

      createPoliciesCookie(settings, usage, campaigns)
      setPreferencesCookie()

      confirmation.style = 'display:block;'
      window.scrollTo(0, 0)

      e.preventDefault()
      return false
    }, false)

    console.log('yeah binding that form for the win')
  }

  return {
    initBanner: init,
    bindForm: bindCookiePolicyForm
  }
}

module.exports = CookieBanner
