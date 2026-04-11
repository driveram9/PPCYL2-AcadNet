const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
    const li = item.parentElement;

    item.addEventListener('click', function () {
        allSideMenu.forEach(i=> {
            i.parentElement.classList.remove('active');
        })
        li.classList.add('active');
    })
});
const menuItems = document.querySelectorAll('#sidebar .side-menu.top li a');
const sections = document.querySelectorAll('main .section');

menuItems.forEach(item => {
    item.addEventListener('click', function (e) {
        e.preventDefault();
        // Ocultar todas las secciones
        sections.forEach(sec => sec.style.display = 'none');

        // Quitar la clase active de todos
        menuItems.forEach(i => i.parentElement.classList.remove('active'));

        // Activar el clic actual
        this.parentElement.classList.add('active');

        // Mostrar la sección correspondiente
        const texto = this.querySelector('.text').textContent
            .toLowerCase()
            .replace(/\s+/g, '-');
        const target = document.getElementById(texto);
        if (target) target.style.display = 'block';
    });
});

