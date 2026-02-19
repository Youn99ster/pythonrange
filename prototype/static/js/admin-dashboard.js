// HackShop 管理员后台JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminDashboard();
});

function initializeAdminDashboard() {
    initializeSidebar();
    initializeCharts();
    initializePageNavigation();
    initializeTableActions();
    initializeFormActions();
    initializeResponsiveActions();
}

// 侧边栏功能
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mainContent = document.getElementById('mainContent');
    const menuLinks = document.querySelectorAll('.sidebar-menu a');

    // 侧边栏折叠/展开
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });
    }

    // 菜单导航
    menuLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // 移除所有活动状态
            menuLinks.forEach(l => l.classList.remove('active'));

            // 添加当前活动状态
            this.classList.add('active');

            // 切换页面内容
            const targetPage = this.getAttribute('data-page');
            switchPage(targetPage);

            // 更新页面标题
            const pageTitle = this.querySelector('span').textContent;
            document.getElementById('pageTitle').textContent = pageTitle;
        });
    });
}

// 页面切换功能
function switchPage(pageName) {
    // 隐藏所有页面内容
    const allContents = document.querySelectorAll('.page-content');
    allContents.forEach(content => {
        content.style.display = 'none';
    });

    // 显示目标页面内容
    const targetContent = document.getElementById(pageName + '-content');
    if (targetContent) {
        targetContent.style.display = 'block';

        // 添加淡入动画
        targetContent.classList.remove('fade-in');
        setTimeout(() => {
            targetContent.classList.add('fade-in');
        }, 10);
    }

    // 特殊页面处理
    switch(pageName) {
        case 'dashboard':
            initializeDashboardCharts();
            break;
        case 'products':
            initializeProductManagement();
            break;
        case 'orders':
            initializeOrderManagement();
            break;
        case 'users':
            initializeUserManagement();
            break;
        case 'settings':
            initializeSettingsManagement();
            break;
        case 'vouchers':
            initializeVoucherManagement();
            break;
    }
}

// 初始化图表
function initializeCharts() {
    // 初始化仪表盘图表
    initializeDashboardCharts();
}

// 仪表盘图表
function initializeDashboardCharts() {
    // 销售趋势图
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{
                    label: '销售额',
                    data: [12000, 19000, 15000, 25000, 22000, 30000, 28000],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }, {
                    label: '订单量',
                    data: [65, 59, 80, 81, 56, 55, 40],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '¥' + value.toLocaleString();
                            }
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    // 商品分类饼图
    const categoryCtx = document.getElementById('categoryChart');
    if (categoryCtx) {
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['手机数码', '电脑办公', '音响耳机', '智能穿戴', '其他'],
                datasets: [{
                    data: [35, 25, 20, 15, 5],
                    backgroundColor: [
                        '#3498db',
                        '#e74c3c',
                        '#f39c12',
                        '#27ae60',
                        '#9b59b6'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
}

// 商品管理功能
function initializeProductManagement() {
    const addProductBtn = document.querySelector('#products-content .btn-primary');
    const batchImportBtn = document.querySelector('#products-content .btn-outline-secondary');
    const deleteButtons = document.querySelectorAll('#products-content .btn-outline-danger');

    if (addProductBtn) {
        addProductBtn.addEventListener('click', function() {
            showNotification('正在打开添加商品对话框', 'info');
        });
    }

    if (batchImportBtn) {
        batchImportBtn.addEventListener('click', function() {
            showNotification('正在打开批量导入对话框', 'info');
        });
    }

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const productName = row.cells[2].textContent;

            if (confirm(`确定要删除商品 "${productName}" 吗？`)) {
                row.remove();
                showNotification(`商品 "${productName}" 已删除`, 'success');
            }
        });
    });

    // 全选功能
    const selectAllCheckbox = document.querySelector('#products-content thead input[type="checkbox"]');
    const itemCheckboxes = document.querySelectorAll('#products-content tbody input[type="checkbox"]');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
}

