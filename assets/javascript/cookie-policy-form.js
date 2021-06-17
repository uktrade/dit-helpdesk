var CookiePolicy = require("./modules/cookie-policy");

var cookiePolicy = new CookiePolicy();
cookiePolicy.bindForm(
  "#cookie-preferences-form",
  ".cookie-settings__confirmation",
  {
    usage: "cookies-usage",
    campaigns: "cookies-campaigns",
    settings: "cookies-settings",
  }
);

// eslint-disable-next-line
bustedfunction();
