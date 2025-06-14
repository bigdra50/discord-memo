#!/usr/bin/env python3
"""
Discord Vault Bot テストスイート
"""

import os
import json
import tempfile
import unittest
from unittest.mock import Mock, patch
import sys

# テスト用にbot.pyをインポート
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bot import UserDataManager, validate_name, validate_value, MAX_NAME_LENGTH, MAX_VALUE_LENGTH, MAX_ITEMS_PER_USER


class TestUserDataManager(unittest.TestCase):
    """UserDataManagerクラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = UserDataManager(self.temp_file.name)
    
    def tearDown(self):
        """各テストの後に実行"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_empty_data_initialization(self):
        """空データでの初期化テスト"""
        self.assertEqual(self.manager.data, {})
    
    def test_set_and_get_user_data(self):
        """データ保存・取得テスト"""
        user_id = "123456789"
        key = "password"
        value = "secret123"
        
        # データ保存
        result = self.manager.set_user_data(user_id, key, value)
        self.assertTrue(result)
        
        # データ取得
        retrieved = self.manager.get_user_data(user_id, key)
        self.assertEqual(retrieved, value)
    
    def test_get_all_user_data(self):
        """全データ取得テスト"""
        user_id = "123456789"
        data = {"password": "secret123", "email": "test@example.com"}
        
        for key, value in data.items():
            self.manager.set_user_data(user_id, key, value)
        
        all_data = self.manager.get_user_data(user_id)
        self.assertEqual(all_data, data)
    
    def test_delete_user_data(self):
        """データ削除テスト"""
        user_id = "123456789"
        key = "password"
        value = "secret123"
        
        # データ保存
        self.manager.set_user_data(user_id, key, value)
        
        # データ削除
        result = self.manager.delete_user_data(user_id, key)
        self.assertTrue(result)
        
        # 削除確認
        retrieved = self.manager.get_user_data(user_id, key)
        self.assertIsNone(retrieved)
    
    def test_delete_nonexistent_data(self):
        """存在しないデータの削除テスト"""
        user_id = "123456789"
        key = "nonexistent"
        
        result = self.manager.delete_user_data(user_id, key)
        self.assertFalse(result)
    
    def test_user_data_isolation(self):
        """ユーザー間データ分離テスト"""
        user1 = "111111111"
        user2 = "222222222"
        key = "password"
        value1 = "secret1"
        value2 = "secret2"
        
        # 異なるユーザーに同じキーで異なる値を保存
        self.manager.set_user_data(user1, key, value1)
        self.manager.set_user_data(user2, key, value2)
        
        # 各ユーザーが自分のデータのみ取得できることを確認
        self.assertEqual(self.manager.get_user_data(user1, key), value1)
        self.assertEqual(self.manager.get_user_data(user2, key), value2)
    
    def test_get_user_data_count(self):
        """ユーザーデータ数取得テスト"""
        user_id = "123456789"
        
        # 初期状態
        self.assertEqual(self.manager.get_user_data_count(user_id), 0)
        
        # データ追加
        self.manager.set_user_data(user_id, "key1", "value1")
        self.assertEqual(self.manager.get_user_data_count(user_id), 1)
        
        self.manager.set_user_data(user_id, "key2", "value2")
        self.assertEqual(self.manager.get_user_data_count(user_id), 2)
        
        # データ削除
        self.manager.delete_user_data(user_id, "key1")
        self.assertEqual(self.manager.get_user_data_count(user_id), 1)


class TestValidation(unittest.TestCase):
    """バリデーション関数のテスト"""
    
    def test_validate_name_valid(self):
        """有効なデータ名のテスト"""
        valid_names = ["password", "test123", "my_password", "key-name", "a", "A1_2-3"]
        for name in valid_names:
            with self.subTest(name=name):
                self.assertIsNone(validate_name(name))
    
    def test_validate_name_invalid_characters(self):
        """無効な文字を含むデータ名のテスト"""
        invalid_names = ["test@key", "key with space", "キー", "test!", "key.name", "key#1"]
        for name in invalid_names:
            with self.subTest(name=name):
                error = validate_name(name)
                self.assertIsNotNone(error)
                self.assertIn("英数字、アンダースコア、ハイフン", error)
    
    def test_validate_name_too_long(self):
        """長すぎるデータ名のテスト"""
        long_name = "a" * (MAX_NAME_LENGTH + 1)
        error = validate_name(long_name)
        self.assertIsNotNone(error)
        self.assertIn(f"{MAX_NAME_LENGTH}文字以内", error)
    
    def test_validate_value_valid(self):
        """有効なデータ値のテスト"""
        valid_values = ["short", "a" * 100, "日本語テキスト", "!@#$%^&*()", ""]
        for value in valid_values:
            with self.subTest(value=value[:20] + "..."):
                self.assertIsNone(validate_value(value))
    
    def test_validate_value_too_long(self):
        """長すぎるデータ値のテスト"""
        long_value = "a" * (MAX_VALUE_LENGTH + 1)
        error = validate_value(long_value)
        self.assertIsNotNone(error)
        self.assertIn(f"{MAX_VALUE_LENGTH}文字以内", error)


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = UserDataManager(self.temp_file.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_data_persistence(self):
        """データ永続化テスト"""
        user_id = "123456789"
        key = "password"
        value = "secret123"
        
        # データ保存
        self.manager.set_user_data(user_id, key, value)
        
        # 新しいマネージャーインスタンスで同じファイルを読み込み
        new_manager = UserDataManager(self.temp_file.name)
        retrieved = new_manager.get_user_data(user_id, key)
        
        self.assertEqual(retrieved, value)
    
    def test_max_items_limit(self):
        """アイテム数上限テスト"""
        user_id = "123456789"
        
        # 上限まで保存
        for i in range(MAX_ITEMS_PER_USER):
            self.manager.set_user_data(user_id, f"key{i}", f"value{i}")
        
        count = self.manager.get_user_data_count(user_id)
        self.assertEqual(count, MAX_ITEMS_PER_USER)
    
    def test_large_data_handling(self):
        """大きなデータの処理テスト"""
        user_id = "123456789"
        key = "large_data"
        # 制限内での最大サイズ
        large_value = "a" * MAX_VALUE_LENGTH
        
        result = self.manager.set_user_data(user_id, key, large_value)
        self.assertTrue(result)
        
        retrieved = self.manager.get_user_data(user_id, key)
        self.assertEqual(retrieved, large_value)


def run_tests():
    """テスト実行関数"""
    print("🧪 Discord Vault Bot テスト開始")
    print("=" * 50)
    
    # テストスイートを作成
    test_classes = [TestUserDataManager, TestValidation, TestIntegration]
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ すべてのテストが成功しました！")
    else:
        print("❌ テストに失敗しました。")
        print(f"失敗: {len(result.failures)}, エラー: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)