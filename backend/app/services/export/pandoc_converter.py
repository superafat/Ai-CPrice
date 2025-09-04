"""
Pandoc 轉換服務 - 將 Markdown+LaTeX 轉換為 Word OMML
"""
import subprocess
import asyncio
import os
import tempfile
from typing import Optional, Dict
from loguru import logger

from ...config import settings


class PandocConverter:
    """Pandoc 轉換器"""
    
    def __init__(self):
        self.pandoc_available = False
        self.version = None
    
    async def initialize(self):
        """初始化 Pandoc 轉換器"""
        try:
            # 檢查 Pandoc 是否可用
            result = await self._run_command(["pandoc", "--version"])
            if result["returncode"] == 0:
                self.pandoc_available = True
                self.version = result["stdout"].split('\n')[0]
                logger.info(f"Pandoc 可用: {self.version}")
            else:
                logger.warning("Pandoc 不可用，嘗試安裝...")
                await self._install_pandoc()
        except FileNotFoundError:
            logger.warning("Pandoc 未找到，嘗試安裝...")
            await self._install_pandoc()
    
    async def _install_pandoc(self):
        """安裝 Pandoc"""
        try:
            logger.info("正在安裝 Pandoc...")
            
            # 檢測作業系統並選擇安裝方式
            install_commands = [
                ["apt-get", "update"],
                ["apt-get", "install", "-y", "pandoc"]
            ]
            
            for cmd in install_commands:
                result = await self._run_command(cmd)
                if result["returncode"] != 0:
                    logger.error(f"安裝命令失敗: {' '.join(cmd)}")
                    logger.error(f"錯誤輸出: {result['stderr']}")
            
            # 再次檢查是否安裝成功
            result = await self._run_command(["pandoc", "--version"])
            if result["returncode"] == 0:
                self.pandoc_available = True
                self.version = result["stdout"].split('\n')[0]
                logger.info(f"Pandoc 安裝成功: {self.version}")
            else:
                logger.error("Pandoc 安裝失敗")
                
        except Exception as e:
            logger.error(f"安裝 Pandoc 時發生錯誤: {e}")
    
    async def convert_markdown_to_docx(
        self,
        markdown_content: str,
        output_path: str,
        reference_docx: Optional[str] = None,
        custom_options: Optional[Dict] = None
    ) -> bool:
        """
        將 Markdown 轉換為 Word 文檔
        
        Args:
            markdown_content: Markdown 內容
            output_path: 輸出檔案路徑
            reference_docx: 參考文檔路徑（樣式模板）
            custom_options: 自訂轉換選項
        
        Returns:
            bool: 轉換是否成功
        """
        if not self.pandoc_available:
            raise RuntimeError("Pandoc 不可用，無法進行轉換")
        
        try:
            # 建立臨時 Markdown 檔案
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md.write(markdown_content)
                temp_md_path = temp_md.name
            
            # 建立 Pandoc 命令
            cmd = [
                "pandoc",
                temp_md_path,
                "-o", output_path,
                "--from", "markdown+tex_math_dollars",  # 支援 $ 和 $$ 語法
                "--to", "docx",
                "--mathml",  # 關鍵：將 LaTeX 轉換為 MathML/OMML
                "--standalone",
                "--wrap", "none"  # 不自動換行
            ]
            
            # 添加參考文檔
            if reference_docx and os.path.exists(reference_docx):
                cmd.extend(["--reference-doc", reference_docx])
            
            # 添加自訂選項
            if custom_options:
                if custom_options.get("table_of_contents"):
                    cmd.append("--toc")
                if custom_options.get("number_sections"):
                    cmd.append("--number-sections")
            
            # 執行轉換
            logger.info(f"執行 Pandoc 轉換: {' '.join(cmd)}")
            result = await self._run_command(cmd, timeout=60)
            
            if result["returncode"] == 0:
                # 檢查輸出檔案是否存在
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    logger.info(f"Pandoc 轉換成功: {output_path}")
                    return True
                else:
                    logger.error("輸出檔案不存在或為空")
                    return False
            else:
                logger.error(f"Pandoc 轉換失敗: {result['stderr']}")
                return False
                
        except Exception as e:
            logger.error(f"Pandoc 轉換異常: {e}")
            return False
        finally:
            # 清理臨時檔案
            try:
                if 'temp_md_path' in locals():
                    os.unlink(temp_md_path)
            except:
                pass
    
    async def validate_latex_syntax(self, latex_content: str) -> Dict:
        """
        驗證 LaTeX 語法
        使用 Pandoc 進行語法檢查
        """
        try:
            # 建立測試 Markdown
            test_markdown = f"$$\n{latex_content}\n$$"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_md:
                temp_md.write(test_markdown)
                temp_md_path = temp_md.name
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
                temp_docx_path = temp_docx.name
            
            # 嘗試轉換
            cmd = [
                "pandoc",
                temp_md_path,
                "-o", temp_docx_path,
                "--from", "markdown+tex_math_dollars",
                "--to", "docx",
                "--mathml"
            ]
            
            result = await self._run_command(cmd, timeout=10)
            
            validation_result = {
                "is_valid": result["returncode"] == 0,
                "error_message": result["stderr"] if result["returncode"] != 0 else None,
                "warnings": []
            }
            
            # 清理臨時檔案
            try:
                os.unlink(temp_md_path)
                os.unlink(temp_docx_path)
            except:
                pass
            
            return validation_result
            
        except Exception as e:
            logger.error(f"LaTeX 驗證失敗: {e}")
            return {
                "is_valid": False,
                "error_message": str(e),
                "warnings": []
            }
    
    async def _run_command(self, cmd: list, timeout: int = 30) -> Dict:
        """執行系統命令"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
            
        except asyncio.TimeoutError:
            logger.error(f"命令執行超時: {' '.join(cmd)}")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "命令執行超時"
            }
        except Exception as e:
            logger.error(f"命令執行失敗: {e}")
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }


# 全域轉換器實例
pandoc_converter = PandocConverter()