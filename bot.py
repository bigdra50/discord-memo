import os
import json
import re
import logging
from typing import Optional, Dict, Any
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import DatabaseManager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vault')

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
DATA_FILE = 'user_data.json'
MAX_NAME_LENGTH = 50
MAX_VALUE_LENGTH = 1900  # Discord表示制限を考慮
MAX_ITEMS_PER_USER = 100  # より多くのデータを保存可能
NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')


class UserDataManager:
    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.use_database = self._should_use_database()
        
        if self.use_database:
            try:
                self.db = DatabaseManager()
                # Test connection and initialize schema if needed
                if self.db.test_connection():
                    self.db.initialize_schema()
                    logger.info("Using PostgreSQL database for data storage")
                else:
                    logger.warning("Database connection failed, falling back to JSON file")
                    self.use_database = False
                    self.data = self.load_data()
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}, falling back to JSON file")
                self.use_database = False
                self.data = self.load_data()
        else:
            self.data = self.load_data()
    
    def _should_use_database(self) -> bool:
        """Check if we should use database based on environment variables"""
        required_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
        return all(os.getenv(var) for var in required_vars)

    def load_data(self) -> Dict[str, Dict[str, str]]:
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            return {}

    def save_data(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.filepath) if os.path.dirname(self.filepath) else '.', exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"データ保存エラー: {e}")
            return False

    def set_user_data(self, user_id: str, key: str, value: str) -> bool:
        if self.use_database:
            return self.db.set_user_data(user_id, key, value)
        else:
            if user_id not in self.data:
                self.data[user_id] = {}
            self.data[user_id][key] = value
            return self.save_data()

    def get_user_data(self, user_id: str, key: Optional[str] = None) -> Optional[Any]:
        if self.use_database:
            return self.db.get_user_data(user_id, key)
        else:
            if user_id not in self.data:
                return None
            if key is None:
                return self.data[user_id]
            return self.data[user_id].get(key)

    def delete_user_data(self, user_id: str, key: str) -> bool:
        if self.use_database:
            return self.db.delete_user_data(user_id, key)
        else:
            if user_id not in self.data or key not in self.data[user_id]:
                return False
            del self.data[user_id][key]
            if not self.data[user_id]:
                del self.data[user_id]
            return self.save_data()

    def get_user_data_count(self, user_id: str) -> int:
        if self.use_database:
            return self.db.get_user_data_count(user_id)
        else:
            return len(self.data.get(user_id, {}))


class VaultBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix='!', intents=intents)
        self.data_manager = UserDataManager()

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            logger.info(f"コマンド同期完了: {len(synced)}件")
        except Exception as e:
            logger.error(f"同期エラー: {e}")

    async def on_ready(self):
        print(f'{self.user} としてログインしました (ID: {self.user.id})')
        print(f'サーバー数: {len(self.guilds)}')
        
        # アプリケーション情報を確認
        try:
            app_info = await self.application_info()
            print(f'アプリケーション名: {app_info.name}')
            print(f'アプリケーション説明: {app_info.description}')
        except Exception as e:
            print(f'アプリケーション情報取得エラー: {e}')
        
        print('Bot準備完了')


bot = VaultBot()



def validate_name(name: str) -> Optional[str]:
    if len(name) > MAX_NAME_LENGTH:
        return f"データ名は{MAX_NAME_LENGTH}文字以内で入力してください。"
    if not NAME_PATTERN.match(name):
        return "データ名は英数字、アンダースコア、ハイフンのみ使用できます。"
    return None


def validate_value(value: str) -> Optional[str]:
    if len(value) > MAX_VALUE_LENGTH:
        return f"データ値は{MAX_VALUE_LENGTH}文字以内で入力してください。"
    return None


