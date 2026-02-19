// HackShop 购物车页面JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    initializeCartPage();
    initializeLanguageSwitcher();
});

// 语言切换和用户菜单功能
function initializeLanguageSwitcher() {
    // 点击页面其他地方关闭下拉菜单
    document.addEventListener('click', function(event) {
        // 关闭语言切换下拉菜单
        const languageSwitcher = document.querySelector('.language-switcher');
        const languageDropdown = document.getElementById('language-dropdown');

        if (languageSwitcher && !languageSwitcher.contains(event.target)) {
            languageDropdown.classList.remove('show');
        }

        // 关闭用户下拉菜单
        const userMenu = document.querySelector('.user-menu');
        const userDropdown = document.getElementById('user-dropdown');

        if (userMenu && !userMenu.contains(event.target)) {
            userDropdown.classList.remove('show');
        }
    });
}

function toggleLanguageDropdown() {
    const dropdown = document.getElementById('language-dropdown');
    dropdown.classList.toggle('show');
}

function changeLanguage(lang) {
    const currentLang = document.getElementById('current-lang');
    const langNames = {
        'zh': '中文',
        'en': 'English',
        'ru': 'Русский'
    };

    currentLang.textContent = langNames[lang];

    // 更新活跃状态
    document.querySelectorAll('.language-option').forEach(option => {
        option.classList.remove('active');
    });
    event.target.closest('.language-option').classList.add('active');

    // 关闭下拉菜单
    document.getElementById('language-dropdown').classList.remove('show');

    // 这里可以添加实际的语言切换逻辑
    console.log('语言已切换至:', lang);
}

// 用户菜单切换功能
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('show');
}

// 退出登录功能
function logout() {
    if (confirm('确定要退出登录吗？')) {
        showNotification('正在退出登录...', 'info');
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
    }
}

function initializeCartPage() {
    initializeCartItems();
    initializeQuantitySelectors();
    initializeBatchOperations();
    initializeCheckoutActions();
    initializeRecommendedProducts();
    initializeMobileMenu();
    initializeScrollEffects();
}

// 购物车商品管理
function initializeCartItems() {
    const cartItems = document.querySelectorAll('.cart-item');
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectAllBottomCheckbox = document.getElementById('selectAllBottom');

    // 单个商品选择
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateCartSummary();
            updateSelectAllState();
        });
    });

    // 全选功能
    [selectAllCheckbox, selectAllBottomCheckbox].forEach(checkbox => {
        if (checkbox) {
            checkbox.addEventListener('change', function() {
                const isChecked = this.checked;
                checkboxes.forEach(itemCheckbox => {
                    itemCheckbox.checked = isChecked;
                });
                if (selectAllCheckbox && selectAllBottomCheckbox) {
                    selectAllCheckbox.checked = isChecked;
                    selectAllBottomCheckbox.checked = isChecked;
                }
                updateCartSummary();
            });
        }
    });

    // 删除单个商品
    const removeButtons = document.querySelectorAll('.cart-item-remove');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cartItem = this.closest('.cart-item');
            const productName = cartItem.querySelector('.cart-item-info h4').textContent;

            if (confirm(`确定要删除 "${productName}" 吗？`)) {
                removeCartItem(cartItem);
            }
        });
    });

    // 初始化购物车汇总
    updateCartSummary();
    updateSelectAllState();
}

// 数量选择器功能
function initializeQuantitySelectors() {
    const quantitySelectors = document.querySelectorAll('.quantity-selector');

    quantitySelectors.forEach(selector => {
        const minusBtn = selector.querySelector('.minus');
        const plusBtn = selector.querySelector('.plus');
        const quantityInput = selector.querySelector('.quantity-input');

        minusBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                quantityInput.value = currentValue - 1;
                updateItemSubtotal(selector.closest('.cart-item'));
                updateCartSummary();
            }
        });

        plusBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue < 99) {
                quantityInput.value = currentValue + 1;
                updateItemSubtotal(selector.closest('.cart-item'));
                updateCartSummary();
            }
        });

        quantityInput.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else if (value > 99) {
                this.value = 99;
            }
            updateItemSubtotal(selector.closest('.cart-item'));
            updateCartSummary();
        });
    });
}

