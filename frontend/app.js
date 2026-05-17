const API_URL = "http://localhost:8000";
let accessToken = localStorage.getItem('accessToken');
let globalProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            try {
                const response = await fetch(`${API_URL}/token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    accessToken = data.access_token;

                    localStorage.setItem('accessToken', accessToken);

                    showAuthorizedUI();

                    await loadCart();
                } else {
                    alert("Помилка авторизації. Перевірте логін та пароль.");
                }
            } catch (error) {
                console.error("Помилка:", error);
            }
        });
    }

    initApp();
});

async function initApp() {
    await loadProducts();

    if (accessToken) {
        showAuthorizedUI();
        await loadCart();
    }
}

async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        if (response.ok) {
            const products = await response.json();
            globalProducts = products;

            const container = document.getElementById('products-container');
            if (!container) return;
            container.innerHTML = "";

            if (products.length === 0) {
                container.innerHTML = "<p>Немає доступних товарів.</p>";
                return;
            }

            products.forEach(product => {
                const div = document.createElement('div');
                div.className = 'product-item';
                div.innerHTML = `
                    <div>
                        <strong>${product.name}</strong> — Ціна: ${product.price} грн
                    </div>
                    <button onclick="addToCart(${product.id})">Додати в корзину</button>
                `;
                container.appendChild(div);
            });
        }
    } catch (error) {
        console.error("Помилка завантаження товарів:", error);
    }
}

async function addToCart(productId) {
    if (!accessToken) {
        alert("Будь ласка, спочатку авторизуйтесь!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/cart/items/?product_id=${productId}&quantity=1`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
            }
        });

        if (response.ok) {
            alert("Товар додано до корзини!");
            await loadCart();
        } else if (response.status === 401) {
            alert("Сесія застаріла. Будь ласка, увійдіть знову.");
            logout();
        } else {
            alert("Помилка додавання до корзини.");
        }
    } catch (error) {
        console.error("Помилка:", error);
    }
}

// Загрузка и рендеринг содержимого корзины (GET)
async function loadCart() {
    if (!accessToken) {
        const container = document.getElementById('cart-container');
        if (container) container.innerHTML = "<p>Авторизуйтесь, щоб переглянути корзину.</p>";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/cart/items/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Accept': 'application/json'
             }
        });

        if (response.ok) {
            const cartData = await response.json();
            const container = document.getElementById('cart-container');
            if (!container) return;
            container.innerHTML = "";

            if (cartData.cart_items && cartData.cart_items.length > 0) {
                cartData.cart_items.forEach(item => {
                    const productInfo = globalProducts.find(p => p.id === item.product_id);
                    const productName = productInfo ? productInfo.name : `Товар ID: ${item.product_id}`;

                    const div = document.createElement('div');
                    div.className = 'product-item';
                    div.innerHTML = `
                        <div>Товар: <strong>${productName}</strong></div>
                        <div>Кількість: <strong>${item.quantity} шт.</strong></div>
                    `;
                    container.appendChild(div);
                });
            } else {
                container.innerHTML = "<p>Корзина порожня.</p>";
            }
        } else if (response.status === 401) {
            logout();
        }
    } catch (error) {
        console.error("Помилка завантаження корзини:", error);
    }
}

function showAuthorizedUI() {
    const authStatus = document.getElementById('auth-status');
    if (authStatus) {
        authStatus.className = "";
        authStatus.style.display = "block";
        authStatus.innerHTML = `Ви авторизовані! <button class="btn-danger" style="margin-top:0; margin-left:15px;" onclick="logout()">Вийти</button>`;
    }

    const loginSection = document.getElementById('login-section');
    if (loginSection) loginSection.style.display = 'none';
}

function logout() {
    accessToken = null;
    localStorage.removeItem('accessToken');

    const authStatus = document.getElementById('auth-status');
    if (authStatus) {
        authStatus.className = "unauthorized";
        authStatus.innerText = "Ви не авторизовані";
    }

    const loginSection = document.getElementById('login-section');
    if (loginSection) loginSection.style.display = 'block';

    const cartContainer = document.getElementById('cart-container');
    if (cartContainer) cartContainer.innerHTML = "";

    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    if (emailInput) emailInput.value = "";
    if (passwordInput) passwordInput.value = "";
}