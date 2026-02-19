// HackShop 主要JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeCarousel();
    initializeSearch();
    initializeCart();
    initializeCountdown();
    initializeScrollEffects();
    initializeMobileMenu();
}

// 轮播图功能
function initializeCarousel() {
    const carousel = document.querySelector('#mainCarousel');
    if (carousel) {
        new bootstrap.Carousel(carousel, {
            interval: 5000,
            ride: 'carousel'
        });
    }
}

// 搜索功能
function initializeSearch() {
    const searchInput = document.querySelector('.search-box input');
    const searchForm = document.querySelector('.search-box form');

    if (searchInput && searchForm) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value);
            }
        });

        // 搜索建议功能
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            if (query.length > 0) {
                showSearchSuggestions(query);
            } else {
                hideSearchSuggestions();
            }
        });
    }
}

function performSearch(query) {
    console.log('搜索商品:', query);
    // 这里可以添加实际的搜索逻辑
    showNotification('正在搜索: ' + query, 'info');
}

function showSearchSuggestions(query) {
    // 模拟搜索建议
    const suggestions = [
        '苹果手机',
        '笔记本电脑',
        '无线耳机',
        '智能手表',
        '平板电脑'
    ];

    // 这里可以添加实际的搜索建议逻辑
    console.log('搜索建议:', suggestions);
}

function hideSearchSuggestions() {
    // 隐藏搜索建议
}

// 购物车功能
function initializeCart() {
    const cartButtons = document.querySelectorAll('.btn-cart');
    const buyButtons = document.querySelectorAll('.btn-buy');

    cartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('.product-name').textContent;
            const productPrice = productCard.querySelector('.product-price').textContent;

            addToCart(productName, productPrice);
        });
    });

    buyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productCard = this.closest('.product-card');
            const productName = productCard.querySelector('.product-name').textContent;
            const productPrice = productCard.querySelector('.product-price').textContent;

            buyNow(productName, productPrice);
        });
    });
}

function addToCart(productName, productPrice) {
    console.log('添加到购物车:', productName, productPrice);

    // 模拟添加到购物车
    const cartBadge = document.querySelector('.cart-badge');
    if (cartBadge) {
        let currentCount = parseInt(cartBadge.textContent);
        cartBadge.textContent = currentCount + 1;
    }

    showNotification('"' + productName + '" 已添加到购物车', 'success');

    // 添加飞入动画效果
    animateCartIcon();
}

function buyNow(productName, productPrice) {
    console.log('立即购买:', productName, productPrice);
    showNotification('正在跳转到结算页面...', 'info');
    // 这里可以添加跳转到结算页面的逻辑
}

function animateCartIcon() {
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.classList.add('pulse');
        setTimeout(() => {
            cartIcon.classList.remove('pulse');
        }, 300);
    }
}

// 倒计时功能
function initializeCountdown() {
    const countdownElements = document.querySelectorAll('.countdown-item');
    if (countdownElements.length > 0) {
        // 设置目标时间（24小时后）
        const targetTime = new Date().getTime() + (24 * 60 * 60 * 1000);

        // 每秒更新倒计时
        setInterval(() => {
            updateCountdown(targetTime);
        }, 1000);
    }
}

function updateCountdown(targetTime) {
    const now = new Date().getTime();
    const distance = targetTime - now;

    if (distance < 0) {
        return;
    }

    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // 更新倒计时显示
    const countdownItems = document.querySelectorAll('.countdown-item');
    if (countdownItems.length >= 3) {
        countdownItems[0].querySelector('.countdown-number').textContent = hours.toString().padStart(2, '0');
        countdownItems[1].querySelector('.countdown-number').textContent = minutes.toString().padStart(2, '0');
        countdownItems[2].querySelector('.countdown-number').textContent = seconds.toString().padStart(2, '0');
    }
}

// 滚动效果
function initializeScrollEffects() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // 观察需要动画的元素
    const animatedElements = document.querySelectorAll('.product-card, .category-card, .promotion-card');
    animatedElements.forEach(el => observer.observe(el));
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

// 商品分类点击
function initializeCategoryClick() {
    const categoryCards = document.querySelectorAll('.category-card');

    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const categoryName = this.querySelector('.category-name').textContent;
            console.log('点击分类:', categoryName);
            showNotification('正在浏览 ' + categoryName + ' 分类', 'info');
            // 这里可以添加跳转到分类页面的逻辑
        });
    });
}

// 页面滚动时的导航栏效果
function initializeNavbarScroll() {
    const navbar = document.querySelector('.navbar');

    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('shadow-lg');
        } else {
            navbar.classList.remove('shadow-lg');
        }
    });
}

// 懒加载图片
function initializeLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    lazyImages.forEach(img => imageObserver.observe(img));
}

// 表单验证
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^1[3-9]\d{9}$/;
    return re.test(phone);
}

// 工具函数
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('zh-CN');
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

// 页面加载完成后初始化所有功能
document.addEventListener('DOMContentLoaded', function() {
    initializeCategoryClick();
    initializeNavbarScroll();
    initializeLazyLoading();

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
window.HackShop = {
    showNotification,
    addToCart,
    buyNow,
    formatPrice,
    formatDate,
    validateEmail,
    validatePhone,
    debounce
};