import re
import os
import tkinter as tk
from tkinter import filedialog



def read_file(file_path):
    """读取文件信息并保留所有字符（包括空格和回车）"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def find_galactic_object_block(content):
    """使用正则表达式定位 galactic_object 块"""
    # 匹配 galactic_object = {
    pattern = r'galactic_object=\n{'
    match = re.search(pattern, content)
    if match:
        start_pos = match.start()
        # 找到匹配的左大括号位置
        brace_start = match.end() - 1

        # 计算括号嵌套以找到结束位置
        bracket_count = 0
        pos = brace_start

        while pos < len(content):
            if content[pos] == '{':
                bracket_count += 1
            elif content[pos] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = pos + 1
                    galactic_block = content[start_pos:end_pos]
                    print(f"找到 galactic_object 块，大小：{len(galactic_block)} 字符")
                    return start_pos, end_pos, galactic_block
            pos += 1

    return None, None, None


def find_id_blocks(galactic_block, id1, id2):
    """在 galactic_object 块内查找两个指定 id 的块"""
    # 确保 id1 <= id2
    if id1 > id2:
        id1, id2 = id2, id1
        #print(f"调整ID顺序：id1={id1}, id2={id2}")

    # 构建正则表达式匹配 id = {
    pattern1 = rf'\n\t{id1}=\n\t{{'
    pattern2 = rf'\n\t{id2}=\n\t{{'

    match1 = re.search(pattern1, galactic_block)
    match2 = re.search(pattern2, galactic_block)

    if not match1 or not match2:
        return None, None

    # 找到 id1 块
    start1 = match1.start()
    brace_start1 = match1.end() - 1

    bracket_count = 0
    pos = brace_start1
    while pos < len(galactic_block):
        if galactic_block[pos] == '{':
            bracket_count += 1
        elif galactic_block[pos] == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end1 = pos + 1
                break
        pos += 1
    else:
        return None, None

    # 找到 id2 块
    start2 = match2.start()
    brace_start2 = match2.end() - 1

    bracket_count = 0
    pos = brace_start2
    while pos < len(galactic_block):
        if galactic_block[pos] == '{':
            bracket_count += 1
        elif galactic_block[pos] == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end2 = pos + 1
                break
        pos += 1
    else:
        return None, None

    id1_block = galactic_block[start1:end1]
    id2_block = galactic_block[start2:end2]

    print(f"找到 id {id1} 块，大小：{len(id1_block)} 字符")
    print(f"找到 id {id2} 块，大小：{len(id2_block)} 字符")

    return (start1, end1, id1_block), (start2, end2, id2_block)


def find_coordinates_and_hyperlanes(id_block):
    """查找 id 块中的 coordinate 和 hyperlane 部分"""
    # 查找 coordinate 块
    coord_pattern = r'coordinate=\n\t\t{'
    coord_match = re.search(coord_pattern, id_block)

    coord_info = None
    if coord_match:
        start = coord_match.start()
        brace_start = coord_match.end() - 1

        bracket_count = 0
        pos = brace_start
        while pos < len(id_block):
            if id_block[pos] == '{':
                bracket_count += 1
            elif id_block[pos] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end = pos + 1
                    coord_info = {'start': start, 'end': end, 'content': id_block[start:end]}
                    break
            pos += 1

    # 查找 hyperlane 块
    hyperlane_pattern = r'hyperlane=\n\t\t{'
    hyperlane_match = re.search(hyperlane_pattern, id_block)

    hyperlane_info = None
    if hyperlane_match:
        start = hyperlane_match.start()
        brace_start = hyperlane_match.end() - 1

        bracket_count = 0
        pos = brace_start
        while pos < len(id_block):
            if id_block[pos] == '{':
                bracket_count += 1
            elif id_block[pos] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end = pos + 1
                    hyperlane_info = {'start': start, 'end': end, 'content': id_block[start:end]}
                    break
            pos += 1

    print(f"Coordinate found: {coord_info is not None}, Hyperlane found: {hyperlane_info is not None}")
    return coord_info, hyperlane_info


def split_id_block(id_block, coord_info, hyperlane_info):
    """将 id 块拆分为不同部分"""
    coord_start = coord_info['start'] if coord_info else len(id_block)
    coord_end = coord_info['end'] if coord_info else len(id_block)
    hyperlane_start = hyperlane_info['start'] if hyperlane_info else len(id_block)
    hyperlane_end = hyperlane_info['end'] if hyperlane_info else len(id_block)

    # 确定各部分边界
    if coord_info and hyperlane_info:
        # 两种情况：coord 在 hyperlane 之前 或者 之后
        if coord_start < hyperlane_start:
            before_coord = id_block[:coord_start]
            coord_block = id_block[coord_start:coord_end]
            between_coord_hyperlane = id_block[coord_end:hyperlane_start]
            hyperlane_block = id_block[hyperlane_start:hyperlane_end]
            after_hyperlane = id_block[hyperlane_end:]
        else:
            before_coord = id_block[:hyperlane_start]
            hyperlane_block = id_block[hyperlane_start:hyperlane_end]
            between_coord_hyperlane = id_block[hyperlane_end:coord_start]
            coord_block = id_block[coord_start:coord_end]
            after_hyperlane = id_block[coord_end:]
    elif coord_info:
        before_coord = id_block[:coord_start]
        coord_block = id_block[coord_start:coord_end]
        between_coord_hyperlane = ""
        hyperlane_block = ""
        after_hyperlane = id_block[coord_end:]
    elif hyperlane_info:
        before_coord = id_block[:hyperlane_start]
        coord_block = ""
        between_coord_hyperlane = ""
        hyperlane_block = id_block[hyperlane_start:hyperlane_end]
        after_hyperlane = id_block[hyperlane_end:]
    else:
        before_coord = id_block
        coord_block = ""
        between_coord_hyperlane = ""
        hyperlane_block = ""
        after_hyperlane = ""

    return before_coord, coord_block, between_coord_hyperlane, hyperlane_block, after_hyperlane


def swap_galactic_objects(id1_block_data, id2_block_data, id1_coords, id1_hyperlanes, id2_coords, id2_hyperlanes):
    """拼接新的 id 块，实现星系交换"""
    # 分割两个 id 块
    id1_parts = split_id_block(id1_block_data, id1_coords, id1_hyperlanes)
    id2_parts = split_id_block(id2_block_data, id2_coords, id2_hyperlanes)

    # 新的 id1: id1 的前部分 + id2 的坐标 + id1 的中间部分 + id2 的航道 + id1 的后部分
    new_id1 = (
            id1_parts[0] +  # before_coord
            (id2_parts[1] if id2_parts[1] else "") +  # coord_block from id2
            id1_parts[2] +  # between_coord_hyperlane
            (id2_parts[3] if id2_parts[3] else "") +  # hyperlane_block from id2
            id1_parts[4]  # after_hyperlane
    )

    # 新的 id2: id2 的前部分 + id1 的坐标 + id2 的中间部分 + id1 的航道 + id2 的后部分
    new_id2 = (
            id2_parts[0] +  # before_coord
            (id1_parts[1] if id1_parts[1] else "") +  # coord_block from id1
            id2_parts[2] +  # between_coord_hyperlane
            (id1_parts[3] if id1_parts[3] else "") +  # hyperlane_block from id1
            id2_parts[4]  # after_hyperlane
    )

    print("成功生成新的 id 块")
    return new_id1, new_id2


def reconstruct_galactic_object_block(galactic_block, id1_info, id2_info, new_id1, new_id2):
    """重构 galactic_object 块"""
    start1, end1, _ = id1_info
    start2, end2, _ = id2_info

    # 确保 start1 <= start2
    if start1 > start2:
        start1, start2 = start2, start1
        end1, end2 = end2, end1
        new_id1, new_id2 = new_id2, new_id1

    # 拼接新的 galactic_object 块
    reconstructed = (
            galactic_block[:start1] +
            new_id1 +
            galactic_block[end1:start2] +
            new_id2 +
            galactic_block[end2:]
    )

    print("成功重构 galactic_object 块")
    return reconstructed


def write_file(file_path, content):
    """将内容写入文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("文件写入完成")


