// Кондитерская лавка - основной JavaScript

// ========== Функции уведомлений ==========
function showNotification(message, type = 'success') {
    // Создаём элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification--${type}`;
    notification.textContent = message;

    // Стили уведомления
    const colors = {
        success: '#4caf50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196f3'
    };

    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${colors[type] || colors.success};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-weight: 500;
        cursor: pointer;
    `;

    document.body.appendChild(notification);

    // Закрытие по клику
    notification.onclick = () => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    };

    // Автоматическое закрытие через 3 секунды
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
    }, 3000);
}

// ========== Счётчик корзины ==========
function updateCartCount() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);

    // Ищем или создаём элемент для счётчика
    let cartBadge = document.querySelector('.cart-badge');
    const cartLink = document.querySelector('a[href="/cart"]');

    if (!cartBadge && cartLink) {
        cartBadge = document.createElement('span');
        cartBadge.className = 'cart-badge';
        cartLink.style.position = 'relative';
        cartLink.appendChild(cartBadge);
    }

    if (cartBadge) {
        if (count > 0) {
            cartBadge.textContent = count;
            cartBadge.style.cssText = `
                position: absolute;
                top: -10px;
                right: -15px;
                background: #e74c3c;
                color: white;
                border-radius: 50%;
                padding: 2px 7px;
                font-size: 0.7rem;
                font-weight: bold;
                min-width: 18px;
                text-align: center;
            `;
        } else {
            cartBadge.textContent = '';
            cartBadge.style.cssText = '';
        }
    }
}

// ========== Добавление в корзину ==========
function addToCart(product, options = {}, quantity = 1) {
    const cartItem = {
        id: Date.now() + Math.random(),
        product_id: product.id,
        name: product.name,
        base_price: product.price,
        price: product.price,
        quantity: quantity,
        options: options.selectedOptions || [],
        inscription: options.inscription || null,
        image_url: product.image_url || '/static/images/default.jpg'
    };

    // Пересчитываем цену с учётом опций
    let extraTotal = 0;
    cartItem.options.forEach(opt => {
        extraTotal += opt.extra || 0;
    });
    cartItem.price = (product.price + extraTotal) * quantity;

    // Получаем текущую корзину
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    cart.push(cartItem);
    localStorage.setItem('cart', JSON.stringify(cart));

    updateCartCount();
    showNotification(`✅ ${product.name} добавлен в корзину!`, 'success');
}

// ========== Очистка корзины ==========
function clearCart() {
    localStorage.removeItem('cart');
    updateCartCount();
    showNotification('Корзина очищена', 'info');
}

// ========== Получение корзины ==========
function getCart() {
    return JSON.parse(localStorage.getItem('cart') || '[]');
}

// ========== Сохранение корзины ==========
function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

// ========== Подсчёт итога корзины ==========
function getCartTotal() {
    const cart = getCart();
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

// ========== Загрузка демо-данных для отладки ==========
function loadDemoCart() {
    const cart = getCart();
    if (cart.length === 0) {
        const demoCart = [
            {
                id: 1,
                product_id: 1,
                name: 'Медовик классический',
                base_price: 1200,
                price: 1200,
                quantity: 1,
                options: [{ value: 'Средний (8 порций)', extra: 500 }],
                inscription: null,
                image_url: '/static/images/cake1.jpg'
            },
            {
                id: 2,
                product_id: 3,
                name: 'Капкейк с вишней',
                base_price: 250,
                price: 250,
                quantity: 2,
                options: [],
                inscription: null,
                image_url: '/static/images/cupcake1.jpg'
            }
        ];
        localStorage.setItem('cart', JSON.stringify(demoCart));
        updateCartCount();
        showNotification('Демо-корзина загружена (для теста)', 'info');
    }
}

// ========== Инициализация при загрузке страницы ==========
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();

    // Добавляем плавную прокрутку для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });

    // Добавляем класс для активной ссылки в навигации
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav__link').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath !== '/' && href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });
});

// ========== Добавляем CSS анимации ==========
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes fadeOut {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }

    .nav__link.active {
        color: #d4a373;
        font-weight: 600;
        border-bottom: 2px solid #d4a373;
    }

    /* Анимация для карточек товаров */
    .product-card {
        transition: transform 0.3s, box-shadow 0.3s;
    }

    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    /* Анимация загрузки */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #d4a373;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// ========== ФУНКЦИИ ДЛЯ ЗАКАЗОВ ==========

// Статусы заказов
const ORDER_STATUSES = {
    'new': { label: '🆕 Новый', class: 'status-new' },
    'confirmed': { label: '✅ Подтверждён', class: 'status-confirmed' },
    'in_progress': { label: '👩‍🍳 Готовится', class: 'status-progress' },
    'delivered': { label: '🚚 Доставлен', class: 'status-delivered' },
    'cancelled': { label: '❌ Отменён', class: 'status-cancelled' }
};

function getStatusText(status) {
    const statuses = {
        'new': '🆕 Новый',
        'confirmed': '✅ Подтверждён',
        'in_progress': '👩‍🍳 Готовится',
        'delivered': '🚚 Доставлен',
        'cancelled': '❌ Отменён'
    };
    return statuses[status] || '🆕 Новый';
}

function getStatusClass(status) {
    const classes = {
        'new': 'status-new',
        'confirmed': 'status-confirmed',
        'in_progress': 'status-progress',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    return classes[status] || 'status-new';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Загрузка заказов пользователя
function loadUserOrders() {
    const ordersContainer = document.getElementById('ordersList');
    if (!ordersContainer) return;

    fetch('/api/my-orders')
        .then(response => response.json())
        .then(orders => {
            if (orders.length === 0) {
                ordersContainer.innerHTML = `
                    <div class="empty-orders">
                        <p>😢 У вас пока нет заказов</p>
                        <a href="/catalog" class="btn btn--primary">Перейти в каталог</a>
                    </div>
                `;
                return;
            }

            ordersContainer.innerHTML = '';
            orders.forEach(order => {
                const orderDate = new Date(order.order_date).toLocaleString('ru-RU');
                const statusText = getStatusText(order.status);
                const statusClass = getStatusClass(order.status);

                let itemsHtml = '';
                order.items.forEach(item => {
                    itemsHtml += `
                        <div class="order-item">
                            <span>${escapeHtml(item.product_name)}</span>
                            <span>${item.quantity} шт × ${item.product_price} ₽</span>
                            <span class="order-item-total">${item.product_price * item.quantity} ₽</span>
                        </div>
                    `;
                });

                ordersContainer.innerHTML += `
                    <div class="order-card">
                        <div class="order-card__header">
                            <div>
                                <span class="order-number">📦 ${escapeHtml(order.order_id)}</span>
                                <span class="order-date">от ${orderDate}</span>
                            </div>
                            <span class="order-status ${statusClass}">${statusText}</span>
                        </div>
                        <div class="order-card__items">
                            ${itemsHtml}
                        </div>
                        <div class="order-card__footer">
                            <div class="order-delivery">
                                🚚 ${escapeHtml(order.delivery_address)}, ${order.delivery_date} ${order.delivery_time || ''}
                            </div>
                            <div class="order-total">Итого: <strong>${order.total_amount} ₽</strong></div>
                        </div>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error('Error:', error);
            if (ordersContainer) {
                ordersContainer.innerHTML = '<p class="error">Ошибка загрузки заказов</p>';
            }
        });
}

// Отправка заказа на сервер
function submitOrder(formData) {
    fetch('/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showNotification('✅ Заказ успешно оформлен! Номер: ' + data.order_id, 'success');
            localStorage.removeItem('cart');
            setTimeout(() => {
                window.location.href = '/profile';
            }, 1500);
        } else {
            showNotification('❌ Ошибка при оформлении заказа', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('❌ Ошибка при оформлении заказа', 'error');
    });
}

// Экранирование HTML (безопасность)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


// ========== Экспорт глобальных функций ==========
window.showNotification = showNotification;
window.updateCartCount = updateCartCount;
window.addToCart = addToCart;
window.clearCart = clearCart;
window.getCart = getCart;
window.saveCart = saveCart;
window.getCartTotal = getCartTotal;
window.loadDemoCart = loadDemoCart;
window.submitOrder = submitOrder;
window.loadUserOrders = loadUserOrders;