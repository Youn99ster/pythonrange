"""
HackShop 工具包 (app.utils)。

子模块：
- db.py             : Redis 客户端初始化
- logging_config.py : 日志系统初始化（控制台 + 文件轮转）
- tools.py          : 鉴权装饰器、验证码、订单号生成、AES 解密、漏洞辅助函数

保持本模块无副作用，避免导入时产生循环依赖。
"""
