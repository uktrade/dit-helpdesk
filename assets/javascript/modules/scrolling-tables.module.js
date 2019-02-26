function ScrollingTable ($component) {
  const $table = $component.querySelector('table')

  this.init = () => {
    const $wrapper = document.createElement('div')
    $wrapper.className = 'app-fullscreen-scrollable-table'

    $wrapper.addEventListener('scroll', (event) => {
      this.toggleShadows(event.target)
    }, {
      passive: true
    })

    $table.parentNode.insertBefore($wrapper, $table)
    $wrapper.appendChild($table)

    this.toggleShadows($wrapper)
  }

  this.toggleShadows = ($target) => {
    const wrapperWidth = $target.offsetWidth
    const tableWidth = $target.querySelector('table').offsetWidth
    const amountScrolled = $target.scrollLeft

    const showLeft = (amountScrolled > 0)
    const showRight = (amountScrolled < tableWidth - wrapperWidth)

    $target.classList.toggle('app-fullscreen--showleft', showLeft)
    $target.classList.toggle('app-fullscreen--showright', showRight)
  }
}

export default ScrollingTable