// 订单管理功能
function initializeOrderManagement() {
    const searchInput = document.querySelector('#orders-content .form-control');
    const statusSelect = document.querySelector('#orders-content .form-select');
    const actionButtons = document.querySelectorAll('#orders-content .action-buttons .btn');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 0) {
                searchOrders(query);
            }
        }, 500));
    }

    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            filterOrdersByStatus(this.value);
        });
    }

    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const orderNumber = row.cells[0].textContent;
            const action = this.textContent.trim();

            switch(action) {
                case '查看':
                    showNotification(`正在查看订单 ${orderNumber} 的详情`, 'info');
                    break;
                case '发货':
                    if (confirm(`确定要为订单 ${orderNumber} 发货吗？`)) {
                        updateOrderStatus(row, 'shipped');
                        showNotification(`订单 ${orderNumber} 已发货`, 'success');
                    }
                    break;
                case '跟踪':
                    showNotification(`正在查看订单 ${orderNumber} 的物流信息`, 'info');
                    break;
            }
        });
    });
}

// 用户管理功能
function initializeUserManagement() {
    const addUserBtn = document.querySelector('#users-content .btn-primary');
    const searchInput = document.querySelector('#users-content .form-control');
    const actionButtons = document.querySelectorAll('#users-content .action-buttons .btn');

    if (addUserBtn) {
        addUserBtn.addEventListener('click', function() {
            showNotification('正在打开添加用户对话框', 'info');
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 0) {
                searchUsers(query);
            }
        }, 500));
    }

    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const username = row.cells[2].textContent;
            const action = this.textContent.trim();

            switch(action) {
                case '编辑':
                    showNotification(`正在编辑用户 "${username}" 的信息`, 'info');
                    break;
                case '禁用':
                    if (confirm(`确定要禁用用户 "${username}" 吗？`)) {
                        updateUserStatus(row, 'inactive');
                        showNotification(`用户 "${username}" 已禁用`, 'success');
                    }
                    break;
            }
        });
    });
}

// 储值券管理功能
function initializeVoucherManagement() {
    const voucherForm = document.getElementById('voucherGenerateForm');
    const generateBtn = document.getElementById('generateVoucherBtn');
    const voucherTableBody = document.getElementById('voucherTableBody');
    const searchInput = document.querySelector('#vouchers-content .form-control');
    const statusSelect = document.querySelector('#vouchers-content .form-select');

    if (voucherForm) {
        voucherForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generateVouchers(this);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 0) {
                searchVouchers(query);
            }
        }, 500));
    }

    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            filterVouchersByStatus(this.value);
        });
    }

    // 储值券操作按钮
    if (voucherTableBody) {
        voucherTableBody.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn')) {
                const row = e.target.closest('tr');
                const voucherCode = row.cells[0].textContent.trim();
                const action = e.target.textContent.trim();

                switch(action) {
                    case '查看':
                        showVoucherDetails(voucherCode);
                        break;
                    case '作废':
                        if (confirm(`确定要作废储值券 "${voucherCode}" 吗？`)) {
                            invalidateVoucher(row, voucherCode);
                        }
                        break;
                    case '删除':
                        if (confirm(`确定要删除储值券 "${voucherCode}" 吗？`)) {
                            deleteVoucher(row, voucherCode);
                        }
                        break;
                }
            }
        });
    }
}

