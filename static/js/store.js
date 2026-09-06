(function () {
    const KEYS = {
        balance:   "my_relax_balance",
        cart:      "my_relax_cart",
        orders:    "my_relax_orders",
        inventory: "my_relax_inventory",
        seq:       "my_relax_order_seq"
    };
    const CATEGORY_TITLES = { cookies: "Печеньки", hints: "Подсказки", toys: "Реплики игр" };
    const STATUS_CLASS = { cookies: "status-cookies-border", hints: "status-success-border", toys: "status-toys-border" };

    /* Хранилище данных */
    function read(key, fallback) {
        try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
        catch (e) { return fallback; }
    }
    function write(key, value) { localStorage.setItem(key, JSON.stringify(value)); }
    function emoji(key) { return (typeof EMOJIS !== "undefined" && EMOJIS[key]) || key; }

    function findProduct(id) {
        for (const [category, items] of Object.entries(CATALOG_DATA)) {
            const item = items.find(i => i.id === Number(id));
            if (item) return { ...item, category };
        }
        return null;
    }

    function productTitle(p) { return p.category === "cookies" ? `${p.name} ${emoji(p.badge)}` : p.name; }

    /* Управление балансом */
    function getBalance() {
        const b = read(KEYS.balance, {});
        return { rubles: Number(b.rubles) || 0, cookies: Number(b.cookies) || 0 };
    }
    function setBalance(b) { write(KEYS.balance, b); refreshMenu(); }

    /* Работа с корзиной */
    function getCart() { return read(KEYS.cart, []).filter(line => findProduct(line.id)); }
    function setCart(cart) { write(KEYS.cart, cart); refreshMenu(); }
    function cartCount() { return getCart().reduce((sum, line) => sum + line.qty, 0); }
    function cartTotal() { return getCart().reduce((sum, line) => sum + line.qty * findProduct(line.id).price, 0); }
    function addToCart(id) {
        const cart = getCart();
        const line = cart.find(l => l.id === id);
        if (line) line.qty += 1; else cart.push({ id, qty: 1 });
        setCart(cart);
    }
    function changeQty(id, delta) {
        const cart = getCart();
        const line = cart.find(l => l.id === id);
        if (!line) return;
        line.qty += delta;
        setCart(cart.filter(l => l.qty > 0));
    }
    function removeFromCart(id) { setCart(getCart().filter(l => l.id !== id)); }

    /* Заказы и инвентарь */
    function getOrders() { return read(KEYS.orders, []); }
    function addOrder(product, qty, total) {
        const number = read(KEYS.seq, 1001);
        const orders = getOrders();
        orders.unshift({
            number,
            name: qty > 1 ? `${productTitle(product)} × ${qty}` : productTitle(product),
            category: product.category,
            price: total,
            currency: product.currency,
            status: "Куплено",
            date: new Date().toISOString()
        });
        write(KEYS.orders, orders);
        write(KEYS.seq, number + 1);
    }
    function getInventory() { return read(KEYS.inventory, {}); }
    function addToInventory(id) {
        const inventory = getInventory();
        inventory[id] = (inventory[id] || 0) + 1;
        write(KEYS.inventory, inventory);
    }

    /* Всплывающие уведомления и окна */
    let confirmModal;

    function ensureUI() {
        if (document.getElementById("store-toasts")) return;
        if (typeof bootstrap === "undefined") { console.error("store.js: не подключён bootstrap.bundle.min.js"); return; }

        document.body.insertAdjacentHTML("beforeend", `
            <div id="store-toasts" class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 2000;"></div>

            <div class="modal fade" id="store-confirm" tabindex="-1">
              <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title fw-bold">Подтверждение</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                  </div>
                  <div class="modal-body fs-5" id="store-confirm-body"></div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
                    <button type="button" class="btn btn-primary fw-bold" id="store-confirm-ok">Подтвердить</button>
                  </div>
                </div>
              </div>
            </div>`);

        confirmModal = new bootstrap.Modal(document.getElementById("store-confirm"));
    }

    function toast(html, type = "success") {
        ensureUI();
        const dark = type === "warning";
        const el = document.createElement("div");
        el.className = `toast align-items-center border-0 bg-${type} ${dark ? "text-dark" : "text-white"}`;
        el.setAttribute("role", "alert");
        el.innerHTML = `
            <div class="d-flex">
              <div class="toast-body">${html}</div>
              <button type="button" class="btn-close ${dark ? "" : "btn-close-white"} me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>`;
        document.getElementById("store-toasts").appendChild(el);
        el.addEventListener("hidden.bs.toast", () => el.remove());
        new bootstrap.Toast(el, { delay: 4000 }).show();
    }

    function confirmDialog(html, okText = "Подтвердить") {
        ensureUI();
        return new Promise(resolve => {
            const modalEl = document.getElementById("store-confirm");
            const okBtn = document.getElementById("store-confirm-ok");
            document.getElementById("store-confirm-body").innerHTML = html;
            okBtn.textContent = okText;
            let confirmed = false;
            const onOk = () => { confirmed = true; confirmModal.hide(); };
            okBtn.addEventListener("click", onOk);
            modalEl.addEventListener("hidden.bs.modal", () => {
                okBtn.removeEventListener("click", onOk);
                resolve(confirmed);
            }, { once: true });
            confirmModal.show();
        });
    }

    function topUp(amount) {
        if (!(amount > 0)) return;
        const balance = getBalance();
        balance.rubles += amount;
        setBalance(balance);
        toast(`Баланс пополнен на ${amount} ${emoji("RUBLE")}. Теперь ${balance.rubles} ${emoji("RUBLE")}`);
    }

    /* Обновление интерфейса */
    function refreshMenu() {
        const balance = getBalance();
        const rub = document.getElementById("balance-rubles");
        const cook = document.getElementById("balance-cookies");
        const badge = document.getElementById("cart-badge");
        if (rub) rub.textContent = balance.rubles;
        if (cook) cook.textContent = balance.cookies;
        if (badge) {
            const count = cartCount();
            badge.textContent = count;
            badge.classList.toggle("d-none", count === 0);
        }
        document.dispatchEvent(new CustomEvent("store:change"));
    }

    /* Обработка действий */
    async function handleAction(product) {
        const RUB = emoji("RUBLE"), COOKIE = emoji("COOKIE");
        const balance = getBalance();

        if (product.actionType === "buy") {
            if (balance.rubles < product.price) {
                toast(`Недостаточно средств: нужно ${product.price} ${RUB}, на балансе ${balance.rubles} ${RUB}. Пополните баланс в меню слева.`, "warning");
                return;
            }
            if (!await confirmDialog(`Купить <b>${product.name} ${COOKIE}</b> за <b>${product.price} ${RUB}</b>?`, "Купить")) return;
            addOrder(product, 1, product.price);
            balance.rubles -= product.price;
            balance.cookies += Number(product.name);
            setBalance(balance);
            toast(`Куплено! На балансе ${balance.cookies} ${COOKIE}`);

        } else if (product.actionType === "add_to_game") {
            if (balance.cookies < product.price) {
                toast(`Недостаточно печенек: нужно ${product.price} ${COOKIE}, у вас ${balance.cookies} ${COOKIE}. <a href="/categories#cookies" class="text-reset fw-bold">Купить печеньки</a>`, "warning");
                return;
            }
            if (!await confirmDialog(`Добавить в игру <b>${product.name}</b> за <b>${product.price} ${COOKIE}</b>?`, "Добавить")) return;
            addToInventory(product.id);
            addOrder(product, 1, product.price);
            balance.cookies -= product.price;
            setBalance(balance);
            toast(`«${product.name}» добавлена в игру. Осталось ${balance.cookies} ${COOKIE}`);

        } else if (product.actionType === "to_cart") {
            addToCart(product.id);
            toast(`«${product.name}» добавлен в корзину. <a href="/orders" class="text-reset fw-bold">Перейти в корзину</a>`);
        }
    }

    async function checkout() {
        const cart = getCart();
        if (!cart.length) return;
        const RUB = emoji("RUBLE");
        const total = cartTotal();
        const balance = getBalance();
        if (balance.rubles < total) {
            toast(`Недостаточно средств: нужно ${total} ${RUB}, на балансе ${balance.rubles} ${RUB}. Пополните баланс в меню слева.`, "warning");
            return;
        }
        if (!await confirmDialog(`Оформить заказ на <b>${total} ${RUB}</b>?`, "Оформить")) return;
        cart.forEach(line => {
            const product = findProduct(line.id);
            addOrder(product, line.qty, product.price * line.qty);
        });
        balance.rubles -= total;
        setBalance(balance);
        setCart([]);
        toast(`Заказ оформлен на ${total} ${RUB}`);
    }

    /* Контекст ИИ-Ассистента */
    function getContext() {
        return {
            balance: getBalance(),
            cart: getCart().map(line => {
                const p = findProduct(line.id);
                return { name: p.name, qty: line.qty, price: p.price, sum: p.price * line.qty };
            }),
            cart_total: cartTotal(),
            orders: getOrders().slice(0, 10).map(o => ({
                number: o.number, name: o.name, category: CATEGORY_TITLES[o.category] || o.category,
                price: o.price, currency: o.currency, status: o.status
            })),
            inventory: Object.entries(getInventory()).map(([id, qty]) => ({
                name: (findProduct(id) || { name: id }).name, qty
            }))
        };
    }

    /* Отслеживание кликов */
    document.addEventListener("click", e => {
        const actionBtn = e.target.closest("[data-action][data-id]");
        if (actionBtn) {
            const product = findProduct(actionBtn.dataset.id);
            if (product) handleAction(product);
        }
        const topupBtn = e.target.closest("[data-topup]");
        if (topupBtn) topUp(Number(topupBtn.dataset.topup));
    });
    document.addEventListener("DOMContentLoaded", () => { refreshMenu(); ensureUI(); });

    window.Store = {
        getBalance, getCart, cartTotal, cartCount, changeQty, removeFromCart, checkout,
        getOrders, getContext, findProduct, toast, topUp, refreshMenu,
        CATEGORY_TITLES, STATUS_CLASS
    };
})();
