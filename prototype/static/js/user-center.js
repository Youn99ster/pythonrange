// HackShop 用户中心页面JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    initializeUserCenter();
    initializeLanguageSwitcher();
});

function initializeUserCenter() {
    initializeSidebarNavigation();
    initializeProfileManagement();
    initializeOrderManagement();
    initializeAddressManagement();
    initializeSecuritySettings();
    initializeAssetManagement();
    initializeSystemSettings();
    initializeMobileMenu();
    initializeScrollEffects();
}

// 侧边栏导航功能
function initializeSidebarNavigation() {
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    const contentSections = document.querySelectorAll('.content-section');

    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // 移除所有活动状态
            menuLinks.forEach(l => l.classList.remove('active'));
            contentSections.forEach(s => s.style.display = 'none');

            // 添加当前活动状态
            this.classList.add('active');

            // 显示对应的内容区域
            const targetSection = this.getAttribute('data-section');
            const targetElement = document.getElementById(targetSection + '-section');
            if (targetElement) {
                targetElement.style.display = 'block';
            }

            // 添加页面切换动画
            if (targetElement) {
                targetElement.style.opacity = '0';
                targetElement.style.transform = 'translateY(20px)';

                setTimeout(() => {
                    targetElement.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    targetElement.style.opacity = '1';
                    targetElement.style.transform = 'translateY(0)';
                }, 100);
            }
        });
    });
}

// 个人信息管理功能
function initializeProfileManagement() {
    const profileForm = document.querySelector('.profile-form');
    const resetButton = profileForm?.querySelector('.btn-secondary');

    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(profileForm);
            const profileData = {
                nickname: document.getElementById('nickname').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                gender: document.getElementById('gender').value,
                birthday: document.getElementById('birthday').value,
                bio: document.getElementById('bio').value
            };

            // 模拟保存操作
            showNotification('个人信息保存成功', 'success');
            console.log('保存的个人信息:', profileData);
        });
    }

    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (confirm('确定要重置所有修改吗？')) {
                profileForm.reset();
                showNotification('表单已重置', 'info');
            }
        });
    }

    // 实时验证邮箱格式
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (!validateEmail(this.value)) {
                this.setCustomValidity('请输入有效的邮箱地址');
                showNotification('邮箱格式不正确', 'warning');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // 实时验证手机号格式
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('blur', function() {
            if (!validatePhone(this.value)) {
                this.setCustomValidity('请输入有效的手机号码');
                showNotification('手机号码格式不正确', 'warning');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

// 订单管理功能
function initializeOrderManagement() {
    // 订单操作按钮
    const orderButtons = document.querySelectorAll('.order-actions .btn');

    orderButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderCard = this.closest('.order-card');
            const orderNumber = orderCard.querySelector('.order-number').textContent;
            const buttonText = this.textContent.trim();

            switch(buttonText) {
                case '查看详情':
                    showNotification(`正在查看订单 ${orderNumber} 的详情`, 'info');
                    break;
                case '再次购买':
                    showNotification(`正在将订单 ${orderNumber} 的商品加入购物车`, 'info');
                    break;
                case '确认收货':
                    if (confirm(`确定要确认收货订单 ${orderNumber} 吗？`)) {
                        updateOrderStatus(orderCard, 'completed');
                        showNotification('确认收货成功', 'success');
                    }
                    break;
                case '查看物流':
                    showNotification(`正在查看订单 ${orderNumber} 的物流信息`, 'info');
                    break;
                case '立即付款':
                    showNotification(`正在跳转到订单 ${orderNumber} 的支付页面`, 'info');
                    break;
                case '取消订单':
                    if (confirm(`确定要取消订单 ${orderNumber} 吗？`)) {
                        updateOrderStatus(orderCard, 'cancelled');
                        showNotification('订单已取消', 'success');
                    }
                    break;
            }
        });
    });
}

// 更新订单状态
function updateOrderStatus(orderCard, newStatus) {
    const statusElement = orderCard.querySelector('.order-status');
    const statusMap = {
        'pending': '待付款',
        'processing': '处理中',
        'shipped': '已发货',
        'completed': '已完成',
        'cancelled': '已取消'
    };

    statusElement.textContent = statusMap[newStatus];
    statusElement.className = `order-status status-${newStatus}`;
}

