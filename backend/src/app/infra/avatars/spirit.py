import base64

import httpx

from app.application.ports.avatar_generator import AvatarGenerator, GeneratedImage
from app.domain.pets.errors import AvatarGenerationFailedError, AvatarGenerationUnavailableError
from app.infra.logger import Logger

DEFAULT_BASE_URL = "https://llm-proxy.spirit.t-education.com"
DEFAULT_MODEL = "openai/gpt-5.6-sol"
DEFAULT_TOOL_MODEL = "gpt-image-1.5"
DEFAULT_TIMEOUT = 180.0
PROMPT = (
    "Создай невероятно кавайный мультяшный 3D-аватар питомца с этой фотографии. "
    "Максимально усиль милоту: выраженные chibi-пропорции милого малыша, очень большая округлая голова, "
    "крошечное пухлое тельце и маленькие мягкие лапки под подбородком. Огромные выразительные глаза "
    "с большими радужками и несколькими яркими бликами, любопытный нежный взгляд, пухлые щёчки "
    "с едва заметным румянцем, маленький носик и добрая застенчивая улыбка. "
    "Образ должен вызывать желание немедленно обнять этого очаровательного маленького питомца. "
    "Сохрани породу, исходный окрас, рисунок шерсти, цвет глаз, форму ушей и узнаваемые черты именно этого питомца. "
    "Стиль премиальной коллекционной 3D-фигурки с бархатистой плюшевой шерстью, "
    "очень мягкими округлыми формами, читаемым объёмом и деликатными бликами. "
    "Тёплый рассеянный студийный свет, нежные тени, пушистые края и воздушное уютное настроение. "
    "Голова занимает большую часть кадра, верх груди и маленькие лапки видны снизу. "
    "Персонаж по центру, взгляд в камеру, "
    "квадратная композиция с небольшим отступом вокруг ушей, простой однотонный пастельный фон, "
    "подходящий для иконки приложения. Без текста, логотипов и водяных знаков."
)
_CONTENT_TYPES = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}

logger = Logger.get_logger()


class SpiritAvatarGenerator(AvatarGenerator):
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        tool_model: str,
        timeout: float,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.tool_model = tool_model
        self.timeout = timeout
        self._client = client

    async def generate(self, image: bytes, content_type: str) -> GeneratedImage:
        if not self.api_key.strip():
            raise AvatarGenerationUnavailableError
        body = {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": PROMPT},
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{base64.b64encode(image).decode('ascii')}",
                        },
                    ],
                }
            ],
            "tools": [{"type": "image_generation", "model": self.tool_model, "action": "edit"}],
            "tool_choice": {"type": "image_generation"},
        }
        if self._client is None:
            async with httpx.AsyncClient() as client:
                return await self._request(client, body)
        return await self._request(self._client, body)

    async def _request(self, client: httpx.AsyncClient, body: dict) -> GeneratedImage:
        try:
            response = await client.post(
                f"{self.base_url}/responses",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=body,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
            _log_failure(status_code)
            raise AvatarGenerationFailedError from exc
        try:
            payload = response.json()
        except ValueError as exc:
            _log_failure(response.status_code)
            raise AvatarGenerationFailedError from exc
        return _image_from_output(payload, response.status_code)


def _log_failure(status_code: int | None) -> None:
    logger.warning("Avatar generation failed, status={}", status_code)


def _image_from_output(payload: object, status_code: int) -> GeneratedImage:
    output = payload.get("output") if isinstance(payload, dict) else None
    image_b64 = None
    output_format = "png"
    if isinstance(output, list):
        for item in output:
            if isinstance(item, dict) and item.get("type") == "image_generation_call" and item.get("result"):
                image_b64 = item["result"]
                output_format = str(item.get("output_format") or "png")
                break
    if not isinstance(image_b64, str) or not image_b64:
        _log_failure(status_code)
        raise AvatarGenerationFailedError
    try:
        content = base64.b64decode(image_b64, validate=False)
    except (ValueError, TypeError) as exc:
        _log_failure(status_code)
        raise AvatarGenerationFailedError from exc
    if not content:
        _log_failure(status_code)
        raise AvatarGenerationFailedError
    fmt = output_format.lower().strip().lstrip(".") or "png"
    return GeneratedImage(
        content=content,
        content_type=_CONTENT_TYPES.get(fmt, f"image/{fmt}"),
        extension=f".{fmt}",
    )