@bot.tree.command(name="save", description="データを保存します")
@discord.app_commands.describe(
    name="データの名前（英数字、アンダースコア、ハイフンのみ）",
    value="保存するデータの値"
)
async def save_command(interaction: discord.Interaction, name: str, value: str):
    user_id = str(interaction.user.id)
    
    name_error = validate_name(name)
    if name_error:
        message = f"❌ **エラー**\n\n{name_error}"
        await interaction.response.send_message(message, ephemeral=True)
        return
    
    value_error = validate_value(value)
    if value_error:
        message = f"❌ **エラー**\n\n{value_error}"
        await interaction.response.send_message(message, ephemeral=True)
        return
    
    current_count = bot.data_manager.get_user_data_count(user_id)
    if current_count >= MAX_ITEMS_PER_USER and name not in (bot.data_manager.get_user_data(user_id) or {}):
        message = f"❌ **エラー**\n\n保存できるデータ数の上限（{MAX_ITEMS_PER_USER}件）に達しています。\n不要なデータを削除してください。"
        await interaction.response.send_message(message, ephemeral=True)
        return
    
    if bot.data_manager.set_user_data(user_id, name, value):
        message = f"✅ **保存完了**\n\nデータ「{name}」を保存しました。"
    else:
        message = "❌ **エラー**\n\nデータの保存に失敗しました。"
    
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="get", description="保存したデータを取得します")
@discord.app_commands.describe(name="取得するデータの名前（省略で全データ表示）")
async def get_command(interaction: discord.Interaction, name: Optional[str] = None):
    user_id = str(interaction.user.id)
    
    if name:
        name_error = validate_name(name)
        if name_error:
            message = f"❌ **エラー**\n\n{name_error}"
            await interaction.response.send_message(message, ephemeral=True)
            return
        
        value = bot.data_manager.get_user_data(user_id, name)
        if value is None:
            message = f"🔍 **データ検索**\n\nデータ「{name}」は見つかりませんでした。"
        else:
            # 長いデータの場合は分割表示
            if len(value) > 1800:
                truncated_value = value[:1800] + "..."
                message = f"📄 **データ: {name}** (一部表示)\n\n```\n{truncated_value}\n```\n\n💡 データが長すぎるため一部のみ表示しています。"
            else:
                message = f"📄 **データ: {name}**\n\n```\n{value}\n```"
    else:
        user_data = bot.data_manager.get_user_data(user_id)
        if not user_data:
            message = "📋 **データ一覧**\n\n保存されたデータはありません。"
        else:
            data_list = "\n".join([f"• **{k}**: {v[:50]}{'...' if len(v) > 50 else ''}" 
                                 for k, v in user_data.items()])
            message = f"📋 **保存されたデータ一覧**\n\n{data_list}\n\n合計: {len(user_data)}件"
    
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="delete", description="保存したデータを削除します")
@discord.app_commands.describe(name="削除するデータの名前")
async def delete_command(interaction: discord.Interaction, name: str):
    user_id = str(interaction.user.id)
    
    name_error = validate_name(name)
    if name_error:
        message = f"❌ **エラー**\n\n{name_error}"
        await interaction.response.send_message(message, ephemeral=True)
        return
    
    if bot.data_manager.delete_user_data(user_id, name):
        message = f"🗑️ **削除完了**\n\nデータ「{name}」を削除しました。"
    else:
        message = f"⚠️ **エラー**\n\nデータ「{name}」は見つかりませんでした。"
    
    await interaction.response.send_message(message, ephemeral=True)


@bot.tree.command(name="list", description="保存したデータの名前一覧を表示します")
async def list_command(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = bot.data_manager.get_user_data(user_id)
    
    if not user_data:
        message = "📋 **データ一覧**\n\n保存されたデータはありません。"
    else:
        data_names = "\n".join([f"• {name}" for name in user_data.keys()])
        message = f"📋 **データ一覧**\n\n{data_names}\n\n合計: {len(user_data)}件 / 上限: {MAX_ITEMS_PER_USER}件"
    
    await interaction.response.send_message(message, ephemeral=True)


@bot.event
async def on_application_command_error(interaction: discord.Interaction, error: Exception):
    logger.error(f"コマンドエラー: {type(error).__name__}")
    
    if not interaction.response.is_done():
        try:
            await interaction.response.send_message(
                "エラーが発生しました。もう一度お試しください。",
                ephemeral=True
            )
        except:
            pass


if __name__ == "__main__":
    if not TOKEN:
        logger.error("DISCORD_TOKENが設定されていません。")
        logger.error(".envファイルを作成し、DISCORD_TOKEN=your_token_here を記載してください。")
    else:
        logger.info("Bot起動中...")
        bot.run(TOKEN)