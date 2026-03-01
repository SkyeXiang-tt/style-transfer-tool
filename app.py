"""
app.py — 政府文件文风迁移工具 v2.0
架构：侧边栏（导航 + API 配置折叠）+ 右侧条件渲染（工作台 / 风格管理）
"""

import streamlit as st
from utils import (
    PROVIDERS,
    get_style_tree,
    get_categories,
    get_styles_in_category,
    read_style_file,
    save_style_file,
    delete_style_file,
    rename_style,
    read_uploaded_file,
    extract_style_content,
    extract_general_style,
    generate_draft,
    polish_draft,
    humanize_text,
    ai_suggest_category,
    ai_suggest_style_name,
    markdown_to_docx,
)

# ════════════════════════════════════════════════════════════════════════════════
#  页面配置
# ════════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="政府文件文风迁移工具",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局 CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* 全局字体 */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ── 侧边栏样式 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    font-size: 0.78rem !important;
    color: #94a3b8 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* 侧边栏品牌区 */
.sidebar-brand {
    padding: 1rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1.5rem;
}
.sidebar-brand-title {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9 !important;
    margin: 0;
}
.sidebar-brand-sub {
    font-size: 0.72rem;
    color: #64748b !important;
    margin-top: 0.2rem;
}

/* 导航按钮 */
.nav-section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #475569 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.5rem 0;
}

.stButton > button[data-nav-btn] {
    width: 100%;
    text-align: left;
}

/* 自定义导航按钮样式 */
/* 1. 导航按钮区域：炭黑 + 琥珀金方案 */
div[data-testid="stSidebar"] .stButton > button {
    background: #2D2D2D !important; 
    border: 1px solid #404040 !important;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    width: 100%;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #D1D5DB !important; /* 未选中态文字：淡灰 */
}

div[data-testid="stSidebar"] .stButton > button:hover {
    background: #404040 !important;
    color: #F3F4F6 !important;
}

/* 导航激活态：琥珀金 */
.nav-item-active-custom {
    background: #F59E0B !important; 
    color: #1F2937 !important;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.9rem;
    font-weight: 700;
    text-align: center;
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    border: 1px solid #F59E0B;
}

/* 2. API 配置区域：独立锁定截图中的深灰蓝方案 (#2d323e) */
[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: #2d323e !important; 
    color: #ffffff !important;
    border-radius: 8px 8px 0 0 !important;
    font-size: 0.9rem !important;
    border: none !important;
}

/* 锁定 API 区域背景，不随交互改变 */
[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
    background: #2d323e !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] .streamlit-expanderContent {
    background: #2d323e !important; /* 整个区域背景统一 */
    border: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1rem !important;
}

/* API 配置区域内的按钮 (确认并保存)：强制保持区域配色，不跳琥珀金 */
[data-testid="stSidebar"] .streamlit-expanderContent .stButton > button {
    background: #404652 !important; /* 稍亮的蓝灰，用于区分 */
    color: #ffffff !important;
    border: 1px solid #4b5563 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] .streamlit-expanderContent .stButton > button:hover {
    background: #4b5563 !important;
}


/* ── 主内容区 ── */
.main-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.2rem 0 0.5rem 0;
    border-bottom: 2px solid #f1f5f9;
    margin-bottom: 1.5rem;
}
.main-header-icon {
    font-size: 1.8rem;
}
.main-header-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}
.main-header-sub {
    font-size: 0.8rem;
    color: #64748b;
    margin: 0;
}

/* 模式切换 Toggle */
.mode-toggle-bar {
    display: flex;
    background: #f1f5f9;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    width: fit-content;
    margin-bottom: 1.2rem;
}
.mode-btn {
    padding: 0.45rem 1.2rem;
    border-radius: 7px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
}
.mode-btn-active {
    background: white;
    color: #1e40af;
    box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
.mode-btn-inactive {
    background: transparent;
    color: #64748b;
}

/* 工作台布局 */
.workbench-toolbar {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem 1rem;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

/* 分栏 */
.panel-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
}

/* 输入面板 */
.input-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    height: 100%;
}