def process_galactic_object_block(galactic_block, id1, id2):
    """处理 galactic_object 块，找到并交换指定的 id 块"""
    # 查找两个 id 块
    id1_info, id2_info = find_id_blocks(galactic_block, id1, id2)

    if not id1_info or not id2_info:
        print(f"错误：找不到 id {id1} 或 id {id2} 的块")
        return galactic_block

    _, _, id1_block = id1_info
    _, _, id2_block = id2_info

    # 查找两个 id 块中的坐标和航道信息
    id1_coords, id1_hyperlanes = find_coordinates_and_hyperlanes(id1_block)
    id2_coords, id2_hyperlanes = find_coordinates_and_hyperlanes(id2_block)

    # 提取并调试输出 hyperlane 的 content 内容
    id1_hyperlane_content = id1_hyperlanes['content'] if id1_hyperlanes else ""
    id2_hyperlane_content = id2_hyperlanes['content'] if id2_hyperlanes else ""

    print(f"\n=== ID {id1} hyperlane content ===")
    print(repr(id1_hyperlane_content))
    print(f"\n=== ID {id2} hyperlane content ===")
    print(repr(id2_hyperlane_content))
    # 解析 hyperlane 中的 to 字段值
    id1_to_list = find_hyperlanes_to_id(id1_hyperlane_content)
    id2_to_list = find_hyperlanes_to_id(id2_hyperlane_content)
    print(f"\nID {id1} 的 hyperlane to 列表：{id1_to_list}")
    print(f"ID {id2} 的 hyperlane to 列表：{id2_to_list}")

    # 交换星系对象
    new_id1, new_id2 = swap_galactic_objects(
        id1_block, id2_block,
        id1_coords, id1_hyperlanes,
        id2_coords, id2_hyperlanes
    )

    # 重构 galactic_object 块
    new_galactic_block = reconstruct_galactic_object_block(
        galactic_block, id1_info, id2_info, new_id1, new_id2
    )

    # 更新指向 id1 的 to 字段
    new_galactic_block = find_toid_blocks(new_galactic_block, id1, id2, id1_to_list)

    # 更新指向 id2 的 to 字段
    new_galactic_block = find_toid_blocks(new_galactic_block, id2, id1, id2_to_list)

    return new_galactic_block


