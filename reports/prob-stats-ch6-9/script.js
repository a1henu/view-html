// 共享脚本：侧边栏滚动高亮 (scrollspy) + 回到顶部
(function () {
  function initScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll('.sidebar nav a[href^="#"]'));
    if (!links.length) return;
    var targets = links
      .map(function (a) {
        var el = document.getElementById(a.getAttribute('href').slice(1));
        return el ? { link: a, el: el } : null;
      })
      .filter(Boolean);

    function onScroll() {
      var pos = window.scrollY + 120;
      var current = null;
      for (var i = 0; i < targets.length; i++) {
        if (targets[i].el.offsetTop <= pos) current = targets[i];
      }
      links.forEach(function (l) { l.classList.remove('active'); });
      if (current) current.link.classList.add('active');
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (document.readyState !== 'loading') initScrollSpy();
  else document.addEventListener('DOMContentLoaded', initScrollSpy);
})();
