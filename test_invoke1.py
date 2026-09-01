import runpy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class _FakeResponse:
    content = "你好，我是一个助手。"


class _FakeModel:
    def invoke(self, prompt):
        assert prompt == "介绍一下你自己"
        return _FakeResponse()


class _GbkStdout:
    encoding = "gbk"
    errors = "strict"

    def __init__(self):
        self.writes = []

    def reconfigure(self, *, encoding=None, errors=None):
        if encoding is not None:
            self.encoding = encoding
        if errors is not None:
            self.errors = errors

    def write(self, text):
        if self.encoding.lower() in {"gbk", "cp936"} and any(
            ord(char) > 127 for char in text
        ):
            raise UnicodeEncodeError("gbk", text, 0, 1, "cannot encode character")
        self.writes.append(text)
        return len(text)

    def flush(self):
        pass


class Invoke1OutputTests(unittest.TestCase):
    def test_prints_response_content_with_room_for_reasoning(self):
        captured = {}

        def fake_init_chat_model(**kwargs):
            captured.update(kwargs)
            return _FakeModel()

        fake_langchain = types.ModuleType("langchain")
        fake_chat_models = types.ModuleType("langchain.chat_models")
        fake_chat_models.init_chat_model = fake_init_chat_model
        fake_langchain.chat_models = fake_chat_models

        fake_dotenv = types.ModuleType("dotenv")
        fake_dotenv.load_dotenv = lambda **kwargs: None

        with (
            patch.dict(
                sys.modules,
                {
                    "langchain": fake_langchain,
                    "langchain.chat_models": fake_chat_models,
                    "dotenv": fake_dotenv,
                },
            ),
            patch("builtins.print") as print_mock,
        ):
            runpy.run_path(
                str(Path(__file__).with_name("invoke1.py")),
                run_name="__main__",
            )

        print_mock.assert_called_once_with("你好，我是一个助手。")
        self.assertGreaterEqual(captured["max_tokens"], 512)

    def test_prints_unicode_response_when_console_starts_as_gbk(self):
        fake_langchain = types.ModuleType("langchain")
        fake_chat_models = types.ModuleType("langchain.chat_models")
        fake_chat_models.init_chat_model = lambda **kwargs: _FakeModel()
        fake_langchain.chat_models = fake_chat_models

        fake_dotenv = types.ModuleType("dotenv")
        fake_dotenv.load_dotenv = lambda **kwargs: None
        stream = _GbkStdout()

        with (
            patch.dict(
                sys.modules,
                {
                    "langchain": fake_langchain,
                    "langchain.chat_models": fake_chat_models,
                    "dotenv": fake_dotenv,
                },
            ),
            patch("sys.stdout", stream),
        ):
            runpy.run_path(
                str(Path(__file__).with_name("invoke1.py")),
                run_name="__main__",
            )

        self.assertIn("你好，我是一个助手。", "".join(stream.writes))


if __name__ == "__main__":
    unittest.main()
