import os
from PIL import Image
from tkinter import Tk, filedialog


def select_folder():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected


# 获取用户选择的图像文件夹路径
try:
    image_folder = select_folder()
    if not os.path.exists(image_folder):
        raise FileNotFoundError(f"指定的路径不存在: {image_folder}")
except Exception as e:
    print(f"发生错误: {e}")
    exit(1)
# 获取文件夹中的所有图像文件名
image_files = [f for f in os.listdir(image_folder) if f.endswith('.jpg')]

# 定义面列表
faces = ['b', 'u', 'd', 'l', 'r', 'f']

# 创建一个字典，存储图像对象及其位置
images = {face: {'l1': {}, 'l2': {}, 'l3': {}} for face in faces}
max_rows_cols = {'l1': (0, 0), 'l2': (0, 0), 'l3': (0, 0)}

# 读取所有图像文件，并记录每张图像的位置
for image_file in image_files:
    parts = image_file.split('_')
    resolution = parts[0]  # 分辨率等级
    face = parts[1]  # 面
    row = int(parts[2]) - 1
    col = int(parts[3].split('.')[0]) - 1
    images[face][resolution][(row, col)] = Image.open(
        os.path.join(image_folder, image_file))

    # 更新最大行数和列数
    max_rows_cols[resolution] = (max(max_rows_cols[resolution][0], row + 1),
                                 max(max_rows_cols[resolution][1], col + 1))

# 处理每个面和每个分辨率
for face in faces:
    for resolution in ['l1', 'l2', 'l3']:
        max_rows, max_cols = max_rows_cols[resolution]

        # 计算每行的最大高度和每列的最大宽度
        row_heights = [0] * max_rows
        col_widths = [0] * max_cols

        for (row, col), img in images[face][resolution].items():
            row_heights[row] = max(row_heights[row], img.height)
            col_widths[col] = max(col_widths[col], img.width)

        # 计算拼接后大图的总宽度和总高度
        total_width = sum(col_widths)
        total_height = sum(row_heights)

        # 创建一个新的空白图像，用于拼接后的大图
        final_image = Image.new("RGB", (total_width, total_height))

        # 按文件名中的位置信息，将图像放置在相应的位置
        current_y = 0
        for row in range(max_rows):
            current_x = 0
            for col in range(max_cols):
                if (row, col) in images[face][resolution]:
                    img = images[face][resolution][(row, col)]
                    final_image.paste(img, (current_x, current_y))
                    current_x += col_widths[col]
                else:
                    print(f"缺失图像: {face}_{resolution}_{
                          row + 1:02}_{col + 1:02}.jpg")
            current_y += row_heights[row]

        # 如果没有任何图像被拼接，则跳过保存
        if final_image.getbbox() is None:
            print(f"没有足够的图像拼接 {face} 面 {resolution} 分辨率")
            continue

        # 创建分辨率等级对应的文件夹
        output_folder = os.path.join(image_folder, resolution)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 保存拼接后的大图，保持图像质量
        output_path = os.path.join(output_folder, f"{resolution}_{face}.jpg")
        final_image.save(output_path, quality=100)
        # print(f'拼接后的{face}面 {resolution} 分辨率图像已保存至 {output_path}')

# 暂停命令行窗口
input("按ENTER键继续...")
