function CopyButton($copyButton) {
  this.$copyButton = $copyButton;

  this.handleClick = this.handleClick.bind(this);
}

CopyButton.prototype.init = function () {
  var inputID = this.$copyButton.dataset.copyButtonFor;
  this.$input = document.querySelector("#" + inputID);

  this.$copyButton.addEventListener("click", this.handleClick);
};

CopyButton.prototype.handleClick = function () {
  this.$input.select();
  document.execCommand("copy");
};

export default CopyButton;
