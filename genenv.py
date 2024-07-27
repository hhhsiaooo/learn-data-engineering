import sys
import configparser

# 检查命令行参数是否包含环境名称
if len(sys.argv) != 2:
    print("Usage: python genenv.py <environment>")
    sys.exit(1)

environment = sys.argv[1]

# 读取配置文件
config = configparser.ConfigParser()
config.read("local.ini")

# 获取指定环境的变量
if environment not in config:
    print(f"Environment '{environment}' not found in config file.")
    sys.exit(1)

env_vars = config[environment]

# 将指定环境的变量写入 .env 文件
with open(".env", "w") as f:
    for key, value in env_vars.items():
        f.write(f"{key.upper()}={value}\n")

print("已生成.env文件")

if __name__ == "__main__":
    print(env_vars)
