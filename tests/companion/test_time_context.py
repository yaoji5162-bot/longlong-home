from datetime import datetime
from zoneinfo import ZoneInfo
import unittest
from honeyos.companion.time_context import build_time_note, message_epoch


class TimeFactsTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 26, 0, 10, tzinfo=ZoneInfo('Asia/Shanghai'))

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