// 生成储值券（支持条件竞争漏洞）
function generateVouchers(form) {
    const amount = document.getElementById('voucherAmount').value;
    const quantity = parseInt(document.getElementById('voucherQuantity').value);
    const expiry = document.getElementById('voucherExpiry').value;
    const type = document.getElementById('voucherType').value;
    const remark = document.getElementById('voucherRemark').value;
    const confirmCheck = document.getElementById('voucherConfirm');

    // 表单验证
    if (!amount || !quantity || !expiry || !confirmCheck.checked) {
        showNotification('请填写所有必填字段并确认生成', 'error');
        return;
    }

    // 模拟生成储值券（这里故意不使用数据库锁，为条件竞争漏洞创造条件）
    const generateBtn = document.getElementById('generateVoucherBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>生成中...';

    // 模拟网络延迟，增加条件竞争的可能性
    setTimeout(() => {
        const generatedVouchers = [];
        const currentDate = new Date();
        const expiryDate = new Date(currentDate.getTime() + (parseInt(expiry) * 24 * 60 * 60 * 1000));

        // 生成储值券数据（实际实现中这里应该有数据库操作）
        for (let i = 0; i < quantity; i++) {
            const voucherCode = generateVoucherCode();
            const voucher = {
                code: voucherCode,
                amount: parseInt(amount),
                type: getVoucherTypeText(type),
                expiry: expiryDate.toISOString().split('T')[0],
                status: '未使用',
                generatedAt: currentDate.toISOString().replace('T', ' ').substring(0, 16),
                usedBy: '-',
                usedAt: '-'
            };
            generatedVouchers.push(voucher);
        }

        // 添加到表格
        addVouchersToTable(generatedVouchers);

        // 更新统计数据（这里故意不使用事务，为条件竞争漏洞创造条件）
        updateVoucherStatistics(quantity, parseInt(amount));

        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-plus me-1"></i>生成储值券';

        showNotification(`成功生成 ${quantity} 张面额 ¥${amount} 的储值券`, 'success');

        // 重置表单
        form.reset();
    }, Math.random() * 2000 + 1000); // 随机延迟1-3秒，增加条件竞争概率
}

// 生成储值券兑换码
function generateVoucherCode() {
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').substring(0, 8);
    const random = Math.random().toString(36).substring(2, 6).toUpperCase();
    const sequence = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `VOU${timestamp}${random}${sequence}`;
}

// 获取储值券类型文本
function getVoucherTypeText(type) {
    const typeMap = {
        'general': '通用储值券',
        'newuser': '新用户专享',
        'birthday': '生日专享',
        'activity': '活动专享'
    };
    return typeMap[type] || '通用储值券';
}

// 添加储值券到表格
function addVouchersToTable(vouchers) {
    const tbody = document.getElementById('voucherTableBody');
    if (!tbody) return;

    vouchers.forEach(voucher => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><code>${voucher.code}</code></td>
            <td>¥${voucher.amount}</td>
            <td>${voucher.type}</td>
            <td>${voucher.expiry}</td>
            <td><span class="status-badge pending">${voucher.status}</span></td>
            <td>${voucher.generatedAt}</td>
            <td>${voucher.usedBy}</td>
            <td>${voucher.usedAt}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline-primary btn-sm">查看</button>
                    <button class="btn btn-outline-danger btn-sm">作废</button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 更新储值券统计数据（故意不使用事务，支持条件竞争）
function updateVoucherStatistics(quantity, amount) {
    // 模拟更新统计数据的函数
    // 在实际实现中，这里会有数据库操作
    // 故意不使用数据库锁或事务，为条件竞争漏洞创造条件

    console.log(`更新统计数据: 新增 ${quantity} 张储值券，总面额 ¥${quantity * amount}`);

    // 这里可以添加更新统计卡片的代码
    const statCards = document.querySelectorAll('#vouchers-content .stat-card-value');
    if (statCards.length >= 1) {
        const currentTotal = parseInt(statCards[0].textContent.replace(',', ''));
        statCards[0].textContent = (currentTotal + quantity).toLocaleString();
    }
    if (statCards.length >= 4) {
        const currentValue = parseInt(statCards[3].textContent.replace(/[¥,]/g, ''));
        statCards[3].textContent = '¥' + (currentValue + quantity * amount).toLocaleString();
    }
}

// 搜索储值券
function searchVouchers(query) {
    const rows = document.querySelectorAll('#vouchers-content tbody tr');
    let foundCount = 0;

    rows.forEach(row => {
        const voucherCode = row.cells[0].textContent.trim();
        const amount = row.cells[1].textContent;
        const type = row.cells[2].textContent;

        if (voucherCode.includes(query) || amount.includes(query) || type.includes(query)) {
            row.style.display = '';
            foundCount++;
        } else {
            row.style.display = 'none';
        }
    });

    showNotification(`找到 ${foundCount} 个匹配的储值券`, 'info');
}

// 按状态筛选储值券
function filterVouchersByStatus(status) {
    const rows = document.querySelectorAll('#vouchers-content tbody tr');
    let visibleCount = 0;

    rows.forEach(row => {
        if (status === '所有状态') {
            row.style.display = '';
            visibleCount++;
        } else {
            const statusBadge = row.querySelector('.status-badge');
            const rowStatus = statusBadge.textContent.trim();

            if (rowStatus === status) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        }
    });

    showNotification(`显示 ${visibleCount} 个${status}储值券`, 'info');
}

// 显示储值券详情
function showVoucherDetails(voucherCode) {
    showNotification(`正在查看储值券 ${voucherCode} 的详情`, 'info');
}

// 作废储值券
function invalidateVoucher(row, voucherCode) {
    const statusBadge = row.querySelector('.status-badge');
    statusBadge.textContent = '已作废';
    statusBadge.className = 'status-badge inactive';

    // 移除操作按钮
    const actionButtons = row.querySelector('.action-buttons');
    actionButtons.innerHTML = '<span class="text-muted">已作废</span>';

    showNotification(`储值券 ${voucherCode} 已作废`, 'success');
}

// 删除储值券
function deleteVoucher(row, voucherCode) {
    row.remove();
    showNotification(`储值券 ${voucherCode} 已删除`, 'success');
}

// 系统设置功能
function initializeSettingsManagement() {
    const settingsForm = document.querySelector('#settings-content form');
    const maintenanceMode = document.getElementById('maintenanceMode');
    const userRegistration = document.getElementById('userRegistration');

    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 模拟保存设置
            const formData = new FormData(settingsForm);
            const settings = {
                siteName: formData.get('网站名称') || settingsForm.querySelector('input[placeholder="网站名称"]').value,
                domain: settingsForm.querySelector('input[placeholder="网站域名"]').value,
                adminEmail: settingsForm.querySelector('input[placeholder="管理员邮箱"]').value,
                supportPhone: settingsForm.querySelector('input[placeholder="客服电话"]').value,
                description: settingsForm.querySelector('textarea').value,
                maintenanceMode: maintenanceMode.checked,
                userRegistration: userRegistration.checked
            };

            console.log('保存的系统设置:', settings);
            showNotification('系统设置已保存', 'success');
        });
    }

    // 设置切换时的实时反馈
    if (maintenanceMode) {
        maintenanceMode.addEventListener('change', function() {
            const status = this.checked ? '已开启' : '已关闭';
            showNotification(`维护模式${status}`, 'info');
        });
    }

    if (userRegistration) {
        userRegistration.addEventListener('change', function() {
            const status = this.checked ? '已开启' : '已关闭';
            showNotification(`用户注册${status}`, 'info');
        });
    }
}

