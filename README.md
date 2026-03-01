# ✍️ 政务公文 AI 写作 & 文风迁移工具

> **专业、严谨、优雅的公文辅助创作平台。** 
> 旨在连接 AI 的生成能力与政府公文的严谨规范，通过「深度风格提炼」实现真正具备“体制内味儿”的公文创作。

---

## ✨ 核心特性

### 1. ✍️ 智能创作工作台 (Workbench)
- **左右分栏布局**：左侧输入原文/要点，右侧实时预览 AI 润色/生成的成果。
- **双模切换**：
    - **💅 润色草稿**：对已有文字进行语感升级，保留核心要素，优化表达。
    - **🚀 生成初稿**：基于主题和关键词，从零构思符合文风要求的政策初稿。
- **可编辑结果区**：AI 生成的内容直接进入编辑器，支持二次修改后再行下载。

### 2. 🗂️ 深度文风库管理 (Style Library)
- **两级文风架构**：
    - **一级通用**：自动提炼该类文件的宏观气质与跨主题常用语。
    - **二级具体**：聚焦样本文件的微观句式与具体主题表达。
- **AI 自动命名**：上传样本后，AI 智能感悟内容并自动推荐分类与标题。
- **云端持久化 (Supabase)**：接入云数据库，多设备登录、多人分享，文风模板永不丢失。

### 3. 🛡️ 专业化增强功能
- **去 AI 化 (Humanizer)**：内置语义降权算法，去除 AI 生成痕迹，增加语言的“组织感”。
- **多格式下载**：完美支持 Markdown 和 **Microsoft Word (.docx)** 导出。
- **API key 记忆**：侧边栏独立配置面板，加密存储，关闭即焚。

---

## 🎨 界面美学 (UI/UX)
- **沉浸式深色侧边栏**：采用炭黑 + 琥珀金高亮方案，视觉重心明确。
- **优雅空状态**：摒弃警告式提示，使用精美引导卡片与 CTA 按钮。
- **响应式交互**：全居中对齐、微阴影动效、极致对比度保障。

---

## 🛠️ 技术栈
- **Frontend/App**: [Streamlit](https://streamlit.io/)
- **Large Language Model**: DeepSeek-V3 / OpenAI GPT-4o
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL)
- **Documents Handling**: `python-docx`, `PyPDF2`
- **Logic Support**: Python 3.12+

---

## 🚀 部署与安装

### 本地运行
1. **克隆仓库**
   ```bash
   git clone https://github.com/your-username/style-transfer-tool.git
   cd style-transfer-tool
   ```
2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```
3. **启动应用**
   ```bash
   streamlit run app.py
   ```

### 部署至 Streamlit Cloud
1. 将代码上传至 GitHub 个人仓库。
2. 在 [Streamlit Share](https://share.streamlit.io/) 关联此仓库。
3. 在 App 设置的 **Secrets** 中填入数据库凭证：
   ```toml
   SUPABASE_URL = "https://your-id.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```

---

## 🤝 贡献与反馈
欢迎在 Issue 区提出您的改进建议或风格建议。

---
*Powered by DeepMind Agentic AI Engine.*
