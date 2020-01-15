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

module.exports = CookieBanner;
