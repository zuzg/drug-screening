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


function onStageIndexChange(newIndex) {
    const points = document.querySelectorAll(".controls__point");
    points.forEach((point, index) => {
        if (index === newIndex) {
            point.classList.add("controls__point--active");
        } else {
            point.classList.remove("controls__point--active");
        }
        if (index < newIndex) {
            point.classList.add("controls__point--visited");
        } else {
            point.classList.remove("controls__point--visited");
        }
    });
}
