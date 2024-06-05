import base64
import logging

from module.models import Notification
from module.network import RequestContent
from module.utils import load_image

logger = logging.getLogger(__name__)


class SatoriNotification(RequestContent):
    def __init__(self, token, chat_id, base_url, self_id, platform):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.base_url = base_url
        self.self_id = self_id
        self.platform = platform

    @staticmethod
    def gen_message(notify: Notification) -> str:
        text = f"""
        番剧名称：{notify.official_title}\n季度： 第{notify.season}季\n更新集数： 第{notify.episode}集
        """
        return text.strip()

    def post_msg(self, notify: Notification) -> bool:
        content = self.gen_message(notify)
        image = load_image(notify.poster_path)

        if image is not None:
            base64_text = base64.b64encode(image).decode("utf-8")
            content += f'<img src="data:image/jpeg;base64,{base64_text}" />'

        resp = self.session.post(
            url=f"{self.base_url}/v1/message.create",
            json={"channel_id": self.chat_id, "content": content},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token or ''}",
                "X-Platform": self.platform,
                "X-Self-ID": self.self_id,
            },
        )

        logger.debug(f"Satori notification: {resp.status_code}")
        return resp.status_code == 200