// 批量操作功能
function initializeBatchOperations() {
    const batchDeleteBtn = document.getElementById('batchDelete');
    const batchMoveToWishlistBtn = document.getElementById('batchMoveToWishlist');
    const clearCartBtn = document.getElementById('clearCart');

    // 批量删除
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.item-checkbox:checked');
            if (selectedItems.length === 0) {
                showNotification('请选择要删除的商品', 'warning');
                return;
            }

            if (confirm(`确定要删除选中的 ${selectedItems.length} 件商品吗？`)) {
                selectedItems.forEach(checkbox => {
                    const cartItem = checkbox.closest('.cart-item');
                    removeCartItem(cartItem);
                });
                showNotification('选中的商品已删除', 'success');
            }
        });
    }

    // 移入收藏
    if (batchMoveToWishlistBtn) {
        batchMoveToWishlistBtn.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.item-checkbox:checked');
            if (selectedItems.length === 0) {
                showNotification('请选择要移入收藏的商品', 'warning');
                return;
            }
            showNotification(`已将 ${selectedItems.length} 件商品移入收藏夹`, 'success');
        });
    }

    // 清空购物车
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            const cartItems = document.querySelectorAll('.cart-item');
            if (cartItems.length === 0) {
                showNotification('购物车已经是空的', 'info');
                return;
            }

            if (confirm('确定要清空购物车吗？')) {
                cartItems.forEach(item => item.remove());
                updateCartSummary();
                showNotification('购物车已清空', 'success');
                checkEmptyCart();
            }
        });
    }
}

// 结算操作
function initializeCheckoutActions() {
    const checkoutBtn = document.getElementById('checkoutBtn');
    const continueShoppingBtn = document.getElementById('continueShopping');

    // 去结算
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.item-checkbox:checked');
            if (selectedItems.length === 0) {
                showNotification('请选择要结算的商品', 'warning');
                return;
            }

            // 准备订单数据
            const orderData = prepareOrderData();
            if (orderData) {
                // 保存订单数据到 localStorage
                localStorage.setItem('checkoutOrderData', JSON.stringify(orderData));
                showNotification('正在跳转到结算页面...', 'success');

                // 延迟跳转到结算页面
                setTimeout(() => {
                    window.location.href = 'checkout.html';
                }, 1000);
            }
        });
    }

    // 继续购物
    if (continueShoppingBtn) {
        continueShoppingBtn.addEventListener('click', function() {
            window.location.href = 'index.html';
        });
    }
}

// 推荐商品功能
function initializeRecommendedProducts() {
    const recommendedCards = document.querySelectorAll('.recommended-card');

    recommendedCards.forEach(card => {
        card.addEventListener('click', function() {
            const productName = this.querySelector('h4').textContent;
            showNotification(`正在查看 "${productName}" 的详情`, 'info');
            // 这里可以添加跳转到商品详情页的逻辑
        });
    });
}

// 更新商品小计
function updateItemSubtotal(cartItem) {
    const price = parseFloat(cartItem.dataset.price);
    const quantity = parseInt(cartItem.querySelector('.quantity-input').value);
    const subtotal = price * quantity;

    const subtotalElement = cartItem.querySelector('.cart-item-subtotal');
    subtotalElement.textContent = `¥${subtotal.toLocaleString()}`;
}

// 更新购物车汇总
function updateCartSummary() {
    const selectedItems = document.querySelectorAll('.item-checkbox:checked');
    let totalItems = 0;
    let subtotal = 0;

    selectedItems.forEach(checkbox => {
        const cartItem = checkbox.closest('.cart-item');
        const price = parseFloat(cartItem.dataset.price);
        const quantity = parseInt(cartItem.querySelector('.quantity-input').value);

        totalItems += quantity;
        subtotal += price * quantity;
    });

    // 更新显示
    const totalItemsElement = document.getElementById('totalItems');
    const subtotalElement = document.getElementById('subtotal');
    const discount = 200; // 固定优惠金额
    const shippingFee = subtotal > 0 ? 0 : 0; // 满0元免运费
    const total = Math.max(0, subtotal - discount + shippingFee);

    if (totalItemsElement) {
        totalItemsElement.textContent = `${totalItems} 件`;
    }

    if (subtotalElement) {
        subtotalElement.textContent = `¥${subtotal.toLocaleString()}`;
    }

    if (document.getElementById('shipping')) {
        document.getElementById('shipping').textContent = shippingFee === 0 ? '免费' : `¥${shippingFee}`;
    }

    if (document.getElementById('discount')) {
        document.getElementById('discount').textContent = `-¥${discount}`;
    }

    if (document.getElementById('total')) {
        document.getElementById('total').textContent = `¥${total.toLocaleString()}`;
    }

    // 更新购物车徽章
    updateCartBadge(totalItems);
}