/* 结果面板 */
.result-panel {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    min-height: 400px;
}
.result-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}
.result-panel-title {
    font-size: 0.82rem;
    font-weight: 600;
    color: #374151;
}

/* 空状态卡片 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3.5rem 2rem;
    text-align: center;
    background: linear-gradient(135deg, #f0f9ff 0%, #f8fafc 100%);
    border-radius: 12px;
    border: 2px dashed #bfdbfe;
    min-height: 380px;
}
.empty-state-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.7;
}
.empty-state-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1e40af;
    margin-bottom: 0.5rem;
}
.empty-state-desc {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.6;
    max-width: 280px;
}

/* 风格管理空状态 */
.empty-state-mgr {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 2rem;
    text-align: center;
    background: linear-gradient(135deg, #fefce8 0%, #f8fafc 100%);
    border-radius: 12px;
    border: 2px dashed #fde68a;
    min-height: 300px;
}
.empty-state-mgr .empty-state-title {
    color: #92400e;
}

/* section 标题 */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-desc {
    font-size: 0.82rem;
    color: #64748b;
    margin-bottom: 1.2rem;
}

/* 卡片容器 */
.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* 成功/信息色块 */
.result-content {
    font-size: 0.9rem;
    line-height: 1.8;
    color: #1e293b;
}

/* 下载按钮行 */
.dl-row { display: flex; gap: 0.5rem; margin-top: 0.8rem; }

/* API Key 状态徽章 */
.key-badge-ok {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(16,185,129,0.12);
    color: #065f46;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.75rem;
    font-weight: 600;
}
.key-badge-empty {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(245,158,11,0.12);
    color: #92400e;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Streamlit 组件微调 */
.stTextArea textarea {
    border-radius: 8px !important;
    border-color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
}
div[data-testid="stVerticalBlock"] > div:has(.stButton > button[kind="primary"]) {
    margin-top: 0.5rem;
}

/* 隐藏 Streamlit 默认 footer */
footer { display: none !important; }

/* 导航激活高亮（通过数据属性方案） */
.nav-item-active > div > button {
    background: rgba(59, 130, 246, 0.18) !important;
    color: #93c5fd !important;
    border-left: 3px solid #3b82f6 !important;
    padding-left: calc(0.9rem - 3px) !important;
}

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
#  Session State 初始化
# ════════════════════════════════════════════════════════════════════════════════
def _init():
    defaults = {
        "api_keys": {},
        "current_page": "workbench",       # "workbench" | "learn_style" | "manage_style"
        "workbench_mode": "polish",         # "polish" | "generate"
        "polish_result": None,
        "generate_result": None,
        "generate_topic": "",
        "learn_suggested_cat": "",
        "learn_suggested_name": "",
        "learn_extracted_content": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ════════════════════════════════════════════════════════════════════════════════
#  侧边栏：品牌 + 导航 + API 配置折叠
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── 品牌 Logo ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">📄 文风迁移工具</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 主导航 ──────────────────────────────────────────────────────────────
    st.markdown('<div class="nav-section-label">工 作 台</div>', unsafe_allow_html=True)

    # 工作台按钮
    _wb_active = st.session_state.current_page == "workbench"
    if _wb_active:
        st.markdown('<div class="nav-item-active-custom">✍️ 润色 / 生成工作台</div>', unsafe_allow_html=True)
    else:
        if st.button("✍️ 润色 / 生成工作台", key="nav_workbench", use_container_width=True):
            st.session_state.current_page = "workbench"
            st.rerun()

    st.markdown('<div class="nav-section-label" style="margin-top:1.2rem;">风 格 库</div>', unsafe_allow_html=True)

    # 学习文风
    _ls_active = st.session_state.current_page == "learn_style"
    if _ls_active:
        st.markdown('<div class="nav-item-active-custom">📥 学习新文风</div>', unsafe_allow_html=True)
    else:
        if st.button("📥 学习新文风", key="nav_learn", use_container_width=True):
            st.session_state.current_page = "learn_style"
            st.rerun()

    # 管理文风
    _ms_active = st.session_state.current_page == "manage_style"
    if _ms_active:
        st.markdown('<div class="nav-item-active-custom">⚙️ 管理风格库</div>', unsafe_allow_html=True)
    else:
        if st.button("⚙️ 管理风格库", key="nav_manage", use_container_width=True):
            st.session_state.current_page = "manage_style"
            st.rerun()

    # ── API 配置折叠框 ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # 判断是否已填写 key，决定默认展开/收起
    _any_key = any(v for v in st.session_state.api_keys.values())
    with st.expander("🔑 API 配置", expanded=not _any_key):
        provider_name = st.selectbox(
            "模型厂商",
            list(PROVIDERS.keys()),
            key="sb_provider",
        )
        model_name = st.selectbox(
            "模型",
            PROVIDERS[provider_name]["models"],
            key="sb_model",
        )

        _widget_key = f"widget_apikey_{provider_name}"
        if _widget_key not in st.session_state:
            st.session_state[_widget_key] = st.session_state.api_keys.get(provider_name, "")

        entered_key: str = st.text_input(
            "API Key",
            key=_widget_key,
            type="password",
            placeholder="sk-…",
        )

        if st.button("💾 确认并保存", key=f"btn_save_key_{provider_name}", use_container_width=True):
            st.session_state.api_keys[provider_name] = entered_key
            st.toast(f"✅ {provider_name} Key 已保存", icon="🔑")

        # 从全局字典获取已保存的 key
        current_key = st.session_state.api_keys.get(provider_name, "")

        if current_key:
            st.markdown(
                '<span class="key-badge-ok">✓ Key 已就绪</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<span class="key-badge-empty">⚠ 待配置 Key</span>',
                unsafe_allow_html=True
            )
            st.caption("填入后点击上方确认按钮")

    # 切换厂商提示
    st.markdown(
        '<div style="font-size:0.7rem;color:#475569;margin-top:0.5rem;padding:0 0.5rem;">'
        '💡 切换厂商后，已填写的 Key 不会丢失</div>',
        unsafe_allow_html=True
    )

# 从侧边栏获取 current_key（供主内容区使用）
# 重新读取（sidebar 可能未触发更新）
current_key = st.session_state.api_keys.get(provider_name, "")

# ════════════════════════════════════════════════════════════════════════════════
#  辅助工具函数
# ════════════════════════════════════════════════════════════════════════════════
def _check_key() -> bool:
    if not current_key:
        st.error("⚠️ 请先在左侧边栏的「API 配置」中填写 API Key")
        return False
    return True

def _go_to(page: str):
    """跳转到指定页面"""
    st.session_state.current_page = page
    st.rerun()

def _style_selector_toolbar(key_prefix: str):
    """
    工具栏用风格选择器（紧凑横排）。
    返回 (category, style_name) 或 (None, None)。
    """
    tree = get_style_tree()
    if not tree:
        return None, None
    categories = list(tree.keys())
    col_a, col_b = st.columns([1, 1])
    with col_a:
        cat = st.selectbox("一级分类", categories, key=f"{key_prefix}_cat", label_visibility="collapsed")
    with col_b:
        styles = tree.get(cat, [])
        style = st.selectbox("二级风格", styles, key=f"{key_prefix}_style", label_visibility="collapsed")
    return cat, style

def _download_row(result: str, filename_base: str, key_prefix: str):
    """
    深度重构下载逻辑，解决 UUID 命名和文件损坏问题。
    """
    if not result:
        return

    import hashlib
    import re

    # 1. 严格清理文件名（仅保留中文、字母、数字，确保不为空）
    clean_name = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', filename_base).strip()
    if not clean_name:
        clean_name = "document"
    clean_name = clean_name[:30]

    # 2. 预生成数据并计算哈希，强制按钮刷新
    md_bytes = result.encode("utf-8")
    data_hash = hashlib.md5(md_bytes).hexdigest()[:8]

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 下载样式 Markdown",
            data=md_bytes,
            file_name=f"{clean_name}.md",
            mime="text/plain", # 改用 text/plain 提高浏览器兼容性
            key=f"dl_md_{key_prefix}_{data_hash}",
            use_container_width=True
        )

    with col2:
        try:
            # 这里的 docx_data 已经是修改过的 utils.py 返回的 bytes 了
            docx_data = markdown_to_docx(result, clean_name)
            st.download_button(
                label="📄 下载样式 Word",
                data=docx_data,
                file_name=f"{clean_name}.docx",
                mime="application/octet-stream", # 通用二进制流，更稳
                key=f"dl_docx_{key_prefix}_{data_hash}",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"生成文件失败: {e}")

# ════════════════════════════════════════════════════════════════════════════════
#  页面路由
# ════════════════════════════════════════════════════════════════════════════════
page = st.session_state.current_page

# ────────────────────────────────────────────────────────────────────────────────
#  页面 1：润色 / 生成工作台
# ────────────────────────────────────────────────────────────────────────────────
if page == "workbench":

    # 页头
    st.markdown("""
    <div class="main-header">
        <span class="main-header-icon">✍️</span>
        <div>
            <div class="main-header-title">文稿工作台</div>
            <div class="main-header-sub">选择文风模板，润色已有草稿或从主题直接生成初稿</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tree = get_style_tree()

    # ── 无文风模板时的空状态引导 ────────────────────────────────────────────
    if not tree:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <div class="empty-state-title">还没有文风模板</div>
            <div class="empty-state-desc">
                先去「学习新文风」上传样本文件，<br>
                AI 会自动提取并保存写作风格，<br>
                之后即可在此处选用。
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='margin-top:1.2rem;text-align:center;'>", unsafe_allow_html=True)
        if st.button("📥 去学习文风 →", type="primary", key="empty_goto_learn"):
            _go_to("learn_style")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # ── 模式切换（润色 / 生成）─────────────────────────────────────────
        mode = st.session_state.workbench_mode
        col_m1, col_m2, col_spacer = st.columns([1.2, 1.2, 6])
        with col_m1:
            if mode == "polish":
                st.markdown(
                    '<div style="background:white;border:1.5px solid #3b82f6;color:#1d4ed8;'
                    'border-radius:8px;padding:0.45rem 1.1rem;font-size:0.88rem;'
                    'font-weight:600;text-align:center;box-shadow:0 1px 4px rgba(59,130,246,0.2);">'
                    '💅 润色草稿</div>', unsafe_allow_html=True
                )
            else:
                if st.button("💅 润色草稿", key="switch_polish", use_container_width=True):
                    st.session_state.workbench_mode = "polish"
                    st.session_state.polish_result = None
                    st.rerun()
        with col_m2:
            if mode == "generate":
                st.markdown(
                    '<div style="background:white;border:1.5px solid #3b82f6;color:#1d4ed8;'
                    'border-radius:8px;padding:0.45rem 1.1rem;font-size:0.88rem;'
                    'font-weight:600;text-align:center;box-shadow:0 1px 4px rgba(59,130,246,0.2);">'
                    '🚀 生成初稿</div>', unsafe_allow_html=True
                )
            else:
                if st.button("🚀 生成初稿", key="switch_generate", use_container_width=True):
                    st.session_state.workbench_mode = "generate"
                    st.session_state.generate_result = None
                    st.rerun()

        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

        # ── 顶部工具条：风格选择 + 选项 ───────────────────────────────────
        with st.container():
            st.markdown("""
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                        padding:0.75rem 1rem 0.3rem 1rem;margin-bottom:1rem;">
            """, unsafe_allow_html=True)

            if mode == "polish":
                tc1, tc2, tc3, tc4 = st.columns([0.8, 2, 2, 1.5])
                with tc1:
                    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;padding-top:0.5rem;">文风模板</div>', unsafe_allow_html=True)
                with tc2:
                    categories = list(tree.keys())
                    pw_cat = st.selectbox("一级分类", categories, key="pw_cat", label_visibility="collapsed")
                with tc3:
                    pw_styles = tree.get(pw_cat, [])
                    pw_style = st.selectbox("二级风格", pw_styles, key="pw_style", label_visibility="collapsed")
                with tc4:
                    st.markdown("<div style='padding-top:0.3rem;'>", unsafe_allow_html=True)
                    humanize_on = st.checkbox("🤖→👤 去 AI 化", value=True, key="pw_humanize",
                        help="润色完成后再走一轮去AI化处理，消除 AI 写作痕迹，约额外增加 30 秒")
                    st.markdown("</div>", unsafe_allow_html=True)

            else:  # generate mode
                tg1, tg2, tg3, tg4, tg5 = st.columns([0.8, 2, 2, 1.5, 1.5])
                with tg1:
                    st.markdown('<div style="font-size:0.78rem;color:#64748b;font-weight:600;padding-top:0.5rem;">文风模板</div>', unsafe_allow_html=True)
                with tg2:
                    categories = list(tree.keys())
                    gn_cat = st.selectbox("一级分类", categories, key="gn_cat", label_visibility="collapsed")
                with tg3:
                    gn_styles = tree.get(gn_cat, [])
                    gn_style = st.selectbox("二级风格", gn_styles, key="gn_style", label_visibility="collapsed")
                with tg4:
                    word_count = st.select_slider(
                        "目标字数", key="gn_wc",
                        options=[1000, 1500, 2000, 3000, 5000, 10000, 20000],
                        value=3000, label_visibility="collapsed",
                    )
                    st.markdown(f'<div style="font-size:0.72rem;color:#94a3b8;text-align:center;margin-top:-0.4rem;">目标 {word_count} 字</div>', unsafe_allow_html=True)
                with tg5:
                    st.markdown("<div style='padding-top:0.3rem;'>", unsafe_allow_html=True)
                    humanize_gn = st.checkbox("🤖→👤 去 AI 化", value=True, key="gn_humanize",
                        help="生成完成后再走一轮去AI化处理")
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── 左右分栏主体 ────────────────────────────────────────────────────
        left_col, right_col = st.columns([1, 1], gap="medium")

        # ─── 左栏：输入区 ───────────────────────────────────────────────────
        with left_col:
            st.markdown('<div class="panel-label">📝 输入</div>', unsafe_allow_html=True)

            if mode == "polish":
                draft_input = st.text_area(
                    "粘贴草稿",
                    placeholder="把需要润色的文字粘贴到这里……\n\n支持多段落，AI 将保留核心信息并向目标文风靠拢。",
                    height=420,
                    key="pw_draft",
                    label_visibility="collapsed",
                )
                btn_col, _ = st.columns([1.5, 2])
                with btn_col:
                    do_polish = st.button("💅 开始润色", type="primary", key="btn_polish", use_container_width=True)

            else:  # generate
                topic = st.text_input(
                    "文件主题",
                    placeholder="例如：促进男女就业平等",
                    key="gn_topic",
                )
                key_points = st.text_area(
                    "核心要点（每行一条，可留空）",
                    placeholder="例如：\n消除招聘性别歧视\n同工同酬权益保障\n女性职业晋升通道",
                    height=320,
                    key="gn_keypoints",
                )
                btn_col, _ = st.columns([1.5, 2])
                with btn_col:
                    do_generate = st.button("🚀 生成初稿", type="primary", key="btn_generate", use_container_width=True)

        # ─── 右栏：结果区 ───────────────────────────────────────────────────
        with right_col:
            st.markdown('<div class="panel-label">📄 结果（可编辑）</div>', unsafe_allow_html=True)

            # ── 润色模式结果 ────────────────────────────────────────────────
            if mode == "polish":
                if st.session_state.polish_result:
                    # 使用 text_area 让用户可以编辑结果
                    # key 使用固定后缀，配合前缀实现唯一性并保持状态
                    edited_polish = st.text_area(
                        "预览与编辑结果",
                        value=st.session_state.polish_result,
                        height=480,
                        key="pw_editor_area",
                        label_visibility="collapsed",
                    )
                    st.divider()
                    # 下载按钮读取编辑器内容
                    _download_row(edited_polish, "润色版本", "pw")
                else:
                    st.markdown("""
                    <div class="empty-state" style="min-height:440px;">
                        <div class="empty-state-icon">💅</div>
                        <div class="empty-state-title">润色结果将在此显示</div>
                        <div class="empty-state-desc">
                            在左侧粘贴草稿，<br>
                            选择目标文风后<br>
                            点击「开始润色」
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── 生成模式结果 ────────────────────────────────────────────────
            else:
                if st.session_state.generate_result:
                    edited_generate = st.text_area(
                        "预览与编辑结果",
                        value=st.session_state.generate_result,
                        height=480,
                        key="gn_editor_area",
                        label_visibility="collapsed",
                    )
                    st.divider()
                    _download_row(
                        edited_generate,
                        st.session_state.generate_topic or "初稿",
                        "gn"
                    )
                else:
                    st.markdown("""
                    <div class="empty-state" style="min-height:440px;">
                        <div class="empty-state-icon">🚀</div>
                        <div class="empty-state-title">生成初稿将在此显示</div>
                        <div class="empty-state-desc">
                            在左侧填写主题和要点，<br>
                            选择目标文风后<br>
                            点击「生成初稿」
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── 触发 AI 调用（在列外执行，避免 spinner 渲染问题）───────────────
        if mode == "polish" and "do_polish" in dir() and do_polish:
            if not _check_key():
                pass
            elif not draft_input.strip():
                st.error("请粘贴需要润色的草稿")
            else:
                with st.spinner("AI 正在润色文稿，约需 30 秒……"):
                    result = polish_draft(
                        draft_input, pw_cat, pw_style,
                        current_key, provider_name, model_name,
                    )
                if humanize_on:
                    with st.spinner("正在进行去 AI 化处理，约需 30 秒……"):
                        result = humanize_text(result, current_key, provider_name, model_name)
                st.session_state.polish_result = result
                st.rerun()

        if mode == "generate" and "do_generate" in dir() and do_generate:
            if not _check_key():
                pass
            elif not topic.strip():
                st.error("请填写文件主题")
            else:
                with st.spinner("AI 正在撰写初稿，约需 1–2 分钟……"):
                    result = generate_draft(
                        gn_cat, gn_style, topic, key_points, word_count,
                        current_key, provider_name, model_name,
                    )
                if humanize_gn:
                    with st.spinner("正在进行去 AI 化处理，约需 30 秒……"):
                        result = humanize_text(result, current_key, provider_name, model_name)
                st.session_state.generate_result = result
                st.session_state.generate_topic = topic
                st.rerun()


# ────────────────────────────────────────────────────────────────────────────────
#  页面 2：学习新文风
# ────────────────────────────────────────────────────────────────────────────────
elif page == "learn_style":

    st.markdown("""
    <div class="main-header">
        <span class="main-header-icon">📥</span>
        <div>
            <div class="main-header-title">学习新文风</div>
            <div class="main-header-sub">上传样本文件，AI 自动提取写作风格并保存为模板</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # 文件上传
        st.markdown('<div class="section-title">📎 上传样本文件</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">支持 TXT / MD / PDF / DOCX，可同时上传多份文件</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "上传样本文件（可多选）",
            type=["txt", "md", "pdf", "docx"],
            accept_multiple_files=True,
            key="learn_files",
            label_visibility="collapsed",
        )
        if uploaded_files:
            st.success(f"已选择 {len(uploaded_files)} 个文件：" + "、".join(f.name for f in uploaded_files))

        st.markdown('</div>', unsafe_allow_html=True)

    # 命名区
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🏷️ 文风命名</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-desc">选择/新建一级分类，填写二级风格名；留空则由 AI 自动命名</div>', unsafe_allow_html=True)

        existing_cats = get_categories()
        cat_options = ["＋ 新建分类"] + existing_cats

        col_cat_type, col_cat_input = st.columns([1, 2])
        with col_cat_type:
            cat_choice = st.selectbox(
                "一级文风分类",
                cat_options,
                key="learn_cat_choice",
                help="选择已有分类或新建"
            )
        with col_cat_input:
            if cat_choice == "＋ 新建分类":
                new_cat_input = st.text_input(
                    "新分类名称（留空则 AI 自动命名）",
                    placeholder="例如：政策行动方案",
                    key="learn_new_cat",
                )
            else:
                new_cat_input = ""
                st.info(f"将保存到已有分类：**{cat_choice}**", icon="📁")

        style_name_input = st.text_input(
            "二级风格名称（留空则 AI 自动命名）",
            placeholder="例如：生态环境保护",
            key="learn_style_name",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # 提取按钮
    if st.button("🔍 开始提取风格", type="primary", key="btn_learn", use_container_width=False):
        if not _check_key():
            pass
        elif not uploaded_files:
            st.error("请上传至少一个样本文件")
        else:
            combined = ""
            for f in uploaded_files:
                combined += f"\n\n{'='*20}\n文件：{f.name}\n{'='*20}\n"
                combined += read_uploaded_file(f)

            is_new_category = (cat_choice == "＋ 新建分类")

            if is_new_category:
                final_cat = new_cat_input.strip()
                if not final_cat:
                    with st.spinner("AI 正在自动命名一级分类……"):
                        final_cat = ai_suggest_category(combined, current_key, provider_name, model_name)
                    st.session_state.learn_suggested_cat = final_cat
            else:
                final_cat = cat_choice
                st.session_state.learn_suggested_cat = ""

            final_style = style_name_input.strip()
            if not final_style:
                with st.spinner("AI 正在自动命名二级风格……"):
                    final_style = ai_suggest_style_name(combined, current_key, provider_name, model_name)
                st.session_state.learn_suggested_name = final_style
            else:
                st.session_state.learn_suggested_name = ""

            # ── 提取二级具体文风 ──────────────────────────────────────────
            with st.spinner(f"AI 正在分析具体文风「{final_style}」，约需 30 秒……"):
                specific_content = extract_style_content(
                    combined, final_style,
                    current_key, provider_name, model_name,
                )
            save_style_file(final_cat, final_style, specific_content)

            # ── 新建分类时，同步生成一级通用文风 ─────────────────────────
            general_content = None
            if is_new_category:
                existing_general = read_style_file(final_cat, "通用")
                if not existing_general:   # 该分类还没有「通用」文件
                    with st.spinner(f"AI 正在提炼「{final_cat}」一级通用文风，约需 30 秒……"):
                        general_content = extract_general_style(
                            combined, final_cat,
                            current_key, provider_name, model_name,
                        )
                    save_style_file(final_cat, "通用", general_content)

            # ── 结果展示 ──────────────────────────────────────────────────
            tip_parts = []
            if st.session_state.learn_suggested_cat:
                tip_parts.append(f"一级分类自动命名为「**{final_cat}**」")
            if st.session_state.learn_suggested_name:
                tip_parts.append(f"二级风格自动命名为「**{final_style}**」")
            if tip_parts:
                st.info("；".join(tip_parts) + "；如需修改，请在「管理风格库」页面重命名。", icon="🤖")

            if general_content:
                st.success(
                    f"✅ 已生成两个文风模板：\n"
                    f"- 🗂️ **一级通用**：{final_cat} / 通用\n"
                    f"- 📄 **二级具体**：{final_cat} / {final_style}"
                )
                tab_general, tab_specific = st.tabs(
                    [f"🗂️ 一级通用：{final_cat} / 通用",
                     f"📄 二级具体：{final_cat} / {final_style}"]
                )
                with tab_general:
                    st.caption("适用于所有「" + final_cat + "」类文件的基础风格基线")
                    st.markdown(general_content)
                with tab_specific:
                    st.caption("专属于本次样本主题的精细化风格模板")
                    st.markdown(specific_content)
            else:
                st.success(f"✅ 文风模板「{final_cat} / {final_style}」已保存！")
                with st.expander("查看提取的风格内容", expanded=True):
                    st.markdown(specific_content)



# ────────────────────────────────────────────────────────────────────────────────
#  页面 3：管理风格库
# ────────────────────────────────────────────────────────────────────────────────
elif page == "manage_style":

    st.markdown("""
    <div class="main-header">
        <span class="main-header-icon">⚙️</span>
        <div>
            <div class="main-header-title">管理风格库</div>
            <div class="main-header-sub">编辑、重命名、补充样本或删除已有文风模板</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tree = get_style_tree()

    if not tree:
        # 优雅空状态 + 跳转按钮
        st.markdown("""
        <div class="empty-state-mgr" style="margin-top:2rem;">
            <div class="empty-state-icon">🗂️</div>
            <div class="empty-state-title">风格库为空</div>
            <div class="empty-state-desc">
                还没有任何文风模板，<br>
                先去「学习新文风」上传样本文件，<br>
                AI 会自动提取并保存写作风格。
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='margin-top:1.2rem;text-align:center;'>", unsafe_allow_html=True)
        if st.button("📥 去学习文风 →", type="primary", key="mgr_empty_goto_learn"):
            _go_to("learn_style")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # 选择要操作的文风
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📂 选择文风模板</div>', unsafe_allow_html=True)
            mgr_cats = list(tree.keys())
            col_mc, col_ms = st.columns(2)
            with col_mc:
                mgr_cat = st.selectbox("选择一级分类", mgr_cats, key="mgr_cat")
            with col_ms:
                mgr_styles = tree.get(mgr_cat, [])
                mgr_style = st.selectbox("选择二级风格", mgr_styles, key="mgr_style")
            st.markdown('</div>', unsafe_allow_html=True)

        current_content = read_style_file(mgr_cat, mgr_style)

        # 编辑内容
        with st.expander("✏️ 编辑风格模板内容", expanded=True):
            # 使用动态 key 确保切换文风时内容刷新
            editor_key = f"mgr_edit_content_{mgr_cat}_{mgr_style}"
            edited = st.text_area(
                "风格模板内容（可直接修改）",
                value=current_content,
                height=380,
                key=editor_key,
            )
            if st.button("💾 保存修改", type="primary", key="mgr_btn_save"):
                save_style_file(mgr_cat, mgr_style, edited)
                st.success("✅ 已保存！")

        # 补充样本
        with st.expander("📎 补充样本文件，重新提取风格"):
            extra_files = st.file_uploader(
                "上传补充样本（可多选）",
                type=["txt", "md", "pdf", "docx"],
                accept_multiple_files=True,
                key="mgr_extra_files",
            )
            if st.button("🔄 补充并重新提取", key="mgr_btn_reextract"):
                if not _check_key():
                    pass
                elif not extra_files:
                    st.error("请上传补充样本文件")
                else:
                    combined = f"【已有风格参考】\n{current_content}\n\n"
                    for f in extra_files:
                        combined += f"\n\n{'='*20}\n补充文件：{f.name}\n{'='*20}\n"
                        combined += read_uploaded_file(f)
                    with st.spinner("AI 正在重新分析，约需 30 秒……"):
                        new_content = extract_style_content(
                            combined, mgr_style,
                            current_key, provider_name, model_name,
                        )
                    save_style_file(mgr_cat, mgr_style, new_content)
                    st.success(f"✅ 风格模板「{mgr_cat} / {mgr_style}」已更新！")
                    st.markdown(new_content)
                    st.rerun()

        # 重命名
        with st.expander("🏷️ 重命名（修改分类或风格名）"):
            st.caption("修改一级分类或二级风格名称，原有内容不变")
            col_nc, col_ns = st.columns(2)
            with col_nc:
                new_cat_rename = st.text_input("新一级分类名", value=mgr_cat, key="mgr_new_cat")
            with col_ns:
                new_style_rename = st.text_input("新二级风格名", value=mgr_style, key="mgr_new_style")
            if st.button("确认重命名", key="mgr_btn_rename"):
                nc = new_cat_rename.strip() or mgr_cat
                ns = new_style_rename.strip() or mgr_style
                if nc == mgr_cat and ns == mgr_style:
                    st.warning("名称未变化，无需保存。")
                else:
                    rename_style(mgr_cat, mgr_style, nc, ns)
                    st.success(f"✅ 已重命名为「{nc} / {ns}」")
                    st.rerun()

        # 删除
        with st.expander("🗑️ 删除此风格模板"):
            st.warning(f"即将删除：**{mgr_cat} / {mgr_style}**，此操作不可恢复！")
            if st.button("确认删除", type="secondary", key="mgr_btn_delete"):
                delete_style_file(mgr_cat, mgr_style)
                st.success(f"✅ 已删除「{mgr_cat} / {mgr_style}」")
                st.rerun()
