import Details from "govuk-frontend/govuk/components/details/details";
import Button from "govuk-frontend/govuk/components/button/button";
import Accordion from "govuk-frontend/govuk/components/accordion/accordion";
import ErrorSummary from "govuk-frontend/govuk/components/error-summary/error-summary";
import common from "govuk-frontend/govuk/common";
import commodityTree from "./modules/commodity-tree";
import Modal from "./modules/modal";
import CookiePolicy from "./modules/cookie-policy";

var nodeListForEach = common.nodeListForEach;

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
    $modalLink.addEventListener("click", function (evt) {
      evt.preventDefault();
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
    target.addEventListener(
      event,
      function () {
        self.setChangedBy(target);
        theForm.submit();
      },
      false
    );
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
