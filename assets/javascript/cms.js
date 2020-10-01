var Button = require('govuk-frontend/components/button/button.js')
var Tabs = require('govuk-frontend/components/tabs/tabs.js')
var common = require('govuk-frontend/common')

var nodeListForEach = common.nodeListForEach

new Tabs(document).init()

var $buttons = document.querySelectorAll('[data-module=govuk-button]')
if ($buttons) {
    nodeListForEach($buttons, function ($button) {
        new Button($button).init()
    })
}
