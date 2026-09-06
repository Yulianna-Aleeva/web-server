/* Генерация бокового меню и блока баланса */
document.addEventListener("DOMContentLoaded", function() {
    const menuContainer = document.getElementById("main-menu");
    if (!menuContainer) return;

    const currentPath = window.location.pathname;
    menuContainer.className = "col-md-3 bg-dark min-vh-100 p-4 text-white position-fixed top-0 start-0 d-flex flex-column";

    /* Функция сборки элемента меню */
    const item = (href, text, active, extra = "") => `
        <li class="nav-item">
            <a href="${href}" class="nav-link btn text-start text-white d-flex justify-content-between align-items-center ${active ? 'btn-primary active' : 'btn-dark'}">
                <span>${text}</span>${extra}
            </a>
        </li>`;

    /* Отрисовка разметки */
    menuContainer.innerHTML = `
        <h3 class="mb-4">Меню</h3>
        <ul class="nav flex-column gap-2">
            ${item("/", "Главная", currentPath === "/")}
            ${item("/categories", "Категории", currentPath.startsWith("/categories"))}
            ${item("/orders", "Заказы", currentPath.startsWith("/orders"),
                `<span id="cart-badge" class="badge rounded-pill bg-warning text-dark d-none">0</span>`)}
            ${item("/contacts", "Контакты", currentPath.startsWith("/contacts"))}
        </ul>

        <div class="mt-auto pt-3 border-top border-secondary">
            <div class="small text-secondary text-uppercase mb-2">Баланс</div>
            <div class="fs-5 fw-bold"><span id="balance-rubles">0</span> ${EMOJIS.RUBLE}</div>
            <div class="fs-5 fw-bold mb-3"><span id="balance-cookies">0</span> ${EMOJIS.COOKIE}</div>
            <div class="small text-secondary text-uppercase mb-2">Пополнить ${EMOJIS.RUBLE}</div>
            <div class="d-flex gap-2">
                ${[100, 500, 1000].map(v => `<button type="button" class="btn btn-outline-light btn-sm flex-fill px-1" data-topup="${v}">+${v}</button>`).join("")}
            </div>
        </div>`;
});
