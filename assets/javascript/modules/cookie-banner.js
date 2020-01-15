"use strict";
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

var OldCookieBanner = {
  init: function(name, value, options) {
    if (typeof value !== "undefined") {
      if (value === false || value === null) {
        return CookieBanner.setCookie(name, "", { days: -1 });
      } else {
        return CookieBanner.setCookie(name, value, options);
      }
    } else {
      return CookieBanner.getCookie(name);
    }
  },
  setCookie: function(name, value, options) {
    if (typeof options === "undefined") {
      options = {};
    }
    var cookieString = name + "=" + value + "; path=/";
    if (options.days) {
      var date = new Date();
      date.setTime(date.getTime() + options.days * 24 * 60 * 60 * 1000);
      cookieString = cookieString + "; expires=" + date.toGMTString();
    }
    if (document.location.protocol === "https:") {
      cookieString = cookieString + "; Secure";
    }
    document.cookie = cookieString;
  },
  getCookie: function(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(";");
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) === " ") {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return null;
  },
  addCookieMessage: function() {
    var message = document.querySelector(".app-cookie-banner");
    var hasCookieMessage = message && CookieBanner.init("cookie_seen") === null;

    var isCookiesPage = document.URL.indexOf("cookies") !== -1;

    var acceptCookiesBtn = document.querySelector(".js-accept-cookie");

    if (acceptCookiesBtn) {
      console.log(acceptCookiesBtn);
      this.addListener(acceptCookiesBtn);

      console.log("added listener");
    }

    // we display the cookie banner until they have saved their changes from the cookies page
    if (isCookiesPage) {
      //CookieBanner.init('cookie_seen', 'true', { days: 28 })
    }

    if (acceptCookiesBtn) {
      // CookieBanner.init('cookie_seen', 'true', { days: 28 })

      var banner = document.querySelector(".app-cookie-banner");
      if (acceptCookiesBtn.attachEvent) {
        acceptCookiesBtn.attachEvent("onclick", function() {
          banner.className = banner.className.replace(
            /app-cookie-banner--show/,
            ""
          );
        });
      } else {
        acceptCookiesBtn.addEventListener(
          "click",
          function() {
            banner.className = banner.className.replace(
              /app-cookie-banner--show/,
              ""
            );
          },
          false
        );
      }
    }

    // show the cookies banner until the cookie has been set
    if (hasCookieMessage) {
      message.className = message.className.replace(
        /js--cookie-banner/,
        "app-cookie-banner--show"
      );
    }
  },
  addListener: function(target) {
    // Support for IE < 9
    if (target.attachEvent) {
      target.attachEvent("onclick", this.addCookieMessage);
    } else {
      target.addEventListener("click", this.addCookieMessage, false);
    }
  }
};

function CookieBanner(document, console) {
  if (!console) {
    console = (function() {
      var nullf = function() {};

      return {
        log: nullf
      };
    })();
  }

  var cookiePreferencesName = "cookie_preferences_set",
    cookiesPolicyName = "cookies_policy";

  function setCookie(name, value, options) {
    if (typeof options === "undefined") {
      options = {};
    }
    var cookieString = name + "=" + value + "; path=/";
    if (options.days) {
      var date = new Date();
      date.setTime(date.getTime() + options.days * 24 * 60 * 60 * 1000);
      cookieString = cookieString + "; expires=" + date.toGMTString();
    }
    if (document.location.protocol === "https:") {
      cookieString = cookieString + "; Secure";
    }
    document.cookie = cookieString;
  }

  function getCookie(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(";");
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) === " ") {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return null;
  }

  function getDefaultPolicy() {
    var policy = {
      essential: true,
      settings: false,
      usage: false,
      campaigns: false
    };

    return policy;
  }

  function createPoliciesCookie(settings, usage, campaigns) {
    var policy = getDefaultPolicy();
    policy.settings = settings || false;
    policy.usage = usage || false;
    policy.campaigns = campaigns || false;
    var json = JSON.stringify(policy);
    setCookie(cookiesPolicyName, json, { days: 365 });
  }

  function hideCookieBanner(className) {
    console.log("hide cookiebanner with classname " + className);
    var banner = document.querySelector(className);
    banner.className = banner.className.replace(/app-cookie-banner--show/, "");
  }

  function displayCookieBanner(className) {
    console.log("displaying cookiebanner with classname " + className);
    var banner = document.querySelector(className);

    banner.className = banner.className.replace(
      /js--cookie-banner/,
      "app-cookie-banner--show"
    );
  }

  function bindAcceptAllCookiesButton(className, onClickFunction) {
    var button = document.querySelector(className);
    if (button.attachEvent) {
      button.attachEvent("onclick", onClickFunction);
    } else {
      button.addEventListener("click", onClickFunction, false);
    }
  }

  function enableCookieBanner(bannerClassName, acceptButtonClassName) {
    console.log("preferences have not been set - display cookie banner");
    displayCookieBanner(bannerClassName);
    bindAcceptAllCookiesButton(acceptButtonClassName, function() {
      console.log("clicked");

      var defaultPolicy = getDefaultPolicy();
      createPoliciesCookie(
        defaultPolicy.settings,
        defaultPolicy.usage,
        defaultPolicy.campaigns
      );

      //confirm that we've seen preferences
      setCookie(cookiePreferencesName, "true", { days: 365 });

      hideCookieBanner(bannerClassName);
      // return false in case button is a link
      return false;
    });
    return;
  }

  function init(bannerClassName, acceptButtonClassName, cookiesPolicyUrl) {
    if (!bannerClassName) {
      throw "Expected bannerClassName";
    }

    //Has the cookie policy been set?
    var preferenceCookie = getCookie(cookiePreferencesName);
    console.log(preferenceCookie);
    console.log("init cookie banner");

    var isCookiesPage = document.URL.indexOf(cookiesPolicyUrl) !== -1;
    console.log(isCookiesPage);

    if ((!preferenceCookie || preferenceCookie == null) && !isCookiesPage) {
      enableCookieBanner(bannerClassName, acceptButtonClassName);
    }
  }

  return {
    init: init
  };
}

module.exports = CookieBanner;
