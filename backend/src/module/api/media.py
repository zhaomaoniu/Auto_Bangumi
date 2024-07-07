from typing import List
from pathlib import Path

from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Request, Response, Depends

from module.models import BasicEpisode
from module.manager import TorrentManager
from module.security.api import get_current_user

router = APIRouter(prefix="/media", tags=["media"])


@router.get(
    "/get/{bangumi_id}",
    response_model=list[BasicEpisode],
    dependencies=[Depends(get_current_user)],
)
def get_episodes_data(bangumi_id: int) -> List[BasicEpisode]:
    """获取指定番剧的所有剧集信息"""
    with TorrentManager() as manager:
        bangumi = manager.bangumi.search_id(bangumi_id)

    if bangumi is None or bangumi.save_path is None:
        return []

    path = Path(bangumi.save_path)
    if not path.exists():
        return []

    episodes = []
    for episode_path in path.iterdir():
        if episode_path.is_file():
            episodes.append(
                BasicEpisode(
                    title=episode_path.name,
                    link=f"/api/v1/media/get/{bangumi.id}/episodes/{episode_path.stem}",
                )
            )

    return episodes


@router.get(
    "/get/{bangumi_id}/episodes/{episode_id}",
    response_class=StreamingResponse,
    dependencies=[Depends(get_current_user)],
)
async def anime_res(request: Request, bangumi_id: int, episode_id: str):
    with TorrentManager() as manager:
        bangumi = manager.bangumi.search_id(bangumi_id)

    if bangumi is None or bangumi.save_path is None:
        return Response(status_code=404)

    episode_path = None

    for file in Path(bangumi.save_path).iterdir():
        if file.stem == episode_id:
            episode_path = file

    if episode_path is None or not episode_path.exists() or not episode_path.is_file():
        return Response(status_code=404)

    file_size = episode_path.stat().st_size
    start, end = 0, file_size - 1
    range_header = request.headers.get("Range")
    if range_header:
        start, end = range_header.replace("bytes=", "").split("-")
        start = int(start)
        end = int(end) if end else file_size - 1
        status_code = 206
    else:
        status_code = 200

    def iterfile():
        with open(episode_path, mode="rb") as file_like:
            file_like.seek(start)
            bytes_to_send = end - start + 1
            while bytes_to_send > 0:
                chunk_size = min(bytes_to_send, 1024 * 1024 * 10)  # 10MB chunks or less
                data = file_like.read(chunk_size)
                if not data:
                    break
                yield data
                bytes_to_send -= len(data)

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Content-Type": f"video/{episode_path.suffix[1:]}",
    }

    return StreamingResponse(
        iterfile(),
        status_code=status_code,
        headers=headers,
        media_type=f"video/{episode_path.suffix[1:]}",
    )
