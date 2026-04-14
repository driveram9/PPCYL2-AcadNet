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
        e.preventDefault() 
        sections.forEach(sec => sec.style.display = 'none');

        menuItems.forEach(i => i.parentElement.classList.remove('active'));

        this.parentElement.classList.add('active');

        const texto = this.querySelector('.text').textContent
            .toLowerCase()
                .replace(/\s+/g, '-');
        const target = document.getElementById(texto);
        if (target) target.style.display = 'block';
    });
});


const toggleModo = document.getElementById('toggle-modo');

toggleModo.addEventListener('change', function () {
    if (this.checked) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
});
