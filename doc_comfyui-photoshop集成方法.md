# ComfyUI-Photoshop 插件安装与使用指南

本文档根据您提供的资料整理而成，旨在帮助您一步步在 Photoshop 中成功安装和使用 `comfyui-photoshop` 插件。

## 第一部分：前期准备 (Photoshop)

在开始之前，请确保您的 Photoshop 环境满足以下条件：

1.  **安装 Photoshop**: 确保您安装了最新版的 Photoshop (至少是 **2024** 版本)。
2.  **Adobe 账号**: 注册并登录您的 Adobe 账号。
3.  **Creative Cloud**: 安装 Adobe Creative Cloud 桌面应用程序，插件安装时需要。
4.  **安装 ZXP Installer**: 下载并安装 ZXP Installer 工具，它用于安装 Photoshop 插件。

## 第二部分：ComfyUI 配置

接下来，我们需要对 ComfyUI 进行一些设置和扩展。

1.  **硬件要求**: 确保您的电脑拥有至少 **6GB** 的独立显存。
2.  **更新 ComfyUI**: 将您的 ComfyUI 更新到最新版本。
3.  **安装必需的 ComfyUI 插件**:
    *   打开 ComfyUI Manager。
    *   搜索并安装以下四个必需的自定义节点：
        *   `comfyui-photoshop`
        *   `MTB Nodes`
        *   `Rgthree's ComfyUI Nodes`
        *   `Use Everywhere`
4.  **设置语言**: **(重要)** 将 ComfyUI 的界面语言设置为 **英文**，中文模式可能会导致报错。
5.  **重启 ComfyUI**: 完成上述操作后，重启 ComfyUI。

## 第三部分：工作流和模型准备

插件需要特定的工作流和模型才能运行。

1.  **加载预设工作流**:
    *   在 ComfyUI 界面中，双击鼠标左键打开搜索框。
    *   搜索并选择 **"Photoshop ComfyUI Plugin"** 选项。
    *   在弹出的菜单中，点击 **"Load SD1.5"** 来加载官方预设工作流。
2.  **下载所需模型**:
    *   在加载的工作流中，点击左侧的 **"Required File"** 按钮，查看并下载所有必需的模型文件。
    *   **模型列表如下**:
        *   **大模型 (Checkpoints)**:
            *   `epicrealism_naturalSinRC1VAE.safetensors`
            *   `epicrealism_pureEvolutionV5-inpainting.safetensors`
        *   **Lora 模型**:
            *   `LCM_LoRA_SD1.5.safetensors`
            *   `add_detail.safetensors`
        *   **ControlNet 模型**: (可通过 ComfyUI Manager > Install Models 搜索安装)
            *   `ControlNet-v1-1 (lineart; fp16)`
            *   `ControlNet-v1-1 (scribble; fp16)`
            *   `ControlNet-v1-1 (inpaint; fp16)`
        *   **放大模型 (Upscale Model)**: (可通过 ComfyUI Manager > Install Models 搜索安装)
            *   `4x-UltraSharp`

## 第四部分：安装 Photoshop 插件

现在，我们将插件文件安装到 Photoshop 中。

1.  **关闭 Photoshop**: 确保 Photoshop 程序已完全关闭。
2.  **登录 Creative Cloud**: 启动 Adobe Creative Cloud 应用并保持登录状态。
3.  **找到插件文件**:
    *   进入 ComfyUI 的根目录。
    *   找到路径 `custom_nodes\comfyui-photoshop\Install_Plugin`。
    *   在该文件夹中找到名为 **`3e6d64e0_PS.ccx`** 的文件。
4.  **安装插件**:
    *   启动 **ZXP Installer**。
    *   将 `3e6d64e0_PS.ccx` 文件拖入 ZXP Installer 窗口或通过其菜单打开该文件。
    *   等待安装完成。

## 第五部分：连接并开始使用

最后一步，连接 ComfyUI 和 Photoshop。

1.  **启动 ComfyUI**: 确保 ComfyUI 正在运行，并且已经加载了第二部分中提到的 **SD1.5 官方工作流**。
2.  **启动 Photoshop**: 打开 Photoshop。
3.  **打开插件面板**:
    *   在 Photoshop 的菜单栏中，找到 **"增效工具" (Plugins)**。
    *   点击打开 **"ComfyUI for adobe Photoshop"** 插件。
4.  **连接服务**:
    *   在插件的 **AI Panel** 面板中，点击 **"Get Started"**。
    *   插件会自动连接到正在运行的 ComfyUI 服务。连接成功后，您就可以开始使用了。

---

## 附录：5 种预设功能使用方法

### 1. 文生图 (Txt 2 Img)

1.  在 Ps 中新建一个空白画布 (推荐尺寸 512-1024px)。
2.  在 AI Panel 中，将模式设为 `Txt 2 Img`。
3.  填写英文提示词，选择合适的步数。
4.  点击 **Render** 生成图像。

### 2. 图生图 (Img 2 Img)

1.  在 Ps 中打开一张图片并确保其处于选中状态。
2.  在 AI Panel 中，将模式设为 `Img 2 Img`。
3.  填写你希望生成效果的提示词，并调节 `creative` 滑块控制与原图的相似度。
4.  点击 **Render**。

### 3. 图像高清放大 (Simple Fast Upscale)

1.  在 Ps 中打开一张图片并选中。
2.  在 AI Panel 中，将模式设为 `Simple Fast Upscale`。
3.  点击 **Render**。

### 4. 局部重绘 (In-Paint)

1.  在 Ps 中打开一张图片，使用套索或选框工具选中要重绘的区域。
2.  在 AI Panel 中，将模式设为 `In-Paint`。
3.  在提示词中描述你想要重绘出的内容 (如 "a red tie")。
4.  点击 **Render**。

### 5. 外绘扩展 (Out-Paint)

1.  在 Ps 中打开一张图片，使用裁剪工具将画布向外扩展。
2.  使用选框工具选中新增加的空白区域。
3.  在 AI Panel 中，将模式设为 `In-Paint`。
4.  在提示词中描述整个画面的主要内容 (以确保生成部分与原图协调)。
5.  点击 **Render**。

---
希望这份指南对您有帮助！