// 表格操作功能
function initializeTableActions() {
    // 导出功能
    const exportButtons = document.querySelectorAll('.btn-outline-secondary');
    exportButtons.forEach(button => {
        if (button.textContent.includes('导出')) {
            button.addEventListener('click', function() {
                const pageName = document.getElementById('pageTitle').textContent;
                showNotification(`正在导出${pageName}数据`, 'info');
            });
        }
    });

    // 分页功能
    const paginationLinks = document.querySelectorAll('.pagination .page-link:not(.disabled)');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.textContent;
            showNotification(`正在跳转到第${page}页`, 'info');
        });
    });
}

// 表单操作功能
function initializeFormActions() {
    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            validateForm(this);
        });
    });
}

// 响应式操作
function initializeResponsiveActions() {
    // 移动端菜单切换
    const sidebar = document.getElementById('sidebar');

    // 在小屏幕下点击外部区域关闭侧边栏
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
                sidebar.classList.remove('show');
            }
        }
    });

    // 窗口大小改变时处理侧边栏
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('show');
        }
    });
}

// 搜索订单
function searchOrders(query) {
    const rows = document.querySelectorAll('#orders-content tbody tr');
    let foundCount = 0;

    rows.forEach(row => {
        const orderNumber = row.cells[0].textContent;
        const userName = row.cells[1].textContent;
        const productName = row.cells[2].textContent;

        if (orderNumber.includes(query) || userName.includes(query) || productName.includes(query)) {
            row.style.display = '';
            foundCount++;
        } else {
            row.style.display = 'none';
        }
    });

    showNotification(`找到 ${foundCount} 个匹配的订单`, 'info');
}

