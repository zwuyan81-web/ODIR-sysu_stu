# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
"""
Teachable Machine 图像数据增强脚本
功能：旋转、翻转、亮度调整、添加噪点、模糊、缩放裁剪
"""

import os
import sys
import random
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import math

def create_augmented_folder(input_folder, output_folder, augment_per_image=3):
    """
    主函数：读取输入文件夹的所有图片，进行增强并保存到输出文件夹
    """
    # 支持的图片格式
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 收集所有图片文件
    image_files = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                full_path = os.path.join(root, file)
                # 保留相对路径结构
                rel_path = os.path.relpath(full_path, input_folder)
                image_files.append((full_path, rel_path))
    
    if not image_files:
        print(f"错误: 在 '{input_folder}' 中没有找到图片文件！")
        print(f"支持的格式: {IMAGE_EXTENSIONS}")
        return
    
    print(f"找到 {len(image_files)} 张图片，开始增强...")
    print(f"每张图片将生成 {augment_per_image} 个增强版本")
    
    processed_count = 0
    
    # 处理每张图片
    for img_idx, (img_path, rel_path) in enumerate(image_files, 1):
        try:
            # 打开图片并转换为RGB模式
            original = Image.open(img_path).convert('RGB')
            
            # 保存原始图片（可选）
            output_rel_dir = os.path.dirname(rel_path)
            if output_rel_dir:
                os.makedirs(os.path.join(output_folder, output_rel_dir), exist_ok=True)
            
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            ext = os.path.splitext(img_path)[1].lower()
            if ext == '.jpeg':
                ext = '.jpg'
            
            # 生成增强版本
            for aug_idx in range(augment_per_image):
                # 随机选择1-3种增强方法组合应用
                augmented = original.copy()
                methods_applied = []
                
                # 方法1: 随机旋转 (-30度到30度之间)
                if random.random() > 0.3:
                    angle = random.uniform(-30, 30)
                    augmented = augmented.rotate(angle, expand=True, fillcolor=(128, 128, 128))
                    methods_applied.append(f"R{angle:.0f}")
                
                # 方法2: 随机翻转
                if random.random() > 0.5:
                    if random.random() > 0.5:
                        augmented = ImageOps.mirror(augmented)  # 水平翻转
                        methods_applied.append("FH")
                    else:
                        augmented = ImageOps.flip(augmented)   # 垂直翻转
                        methods_applied.append("FV")
                
                # 方法3: 随机亮度调整
                if random.random() > 0.3:
                    factor = random.uniform(0.7, 1.3)
                    enhancer = ImageEnhance.Brightness(augmented)
                    augmented = enhancer.enhance(factor)
                    methods_applied.append(f"B{factor:.1f}")
                
                # 方法4: 随机对比度调整
                if random.random() > 0.3:
                    factor = random.uniform(0.7, 1.3)
                    enhancer = ImageEnhance.Contrast(augmented)
                    augmented = enhancer.enhance(factor)
                    methods_applied.append(f"C{factor:.1f}")
                
                # 方法5: 随机缩放裁剪 (模拟不同距离)
                if random.random() > 0.5:
                    w, h = augmented.size
                    # 随机缩放因子
                    scale = random.uniform(0.8, 1.2)
                    new_w, new_h = int(w * scale), int(h * scale)
                    
                    # 调整大小
                    resized = augmented.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    
                    if scale > 1.0:
                        # 随机裁剪回原始尺寸
                        left = random.randint(0, new_w - w)
                        top = random.randint(0, new_h - h)
                        augmented = resized.crop((left, top, left + w, top + h))
                    else:
                        # 放置到灰色背景上
                        new_img = Image.new('RGB', (w, h), (128, 128, 128))
                        left = (w - new_w) // 2
                        top = (h - new_h) // 2
                        new_img.paste(resized, (left, top))
                        augmented = new_img
                    methods_applied.append(f"Z{scale:.1f}")
                
                # 方法6: 随机模糊
                if random.random() > 0.7:
                    radius = random.uniform(0.5, 2.0)
                    augmented = augmented.filter(ImageFilter.GaussianBlur(radius))
                    methods_applied.append(f"BL{radius:.1f}")
                
                # 生成输出文件名
                methods_str = "_".join(methods_applied) if methods_applied else "original"
                output_filename = f"{base_name}_aug{aug_idx+1}_{methods_str}{ext}"
                
                # 保持原始目录结构
                if output_rel_dir:
                    output_path = os.path.join(output_folder, output_rel_dir, output_filename)
                else:
                    output_path = os.path.join(output_folder, output_filename)
                
                # 保存图片（调整质量为95%以平衡文件大小和清晰度）
                augmented.save(output_path, quality=95)
                processed_count += 1
            
            # 显示进度
            if img_idx % 10 == 0 or img_idx == len(image_files):
                print(f"进度: {img_idx}/{len(image_files)} 张原图处理完成，已生成 {processed_count} 张增强图片")
                
        except Exception as e:
            print(f"警告: 处理图片 {img_path} 时出错: {e}")
            continue
    
    print(f"\n✅ 增强完成！")
    print(f"原图数量: {len(image_files)}")
    print(f"增强后总数量: {processed_count}")
    print(f"输出文件夹: {os.path.abspath(output_folder)}")
    print(f"\n📁 你现在可以将 '{output_folder}' 整个文件夹上传到 Teachable Machine")

