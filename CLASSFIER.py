# -*- coding: gbk -*-
# import os
# import shutil
# import pandas as pd
# from pathlib import Path

# # 设置路径
# EXCEL_FILE = r"C:\Users\天天\Desktop\our group\ODIR-5K\ODIR-5K\data.xlsx"  # 替换为你的Excel文件路径
# IMAGE_SOURCE_DIR = r"C:\Users\天天\Desktop\our group\ODIR-5K\ODIR-5K\Training Images"  # 替换为图片所在文件夹路径
# OUTPUT_DIR = r"C:\Users\天天\Desktop\12331"  # 输出文件夹路径

# def main():
#     # 创建输出目录
#     output_dir = Path(OUTPUT_DIR)
#     image_source_dir = Path(IMAGE_SOURCE_DIR)
    
#     # 创建文件夹
#     n_folder = output_dir / "N"
#     n_folder.mkdir(parents=True, exist_ok=True)
    
#     for i in range(1, 9):
#         (output_dir / f"class_{i}").mkdir(parents=True, exist_ok=True)
    
#     # 读取Excel
#     df = pd.read_excel(EXCEL_FILE)
    
#     # 遍历每一行
#     for idx, row in df.iterrows():
#         # 获取独热编码 (第8-15列)
#         one_hot = row.iloc[7:15].values
        
#         # 检查是否只有一个1
#         if sum(one_hot) != 1:
#             continue  # 跳过这一行
        
#         # 获取图片文件名和性质
#         img1 = str(row.iloc[3])
#         img2 = str(row.iloc[4])
#         prop1 = str(row.iloc[5]).lower()
#         prop2 = str(row.iloc[6]).lower()
        
#         # 获取类别索引
#         class_idx = [i for i, val in enumerate(one_hot) if val == 1][0] + 1
        
#         # 处理两张图片
#         for img_name, prop in [(img1, prop1), (img2, prop2)]:
#             if pd.isna(img_name):
#                 continue
          
#             # 查找图片文件
#             img_path = None
#             for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
#                 test_path = image_source_dir / f"{img_name}"
#                 if test_path.exists():
#                     img_path = test_path
#                     break
            
#             if img_path is None:
#                 print(f"未找到图片: {img_name}")
#                 continue
            
#             # 确定目标文件夹
#             if prop == 'normal fundus':
#                 target_folder = n_folder
#             else:
#                 target_folder = output_dir / f"class_{class_idx}"
            
#             # 复制图片
#             shutil.copy2(img_path, target_folder / img_path.name)
#             print(f"已复制: {img_name} -> {target_folder.name}")

# if __name__ == "__main__":
#     main()











































import os
import shutil
import pandas as pd
from pathlib import Path

# 设置路径
EXCEL_FILE = r"C:\Users\天天\Desktop\our group\ODIR-5K\ODIR-5K\data.xlsx"  # 替换为你的Excel文件路径
IMAGE_SOURCE_DIR = r"C:\Users\天天\Desktop\our group\ODIR-5K\ODIR-5K\Training Images"  # 替换为图片所在文件夹路径
OUTPUT_DIR = r"C:\Users\天天\Desktop\12332"  # 输出文件夹路径

