# main_gui.py - AI线稿打印工具主界面
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# 导入自定义工具模块（确保和本文件同目录）
from camera_utils import (
    start_camera_preview, stop_camera_preview,
    capture_photo, check_camera_device
)
from image_processing import convert_to_line_art
from print_utils import print_photo

# ========== 全局配置 ==========
WINDOW_TITLE = "AI卡通线稿打印工具"
WINDOW_SIZE = "600x400"
FONT_NORMAL = ("微软雅黑", 12)
FONT_BOLD = ("微软雅黑", 14, "bold")
FONT_STATUS = ("微软雅黑", 10)

# ========== GUI 主类 ==========
class LineArtPrintGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        
        # 禁止窗口关闭时直接退出，先清理资源
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 状态变量
        self.is_preview_running = False
        
        # 创建界面元素
        self._create_widgets()
        self._update_status("就绪：请先检查摄像头设备")
        
        # 初始化检查摄像头
        self._check_camera_init()

    def _create_widgets(self):
        """创建所有GUI控件"""
        # 标题栏
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        title_label = ttk.Label(
            title_frame, text="AI卡通线稿打印工具", 
            font=FONT_BOLD, foreground="#2c3e50"
        )
        title_label.pack()

        # 功能按钮区
        btn_frame = ttk.Frame(self.root, padding="20")
        btn_frame.pack(fill=tk.X, expand=True)
        
        # 按钮样式
        btn_style = ttk.Style()
        btn_style.configure("Custom.TButton", font=FONT_NORMAL, padding=8)
        
        # 第一行按钮（预览控制）
        self.preview_btn = ttk.Button(
            btn_frame, text="启动摄像头预览", 
            style="Custom.TButton", command=self.toggle_preview
        )
        self.preview_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.capture_btn = ttk.Button(
            btn_frame, text="拍照", 
            style="Custom.TButton", command=self.do_capture, state=tk.DISABLED
        )
        self.capture_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 第二行按钮（线稿+打印）
        self.line_art_btn = ttk.Button(
            btn_frame, text="生成AI线稿", 
            style="Custom.TButton", command=self.do_line_art, state=tk.DISABLED
        )
        self.line_art_btn.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.print_btn = ttk.Button(
            btn_frame, text="打印线稿", 
            style="Custom.TButton", command=self.do_print, state=tk.DISABLED
        )
        self.print_btn.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # 均分按钮列宽
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # 状态显示区
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X, anchor=tk.S)
        
        status_label = ttk.Label(
            status_frame, text="状态：", 
            font=FONT_STATUS, foreground="#7f8c8d"
        )
        status_label.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar()
        self.status_display = ttk.Label(
            status_frame, textvariable=self.status_var, 
            font=FONT_STATUS, foreground="#27ae60"
        )
        self.status_display.pack(side=tk.LEFT, padx=5)

    def _update_status(self, msg, color="#27ae60"):
        """更新状态显示"""
        self.status_var.set(msg)
        self.status_display.config(foreground=color)
        self.root.update_idletasks()  # 强制刷新界面

    def _check_camera_init(self):
        """初始化检查摄像头"""
        if check_camera_device():
            self._update_status("摄像头设备正常，可启动预览", "#27ae60")
            self.preview_btn.config(state=tk.NORMAL)
        else:
            self._update_status("错误：未检测到摄像头设备！", "#e74c3c")
            self.preview_btn.config(state=tk.DISABLED)

    def toggle_preview(self):
        """切换摄像头预览（启动/停止）"""
        if not self.is_preview_running:
            # 启动预览
            self._update_status("正在启动摄像头预览...", "#f39c12")
            # 用线程避免阻塞GUI
            threading.Thread(target=self._start_preview_thread, daemon=True).start()
        else:
            # 停止预览
            self._update_status("正在停止摄像头预览...", "#f39c12")
            stop_camera_preview()
            self.is_preview_running = False
            self.preview_btn.config(text="启动摄像头预览")
            self.capture_btn.config(state=tk.NORMAL)  # 停止预览后允许拍照
            self._update_status("摄像头预览已停止，可拍照", "#27ae60")

    def _start_preview_thread(self):
        """启动预览的线程函数"""
        success = start_camera_preview()
        if success:
            self.is_preview_running = True
            self.preview_btn.config(text="停止摄像头预览")
            self.capture_btn.config(state=tk.NORMAL)
            self._update_status("摄像头预览已启动，可点击拍照", "#27ae60")
        else:
            self.is_preview_running = False
            self.preview_btn.config(text="启动摄像头预览")
            self._update_status("摄像头预览启动失败！", "#e74c3c")

    def do_capture(self):
        """拍照操作（线程执行）"""
        self.capture_btn.config(state=tk.DISABLED)
        self._update_status("正在拍照，请稍候...", "#f39c12")
        threading.Thread(target=self._capture_thread, daemon=True).start()

    def _capture_thread(self):
        """拍照的线程函数"""
        success, msg = capture_photo()
        if success:
            self._update_status("拍照成功！可生成AI线稿", "#27ae60")
            self.line_art_btn.config(state=tk.NORMAL)
        else:
            self._update_status(f"拍照失败：{msg}", "#e74c3c")
            self.capture_btn.config(state=tk.NORMAL)

    def do_line_art(self):
        """生成AI线稿（线程执行）"""
        self.line_art_btn.config(state=tk.DISABLED)
        self._update_status("AI正在生成线稿...（约10秒）", "#f39c12")
        threading.Thread(target=self._line_art_thread, daemon=True).start()

    def _line_art_thread(self):
        """生成线稿的线程函数"""
        success, img, msg = convert_to_line_art()
        if success:
            self._update_status("AI线稿生成成功！可打印", "#27ae60")
            self.print_btn.config(state=tk.NORMAL)
        else:
            self._update_status(f"线稿生成失败：{msg}", "#e74c3c")
            self.line_art_btn.config(state=tk.NORMAL)

    def do_print(self):
        """打印线稿（线程执行）"""
        self.print_btn.config(state=tk.DISABLED)
        self._update_status("正在打印线稿...", "#f39c12")
        threading.Thread(target=self._print_thread, daemon=True).start()

    def _print_thread(self):
        """打印的线程函数"""
        success = print_photo()
        if success:
            self._update_status("线稿打印完成！", "#27ae60")
            # 打印完成后重置按钮状态（可选）
            self.capture_btn.config(state=tk.DISABLED)
            self.line_art_btn.config(state=tk.DISABLED)
            self.print_btn.config(state=tk.DISABLED)
            messagebox.showinfo("成功", "线稿打印完成！")
        else:
            self._update_status("线稿打印失败！", "#e74c3c")
            self.print_btn.config(state=tk.NORMAL)

    def on_close(self):
        """窗口关闭时清理资源"""
        self._update_status("正在清理资源...", "#f39c12")
        # 停止摄像头预览
        if self.is_preview_running:
            stop_camera_preview()
        # 关闭串口（如果打开）
        from print_utils import close_printer
        close_printer()
        # 退出程序
        self.root.destroy()
        sys.exit(0)

# ========== 程序入口 ==========
if __name__ == "__main__":
    # 确保工作目录是脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建主窗口并运行
    root = tk.Tk()
    app = LineArtPrintGUI(root)
    root.mainloop()
