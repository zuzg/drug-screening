function onPageLoad() {
    const navItems = document.querySelectorAll('.nav-link');
    navItems.forEach((item) => {
        if (item.href === window.location.href) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}
