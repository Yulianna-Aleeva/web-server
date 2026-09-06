const CATALOG_DATA = {
    cookies: [
        { id: 1, name: "10", price: 100, currency: "RUBLE", badge: "COOKIE", actionText: "Купить", actionType: "buy", style: "primary" },
        { id: 2, name: "50", price: 450, currency: "RUBLE", badge: "COOKIE", actionText: "Купить", actionType: "buy", style: "primary" },
        { id: 3, name: "100", price: 800, currency: "RUBLE", badge: "COOKIE", actionText: "Купить", actionType: "buy", style: "primary" }
    ],
    hints: [
        { id: 4, name: "Сапёр — Открытие", desc: "Открывает безопасную клетку", price: 10, currency: "COOKIE", actionText: "Добавить", actionType: "add_to_game", style: "success" },
        { id: 5, name: "Сапёр — Метка", desc: "Помечает одну мину флагом", price: 15, currency: "COOKIE", actionText: "Добавить", actionType: "add_to_game", style: "success" },
        { id: 6, name: "Морской бой — Сужение", desc: "Уменьшает зону поиска цели", price: 30, currency: "COOKIE", actionText: "Добавить", actionType: "add_to_game", style: "success" },
        { id: 7, name: "Морской бой — Удар", desc: "Автоматический точный выстрел", price: 50, currency: "COOKIE", actionText: "Добавить", actionType: "add_to_game", style: "success" }
    ],
    toys: [
        { id: 8, name: "Крестики-Нолики", desc: "Деревянный настольный набор", price: 300, currency: "RUBLE", actionText: "В корзину", actionType: "to_cart", style: "warning" },
        { id: 9, name: "Сапёр", desc: "Магнитная доска-головоломка", price: 500, currency: "RUBLE", actionText: "В корзину", actionType: "to_cart", style: "warning" },
        { id: 10, name: "Морской бой", desc: "Кейсы со складным полем боя", price: 800, currency: "RUBLE", actionText: "В корзину", actionType: "to_cart", style: "warning" },
        { id: 11, name: "Кубик-рубика", desc: "Фирменный скоростной кубик", price: 1000, currency: "RUBLE", actionText: "В корзину", actionType: "to_cart", style: "warning" }
    ]
};