// 按状态筛选订单
function filterOrdersByStatus(status) {
    const rows = document.querySelectorAll('#orders-content tbody tr');
    let visibleCount = 0;

    rows.forEach(row => {
        if (status === '所有状态') {
            row.style.display = '';
            visibleCount++;
        } else {
            const statusBadge = row.querySelector('.status-badge');
            const rowStatus = statusBadge.textContent.trim();

            if (rowStatus === status || status === '所有状态') {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        }
    });

    showNotification(`显示 ${visibleCount} 个${status}订单`, 'info');
}

// 搜索用户
function searchUsers(query) {
    const rows = document.querySelectorAll('#users-content tbody tr');
    let foundCount = 0;

    rows.forEach(row => {
        const userId = row.cells[0].textContent;
        const username = row.cells[2].textContent;
        const email = row.cells[3].textContent;

        if (userId.includes(query) || username.includes(query) || email.includes(query)) {
            row.style.display = '';
            foundCount++;
        } else {
            row.style.display = 'none';
        }
    });

    showNotification(`找到 ${foundCount} 个匹配的用户`, 'info');
}

// 更新订单状态
function updateOrderStatus(row, newStatus) {
    const statusBadge = row.querySelector('.status-badge');
    const statusMap = {
        'shipped': '已发货',
        'completed': '已完成',
        'cancelled': '已取消'
    };

    if (statusBadge && statusMap[newStatus]) {
        statusBadge.textContent = statusMap[newStatus];
        statusBadge.className = `status-badge ${newStatus === 'completed' ? 'active' : 'pending'}`;
    }
}

// 更新用户状态
function updateUserStatus(row, newStatus) {
    const statusBadge = row.querySelector('.status-badge');
    const statusMap = {
        'active': '活跃',
        'inactive': '禁用'
    };

    if (statusBadge && statusMap[newStatus]) {
        statusBadge.textContent = statusMap[newStatus];
        statusBadge.className = `status-badge ${newStatus}`;
    }
}

// 表单验证
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    if (isValid) {
        showNotification('表单验证通过', 'success');
    } else {
        showNotification('请填写所有必填字段', 'error');
    }

    return isValid;
}

// 通知系统
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 300px;';

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

// 格式化函数
function formatCurrency(amount) {
    return '¥' + parseFloat(amount).toFixed(2);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('zh-CN');
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

    // 添加页面加载动画
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
        }, index * 100);
    });
});

// 导出功能供其他页面使用
window.HackShopAdmin = {
    showNotification,
    formatCurrency,
    formatDate,
    debounce,
    switchPage,
    searchOrders,
    searchUsers
};

// ========== 批量导入商品 Dialog 功能 ==========

let currentStep = 1;
let uploadedFile = null;

// 打开批量导入dialog
function openBatchImportDialog() {
    currentStep = 1;
    uploadedFile = null;
    resetImportDialog();

    const modal = new bootstrap.Modal(document.getElementById('batchImportModal'));
    modal.show();
}

// 重置dialog状态
function resetImportDialog() {
    // 重置步骤
    currentStep = 1;
    updateStepDisplay();

    // 重置文件输入
    document.getElementById('fileInput').value = '';
    document.getElementById('fileUrlSection').classList.add('d-none');

    // 重置进度和日志
    document.getElementById('importProgress').style.width = '0%';
    document.getElementById('importProgress').textContent = '0%';
    document.getElementById('successCount').textContent = '0';
    document.getElementById('failCount').textContent = '0';
    document.getElementById('importLog').innerHTML = '<div class="log-entry"><small class="text-muted">等待开始导入...</small></div>';
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // 验证文件类型
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(fileExtension)) {
        showNotification('请选择Excel或CSV文件', 'error');
        return;
    }

    // 验证文件大小 (10MB)
    if (file.size > 10 * 1024 * 1024) {
        showNotification('文件大小不能超过10MB', 'error');
        return;
    }

    uploadedFile = file;

    // 模拟文件上传过程
    simulateFileUpload(file);
}

// 模拟文件上传过程
function simulateFileUpload(file) {
    addImportLog('开始上传文件: ' + file.name, 'info');

    // 模拟上传进度
    let progress = 0;
    const uploadInterval = setInterval(() => {
        progress += Math.random() * 30;
        if (progress >= 100) {
            progress = 100;
            clearInterval(uploadInterval);
            onFileUploadComplete(file);
        }
    }, 200);
}

// 文件上传完成
function onFileUploadComplete(file) {
    addImportLog('文件上传成功', 'success');

    // 生成文件URL (SSRF漏洞点)
    const fileUrl = `https://api.hackshop.com/uploads/temp_file_${new Date().getTime()}.${file.name.split('.').pop()}`;
    document.getElementById('fileUrl').value = fileUrl;

    // 显示隐藏的文件URL区域
    setTimeout(() => {
        document.getElementById('fileUrlSection').classList.remove('d-none');
        addImportLog('文件URL已生成: ' + fileUrl, 'warning');

        // SSRF漏洞演示
        setTimeout(() => {
            simulateSSRFVulnerability(fileUrl);
        }, 1000);
    }, 500);
}

