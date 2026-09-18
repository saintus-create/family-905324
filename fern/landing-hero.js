(function () {
  document.addEventListener('keydown', function (event) {
    if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== 'k') return;
    if (!document.querySelector('.landing-hero__search')) return;
    var button = document.getElementById('fern-ask-ai-button');
    if (!button) return;
    event.preventDefault();
    button.click();
  });
})();
