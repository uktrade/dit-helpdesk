var Details = require("govuk-frontend/govuk/components/details/details.js");
var Button = require("govuk-frontend/govuk/components/button/button.js");
var Accordion = require("govuk-frontend/govuk/components/accordion/accordion.js");
var ErrorSummary = require("govuk-frontend/govuk/components/error-summary/error-summary.js");
var common = require("govuk-frontend/govuk/common");
var commodityTree = require("./modules/commodity-tree");
// var showHideHeadings = require('./modules/showhide-headings')
var Modal = require("./modules/modal");
var CookiePolicy = require("./modules/cookie-policy");
var nodeListForEach = common.nodeListForEach;

var addListener = function (target, event, handler) {
  if (target.attachEvent) {
    target.attachEvent("on" + event, handler);
  } else {
    target.addEventListener(event, handler, false);
  }
};

var cookiePolicy = new CookiePolicy();
cookiePolicy.initBanner(".app-cookie-banner", ".js-accept-cookie", "cookies");

// accessibility feature
new Button(document).init();

// details polyfill for MS browsers
var $details = document.querySelectorAll("details");
if ($details) {
  nodeListForEach($details, function ($detail) {
    new Details($detail).init();
  });
}

// Find all global accordion components to enhance.
var $accordions = document.querySelectorAll(
  '[data-module="accordion"], [data-module="govuk-accordion"]'
);
nodeListForEach($accordions, function ($accordion) {
  new Accordion($accordion).init();
});

var $commodityTree = document.querySelector(".app-hierarchy-tree");
if ($commodityTree) {
  commodityTree.init($commodityTree);
}

// error summary focus on page load
var $errorSummary = document.querySelector('[data-module="error-summary"]');
if ($errorSummary) {
  new ErrorSummary($errorSummary).init();
}

var $modals = document.querySelectorAll('[data-module="modal-dialogue"]');
if ($modals) {
  nodeListForEach($modals, function ($modal) {
    new Modal($modal).start();
  });
}

var makeRequest = function (url, handler) {
  var request = new XMLHttpRequest();

  request.open("GET", url, true);

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      var resp = request.responseText;
      handler(resp);
    }
  };

  request.send();
};

var $hierarchyModalLinks = document.querySelectorAll(".hierarchy-modal");
if ($hierarchyModalLinks) {
  var modal = document.querySelector("#hierarchy-modal");

  nodeListForEach($hierarchyModalLinks, function ($modalLink) {
    console.log("modal link: " + $modalLink);
    addListener($modalLink, "click", function () {
      console.log("Inside onclick");
      modal.querySelector(".app-modal-dialogue__content").innerHTML = "";

      var url = $modalLink.getAttribute("data-href");
      makeRequest(url, function (responseText) {
        modal.querySelector(".app-modal-dialogue__content").innerHTML =
          responseText;

        var modalWindow = new Modal(modal);
        modalWindow.start();
        modal.open();
      });
    });
  });
}

var CommoditySearchForm = {
  init: function (target, event, form) {
    this.target = target;
    this.searchForm = form;
    for (var i = 0; i < target.length; i++) {
      this.addListener(target[i], event);
    }
  },
  setChangedBy: function (target) {
    var changedByValue = target.dataset.changedBy;
    if (changedByValue) {
      var $changedBy = document.querySelector("#changed_by");
      $changedBy.value = changedByValue;
    }
  },
  addListener: function (target, event) {
    var theForm = this.searchForm;
    var self = this;
    if (target.attachEvent) {
      target.attachEvent("on" + event, function () {
        self.setChangedBy(target);
        theForm.submit();
      });
    } else {
      target.addEventListener(
        event,
        function () {
          self.setChangedBy(target);
          theForm.submit();
        },
        false
      );
    }
  },
};

var $searchForm = document.getElementById("commodity-search");
var $radioToggleElems = document.querySelectorAll(
  "#toggle_headings .govuk-radios__input"
);
if ($radioToggleElems) {
  CommoditySearchForm.init($radioToggleElems, "click", $searchForm);
}

var $selectSortBy = document.querySelectorAll("#select-sortby select");
if ($selectSortBy) {
  CommoditySearchForm.init($selectSortBy, "change", $searchForm);
}
