  function Modal ($module) {
    this.$module = $module
  }
  Modal.prototype.start = function () {
    this.$dialogBox = this.$module.querySelector('.app-modal-dialogue__box')
    this.$closeButton = (
        this.$module.querySelector('.app-modal-dialogue__close-button')
        || this.$module.querySelector('.app-modal-dialogue__close-button-white')
    )
    this.$html = document.querySelector('html')
    this.$body = document.querySelector('body')

    this.$module.resize = this.handleResize.bind(this)
    this.$module.open = this.handleOpen.bind(this)
    this.$module.close = this.handleClose.bind(this)
    this.$module.focusDialog = this.handleFocusDialog.bind(this)
    this.$module.boundKeyDown = this.handleKeyDown.bind(this)

    var $triggerElements = document.querySelectorAll(
      '[data-toggle="modal"][data-target="' + this.$module.id + '"]'
    )

    $triggerElements.forEach(function ($triggerElement) {
      if ($triggerElement) {
        $triggerElement.addEventListener('click', this.$module.open)
      }
  
      if (this.$closeButton) {
        this.$closeButton.addEventListener('click', this.$module.close)
      }
    }, this)
  }

  Modal.prototype.handleResize = function (size) {
    if (size == "narrow") {
      this.$dialogBox.classList.remove('app-modal-dialogue__box--wide')
    }

    if (size == "wide") {
      this.$dialogBox.classList.add('app-modal-dialogue__box--wide')
    }
  }

  Modal.prototype.handleOpen = function (event) {
    if (event) {
      event.preventDefault()
    }

    this.$html.classList.add('app-template--modal')
    this.$body.classList.add('app-template__body--modal')
    this.$focusedElementBeforeOpen = document.activeElement
    this.$module.style.display = 'block'
    this.$dialogBox.focus()

    document.addEventListener('keydown', this.$module.boundKeyDown, true)
  }

  Modal.prototype.handleClose = function (event) {
    if (event) {
      event.preventDefault()
    }

    this.$html.classList.remove('app-template--modal')
    this.$body.classList.remove('app-template__body--modal')
    this.$module.style.display = 'none'
    this.$focusedElementBeforeOpen.focus()

    document.removeEventListener('keydown', this.$module.boundKeyDown, true)
  }

  Modal.prototype.handleFocusDialog = function () {
    this.$dialogBox.focus()
  }

  // while open, prevent tabbing to outside the dialogue
  // and listen for ESC key to close the dialogue
  Modal.prototype.handleKeyDown = function (event) {
    var KEY_TAB = 9
    var KEY_ESC = 27

    switch (event.keyCode) {
      case KEY_TAB:
        if (event.shiftKey) {
          if (document.activeElement === this.$dialogBox) {
            event.preventDefault()
            this.$closeButton.focus()
          }
        } else {
          if (document.activeElement === this.$closeButton) {
            event.preventDefault()
            this.$dialogBox.focus()
          }
        }

        break
      case KEY_ESC:
        this.$module.close()
        break
      default:
        break
    }
  }
module.exports = Modal
