$(document).ready(function() {
  const themeToggleButton = $('#theme-toggle-button');
  const body = $('body');
  // documentElement (<html> tagı) üzerinde de sınıfı yönetmek daha tutarlı olabilir
  const htmlElement = $(document.documentElement);
  const moonIcon = 'bi-moon-stars-fill';
  const sunIcon = 'bi-brightness-high-fill';

  // Sayfa yüklendiğinde ikonu ve body/html sınıfını ayarla
  function setInitialTheme() {
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
      body.addClass('dark-mode');
      htmlElement.addClass('dark-mode'); // HTML elementine de ekle
      themeToggleButton.html(`<i class="bi ${sunIcon}"></i>`); // Karanlık modda güneş ikonu
    } else {
      body.removeClass('dark-mode');
      htmlElement.removeClass('dark-mode'); // HTML elementinden kaldır
      themeToggleButton.html(`<i class="bi ${moonIcon}"></i>`); // Açık modda ay ikonu
    }
  }

  setInitialTheme(); // Sayfa ilk yüklendiğinde temayı ayarla

  themeToggleButton.on('click', function() {
    body.toggleClass('dark-mode'); // dark-mode sınıfını değiştir
    htmlElement.toggleClass('dark-mode'); // HTML elementindeki sınıfı da değiştir

    // Yeni temayı localStorage'a kaydet
    if (body.hasClass('dark-mode')) {
      localStorage.setItem('theme', 'dark');
      $(this).html(`<i class="bi ${sunIcon}"></i>`); // İkonu güneşe çevir
       console.log("Dark mode enabled");
    } else {
      localStorage.setItem('theme', 'light');
      $(this).html(`<i class="bi ${moonIcon}"></i>`); // İkonu aya çevir
       console.log("Light mode enabled");
    }
  });
});