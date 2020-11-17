var Button = require('govuk-frontend/govuk/components/button/button.js')
var common = require('govuk-frontend/govuk/common')

var nodeListForEach = common.nodeListForEach

var $buttons = document.querySelectorAll('[data-module=govuk-button]')
if ($buttons) {
    nodeListForEach($buttons, function ($button) {
        new Button($button).init()
    })
}
