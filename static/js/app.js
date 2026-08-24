(function () {
  window.copyShareLink = function () {
    var input = document.getElementById('share-url-input');
    if (!input) return;
    navigator.clipboard.writeText(input.value).then(function () {
      var btn = document.querySelector('.share-copy-btn');
      if (btn) {
        btn.innerHTML = '<i class="bi bi-check2"></i>';
        setTimeout(function () { btn.innerHTML = '<i class="bi bi-clipboard"></i>'; }, 2000);
      }
    });
  };
})();
