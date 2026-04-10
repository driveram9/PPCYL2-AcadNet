const menuItems = document.querySelectorAll('#sidebar .side-menu.top li a');
const sections = document.querySelectorAll('.section');

menuItems.forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();

        sections.forEach(sec => sec.style.display = 'none');

        menuItems.forEach(i => i.parentElement.classList.remove('active'));

        this.parentElement.classList.add('active');

        const texto = this.querySelector('.text').textContent.toLowerCase().replace(" ","_");
        const target = document.getElementById(texto);

        if (target) target.style.display = 'block';
    });
});