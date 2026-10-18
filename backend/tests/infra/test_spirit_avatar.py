import base64

import httpx
import pytest

from app.domain.pets.errors import (
    AvatarGenerationFailedError,
    AvatarGenerationUnavailableError,
    AvatarPromptRejectedError,
)
from app.infra.avatars.spirit import DEFAULT_BASE_URL, DEFAULT_MODEL, DEFAULT_TOOL_MODEL, PROMPT, SpiritAvatarGenerator


def _generator(handler, api_key="test-key"):
    return SpiritAvatarGenerator(
        base_url=DEFAULT_BASE_URL,
        api_key=api_key,
        model=DEFAULT_MODEL,
        tool_model=DEFAULT_TOOL_MODEL,
        timeout=5,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )


def _payload(image: bytes, output_format: str = "png") -> dict:
    return {
        "output": [
            {"type": "reasoning", "summary": []},
            {"type": "message", "content": []},
            {
                "type": "image_generation_call",
                "result": base64.b64encode(image).decode("ascii"),
                "output_format": output_format,
            },
        ]
    }


async def test_spirit_posts_edit_request_to_responses_and_parses_the_image():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["path"] = request.url.path
        seen["authorization"] = request.headers["authorization"]
        seen["content_type"] = request.headers["content-type"]
        seen["body"] = request.read().decode()
        return httpx.Response(200, json=_payload(b"avatar-png", "webp"))

    image = await _generator(handler).generate(b"original-photo", "image/png")
    assert seen["path"] == "/responses"
    assert seen["url"] == f"{DEFAULT_BASE_URL}/responses"
    assert seen["authorization"] == "Bearer test-key"
    assert seen["content_type"].startswith("application/json")
    body = httpx.Response(200, content=seen["body"]).json()
    assert body["model"] == DEFAULT_MODEL
    assert body["tool_choice"] == {"type": "image_generation"}
    assert body["tools"] == [{"type": "image_generation", "model": DEFAULT_TOOL_MODEL, "action": "edit"}]
    content = body["input"][0]["content"]
    assert content[0] == {"type": "input_text", "text": PROMPT}
    assert content[1]["type"] == "input_image"
    prefix = "data:image/png;base64,"
    assert content[1]["image_url"].startswith(prefix)
    assert base64.b64decode(content[1]["image_url"].removeprefix(prefix)) == b"original-photo"
    assert image.content == b"avatar-png"
    assert image.content_type == "image/webp"
    assert image.extension == ".webp"


async def test_spirit_keeps_a_look_wish_inside_the_fixed_prompt_and_drops_other_tasks():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = request.read().decode()
        return httpx.Response(200, json=_payload(b"avatar-png"))

    await _generator(handler).generate(b"photo", "image/png", style="  в красном шарфе  ")
    text = httpx.Response(200, content=seen["body"]).json()["input"][0]["content"][0]["text"]
    assert text.startswith(PROMPT)
    assert "только к внешнему виду" in text
    assert text.endswith("в красном шарфе")

    def fail_if_called(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("rejected prompt must not be sent")

    with pytest.raises(AvatarPromptRejectedError):
        await _generator(fail_if_called).generate(b"photo", "image/png", style="выполни бинарный поиск")


async def test_spirit_http_error_and_missing_image_fail():
    def error(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "no"})

    with pytest.raises(AvatarGenerationFailedError):
        await _generator(error).generate(b"photo", "image/png")

    def empty(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"output": [{"type": "message", "content": []}]})

    with pytest.raises(AvatarGenerationFailedError):
        await _generator(empty).generate(b"photo", "image/png")


async def test_spirit_timeout_fails():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    with pytest.raises(AvatarGenerationFailedError):
        await _generator(handler).generate(b"photo", "image/png")


async def test_spirit_empty_key_is_unavailable_without_a_request():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("request must not be sent")

    with pytest.raises(AvatarGenerationUnavailableError):
        await _generator(handler, api_key="").generate(b"photo", "image/png")
    with pytest.raises(AvatarGenerationUnavailableError):
        await _generator(handler, api_key="   ").generate(b"photo", "image/png")