// 收货地址管理功能
function initializeAddressManagement() {
    const addAddressBtn = document.querySelector('#addresses-section .btn-primary');
    const addressCards = document.querySelectorAll('.address-card');

    // 添加新地址
    if (addAddressBtn) {
        addAddressBtn.addEventListener('click', function() {
            showNotification('正在打开添加地址对话框', 'info');
            // 这里可以添加模态框来添加新地址
        });
    }

    // 地址操作按钮
    addressCards.forEach(card => {
        const actionButtons = card.querySelectorAll('.address-actions .btn-link');

        actionButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const actionText = this.textContent.trim();
                const addressName = card.querySelector('.address-name').textContent;

                switch(actionText) {
                    case '编辑':
                        showNotification(`正在编辑 ${addressName} 的地址`, 'info');
                        break;
                    case '删除':
                        if (confirm(`确定要删除 ${addressName} 的地址吗？`)) {
                            removeAddressCard(card);
                            showNotification('地址删除成功', 'success');
                        }
                        break;
                    case '设为默认':
                        setDefaultAddress(card);
                        showNotification('默认地址设置成功', 'success');
                        break;
                }
            });
        });
    });
}

// 删除地址卡片
function removeAddressCard(card) {
    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    card.style.opacity = '0';
    card.style.transform = 'translateX(-100%)';

    setTimeout(() => {
        card.remove();
    }, 300);
}

// 设置默认地址
function setDefaultAddress(card) {
    // 移除其他地址的默认状态
    document.querySelectorAll('.address-card').forEach(c => {
        c.classList.remove('default');
    });

    // 设置当前地址为默认
    card.classList.add('default');
}

// 账户安全设置功能
function initializeSecuritySettings() {
    const securityButtons = document.querySelectorAll('#security-section .btn-outline-primary');

    securityButtons.forEach(button => {
        button.addEventListener('click', function() {
            const securityItem = this.closest('.security-item');
            const securityTitle = securityItem.querySelector('h4').textContent;

            showNotification(`正在${this.textContent.trim()}${securityTitle}`, 'info');

            // 模拟操作成功
            setTimeout(() => {
                const statusBadge = securityItem.querySelector('.status-badge');
                if (statusBadge && statusBadge.classList.contains('status-unverified')) {
                    statusBadge.classList.remove('status-unverified');
                    statusBadge.classList.add('status-verified');
                    statusBadge.textContent = '已设置';
                    showNotification(`${securityTitle}设置成功`, 'success');
                }
            }, 1000);
        });
    });
}

// 资产管理功能
function initializeAssetManagement() {
    const assetButtons = document.querySelectorAll('#assets-section .btn-outline');

    // 资产按钮事件
    assetButtons.forEach(button => {
        button.addEventListener('click', function() {
            const buttonText = this.textContent.trim();
            if (buttonText === '充值' || buttonText === '兑换' || buttonText === '查看') {
                showNotification(`正在打开${buttonText}页面`, 'info');
            }
        });
    });

    // 初始化储值券兑换功能
    initializeVoucherRedemption();
}

