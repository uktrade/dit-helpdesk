import common from "govuk-frontend/govuk/common";
import Button from "govuk-frontend/govuk/components/button/button";
import Header from "govuk-frontend/govuk/components/header/header";

import CopyButton from "./modules/copy-button";

var nodeListForEach = common.nodeListForEach;

var $buttons = document.querySelectorAll("[data-module=govuk-button]");
if ($buttons) {
  nodeListForEach($buttons, function ($button) {
    new Button($button).init();
  });
}

var $header = document.querySelector("[data-module=header]");
new Header($header).init();

var $copyButtons = document.querySelectorAll("[data-copy-button-for]");
if ($copyButtons) {
  nodeListForEach($copyButtons, function ($copyButton) {
    new CopyButton($copyButton).init();
  });
}
