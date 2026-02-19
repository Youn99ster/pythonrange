# HackShop 仿真商城漏洞靶场 - UI/UX 设计文档

## 1. 目标
- 提供接近真实电商的视觉与交互体验
- 漏洞演示入口嵌入正常业务流程，避免“题目化界面”
- 支持桌面端与移动端可用

## 2. 设计原则
- 真实性：业务页面结构贴近主流 B2C
- 一致性：导航、按钮、状态反馈统一
- 可用性：关键流程最少跳转、异常有反馈
- 响应式：主流程在手机端可操作

## 3. 页面清单（当前实现）

### 用户侧
- 首页：`main/index.html`
- 商品详情：`main/product-detail.html`
- 搜索：`main/search.html`
- 登录：`auth/login.html`
- 注册：`auth/register.html`
- 忘记密码：`auth/forgot-password.html`
- 重置密码：`auth/reset-password.html`
- 购物车：`order/cart.html`
- 结算：`order/checkout.html`
- 支付成功：`order/success.html`
- 个人中心：`user/profile.html`
- 模拟收件箱：`main/inbox.html`

### 管理侧
- 登录：`admin/login.html`
- 仪表盘：`admin/dashboard.html`
- 商品管理：`admin/products.html`
- 订单管理：`admin/orders.html`
- 用户管理：`admin/users.html`
- 储值券：`admin/vouchers.html`
- 设置：`admin/settings.html`

## 4. 交互要点
- 商品管理：支持筛选、编辑、上下架、下架删除、批量导入
- 订单管理：支持关键词筛选、状态筛选、状态更新
- 异步流程：上传与导入都有错误反馈与预览
- 权限流程：后台页未登录统一重定向登录

## 5. 漏洞 UI 隐蔽策略
- 主页面不直接标注漏洞名称
- 漏洞触发融入业务操作（支付、导入、详情查看等）
- 演示说明仅在文档和课程材料中呈现

## 6. 完成状态
- UI 任务总计：17
- 已完成：17
- 完成率：100%

## 7. 后续优化（不影响当前验收）
- 增加全局 Toast 与骨架屏
- 订单物流时间线与售后入口
- 后台表格批量操作与导出能力

## 8. 文档历史
- 2026-02-16：与最新后台交互与工程状态同步
