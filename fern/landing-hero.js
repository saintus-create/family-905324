(function () {
  var openAskAi = function () {
    var button = document.getElementById('fern-ask-ai-button');
    if (button) button.click();
  };

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest && event.target.closest('.landing-hero__search');
    if (!trigger) return;
    event.preventDefault();
    openAskAi();
  });

  document.addEventListener('keydown', function (event) {
    if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== 'k') return;
    if (!document.querySelector('.landing-hero__search')) return;
    event.preventDefault();
    openAskAi();
  });
})();