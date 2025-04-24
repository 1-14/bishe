import random
from sympy import isprime
import time

def generate_large_prime(bits):
    """生成指定位数的大素数"""
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1  # 确保最高位和最低位为1
        if isprime(p):
            return p

def extended_gcd(a, b):
    """扩展欧几里得算法，返回gcd(a, b), x, y使得ax + by = gcd(a, b)"""
    if b == 0:
        return (a, 1, 0)
    else:
        g, y, x = extended_gcd(b, a % b)
        return (g, x - (a // b) * y, y)

def mod_inverse(a, m):
    """计算a模m的逆元"""
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError('a和m不互质，无法计算逆元')
    else:
        return x % m

def setup_vdf(bits):
    """设置VDF参数，返回lambda_value, x, phi_lambda"""
    p = generate_large_prime(bits)
    q = generate_large_prime(bits)
    lambda_value = p * q
    phi_lambda = (p - 1) * (q - 1)
    x = random.randint(2, lambda_value - 1)
    # 确保x与lambda_value互质
    while extended_gcd(x, lambda_value)[0] != 1:
        x = random.randint(2, lambda_value - 1)
    return lambda_value, x, phi_lambda

def vdf_compute(t, lambda_value, x):
    """计算VDF函数值y = x^(2^t) mod lambda_value"""
    e = 1
    for _ in range(t):
        e *= 2
    y = pow(x, e, lambda_value)
    return y

def vdf_verify(t, y, lambda_value, x, phi_lambda):
    """验证VDF计算结果是否正确"""
    # 计算e = 2^t mod phi_lambda
    e = pow(2, t, phi_lambda)
    # 验证y^e ≡ x mod lambda_value
    return pow(x, e, lambda_value) == y

# 示例使用
if __name__ == "__main__":
    # 设置VDF参数
    bits = 256  # 选择适当的安全参数
    lambda_value, x, phi_lambda = setup_vdf(bits)
    print(f"lambda = {lambda_value}")
    print(f"x = {x}")
    print(f"phi(lambda) = {phi_lambda}")

    # 输入t
    t = 10000
    print(f"输入t = {t}")

    # 计算VDF并统计时间
    start_time = time.time()
    y = vdf_compute(t, lambda_value, x)
    compute_time = time.time() - start_time
    print(f"计算得到y = {y}")
    print(f"VDF计算时间: {compute_time:.6f}秒")

    # 验证VDF并统计时间
    start_time = time.time()
    is_valid = vdf_verify(t, y, lambda_value, x, phi_lambda)
    verify_time = time.time() - start_time
    if is_valid:
        print("验证通过，y是正确的VDF结果")
    else:
        print("验证失败，y不是正确的VDF结果")
    print(f"VDF验证时间: {verify_time:.6f}秒")
