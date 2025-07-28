import subprocess
import re
from datetime import datetime

def get_git_commit_info():
    try:
        # 获取最后一次提交的哈希值
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving git information: {e}")
        return None

def read_version_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # 使用正则表达式查找版本号和提交哈希
    version_match = re.search(r'#define\s+CK_SOFTWARE_VERSION\s+"(\d+\.\d+\.\d+)"', content)
    commit_hash_match = re.search(r'#define\s+CK_SOFTWARE_COMMIT_HASH\s+"([a-f0-9]+)"', content)
    
    if version_match and commit_hash_match:
        version = version_match.group(1)
        commit_hash = commit_hash_match.group(1)
        major, minor, patch = map(int, version.split('.'))
        
        return (major, minor, patch, commit_hash)
    else:
        print("Version or commit hash not found in the file.")
        return None

def update_ck_version_h(file_path):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_commit_hash = get_git_commit_info()
    
    if not current_commit_hash:
        print("Failed to retrieve commit hash.")
        return
    
    # 获取当前版本和上次的提交哈希
    version_info = read_version_from_file(file_path)
    if not version_info:
        print("Failed to determine version and commit hash from the file.")
        return
    
    major, minor, patch, last_commit_hash = version_info
    
    # 如果 Git 哈希不同，增加 minor 并清零 patch
    if current_commit_hash != last_commit_hash:
        minor += 1  # 增加 minor 版本号
        patch = 0   # 清零 patch 版本号
    else:
        patch += 1  # 如果哈希不变，增加 patch 版本号
    
    new_version = f"{major}.{minor}.{patch}"
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    updated_lines = []
    for line in lines:
        if '#define CK_SOFTWARE_VERSION' in line:
            updated_lines.append(f'#define CK_SOFTWARE_VERSION "{new_version}"\n')
        elif '#define CK_SOFTWARE_BUILD_TIME' in line:
            updated_lines.append(f'#define CK_SOFTWARE_BUILD_TIME "{current_time}"\n')
        elif '#define CK_SOFTWARE_COMMIT_HASH' in line:
            updated_lines.append(f'#define CK_SOFTWARE_COMMIT_HASH "{current_commit_hash}"\n')
        else:
            updated_lines.append(line)
    
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)
    
    print(f"Updated {file_path} with new version {new_version}, build time {current_time}, and commit hash {current_commit_hash}")

if __name__ == "__main__":
    ck_version_h_path = 'ck_config.h'
    update_ck_version_h(ck_version_h_path)