def find_hyperlanes_to_id(hyperlane_block):
    """查找 hyperlane 块中的 to 字段对应的 id 值"""
    if not hyperlane_block:
        return []

    # 匹配 \n\t\t\t\tto=id_to\n\t\t\t\t 格式的模式
    pattern = r'\n\t\t\t\tto=(\d+)\n\t\t\t\t'
    matches = re.findall(pattern, hyperlane_block)

    # 将字符串转换为整数
    id_list = [int(match) for match in matches]
    print(f"找到 hyperlane 中的 to id: {id_list}")
    return id_list


def find_toid_blocks(new_galactic_block, id_a, id_b, id_to_list):
    """更新 galactic_object 块中指向 id_a 的 to 字段为 id_b"""
    current_galactic_block = new_galactic_block

    for target_id in id_to_list:
        # 定位目标 ID 块
        pattern = rf'\n\t{target_id}=\n\t{{'
        match = re.search(pattern, current_galactic_block)

        if not match:
            continue  # 如果找不到目标 ID 块，则跳过

        # 找到目标块的起始和结束位置
        start = match.start()
        brace_start = match.end() - 1

        bracket_count = 0
        pos = brace_start
        while pos < len(current_galactic_block):
            if current_galactic_block[pos] == '{':
                bracket_count += 1
            elif current_galactic_block[pos] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end = pos + 1
                    break
            pos += 1
        else:
            continue  # 如果找不到结束括号，则跳过

        # 分解 galactic_object 块为三部分
        prefix = current_galactic_block[:start]
        target_block = current_galactic_block[start:end]
        suffix = current_galactic_block[end:]

        # 在目标块内查找并替换 to 字段
        to_pattern = rf'\n\t\t\t\tto={id_a}\n\t\t\t\t'
        replacement = f'\n\t\t\t\tto={id_b}\n\t\t\t\t'
        updated_target_block = re.sub(to_pattern, replacement, target_block)

        # 重新拼接 galactic_object 块
        current_galactic_block = prefix + updated_target_block + suffix

        print(f"已更新 ID {target_id} 中的 to 字段，从 {id_a} 改为 {id_b}")

    return current_galactic_block


