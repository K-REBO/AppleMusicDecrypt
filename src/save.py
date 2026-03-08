import os
from pathlib import Path

from creart import it

from src.config import Config
from src.metadata import SongMetadata
from src.models import PlaylistInfo
from src.utils import ttml_convent, get_song_name_and_dir_path, get_suffix


def save_m3u(playlist_info: PlaylistInfo):
    from src.utils import get_valid_filename, playlist_metadata_to_params, get_path_safe_dict

    config = it(Config)
    safe_pl_meta = get_path_safe_dict(playlist_metadata_to_params(playlist_info))

    playlist_dir = Path(config.download.playlistDirPathFormat.format(**safe_pl_meta))
    if not playlist_dir.exists():
        os.makedirs(playlist_dir.absolute())

    playlist_name = get_valid_filename(playlist_info.data[0].attributes.name)
    m3u_path = playlist_dir / Path(f"{playlist_name}.m3u")

    sorted_song_ids = sorted(
        playlist_info.saved_song_paths.keys(),
        key=lambda sid: playlist_info.songIdIndexMapping.get(sid, 0)
    )

    lines = ["#EXTM3U"]
    for song_id in sorted_song_ids:
        song_abs_path = Path(playlist_info.saved_song_paths[song_id])
        rel_path = os.path.relpath(song_abs_path, playlist_dir.absolute())
        lines.append(rel_path)

    m3u_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save(song: bytes, codec: str, metadata: SongMetadata, playlist: PlaylistInfo = None):
    song_name, dir_path = get_song_name_and_dir_path(codec.upper(), metadata, playlist)
    if not dir_path.exists() or not dir_path.is_dir():
        os.makedirs(dir_path.absolute())
    song_path = dir_path / Path(song_name + get_suffix(codec, it(Config).download.atmosConventToM4a))
    with open(song_path.absolute(), "wb") as f:
        f.write(song)
    if it(Config).download.saveCover and not playlist:
        cover_path = dir_path / Path(f"cover.{it(Config).download.coverFormat}")
        with open(cover_path.absolute(), "wb") as f:
            f.write(metadata.cover)
    if it(Config).download.saveLyrics and metadata.lyrics:
        lrc = ttml_convent(metadata.lyrics)
        if lrc:
            if it(Config).download.lyricsFormat == "ttml":
                lrc_path = dir_path / Path(song_name + ".ttml")
            else:
                lrc_path = dir_path / Path(song_name + ".lrc")
            lrc_path.write_text(lrc, encoding="utf-8")
    return song_path.absolute()
