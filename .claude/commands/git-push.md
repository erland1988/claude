# /git-push

一键完成 `git add` → `git commit` → `git push`，提交信息自动生成。

## 执行步骤

按顺序完成：

### 1. 检查变更

执行 `git status --porcelain`，若无任何输出（工作区干净），告知用户"没有需要提交的变更"并结束。

### 2. 展示变更并确认

执行 `git diff --stat` 和 `git diff --stat --cached`，展示待提交的文件变更摘要。
若用户未明确确认，询问用户是否继续提交。

### 3. 暂存所有变更

执行 `git add .`

### 4. 生成提交信息并提交

根据 `git diff --cached` 的内容和当前对话上下文，提炼一句合适的中文提交信息（如"新增 /git-push 自定义命令"），执行：

```
git commit -m "<生成的提交信息>"
```

### 5. 推送到远端

执行 `git push`