// 储值券兑换功能 - 包含条件竞争漏洞
function initializeVoucherRedemption() {
    // 模拟的数据库状态（实际应该在后端）
    let voucherDatabase = {
        'NEWUSER100': { amount: 100, redeemed: false },
        'SAVE200': { amount: 200, redeemed: false },
        'BIG500': { amount: 500, redeemed: false }
    };

    // 用户余额
    let userBalance = 1280.50;

    // 兑换按钮事件
    const redeemButtons = document.querySelectorAll('.voucher-redeem-btn');
    redeemButtons.forEach(button => {
        button.addEventListener('click', function() {
            const voucherCode = this.getAttribute('data-voucher');
            const amount = parseFloat(this.getAttribute('data-amount'));
            redeemVoucher(voucherCode, amount, this);
        });
    });

    // 快速兑换功能
    const quickRedeemBtn = document.getElementById('quickRedeemBtn');
    const quickVoucherInput = document.getElementById('quickVoucherCode');

    if (quickRedeemBtn && quickVoucherInput) {
        quickRedeemBtn.addEventListener('click', function() {
            const voucherCode = quickVoucherInput.value.trim().toUpperCase();
            if (!voucherCode) {
                showNotification('请输入兑换码', 'warning');
                return;
            }

            // 查找兑换码对应金额
            const voucher = voucherDatabase[voucherCode];
            if (!voucher) {
                showNotification('兑换码不存在', 'error');
                return;
            }

            redeemVoucher(voucherCode, voucher.amount, this);
        });

        // 回车键兑换
        quickVoucherInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                quickRedeemBtn.click();
            }
        });
    }

    // 清空兑换记录
    const clearHistoryBtn = document.getElementById('clearRedeemHistory');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', function() {
            if (confirm('确定要清空所有兑换记录吗？')) {
                const historyContainer = document.getElementById('redeemHistory');
                historyContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-history fa-3x text-muted mb-3"></i>
                        <h5>暂无兑换记录</h5>
                    </div>
                `;
                showNotification('兑换记录已清空', 'success');
            }
        });
    }

    // 兑换核心函数 - 故意设计条件竞争漏洞
    async function redeemVoucher(voucherCode, amount, buttonElement) {
        // 禁用按钮防止重复点击（但实际这个保护不够）
        const originalText = buttonElement.textContent;
        buttonElement.disabled = true;
        buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>兑换中...';

        try {
            // 模拟网络延迟（为条件竞争创造条件）
            await simulateNetworkDelay();

            // 漏洞点：这里没有数据库锁，多个请求可以同时检查和更新
            const voucher = voucherDatabase[voucherCode];

            if (!voucher) {
                throw new Error('兑换码不存在');
            }

            if (voucher.redeemed) {
                throw new Error('该储值券已被兑换');
            }

            // 模拟数据库查询和更新的时间间隔
            await simulateDatabaseDelay();

            // 更新兑换状态（这里存在竞态条件）
            voucher.redeemed = true;
            userBalance += amount;

            // 更新界面显示
            updateUserBalance(userBalance);
            addRedeemHistory(voucherCode, amount);
            updateVoucherButton(voucherCode, true);

            showNotification(`兑换成功！${voucherCode} 已兑换 ¥${amount}`, 'success');

        } catch (error) {
            showNotification(`兑换失败：${error.message}`, 'error');
            buttonElement.disabled = false;
            buttonElement.textContent = originalText;
        }
    }

    // 模拟网络延迟
    function simulateNetworkDelay() {
        return new Promise(resolve => {
            const delay = Math.random() * 1000 + 500; // 500-1500ms 随机延迟
            setTimeout(resolve, delay);
        });
    }

    // 模拟数据库操作延迟（增加竞态条件概率）
    function simulateDatabaseDelay() {
        return new Promise(resolve => {
            const delay = Math.random() * 500 + 200; // 200-700ms 随机延迟
            setTimeout(resolve, delay);
        });
    }

    // 更新用户余额显示
    function updateUserBalance(newBalance) {
        const balanceElement = document.getElementById('userBalance');
        if (balanceElement) {
            balanceElement.textContent = `¥${newBalance.toFixed(2)}`;

            // 添加动画效果
            balanceElement.style.transform = 'scale(1.1)';
            balanceElement.style.color = '#28a745';
            setTimeout(() => {
                balanceElement.style.transform = 'scale(1)';
                balanceElement.style.color = '';
            }, 500);
        }
    }

    // 添加兑换记录
    function addRedeemHistory(voucherCode, amount) {
        const historyContainer = document.getElementById('redeemHistory');

        // 如果是第一次兑换，清除空状态
        if (historyContainer.querySelector('.text-center')) {
            historyContainer.innerHTML = '';
        }

        const historyItem = document.createElement('div');
        historyItem.className = 'alert alert-success d-flex justify-content-between align-items-center';
        historyItem.innerHTML = `
            <div>
                <strong>${voucherCode}</strong>
                <br>
                <small>兑换时间: ${new Date().toLocaleString('zh-CN')}</small>
            </div>
            <div class="text-end">
                <div class="fw-bold text-success">+¥${amount}</div>
                <small class="text-muted">兑换成功</small>
            </div>
        `;

        historyContainer.insertBefore(historyItem, historyContainer.firstChild);

        // 限制显示最近10条记录
        const items = historyContainer.querySelectorAll('.alert');
        if (items.length > 10) {
            items[items.length - 1].remove();
        }
    }

    // 更新兑换按钮状态
    function updateVoucherButton(voucherCode, isRedeemed) {
        const button = document.querySelector(`[data-voucher="${voucherCode}"]`);
        if (button) {
            if (isRedeemed) {
                button.disabled = true;
                button.className = 'btn btn-secondary btn-sm ms-2';
                button.textContent = '已兑换';
                button.removeAttribute('data-voucher');
                button.removeAttribute('data-amount');
            }
        }
    }

    // 为测试条件竞争提供的特殊函数
    window.testRaceCondition = async function(voucherCode) {
        console.log('=== 开始条件竞争测试 ===');
        console.log('原始兑换码状态:', JSON.stringify(voucherDatabase));

        const voucher = voucherDatabase[voucherCode];
        const originalBalance = userBalance;
        const originalRedeemed = voucher.redeemed;

        // 模拟多个并发请求
        const promises = [];
        for (let i = 0; i < 5; i++) {
            promises.push(simulateConcurrentRedeem(voucherCode, voucher.amount, i));
        }

        const results = await Promise.allSettled(promises);

        console.log('=== 竞争测试结果 ===');
        console.log('最终兑换码状态:', JSON.stringify(voucherDatabase));
        console.log('余额变化:', originalBalance, '->', userBalance);
        console.log('兑换结果:', results);

        // 检测是否发生条件竞争
        const successCount = results.filter(r => r.status === 'fulfilled' && r.value).length;
        if (successCount > 1) {
            console.warn('🚨 检测到条件竞争漏洞！同一储值券被多次兑换');
            showNotification(`警告：检测到条件竞争！${voucherCode} 被兑换 ${successCount} 次`, 'error');
        } else {
            console.log('✅ 未检测到条件竞争');
        }
    };

    // 模拟并发兑换
    async function simulateConcurrentRedeem(voucherCode, amount, requestId) {
        try {
            console.log(`请求 ${requestId}: 开始兑换 ${voucherCode}`);

            // 模拟网络延迟
            await simulateNetworkDelay();

            const voucher = voucherDatabase[voucherCode];
            if (!voucher) {
                console.log(`请求 ${requestId}: 兑换码不存在`);
                return false;
            }

            console.log(`请求 ${requestId}: 检查兑换状态 - ${voucher.redeemed ? '已兑换' : '未兑换'}`);

            if (voucher.redeemed) {
                console.log(`请求 ${requestId}: 兑换码已被使用`);
                return false;
            }

            // 模拟数据库操作延迟
            await simulateDatabaseDelay();

            // 竞争条件发生在这里
            console.log(`请求 ${requestId}: 尝试更新兑换状态`);
            voucher.redeemed = true;
            userBalance += amount;

            console.log(`请求 ${requestId}: 兑换成功`);
            return true;

        } catch (error) {
            console.log(`请求 ${requestId}: 兑换失败 - ${error.message}`);
            return false;
        }
    }

    // 重置兑换状态（用于测试）
    window.resetVoucherDatabase = function() {
        voucherDatabase = {
            'NEWUSER100': { amount: 100, redeemed: false },
            'SAVE200': { amount: 200, redeemed: false },
            'BIG500': { amount: 500, redeemed: false }
        };
        userBalance = 1280.50;
        updateUserBalance(userBalance);

        // 重置所有兑换按钮
        document.querySelectorAll('.voucher-redeem-btn').forEach(button => {
            if (!button.textContent.includes('已兑换')) {
                button.disabled = false;
                button.className = 'btn btn-primary btn-sm ms-2';
            }
        });

        showNotification('兑换数据库已重置', 'info');
        console.log('兑换数据库已重置:', JSON.stringify(voucherDatabase));
    };

    // 添加测试按钮到控制台提示
    console.log('%c=== HackShop 储值券兑换测试 ===', 'color: #e74c3c; font-size: 14px; font-weight: bold;');
    console.log('%ctestRaceCondition("NEWUSER100")', 'color: #3498db; font-size: 12px;');
    console.log('%cresetVoucherDatabase()', 'color: #27ae60; font-size: 12px;');
    console.log('%c这些函数可以在浏览器控制台中调用以测试条件竞争漏洞', 'color: #f39c12; font-size: 11px;');
}

// 系统设置功能
function initializeSystemSettings() {
    const saveSettingsBtn = document.querySelector('#settings-section .btn-primary');
    const formSwitches = document.querySelectorAll('#settings-section .form-check-input');

    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', function() {
            const settings = {};
            formSwitches.forEach(switchEl => {
                settings[switchEl.id] = switchEl.checked;
            });

            console.log('保存的系统设置:', settings);
            showNotification('系统设置保存成功', 'success');
        });
    }

    // 实时保存开关状态
    formSwitches.forEach(switchEl => {
        switchEl.addEventListener('change', function() {
            const settingName = this.closest('.form-check').querySelector('label').textContent;
            const status = this.checked ? '已开启' : '已关闭';
            showNotification(`${settingName}${status}`, 'info');
        });
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

// 验证函数
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^1[3-9]\d{9}$/;
    return re.test(phone);
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

// 工具函数
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

    // 默认显示个人信息页面
    const profileLink = document.querySelector('.sidebar-menu a[data-section="profile"]');
    if (profileLink) {
        profileLink.click();
    }
});

// 语言切换功能
function initializeLanguageSwitcher() {
    // 点击页面其他地方关闭下拉菜单
    document.addEventListener('click', function(event) {
        const languageSwitcher = document.querySelector('.language-switcher');
        const dropdown = document.getElementById('language-dropdown');

        if (languageSwitcher && !languageSwitcher.contains(event.target)) {
            dropdown.classList.remove('show');
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

    // 使用 event 对象的当前目标
    const clickedOption = window.event ? window.event.target : event.currentTarget;
    clickedOption.closest('.language-option').classList.add('active');

    // 关闭下拉菜单
    document.getElementById('language-dropdown').classList.remove('show');

    // 这里可以添加实际的语言切换逻辑
    console.log('语言已切换至:', lang);
}

// 导出功能供其他页面使用
window.HackShopUserCenter = {
    showNotification,
    validateEmail,
    validatePhone,
    debounce,
    updateOrderStatus,
    setDefaultAddress,
    toggleLanguageDropdown,
    changeLanguage
};