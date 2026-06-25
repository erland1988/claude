import json
import os
import re
import sys
from datetime import datetime

import requests

from feishu_common import (
    _check_resp, get_tenant_token,
    find_or_create_root_folder, find_or_create_subfolder, ROOT_FOLDER
)

BASE_URL = "https://open.feishu.cn/open-apis"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.normpath(os.path.join(SCRIPT_DIR, os.pardir, "config.json"))


def load_config():
    """从 config.json 加载飞书配置"""
    if not os.path.isfile(CONFIG_PATH):
        print(f"[FAIL] 配置文件不存在: {CONFIG_PATH}")
        print("请在 .claude/skills/work-in-process/config.json 填入 appId/appSecret/folderName")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_wip_title(file_path):
    """从 WIP.md 提取标题"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^#\s+WIP:\s*(.+)$", line.strip())
                if m:
                    title = m.group(1).strip()
                    title = re.sub(r'[<>:"/\\|?*]', "_", title)
                    return title[:80]
    except Exception:
        pass
    return os.path.splitext(os.path.basename(file_path))[0]


def create_doc(token, title, folder_token=None):
    """创建飞书文档，返回 document_id"""
    url = f"{BASE_URL}/docx/v1/documents"
    body = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token
    resp = requests.post(url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body)
    body = _check_resp(resp, "创建文档")
    doc_id = body["data"]["document"]["document_id"]
    print(f"[OK] 创建文档: {doc_id}")
    return doc_id


def add_doc_content(token, doc_id, file_path):
    """读取 WIP.md 内容，转换为 docx blocks 写入文档"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    children = []
    for line in lines:
        line = line.rstrip()
        if not line:
            children.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": ""}}]}})
        elif line.startswith("### "):
            children.append({"block_type": 5, "heading3": {"elements": [{"text_run": {"content": line[4:]}}]}})
        elif line.startswith("## "):
            children.append({"block_type": 4, "heading2": {"elements": [{"text_run": {"content": line[3:]}}]}})
        elif line.startswith("# "):
            children.append({"block_type": 3, "heading1": {"elements": [{"text_run": {"content": line[2:]}}]}})
        else:
            children.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": line}}]}})

    # 分批写入（每批最多 50 个 block）
    BATCH = 50
    for i in range(0, len(children), BATCH):
        batch = children[i:i + BATCH]
        url = f"{BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
        resp = requests.post(url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"children": batch})
        _check_resp(resp, f"写入内容 batch {i // BATCH + 1}/{(len(children) - 1) // BATCH + 1}")

    print(f"[OK] 写入 {len(children)} 行内容")


# === 主流程 ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python feishu_upload.py <WIP.md 文件路径>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"[FAIL] 文件不存在: {file_path}")
        sys.exit(1)

    cfg = load_config()
    app_id = cfg.get("appId", "")
    app_secret = cfg.get("appSecret", "")
    folder_name = cfg.get("folderName", "")

    missing = [k for k, v in [("appId", app_id), ("appSecret", app_secret)] if not v]
    if missing:
        print(f"[FAIL] config.json 缺少配置项: {', '.join(missing)}")
        sys.exit(1)

    title = parse_wip_title(file_path)
    if title == "{需求标题}":
        print("[FAIL] WIP.md 是空骨架，请先执行 wip-build 填充内容")
        sys.exit(1)

    doc_title = f"{datetime.now().strftime('%Y%m%d')}_{title}"
    print(f"[INFO] 标题: {title}")
    print(f"[INFO] 文档名: {doc_title}")
    if folder_name:
        print(f"[INFO] 目标文件夹: {ROOT_FOLDER}/{folder_name}")
    else:
        print(f"[INFO] 目标文件夹: {ROOT_FOLDER}")

    token = get_tenant_token(app_id, app_secret)

    # 先找到或创建根目录，再在根目录下查找或创建子文件夹
    root_token = find_or_create_root_folder(token)
    folder_token = find_or_create_subfolder(token, root_token, folder_name) if folder_name else root_token

    doc_id = create_doc(token, doc_title, folder_token)
    add_doc_content(token, doc_id, file_path)

    url = f"https://bytedance.feishu.cn/docx/{doc_id}"
    print(f"\n[DONE] 上传完成: {url}")