def main(file_path, id1, id2):
    """主函数"""
    print(f"正在处理文件：{file_path}")
    print(f"交换星系 ID {id1} 和 {id2}")

    # 读取文件
    content = read_file(file_path)
    print(f"文件读取完成，大小：{len(content)} 字符")

    # 定位 galactic_object 块
    start_pos, end_pos, galactic_block = find_galactic_object_block(content)
    if not galactic_block:
        print("错误：未找到 galactic_object 块")
        return

    # 分割文件内容为三部分
    prefix = content[:start_pos]
    suffix = content[end_pos:]

    print("文件内容分割完成")

    # 处理 galactic_object 块
    new_galactic_block = process_galactic_object_block(galactic_block, id1, id2)

    # 重构完整文件内容
    new_content = prefix + new_galactic_block + suffix

    # 写入文件
    write_file(file_path, new_content)

    print("星系位置交换完成！ / Galaxy position swap completed!")
    return True

def log_operation(id1, id2):
    """
    记录操作日志到 log.txt文件

    参数:
       id1: 第一个星系 ID
      id2: 第二个星系 ID
    """
    from datetime import datetime

    # 获取当前日期时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备日志内容
    log_entry = f"{current_time}\nID1={id1}\nID2={id2}\n{'=' * 50}\n"

    try:
        # 以追加模式打开文件（如果不存在会自动创建）
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(f"日志已记录到 log.txt: {current_time}, ID1={id1}, ID2={id2}")
    except Exception as e:
        print(f"写入日志时出错：{e}")


def get_file_path():
    """
    从 config.txt文件中读取 file_path 字段，如果不存在或格式不正确，则弹出文件选择对话框让用户选择，
    并将选择的路径写入 config.txt文件。
    """
    config_file = 'config.txt'

    # 检查配置文件是否存在
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 寻找 file_path 行
            for line in lines:
                if line.startswith('file_path='):
                    path = line[len('file_path='):].strip()
                    if path and os.path.exists(path):  # 检查路径是否有效
                        print("已识别到常用路径，如果想更换路径就删除config.txt或者编辑它")
                        print("Common path detected. To change the path, delete or edit config.txt")
                        return path
                    else:
                        print("配置文件中的路径无效，将重新选择路径")
                        print("The path in config file is invalid, will reselect the path")
                        break  # 如果路径无效，跳出循环进行选择
        except Exception as e:
            print(f"读取配置文件时出错: {e}")

    # 如果配置文件不存在、格式不正确或路径无效，则弹出文件选择对话框
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    selected_path = filedialog.askopenfilename(title="请选择游戏存档文件/gamestate file path configuration",
                                               filetypes=[("Gamestate files", "gamestate"), ("All files", "*.*")])
    root.destroy()

    if selected_path:
        # 将选择的路径写入配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(f'file_path={selected_path}\n')
        print(f"已将路径保存到配置文件: {selected_path}")
        print(f"Path saved to config file: {selected_path}")
        return selected_path
    else:
        print("未选择文件，程序退出")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("星系位置交换工具 / Galaxy Position Swap Tool")
    print("=" * 60)
    # 示例调用
    #file_path = "D:\\admin\\Documents\\Paradox Interactive\\Stellaris\\save games\\m3_-934934054\\gamestate"
    # 获取文件路径
    file_path = get_file_path()
    print("文件路径gamestate_path:", file_path)
    if os.path.exists(file_path):
        # 从用户获取输入
        while True:
        # 从用户获取输入
            try:
                id1 = int(input("请输入第一个星系ID/ Please input the first galaxy ID: "))
                id2 = int(input("请输入第二个星系ID/ Please input the second galaxy ID: "))
                log_operation(id1, id2)
                success = main(file_path, id1, id2)
                if success:
                    print("\n" + "=" * 60)
                    choice = input("是否要继续交换其他星系？(y/n) / Continue to swap other galaxies? (y/n): ")
                    if choice.lower() != 'y':
                        print("\n感谢使用，再见！ / Thanks for using, goodbye!")
                        break
                    print("\n" + "=" * 60)
                else:
                    print("\n操作失败，是否重试？(y/n) / Operation failed, retry? (y/n): ")
                    retry = input()
                    if retry.lower() != 'y':
                        break
            except ValueError:
                print("输入错误，请输入有效的整数ID/Input error, please enter a valid integer ID")
                continue
            except KeyboardInterrupt:
                print("\n\n程序被用户中断 / Program interrupted by user")
                break
            except Exception as e:
                print(f"\n发生未知错误：{e} / Unknown error occurred: {e}")
                print("是否继续？(y/n) / Continue? (y/n): ")
                cont = input()
                if cont.lower() != 'y':
                    break
    else:
        print(f"错误：文件 {file_path} 不存在")
