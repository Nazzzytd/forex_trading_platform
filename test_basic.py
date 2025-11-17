import sys
import os

print("🔍 调试信息:")
print(f"当前目录: {os.getcwd()}")
print(f"Python版本: {sys.version}")

# 添加src到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

print(f"添加路径: {src_path}")
print("Python路径:")
for i, path in enumerate(sys.path[:5]):  # 只显示前5个
    print(f"  {i+1}. {path}")

# 检查agents目录是否存在
agents_path = os.path.join(src_path, 'agents')
print(f"\n📁 Agents目录: {agents_path}")
print(f"目录存在: {os.path.exists(agents_path)}")

if os.path.exists(agents_path):
    print("Agents目录内容:")
    for item in os.listdir(agents_path):
        item_path = os.path.join(agents_path, item)
        print(f"  {item} - {'目录' if os.path.isdir(item_path) else '文件'}")
