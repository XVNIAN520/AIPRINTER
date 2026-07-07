# AI Voice Printer

基于 RK3588 的 AI 语音打印一体机，支持语音识别 + AI 绘图 + 热敏打印，同时提供摄像头拍照 + AI 线稿生成的完整工作流。

## 功能特性

- **语音识别**：通过麦克风录音，使用 Vosk 离线中文语音模型将语音转为文字
- **AI 绘图**：将识别文字作为提示词，调用火山方舟图像生成 API 生成 3 张黑白线稿风格图片
- **热敏打印**：将生成的图片通过串口发送至热敏打印机输出
- **摄像头拍照**：支持 GStreamer 管道驱动 V4L2 摄像头实时预览与抓拍
- **AI 线稿生成**：将实拍照片通过图生图 API 转换为适合打印上色的卡通线稿
- **GUI 界面**：基于 Tkinter 的现代化渐变 UI，支持语音、绘图、打印全流程操作

## 环境依赖

### 系统要求
- Python 3.10+
- Linux（推荐 RK3588 开发板，如 Orange Pi 5 / Rock Pi 5）
- 热敏打印机（串口，如厦门旻佑）
- USB 摄像头（V4L2 兼容）

### Python 依赖

```bash
pip install pyaudio wave vosk requests pillow pyserial
```

各依赖说明：
| 包名 | 用途 |
|------|------|
| `pyaudio` | 麦克风录音 |
| `vosk` | 离线中文语音识别 |
| `requests` | 调用火山方舟图像生成 API |
| `pillow` | 图片处理与格式转换 |
| `pyserial` | 热敏打印机串口通信 |

### Vosk 中文语音模型（必须自行下载）

本项目使用 `vosk-model-cn-kaldi-multicn-0.15` 离线中文语音模型，**未包含在仓库中**（文件过大）。

**下载步骤：**

1. 前往 Vosk 官方模型页面：https://alphacephei.com/vosk/models
2. 找到 **`vosk-model-cn-kaldi-multicn-0.15`**（中文普通话，约 2.5GB）
3. 下载并解压，将 `vosk-model-cn-kaldi-multicn-0.15` 文件夹放置于项目根目录
4. 修改 `voice_to_text.py` 中的 `ASR_MODEL_PATH` 指向该模型路径

```python
# voice_to_text.py
ASR_MODEL_PATH = r"./vosk-model-cn-kaldi-multicn-0.15"
```

> 若使用 RK3588 板子，建议将模型放在 `/home/elf/print/model` 并相应修改路径。

### 系统工具依赖（摄像头功能）

摄像头预览与拍照依赖 GStreamer：

```bash
sudo apt install gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
```

## 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/XVNIAN520/AIPRINTER.git
cd AIPRINTER
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
# 或手动安装（见上方依赖列表）
```

### 3. 下载 Vosk 语音模型

按上述「Vosk 中文语音模型」说明下载并放置模型文件夹。

### 4. 配置参数

根据硬件环境修改以下文件中的路径/设备号：

- `gui_constants.py`：摄像头设备号、串口路径、图片保存路径
- `voice_to_text.py`：Vosk 模型路径
- `print_image.py`：串口设备路径（`COM_PORT`）
- `ai_draw.py` / `image_processing.py`：火山方舟 API Key 和模型 ID（`ARK_API_KEY`、`MODEL_ID`）

### 5. 运行 GUI

```bash
python thinker.py
```

### 6. 命令行测试（无 GUI）

```bash
# 完整 AI 流程（录音 → 识别 → 生图）
python runall.py

# 单独测试语音识别
python voice_to_text.py

# 单独测试 AI 绘图
python ai_draw.py

# 单独测试打印
python print_image.py
```

## 项目结构

```
AIPRINTER/
├── thinker.py              # 主 GUI 程序（渐变 UI，推荐入口）
├── main_gui.py            # 线稿打印工具 GUI（简化版）
├── runall.py              # 命令行完整流程脚本
├── gui.py                 # GUI 界面 Mock 版（开发测试用）
├── gui_constants.py       # 全局配置常量（摄像头/打印/路径）
│
├── record.py              # 麦克风录音（PyAudio）
├── voice_to_text.py       # 语音转文字（Vosk）
├── ai_draw.py             # AI 绘图（火山方舟 API）
├── print_image.py         # 热敏打印（串口 ESC/POS 指令）
├── camera_utils.py        # 摄像头预览与拍照（GStreamer）
├── image_processing.py    # 照片转 AI 线稿（图生图 API）
├── print_utils.py         # 打印工具函数
├── limit_hight.py         # 图片高度限制工具
├── pinyin_data.py         # 拼音数据（语音相关）
│
├── picoclaw               # picoclaw AI Agent 框架可执行文件
│
├── ai-printer.desktop     # Linux 桌面快捷方式
├── thinker.desktop        # Linux 桌面快捷方式
├── run_thinker.sh         # 启动脚本
├── start_thinker.sh       # 启动脚本
├── icon.png               # 应用图标
├── logo.jpg               # 项目 Logo
└── .gitignore
```

## 硬件说明

| 硬件 | 说明 |
|------|------|
| 主控 | RK3588（Orange Pi 5 / Rock Pi 5 等） |
| 打印机 | 厦门旻佑热敏打印机，串口 `/dev/ttyS9`，波特率 9600 |
| 摄像头 | V4L2 兼容 USB 摄像头，设备号 `/dev/video21` |
| 麦克风 | 系统默认输入设备（RK3588 优先 NAU8822） |

## API 说明

图像生成使用**火山方舟（Volcengine Ark）** 服务，需自行申请 API Key：

- 申请地址：https://www.volcengine.com/product/ark
- 配置位置：`ai_draw.py` 和 `image_processing.py` 中的 `ARK_API_KEY` 和 `MODEL_ID`

## 许可证

MIT License

## 作者

XVNIAN520
