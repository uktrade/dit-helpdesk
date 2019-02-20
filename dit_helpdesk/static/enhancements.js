import ScrollingTable from './modules/scrolling-tables.module.js'

let $scrollingTables = document.querySelectorAll('[data-module="scrolling-table"]')

$scrollingTables.forEach(($scrollingTable) => {
  new ScrollingTable($scrollingTable).init()
})
