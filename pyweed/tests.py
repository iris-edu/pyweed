from time import sleep
from pyweed.pyweed_utils import get_distance, get_arrivals, TimeWindow
import unittest
from obspy.core.utcdatetime import UTCDateTime


def gui_test(pyweed):
    pyweed.fetch_events()
    pyweed.fetch_stations()
    sleep(2)
    for i in range(5):
        pyweed.mainWindow.eventsTable.selectRow(i)
    for i in range(5):
        pyweed.mainWindow.stationsTable.selectRow(i)
    pyweed.openWaveformsDialog()


class DistanceTest(unittest.TestCase):
    """
    Some sanity tests, mainly to ensure we have the units right
    """
    def test_distance_1(self):
        dist = get_distance(0, 0, 10, 0)
        self.assertAlmostEqual(dist, 10, delta=1)

    def test_distance_2(self):
        dist = get_distance(0, 0, 0, 10)
        self.assertAlmostEqual(dist, 10, delta=1)

    def test_distance_3(self):
        dist = get_distance(0, 170, 0, -170)
        self.assertAlmostEqual(dist, 20, delta=1)


class ArrivalsTest(unittest.TestCase):
    def test_arrivals_1(self):
        arrivals = get_arrivals(20, 100)
        self.assertAlmostEqual(arrivals['P'], 264, delta=1)
        self.assertAlmostEqual(arrivals['S'], 484, delta=1)


class TimeWindowTest(unittest.TestCase):
    def test_timewindow_1(self):
        time_window = TimeWindow(60, 600, 'P', 'P')
        event_time = UTCDateTime("2017-01-01T12:00:00")
        arrivals = {
            'P': 264
        }
        (start, end) = time_window.calculate_window(
            event_time, arrivals)
        # 264s arrival time, -60s offset
        expected_start = UTCDateTime("2017-01-01T12:03:24")
        # 264s arrival time, 600s offset
        expected_end = UTCDateTime("2017-01-01T12:14:24")
        self.assertAlmostEqual(
            start, expected_start, delta=1)
        self.assertAlmostEqual(
            end, expected_end, delta=1)


if __name__ == '__main__':
    unittest.main()
