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

class Node:
    """表示网络中的一个节点"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.entropy = None

    def generate_entropy(self):
        """生成熵贡献"""
        self.entropy = random.getrandbits(256)
        print(f"Node {self.node_id} generated entropy: {self.entropy}")

    def get_entropy(self):
        """获取熵贡献"""
        return self.entropy

class BeaconPlusVDF:
    """Beacon+VDF 协议实现"""
    @staticmethod
    def run_protocol(nodes, t):
        start_time = time.time()
        # 各节点生成并广播熵贡献
        for node in nodes:
            node.generate_entropy()
            print(f"Node {node.node_id} broadcasts entropy: {node.get_entropy()}")
        entropy_gen_time = time.time() - start_time
        print(f"Entropy generation time: {entropy_gen_time:.6f} seconds")

        start_time = time.time()
        # 模拟合并熵贡献
        combined_entropy = sum(node.get_entropy() for node in nodes) % (2 ** 256)
        print(f"Combined entropy: {combined_entropy}")
        entropy_combine_time = time.time() - start_time
        print(f"Entropy combination time: {entropy_combine_time:.6f} seconds")

        start_time = time.time()
        # 使用合并的熵作为 VDF 的输入
        lambda_value, x, phi_lambda = setup_vdf(256)
        vdf_input = combined_entropy
        print(f"VDF input: {vdf_input}")
        vdf_setup_time = time.time() - start_time
        print(f"VDF setup time: {vdf_setup_time:.6f} seconds")

        start_time = time.time()
        # 计算 VDF
        y = vdf_compute(t, lambda_value, x)
        print(f"VDF output: {y}")
        vdf_compute_time = time.time() - start_time
        print(f"VDF computation time: {vdf_compute_time:.6f} seconds")

        start_time = time.time()
        # 验证 VDF
        if vdf_verify(t, y, lambda_value, x, phi_lambda):
            print("VDF verification succeeded")
        else:
            print("VDF verification failed")
        vdf_verify_time = time.time() - start_time
        print(f"VDF verification time: {vdf_verify_time:.6f} seconds")

        start_time = time.time()
        # 生成最终的随机输出
        final_randomness = (combined_entropy + y) % (2 ** 256)
        print(f"Final randomness: {final_randomness}")
        final_gen_time = time.time() - start_time
        print(f"Final randomness generation time: {final_gen_time:.6f} seconds")

        total_time = entropy_gen_time + entropy_combine_time + vdf_setup_time + vdf_compute_time + vdf_verify_time + final_gen_time
        print(f"Total protocol time: {total_time:.6f} seconds")

        return final_randomness

# 示例使用
if __name__ == "__main__":
    # 创建节点
    nodes = [Node(i) for i in range(7)]  # 创建7个节点

    # 运行协议
    t = 20  # 设置延迟参数
    BeaconPlusVDF.run_protocol(nodes, t)