def main():
    # 创建输出目录
    output_dir = Path(OUTPUT_DIR)
    image_source_dir = Path(IMAGE_SOURCE_DIR)
    
    # 创建文件夹
    n_folder = output_dir / "N"
    n_folder.mkdir(parents=True, exist_ok=True)
    
    for i in range(1, 9):
        (output_dir / f"class_{i}").mkdir(parents=True, exist_ok=True)
    
    # 读取Excel
    df = pd.read_excel(EXCEL_FILE)
    
    # 统计变量
    total_rows = len(df)
    skipped_rows = 0
    processed_images = 0
    missing_images = 0
    
    print(f"开始处理Excel文件，共 {total_rows} 行数据...")
    print("-" * 50)
    
    # 遍历每一行
    for idx, row in df.iterrows():
        row_num = idx + 1  # Excel行号从1开始
        
        # 获取独热编码 (第8-15列)
        one_hot = row.iloc[7:15].values
        
        # 计算1的数量
        ones_count = sum([1 for val in one_hot if val == 1])
        
        # 检查是否只有一个1
        if ones_count == 2:
            skipped_rows += 1
            if ones_count == 0:
                print(f"第{row_num}行: 跳过 - 独热编码中没有1（全0）")
            elif ones_count > 1:
                print(f"第{row_num}行: 跳过 - 独热编码中有 {ones_count} 个1（多类别）")
            continue  # 跳过这一行
        
        # 获取图片文件名和性质
        img1 = str(row.iloc[3])
        img2 = str(row.iloc[4])
        prop1 = str(row.iloc[5]).lower()
        prop2 = str(row.iloc[6]).lower()
        
        # 获取类别索引
        class_idx = [i for i, val in enumerate(one_hot) if val == 1][0] + 1
        
        # 处理两张图片
        images_in_row = 0
        for img_idx, (img_name, prop) in enumerate([(img1, prop1), (img2, prop2)], 1):
            if pd.isna(img_name) or str(img_name).strip() == 'nan':
                continue
                
            # 查找图片文件
            img_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']:
                test_path = image_source_dir / f"{img_name}{ext}"
                if test_path.exists():
                    img_path = test_path
                    break
            
            # 如果找不到图片，尝试直接使用提供的文件名
            if img_path is None:
                test_path = image_source_dir / img_name
                if test_path.exists():
                    img_path = test_path
                else:
                    # 尝试查找忽略大小写的匹配
                    for file in image_source_dir.iterdir():
                        if file.stem.lower() == img_name.lower() or file.name.lower() == img_name.lower():
                            img_path = file
                            break
            
            if img_path is None or not img_path.exists():
                missing_images += 1
                print(f"第{row_num}行，图片{img_idx}: 未找到图片 '{img_name}'")
                continue
            
            # 确定目标文件夹
            if prop == 'normal fundus':
                target_folder = n_folder
            else:
                target_folder = output_dir / f"class_{class_idx}"
            
            # 复制图片
            try:
                shutil.copy2(img_path, target_folder / img_path.name)
                processed_images += 1
                images_in_row += 1
                print(f"第{row_num}行，图片{img_idx}: 已复制 '{img_path.name}' -> {target_folder.name}")
            except Exception as e:
                print(f"第{row_num}行，图片{img_idx}: 复制失败 '{img_path.name}' - {str(e)}")
                missing_images += 1
        
        if images_in_row == 0:
            print(f"第{row_num}行: 没有找到任何图片")
    
    # 打印统计信息
    print("\n" + "="*50)
    print("分类任务完成！统计信息:")
    print(f"总行数: {total_rows}")
    print(f"跳过的行数: {skipped_rows}")
    if skipped_rows > 0:
        print(f"  其中: 独热编码中没有1的行数: {sum(1 for idx, row in df.iterrows() if sum([1 for val in row.iloc[7:15].values if val == 1]) == 0)}")
        print(f"  其中: 独热编码中多个1的行数: {sum(1 for idx, row in df.iterrows() if sum([1 for val in row.iloc[7:15].values if val == 1]) > 1)}")
    print(f"处理的图片数量: {processed_images}")
    print(f"缺失的图片数量: {missing_images}")
    print(f"成功处理的图片比例: {processed_images/(processed_images+missing_images)*100:.1f}%") if (processed_images+missing_images) > 0 else print("成功处理的图片比例: 0.0%")
    print("="*50)
    
    # 显示各文件夹中的图片数量
    print("\n各文件夹中的图片数量:")
    total_files = 0
    for folder in sorted(output_dir.iterdir()):
        if folder.is_dir():
            file_count = len([f for f in folder.iterdir() if f.is_file()])
            total_files += file_count
            print(f"  {folder.name}: {file_count} 张图片")
    print(f"总计: {total_files} 张图片")
    
    # 验证统计
    if processed_images + missing_images + skipped_rows * 2 >= total_rows * 2:
        print("\n统计验证: 数据一致性检查通过")
    else:
        print(f"\n警告: 数据统计可能存在不一致 (期望至少处理 {total_rows*2} 张图片，实际统计 {processed_images+missing_images+skipped_rows*2} 张)")

if __name__ == "__main__":
    main()