def print_help():
    """打印帮助信息"""
    print("=" * 60)
    print("Teachable Machine 图像数据增强工具")
    print("=" * 60)
    print("\n使用方法:")
    print("  方式1: python simple_augment.py <输入文件夹> [增强倍数] [输出文件夹]")
    print("  方式2: 直接运行脚本，然后按照提示输入参数")
    print("\n参数说明:")
    print("  输入文件夹: 包含原始图片的文件夹（支持子文件夹）")
    print("  增强倍数: 每张原图生成多少增强版本（默认: 3）")
    print("  输出文件夹: 保存增强图片的文件夹（默认: augmented_images）")
    print("\n示例:")
    print("  python simple_augment.py ./my_photos")
    print("  python simple_augment.py ./training_data 5 ./enhanced_data")
    print("\n增强方法包括: 旋转、翻转、亮度/对比度调整、缩放裁剪、模糊")
    print("=" * 60)

def main():
    """主函数：处理命令行参数"""
    # 默认参数
    input_folder = ""
    augment_per_image = 3
    output_folder = "augmented_images"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print_help()
            return
        
        input_folder = sys.argv[1]
        
        if len(sys.argv) > 2:
            try:
                augment_per_image = int(sys.argv[2])
            except ValueError:
                print(f"错误: 增强倍数必须是整数，接收到 '{sys.argv[2]}'")
                print_help()
                return
        
        if len(sys.argv) > 3:
            output_folder = sys.argv[3]
    
    # 如果没有提供命令行参数，则交互式获取
    if not input_folder:
        print_help()
        print("\n" + "=" * 60)
        input_folder = input("请输入原始图片所在的文件夹路径: ").strip()
        
        if not input_folder:
            print("错误: 必须提供输入文件夹路径！")
            return
        
        multiplier = input("请输入每张图片的增强倍数 [默认: 3]: ").strip()
        if multiplier:
            try:
                augment_per_image = int(multiplier)
            except ValueError:
                print(f"警告: '{multiplier}' 不是有效数字，使用默认值 3")
        
        custom_output = input("请输入输出文件夹名称 [默认: augmented_images]: ").strip()
        if custom_output:
            output_folder = custom_output
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹 '{input_folder}' 不存在！")
        return
    
    # 显示配置信息
    print("\n" + "=" * 60)
    print("配置摘要:")
    print(f"  输入文件夹: {os.path.abspath(input_folder)}")
    print(f"  增强倍数: {augment_per_image}")
    print(f"  输出文件夹: {output_folder}")
    print("=" * 60 + "\n")
    
    # 执行增强
    create_augmented_folder(input_folder, output_folder, augment_per_image)

if __name__ == "__main__":
    main()