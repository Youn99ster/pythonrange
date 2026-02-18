document.addEventListener('DOMContentLoaded', function() {
    initializeCartPage();
});

function initializeCartPage() {
    initializeCartItems();
    initializeQuantitySelectors();
    initializeBatchOperations();
    initializeCheckoutActions();
    updateCartSummary();
}

// 购物车商品管理
function initializeCartItems() {
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
                if (selectAllCheckbox) selectAllCheckbox.checked = isChecked;
                if (selectAllBottomCheckbox) selectAllBottomCheckbox.checked = isChecked;
                updateCartSummary();
            });
        }
    });

    // 删除单个商品
    const removeButtons = document.querySelectorAll('.cart-item-remove');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const cartItem = this.closest('.cart-item');
            const itemId = cartItem.dataset.id;
            const productName = cartItem.querySelector('.cart-item-info h4').textContent;

            if (confirm(`确定要删除 "${productName.trim()}" 吗？`)) {
                removeCartItem(itemId, cartItem);
            }
        });
    });
}

// 数量选择器功能
function initializeQuantitySelectors() {
    const quantitySelectors = document.querySelectorAll('.quantity-selector');

    quantitySelectors.forEach(selector => {
        const minusBtn = selector.querySelector('.minus');
        const plusBtn = selector.querySelector('.plus');
        const quantityInput = selector.querySelector('.quantity-input');
        const cartItem = selector.closest('.cart-item');
        const itemId = cartItem.dataset.id;

        minusBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue > 1) {
                updateCartItemQuantity(itemId, currentValue - 1, quantityInput, cartItem);
            }
        });

        plusBtn.addEventListener('click', function() {
            let currentValue = parseInt(quantityInput.value);
            if (currentValue < 99) {
                updateCartItemQuantity(itemId, currentValue + 1, quantityInput, cartItem);
            }
        });

        quantityInput.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                value = 1;
            } else if (value > 99) {
                value = 99;
            }
            updateCartItemQuantity(itemId, value, quantityInput, cartItem);
        });
    });
}

// 更新购物车商品数量
function updateCartItemQuantity(itemId, quantity, inputElement, rowElement) {
    fetch('/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            inputElement.value = quantity;
            // Update item subtotal
            const subtotalElement = rowElement.querySelector('.cart-item-subtotal');
            subtotalElement.textContent = `¥${data.item_subtotal}`;
            updateCartSummary();
        } else {
            alert(data.message || '更新失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('网络错误，请稍后重试');
    });
}

// 删除购物车商品
function removeCartItem(itemId, rowElement) {
    fetch('/cart/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            item_id: itemId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            rowElement.remove();
            updateCartSummary();
            checkEmptyCart();
        } else {
            alert(data.message || '删除失败');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('网络错误，请稍后重试');
    });
}

// 批量操作功能
function initializeBatchOperations() {
    const batchDeleteBtn = document.getElementById('batchDelete');

    // 批量删除
    if (batchDeleteBtn) {
        batchDeleteBtn.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.item-checkbox:checked');
            if (selectedItems.length === 0) {
                alert('请选择要删除的商品');
                return;
            }

            if (confirm(`确定要删除选中的 ${selectedItems.length} 件商品吗？`)) {
                const itemIds = Array.from(selectedItems).map(checkbox => {
                    return checkbox.closest('.cart-item').dataset.id;
                });

                fetch('/cart/batch_remove', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        item_ids: itemIds
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        selectedItems.forEach(checkbox => {
                            checkbox.closest('.cart-item').remove();
                        });
                        updateCartSummary();
                        checkEmptyCart();
                    } else {
                        alert(data.message || '批量删除失败');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('网络错误，请稍后重试');
                });
            }
        });
    }
}

// 结算操作
function initializeCheckoutActions() {
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            const selectedItems = document.querySelectorAll('.item-checkbox:checked');
            if (selectedItems.length === 0) {
                alert('请选择要结算的商品');
                return;
            }
            
            const itemIds = Array.from(selectedItems).map(checkbox => {
                return checkbox.closest('.cart-item').dataset.id;
            });

            fetch('/cart/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    item_ids: itemIds
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/checkout/' + data.order_id;
                } else {
                    alert(data.message || '结算失败');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('网络错误，请稍后重试');
            });
        });
    }
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

    const totalItemsElement = document.getElementById('totalItems');
    const subtotalElement = document.getElementById('subtotal');
    const totalElement = document.getElementById('total');

    if (totalItemsElement) totalItemsElement.textContent = `${totalItems} 件`;
    if (subtotalElement) subtotalElement.textContent = `¥${subtotal.toLocaleString()}`;
    if (totalElement) totalElement.textContent = `¥${subtotal.toLocaleString()}`;
}

// 更新全选状态
function updateSelectAllState() {
    const checkboxes = document.querySelectorAll('.item-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectAllBottomCheckbox = document.getElementById('selectAllBottom');
    
    if (checkboxes.length === 0) return;

    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    if (selectAllCheckbox) selectAllCheckbox.checked = allChecked;
    if (selectAllBottomCheckbox) selectAllBottomCheckbox.checked = allChecked;
}

// 检查购物车是否为空
function checkEmptyCart() {
    const cartItems = document.querySelectorAll('.cart-item');
    if (cartItems.length === 0) {
        location.reload(); // Reload to show empty cart state from server template
    }
}