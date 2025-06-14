#!/usr/bin/env python3
"""
Discord Vault Bot 手動テスト用スクリプト
実際のDiscordコマンドをシミュレートしてテストします
"""

import os
import sys
import tempfile
from unittest.mock import Mock

# テスト用にbot.pyをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot import UserDataManager, validate_name, validate_value, MAX_NAME_LENGTH, MAX_VALUE_LENGTH


def test_scenario(name, func):
    """テストシナリオ実行"""
    print(f"\n🧪 {name}")
    print("-" * 40)
    try:
        func()
        print("✅ 成功")
    except Exception as e:
        print(f"❌ 失敗: {e}")


def basic_crud_test():
    """基本CRUD操作テスト"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        manager = UserDataManager(temp_file.name)
        user_id = "123456789"
        
        # 保存
        assert manager.set_user_data(user_id, "password", "secret123")
        print("データ保存: OK")
        
        # 取得
        value = manager.get_user_data(user_id, "password")
        assert value == "secret123"
        print("データ取得: OK")
        
        # 一覧
        all_data = manager.get_user_data(user_id)
        assert "password" in all_data
        print("データ一覧: OK")
        
        # 削除
        assert manager.delete_user_data(user_id, "password")
        print("データ削除: OK")
        
        # 削除確認
        value = manager.get_user_data(user_id, "password")
        assert value is None
        print("削除確認: OK")
        
    finally:
        os.unlink(temp_file.name)


def validation_test():
    """バリデーションテスト"""
    # 有効なデータ名
    assert validate_name("valid_name") is None
    assert validate_name("test123") is None
    assert validate_name("my-key") is None
    print("有効なデータ名: OK")
    
    # 無効なデータ名
    assert validate_name("invalid@name") is not None
    assert validate_name("key with space") is not None
    assert validate_name("a" * (MAX_NAME_LENGTH + 1)) is not None
    print("無効なデータ名検出: OK")
    
    # 有効なデータ値
    assert validate_value("short value") is None
    assert validate_value("a" * 100) is None
    print("有効なデータ値: OK")
    
    # 無効なデータ値
    assert validate_value("a" * (MAX_VALUE_LENGTH + 1)) is not None
    print("無効なデータ値検出: OK")


def large_data_test():
    """大きなデータのテスト"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        manager = UserDataManager(temp_file.name)
        user_id = "123456789"
        
        # 長いデータ（制限内）
        large_data = "a" * MAX_VALUE_LENGTH
        assert manager.set_user_data(user_id, "large", large_data)
        retrieved = manager.get_user_data(user_id, "large")
        assert retrieved == large_data
        print(f"大きなデータ({MAX_VALUE_LENGTH}文字): OK")
        
        # 日本語データ
        japanese_data = "これは日本語のテストデータです。" * 50
        if len(japanese_data) <= MAX_VALUE_LENGTH:
            assert manager.set_user_data(user_id, "japanese", japanese_data)
            retrieved = manager.get_user_data(user_id, "japanese")
            assert retrieved == japanese_data
            print("日本語データ: OK")
        
    finally:
        os.unlink(temp_file.name)


def multiple_users_test():
    """複数ユーザーテスト"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        manager = UserDataManager(temp_file.name)
        
        # 複数ユーザーのデータ保存
        users = ["111111111", "222222222", "333333333"]
        for i, user_id in enumerate(users):
            manager.set_user_data(user_id, "password", f"secret{i}")
            manager.set_user_data(user_id, "email", f"user{i}@example.com")
        
        # データ分離確認
        for i, user_id in enumerate(users):
            password = manager.get_user_data(user_id, "password")
            email = manager.get_user_data(user_id, "email")
            assert password == f"secret{i}"
            assert email == f"user{i}@example.com"
        
        print("複数ユーザーデータ分離: OK")
        
        # データ数確認
        for user_id in users:
            count = manager.get_user_data_count(user_id)
            assert count == 2
        
        print("ユーザー別データ数カウント: OK")
        
    finally:
        os.unlink(temp_file.name)


def performance_test():
    """パフォーマンステスト"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        import time
        manager = UserDataManager(temp_file.name)
        user_id = "123456789"
        
        # 大量データ保存テスト
        start_time = time.time()
        for i in range(50):  # MAX_ITEMS_PER_USER の半分
            manager.set_user_data(user_id, f"key{i:03d}", f"value{i}" * 10)
        save_time = time.time() - start_time
        
        print(f"50件データ保存時間: {save_time:.3f}秒")
        
        # データ取得テスト
        start_time = time.time()
        for i in range(50):
            manager.get_user_data(user_id, f"key{i:03d}")
        get_time = time.time() - start_time
        
        print(f"50件データ取得時間: {get_time:.3f}秒")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(temp_file.name)
        print(f"データファイルサイズ: {file_size} bytes")
        
    finally:
        os.unlink(temp_file.name)


def discord_limits_test():
    """Discord制限テスト"""
    # メッセージ長制限のシミュレーション
    test_data = "a" * 1800  # Discord表示制限近く
    
    # 表示用メッセージ生成のシミュレーション
    message = f"📄 **データ: test**\n\n```\n{test_data}\n```"
    
    if len(message) < 2000:
        print("Discord制限内メッセージ生成: OK")
    else:
        print(f"Discord制限超過: {len(message)}文字")
    
    # 長いデータの切り詰め処理テスト
    long_data = "a" * 2000
    if len(long_data) > 1800:
        truncated = long_data[:1800] + "..."
        message = f"📄 **データ: test** (一部表示)\n\n```\n{truncated}\n```\n\n💡 データが長すぎるため一部のみ表示しています。"
        if len(message) < 2000:
            print("長いデータの切り詰め処理: OK")


def main():
    """メインテスト実行"""
    print("🚀 Discord Vault Bot 手動テスト")
    print("=" * 50)
    
    # テストシナリオ実行
    test_scenario("基本CRUD操作", basic_crud_test)
    test_scenario("バリデーション", validation_test)
    test_scenario("大きなデータ処理", large_data_test)
    test_scenario("複数ユーザー", multiple_users_test)
    test_scenario("パフォーマンス", performance_test)
    test_scenario("Discord制限", discord_limits_test)
    
    print("\n" + "=" * 50)
    print("✅ 手動テスト完了")
    
    print(f"\n📊 現在の制限値:")
    print(f"  - データ名最大長: {MAX_NAME_LENGTH}文字")
    print(f"  - データ値最大長: {MAX_VALUE_LENGTH}文字")
    print(f"  - ユーザー最大データ数: 100件")


if __name__ == "__main__":
    main()