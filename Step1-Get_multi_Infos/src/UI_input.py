import tkinter as tk
from tkinter import filedialog, messagebox
import asyncio
import os
import sys


# 检查是否在打包环境中运行
if getattr(sys, 'frozen', False):
    # 打包后
    base_path = sys._MEIPASS
else:
    # 源码运行
    base_path = os.path.dirname(os.path.abspath(__file__))

chrome_path = os.path.join(base_path, "chrome-win", "chrome.exe")





sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from GetInfos_outputCSV_Commands import main

def select_cookies():
    path = filedialog.askopenfilename(
        title="选择 cookies.json 文件",
        filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
    )
    if path:
        cookies_entry.delete(0, tk.END)
        cookies_entry.insert(0, path)

def select_chrome():
    path = filedialog.askopenfilename(
        title="请选择chrome.exe",
        filetypes=[("chrome.exe", "chrome.exe"), ("所有文件", "*.*")]
    )
    if path:
        chrome_entry.delete(0, tk.END)
      
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        chrome_entry.insert(0, os.path.join(base_path, "chrome-win", "chrome.exe"))  # 设置默认路径




def start():
    mainurl = mainurl_entry.get().strip()
    targeturl = targeturl_entry.get().strip()
    cookies_path = cookies_entry.get().strip()
    chromium_path = chrome_entry.get().strip()
    if not mainurl or not targeturl or not cookies_path or not chromium_path:
        messagebox.showerror("错误", "请填写所有内容")
        return
    asyncio.run(main(mainurl, targeturl, cookies_path, chromium_path))
    messagebox.showinfo("提示", "调用完成")

root = tk.Tk()
root.title("基本参数输入")

tk.Label(root, text="mainurl:").grid(row=0, column=0, sticky="e")
mainurl_entry = tk.Entry(root, width=50)
mainurl_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Label(root, text="主页url，eg：https://www.openrec.tv", fg="gray").grid(row=1, column=1, sticky="w")

tk.Label(root, text="targeturl:").grid(row=2, column=0, sticky="e")
targeturl_entry = tk.Entry(root, width=50)
targeturl_entry.grid(row=2, column=1, padx=5, pady=5)
tk.Label(root, text="待抓url，eg：https://www.openrec.tv/user/aiba_derby", fg="gray").grid(row=3, column=1, sticky="w")

tk.Label(root, text="cookies.json:").grid(row=4, column=0, sticky="e")
cookies_entry = tk.Entry(root, width=40)
cookies_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
tk.Button(root, text="选择文件", command=select_cookies).grid(row=4, column=2, padx=5)
tk.Label(root, text="请上传包含有效 cookies 的 JSON 文件", fg="gray").grid(row=5, column=1, sticky="w")

# Chrome路径选择
tk.Label(root, text="Chrome路径:").grid(row=6, column=0, sticky="e")
chrome_entry = tk.Entry(root, width=40)
chrome_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
# 兼容源码和打包环境的默认路径
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
chrome_entry.insert(0, os.path.join(base_path, "chrome-win", "chrome.exe"))
tk.Button(root, text="选择chrome.exe", command=select_chrome).grid(row=6, column=2, padx=5)
tk.Label(root, text="请选择 ms-playwright 目录下的 chrome.exe", fg="gray").grid(row=7, column=1, sticky="w")

tk.Button(root, text="开始", command=start, width=20).grid(row=8, column=0, columnspan=3, pady=15)

root.mainloop()