// 更新全选状态
function updateSelectAllState() {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectAllBottomCheckbox = document.getElementById('selectAllBottom');

    if (checkboxes.length === 0) {
        if (selectAllCheckbox) selectAllCheckbox.checked = false;
        if (selectAllBottomCheckbox) selectAllBottomCheckbox.checked = false;
        return;
    }

    const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
    const allChecked = checkedBoxes.length === checkboxes.length;

    if (selectAllCheckbox) selectAllCheckbox.checked = allChecked;
    if (selectAllBottomCheckbox) selectAllBottomCheckbox.checked = allChecked;
}

// 删除购物车商品
function removeCartItem(cartItem) {
    const productName = cartItem.querySelector('.cart-item-info h4').textContent;

    // 添加删除动画
    cartItem.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    cartItem.style.opacity = '0';
    cartItem.style.transform = 'translateX(-100%)';

    setTimeout(() => {
        cartItem.remove();
        updateCartSummary();
        updateSelectAllState();
        showNotification(`"${productName}" 已从购物车中删除`, 'success');
        checkEmptyCart();
    }, 300);
}

// 检查空购物车
function checkEmptyCart() {
    const cartItems = document.querySelectorAll('.cart-item');
    const cartTable = document.getElementById('cartTable');
    const cartPage = document.querySelector('.cart-page');

    if (cartItems.length === 0) {
        const emptyCartHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <h3>您的购物车是空的</h3>
                <p>快去挑选您喜欢的商品吧！</p>
                <button class="continue-shopping" onclick="window.location.href='index.html'">
                    <i class="fas fa-arrow-left me-2"></i>去购物
                </button>
            </div>
        `;

        if (cartTable) {
            cartTable.innerHTML = emptyCartHTML;
        }

        // 隐藏批量操作栏
        const batchActions = document.querySelector('.cart-batch-actions');
        if (batchActions) {
            batchActions.style.display = 'none';
        }
    }
}

// 更新购物车徽章
function updateCartBadge(totalItems) {
    const cartBadges = document.querySelectorAll('.cart-badge');
    cartBadges.forEach(badge => {
        badge.textContent = totalItems;
        badge.style.display = totalItems > 0 ? 'flex' : 'none';
    });
}

// 移动端菜单
function initializeMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');

    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });

        // 点击菜单项后关闭移动端菜单
        const menuItems = navbarCollapse.querySelectorAll('.nav-link');
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                navbarCollapse.classList.remove('show');
            });
        });
    }
}

// 滚动效果
function initializeScrollEffects() {
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow-lg');
        } else {
            navbar.classList.remove('shadow-lg');
        }
    });
}

// 通知系统
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';

    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // 3秒后自动关闭
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// 准备订单数据
function prepareOrderData() {
    const selectedItems = document.querySelectorAll('.item-checkbox:checked');
    const items = [];

    selectedItems.forEach(checkbox => {
        const cartItem = checkbox.closest('.cart-item');
        const item = {
            name: cartItem.querySelector('.cart-item-info h4').textContent,
            description: cartItem.querySelector('.cart-item-info p').textContent,
            price: parseFloat(cartItem.dataset.price),
            quantity: parseInt(cartItem.querySelector('.quantity-input').value),
            image: cartItem.querySelector('.cart-item-image').src
        };
        items.push(item);
    });

    const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const discount = 200; // 固定优惠
    const shipping = 0; // 免运费
    const total = Math.max(0, subtotal - discount + shipping);

    return {
        items: items,
        subtotal: subtotal,
        discount: discount,
        shipping: shipping,
        total: total,
        totalItems: items.reduce((sum, item) => sum + item.quantity, 0),
        orderDate: new Date().toISOString()
    };
}

// 工具函数
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化工具提示
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化弹出框
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// 导出功能供其他页面使用
window.HackShopCart = {
    updateCartSummary,
    updateCartBadge,
    showNotification,
    formatPrice,
    debounce
};