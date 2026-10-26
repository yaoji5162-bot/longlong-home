"""Objective per-turn time facts; no inferred activities or response schedules."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Shanghai"


def message_epoch(value):
    """Only accept unambiguous instants. Missing/naive history stays unknown."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            result = float(value)
        else:
            parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return None
            result = parsed.timestamp()
        return result if math.isfinite(result) and result > 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def companion_timezone():
    # Explicit user configuration wins; a proot host's accidental UTC does not.
    from honeyos.core.time import get_timezone
    configured = get_timezone()
    if configured is not None:
        return configured
    try:
        return ZoneInfo(DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError:
        # Minimal Ubuntu/proot and standalone Python may have neither system
        # tzdata nor the Python tzdata package. Modern Shanghai uses UTC+08:00;
        # keep the IANA display name so the browser's Intl formatter accepts it.
        # This fallback is for the current companion clock, not historical
        # timezone-rule conversion (Shanghai had DST before 1992).
        return timezone(timedelta(hours=8), name=DEFAULT_TIMEZONE)


def build_time_note(history, *, current, received=None):
    tz = current.tzinfo
    received_epoch = message_epoch(received) or current.timestamp()
    arrival = datetime.fromtimestamp(received_epoch, tz)
    prior = next((m for m in reversed(history or []) if m.get("role") == "user" and not m.get("display_kind")), None)
    epoch = message_epoch(prior.get("timestamp")) if prior else None
    facts = ["<companion_time_context>",
             "此时间快照仅对应这条消息；历史快照不是此刻时间，以最新一轮为准。",
             f"当前处理时间：{current.isoformat(timespec='seconds')}",
             f"时区：{getattr(tz, 'key', str(tz))}",
             f"本条消息到达时间：{arrival.isoformat(timespec='seconds')}"]
    if epoch is not None and epoch <= received_epoch:
        previous = datetime.fromtimestamp(epoch, tz)
        facts.extend([f"本会话上一条用户消息：{previous.isoformat(timespec='seconds')}",
                      f"两条用户消息间隔秒数：{int(received_epoch - epoch)}",
                      f"是否跨本地日期：{'是' if previous.date() != arrival.date() else '否'}"])
    else:
        facts.append("上一条用户消息时间或间隔未知；不要估算。")
    facts.extend([
        "以上仅是时间事实，不证明用户离开、睡觉、忙碌或期间做过任何事；消息间隔也不等于离开时长。",
        "请结合前文话题、关系与边界、未完的约定和当前消息，自主判断间隔是否改变此刻语境。",
        "默认不提时间，不报时、不复述间隔，不要每轮打招呼或提醒作息。短间隔可直接接着聊；长间隔也不要求特别反应。",
        "如果前文与当前表达适合，可以自然表达想念、欢迎回来或接续关心；不是每次回来都说想念，不按分钟/小时套固定台词或情绪强度。",
        "表达想念不等于声称后台一直等待、持续思考、计时或观察用户；不因久未发消息责备、索取回应或制造内疚。",
        "只有用户询问或任务确需时才明确引用时间。时间事实不能替代对前文的理解。",
        "</companion_time_context>",
    ])
    return "\n".join(facts)
