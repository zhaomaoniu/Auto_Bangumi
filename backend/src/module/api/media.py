from typing import List
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from module.conf import settings
from module.models import Bangumi
from module.manager import TorrentManager


router = APIRouter(prefix="/media", tags=["media"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


def get_all_bangumi() -> List[Bangumi]:
    with TorrentManager() as manager:
        return sorted(manager.bangumi.search_all(), key=lambda x: x.id, reverse=True)


def gen_episodes_data(bangumi: Bangumi) -> List[dict]:
    if bangumi.save_path is None:
        return []

    path = Path(bangumi.save_path)

    if not path.exists():
        return []

    episodes = []
    for episode_path in path.iterdir():
        if episode_path.is_file():
            episodes.append(
                {
                    "number": (
                        episode_path.stem.split()[-1]
                        if settings.bangumi_manage.rename_method != "none"
                        else episode_path.stem
                    ),
                    "title": episode_path.name,
                    "link": f"/api/v1/media/{bangumi.id}/episodes/{episode_path.stem}",
                }
            )

    return sorted(episodes, key=lambda x: x["number"])


@router.get("/", response_class=HTMLResponse)
def get_all_bangumi_info(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "animes": [bangumi.dict() for bangumi in get_all_bangumi()],
        },
    )


@router.get("/{bangumi_id}", response_class=HTMLResponse)
def get_bangumi_info(request: Request, bangumi_id: int):
    with TorrentManager() as manager:
        bangumi = manager.bangumi.search_id(bangumi_id)

    if bangumi is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    return templates.TemplateResponse(
        "episode.html",
        {
            "request": request,
            "episodes": gen_episodes_data(bangumi),
            "back_link": "/api/v1/media/",
        },
    )


@router.get("/{bangumi_id}/episodes/{episode_id}", response_class=HTMLResponse)
def get_episode_info(request: Request, bangumi_id: int, episode_id: str):
    with TorrentManager() as manager:
        bangumi = manager.bangumi.search_id(bangumi_id)

    if bangumi is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    if bangumi.save_path is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    episode_path = None

    for file in Path(bangumi.save_path).iterdir():
        if file.stem == episode_id:
            episode_path = file

    if episode_path is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    if not episode_path.exists():
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    return templates.TemplateResponse(
        "display.html",
        {
            "request": request,
            "anime_title": bangumi.official_title,
            "episode_number": (
                episode_path.stem.split()[-1]
                if settings.bangumi_manage.rename_method != "none"
                else episode_path.stem
            ),
            "episode_title": episode_path.name,
            "video_link": f"/api/v1/media/res/{bangumi_id}/episodes/{episode_path.stem}",
            "back_link": f"/api/v1/media/{bangumi_id}/",
        },
    )


@router.get("/res/{bangumi_id}/episodes/{episode_id}")
async def anime_res(request: Request, bangumi_id: int, episode_id: str):
    with TorrentManager() as manager:
        bangumi = manager.bangumi.search_id(bangumi_id)

    if bangumi is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    if bangumi.save_path is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    episode_path = None

    for file in Path(bangumi.save_path).iterdir():
        if file.stem == episode_id:
            episode_path = file

    if episode_path is None:
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

    if not episode_path.exists():
        return templates.TemplateResponse(
            "not_found.html",
            {
                "request": request,
            },
        )

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