// SSRF漏洞演示
function simulateSSRFVulnerability(fileUrl) {
    addImportLog('正在验证文件URL...', 'info');
    addImportLog('SSRF漏洞演示: 系统将请求该URL处理文件内容', 'warning');
    addImportLog('安全风险: 攻击者可能通过构造恶意URL访问内网服务', 'error');
    addImportLog('例如: file:///etc/passwd, http://127.0.0.1:8080, etc.', 'error');
}

// 添加导入日志
function addImportLog(message, type = 'info') {
    const logContainer = document.getElementById('importLog');
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry mb-1';

    const timestamp = new Date().toLocaleTimeString();
    const iconClass = {
        'info': 'fas fa-info-circle text-info',
        'success': 'fas fa-check-circle text-success',
        'warning': 'fas fa-exclamation-triangle text-warning',
        'error': 'fas fa-times-circle text-danger'
    }[type] || 'fas fa-info-circle text-info';

    logEntry.innerHTML = `
        <small class="text-muted">[${timestamp}]</small>
        <i class="${iconClass} ms-1 me-1"></i>
        <span>${message}</span>
    `;

    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// 下一步
function nextStep() {
    if (currentStep === 1) {
        if (!uploadedFile) {
            showNotification('请先选择文件', 'warning');
            return;
        }
        currentStep = 2;
    } else if (currentStep === 2) {
        currentStep = 3;
        startImportProcess();
    }

    updateStepDisplay();
}

// 上一步
function previousStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

// 更新步骤显示
function updateStepDisplay() {
    // 更新步骤指示器
    for (let i = 1; i <= 3; i++) {
        const stepItem = document.getElementById(`step${i}`);
        if (i < currentStep) {
            stepItem.classList.add('completed');
            stepItem.classList.remove('active');
        } else if (i === currentStep) {
            stepItem.classList.add('active');
            stepItem.classList.remove('completed');
        } else {
            stepItem.classList.remove('active', 'completed');
        }
    }

    // 更新步骤内容
    document.getElementById('uploadStep').classList.toggle('d-none', currentStep !== 1);
    document.getElementById('previewStep').classList.toggle('d-none', currentStep !== 2);
    document.getElementById('executeStep').classList.toggle('d-none', currentStep !== 3);

    // 更新按钮显示
    document.getElementById('prevBtn').style.display = currentStep === 1 ? 'none' : 'inline-block';
    document.getElementById('nextBtn').style.display = currentStep === 3 ? 'none' : 'inline-block';
    document.getElementById('finishBtn').style.display = currentStep === 3 ? 'inline-block' : 'none';
}

// 开始导入过程
function startImportProcess() {
    addImportLog('开始批量导入商品...', 'info');
    addImportLog('正在读取文件内容...', 'info');

    let progress = 0;
    const importInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(importInterval);
            completeImport();
        }

        document.getElementById('importProgress').style.width = progress + '%';
        document.getElementById('importProgress').textContent = Math.round(progress) + '%';

        // 模拟导入过程中的日志
        if (progress > 20 && progress < 25) {
            addImportLog('解析文件格式...', 'info');
        } else if (progress > 40 && progress < 45) {
            addImportLog('验证数据完整性...', 'info');
        } else if (progress > 60 && progress < 65) {
            addImportLog('写入数据库...', 'info');
        } else if (progress > 80 && progress < 85) {
            addImportLog('更新商品索引...', 'info');
        }
    }, 300);
}

// 完成导入
function completeImport() {
    const successCount = Math.floor(Math.random() * 10) + 1;
    const failCount = Math.floor(Math.random() * 3);

    document.getElementById('successCount').textContent = successCount;
    document.getElementById('failCount').textContent = failCount;

    addImportLog('导入完成!', 'success');
    addImportLog(`成功导入 ${successCount} 个商品`, 'success');
    if (failCount > 0) {
        addImportLog(`失败 ${failCount} 个商品`, 'error');
    }

    showNotification(`导入完成！成功 ${successCount} 个，失败 ${failCount} 个`, 'success');
}

// 完成导入并关闭dialog
function finishImport() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('batchImportModal'));
    modal.hide();

    // 可以在这里刷新商品列表
    showNotification('批量导入操作已完成', 'success');
}