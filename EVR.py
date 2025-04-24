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
    def __init__(self, node_id, public_key):
        self.node_id = node_id
        self.public_key = public_key
        self.encrypted_shares = []
        self.decrypted_shares = []

    def broadcast(self, message):
        print(f"Node {self.node_id} broadcasts: {message}")

    def receive(self, sender_id, encrypted_share, proof):
        self.encrypted_shares.append((sender_id, encrypted_share, proof))
        # 这里简化处理，实际需要验证证明


class EVR:
    """EVR 协议简化实现"""
    @staticmethod
    def run_protocol(nodes, t, escrow, secret):
        start_time = time.time()
        # 各节点生成并广播熵贡献
        for node in nodes:
            entropy = random.getrandbits(256)
            print(f"Node {node.node_id} generated entropy: {entropy}")
            node.broadcast(f"Entropy: {entropy}")
        entropy_gen_time = time.time() - start_time
        print(f"Entropy generation time: {entropy_gen_time:.6f} seconds")

        start_time = time.time()
        # 模拟合并熵贡献
        combined_entropy = sum(entropy for node in nodes if hasattr(node, 'entropy')) % (2 ** 256)
        print(f"Combined entropy: {combined_entropy}")
        entropy_combine_time = time.time() - start_time
        print(f"Entropy combination time: {entropy_combine_time:.6f} seconds")

        start_time = time.time()
        # 设置 VDF 参数
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

        start_time = time.time()
        # 模拟托管机制
        escrow.deposit(final_randomness)
        escrow_time = time.time() - start_time
        print(f"Escrow deposit time: {escrow_time:.6f} seconds")

        total_time = entropy_gen_time + entropy_combine_time + vdf_setup_time + vdf_compute_time + vdf_verify_time + final_gen_time + escrow_time
        print(f"Total protocol time: {total_time:.6f} seconds")

        return final_randomness


class Escrow:
    """托管平台"""
    def __init__(self):
        self.deposits = []

    def deposit(self, value):
        self.deposits.append(value)
        print(f"Deposited value: {value}")

    def slash(self, node_id):
        # 惩罚机制
        print(f"Node {node_id} is slashed")
        # 实际中需要从 deposits 中扣除相应的押金


# 示例使用
if __name__ == "__main__":
    # 创建节点
    nodes = [Node(i, random.randint(2, 256)) for i in range(5)]  # 创建5个节点

    # 创建托管平台
    escrow = Escrow()

    # 运行协议
    t = 20  # 设置延迟参数
    secret = random.randint(1, 256)  # 简化的秘密值
    final_randomness = EVR.run_protocol(nodes, t, escrow, secret)

    # 模拟惩罚节点
    escrow.slash(2)
