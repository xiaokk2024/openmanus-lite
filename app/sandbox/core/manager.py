from typing import Optional

from app.sandbox.core.sandbox import Sandbox

_sandbox_instance: Optional[Sandbox] = None

def get_sandbox() -> Sandbox:
    """获取沙箱的单例"""
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = Sandbox()
    return _sandbox_instance

def close_sandbox():
    """关闭并清理沙箱实例"""
    global _sandbox_instance
    if _sandbox_instance:
        _sandbox_instance.close()
        _sandbox_instance = None