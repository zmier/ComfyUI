# Makefile for ComfyUI

# 定义变量
# VENV_DIR: 虚拟环境目录
# VENV_ACTIVATE: 激活虚拟环境的脚本
# PYTHON: 虚拟环境中的 Python 解释器
# PIP: 虚拟环境中的 pip
VENV_DIR = .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

# 默认目标, 执行 make 时默认执行 help
.PHONY: all
all: help

# 显示帮助信息
.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo "  install             - Install dependencies"
	@echo "  run                 - Run ComfyUI"
	@echo "  clean               - Remove virtual environment"
	@echo "  install-ps-plugin   - Install the Photoshop plugin and download all required models"

# 安装依赖
# 首先确保虚拟环境存在, 然后安装 requirements.txt 中的依赖
.PHONY: install
install: $(VENV_DIR)
	@echo "Installing dependencies..."
	@source $(VENV_ACTIVATE); $(PIP) install -r requirements.txt

# 运行 ComfyUI
# 首先确保虚拟环境存在, 然后运行 main.py
.PHONY: run
run: $(VENV_DIR)
	@echo "Starting ComfyUI..."
	@source $(VENV_ACTIVATE); $(PYTHON) main.py

# 创建虚拟环境
# 如果 $(VENV_DIR) 目录不存在, 则创建它
$(VENV_DIR):
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV_DIR)

# 清理虚拟环境
# 删除虚拟环境目录
.PHONY: clean
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENV_DIR)

# 安装 Photoshop 插件
.PHONY: install-ps-plugin
install-ps-plugin:
	@echo "Starting Photoshop plugin setup..."
	@$(PYTHON) setup_photoshop_integration.py
