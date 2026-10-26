from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import unittest
from unittest.mock import patch
import subprocess
import sys
from pathlib import Path
from honeyos.companion.time_context import build_time_note, message_epoch


class TimeFactsTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 26, 0, 10, tzinfo=timezone(timedelta(hours=8), 'Asia/Shanghai'))

    def test_cross_midnight_and_real_gap(self):
        previous = datetime(2026, 10, 25, 23, 50, tzinfo=self.now.tzinfo)
        note = build_time_note([{'role': 'user', 'timestamp': previous.timestamp()}], current=self.now)
        self.assertIn('间隔秒数：1200', note)
        self.assertIn('是否跨本地日期：是', note)
        self.assertIn('Asia/Shanghai', note)

    def test_latest_unknown_time_does_not_borrow_an_older_one(self):
        note = build_time_note([{'role': 'user', 'timestamp': 1000}, {'role': 'user'}], current=self.now)
        self.assertIn('间隔未知', note)
        self.assertNotIn('间隔秒数：', note)

    def test_invalid_and_future_values_remain_unknown(self):
        for value in (True, 'broken', '2026-10-26T00:00:00', float('nan'), float('inf'), -1):
            self.assertIsNone(message_epoch(value))
        note = build_time_note([{'role': 'user', 'timestamp': self.now.timestamp()+90}], current=self.now)
        self.assertIn('间隔未知', note)

    def test_received_time_excludes_queue_delay(self):
        arrival = self.now.timestamp()-60
        note = build_time_note([{'role': 'user', 'timestamp': arrival-10}], current=self.now, received=arrival)
        self.assertIn('间隔秒数：10', note)

    def test_first_turn_has_no_fictional_gap(self):
        self.assertIn('间隔未知', build_time_note([], current=self.now))

    def test_synthetic_turns_do_not_replace_last_user(self):
        note = build_time_note([{'role':'user', 'timestamp':self.now.timestamp()-30},
            {'role':'user', 'display_kind':'internal', 'timestamp':self.now.timestamp()-1}], current=self.now)
        self.assertIn('间隔秒数：30', note)


class MissingTimezoneDataTest(unittest.TestCase):
    def test_configured_zone_wins_even_without_default_database(self):
        from honeyos.companion.time_context import companion_timezone
        configured = timezone(timedelta(hours=-5), 'test-configured')
        with patch('honeyos.core.time.get_timezone', return_value=configured), \
             patch('honeyos.companion.time_context.ZoneInfo', side_effect=AssertionError('must not load default')):
            self.assertIs(companion_timezone(), configured)

    def test_bootstrap_clock_without_system_or_python_tzdata(self):
        # -S removes site-packages (including tzdata); empty TZPATH removes OS
        # data. Exercise the real resolver and bootstrap JSON serialization.
        code = """
import json, zoneinfo
from datetime import datetime, timezone
zoneinfo.reset_tzpath([])
from honeyos.companion.time_context import companion_timezone, build_time_note
zone = companion_timezone()
assert str(zone) == 'Asia/Shanghai'
current = datetime(2026, 10, 25, 16, 10, tzinfo=timezone.utc).astimezone(zone)
assert current.hour == 0 and current.day == 26
assert current.utcoffset().total_seconds() == 8 * 3600
json.dumps({'timezone': str(zone)})
previous = current.timestamp() - 1200
note = build_time_note([{'role':'user','timestamp':previous}], current=current)
assert '是否跨本地日期：是' in note
assert '间隔秒数：1200' in note
"""
        result = subprocess.run([sys.executable, '-S', '-c', code],
            cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
