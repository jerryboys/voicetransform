# VoiceTransform

VoiceTransform 是一个语音转写和翻译工具，可进行语音识别、离线音频处理和多语言翻译功能。

## 功能特点

- 语音转写（在线模式）
- 离线音频文件处理
- 多语言支持（包括英语、中文、俄语、西班牙语等）
- 支持多通道音频处理
- 自动标点符号
- 基于 Google Cloud 的STT、翻译服务
- 友好的 Web UI 界面
服务将在 http://localhost:8080 启动，默认用户名和密码为：Demo/DemoPW

### 语音识别功能

1. **实时语音识别**
   - 选择 "STT(OnLine)" 标签页
   - 选择目标语言
   - 点击麦克风图标开始录音
   - 实时查看转写结果

2. **离线音频处理**
   - 选择 "STT(Offline)" 标签页
   - 上传音频文件（支持 WAV 格式）
   - 配置识别参数（语言、采样率等）
   - 点击"执行转录"获取结果

### 翻译功能

多种翻译方式：
- AutoML Translation
- Cloud Translation API (v2 和 v3)

## 项目结构
voicetransform/
├── app-ui/ # Web UI 相关文件
├── data_exploration/ # 数据分析和模型评估工具
├── stt/ # 语音识别核心模块
├── storage/ # 云存储相关功能
├── translate/ # 翻译服务
├── main.py # 主程序入口
└── requirements.txt # 项目依赖
## app-ui/
Web UI 相关文件目录，包含：
- `index.html`: 基础音频播放界面
- `main.py`: Flask 服务器实现，提供音频流和实时音频播放功能

## data_exploration/
数据分析和模型评估工具目录，包含：
- `comparison.py`: 语音识别结果比较工具，使用 Gemini 模型评估不同 ASR 模型的识别效果
- `stt_v1.py`: Google Cloud Speech-to-Text V1 API 实现
- `stt_v2.py`: Google Cloud Speech-to-Text V2 API 实现，支持更多高级特性

## stt/
语音识别核心模块，包含：
- `client.py`: STT 客户端实现，提供：
  - 实时语音识别
  - 短音频文件处理
  - 长音频文件处理
  - 多通道音频处理
  - 支持多种语言模型配置

## storage/
云存储相关功能，包含：
- `client.py`: Google Cloud Storage 客户端实现
  - 文件上传功能
  - 存储桶管理
  - 用于处理超过 60 秒的长音频文件

## translate/
翻译服务模块，包含：
- `automl_translate.py`: AutoML Translation 实现，支持自定义翻译模型
- `translate_cf.py`: Cloud Translation API 实现，包含：
  - V2 API 实现
  - V3 API 实现
  - 翻译质量比较功能
  - 性能评估工具

## main.py
主程序入口文件：
- Gradio Web UI 界面实现
- 语音识别功能集成
- 实时转写和离线处理模式
- 用户认证功能