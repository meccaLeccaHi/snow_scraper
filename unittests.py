import unittest
from main_file import *
from google_api import *
from opensnow import *
from yelp import *

class TestDatabase(unittest.TestCase):

    def test_Mountain_Snow(self):
        conn = sqlite3.connect('snowfall.db')
        cur = conn.cursor()

        sql = 'SELECT MountainName FROM Mountain_Snow'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 604)
        for c in result_list:
            if 'Cloudmont' in c[0]:
                cloudmount_test = True
                break
            else:
                cloudmount_test = False
        for c in result_list:
            if 'Beaver Creek' in c[0]:
                beaverCreek_test = True
                break
            else:
                beaverCreek_test = False
        self.assertTrue(cloudmount_test)
        self.assertTrue(beaverCreek_test)

        sql = 'SELECT * FROM Mountain_Snow WHERE State="Colorado"'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 30)
        for c in result_list:
            if c[2] != 'Colorado':
                colorado_test = False
            else:
                colorado_test = True
        self.assertTrue(colorado_test)

        conn.close()

    def test_Mountain_Locations(self):
        conn = sqlite3.connect('snowfall.db')
        cur = conn.cursor()

        sql = 'SELECT * FROM Mountain_Locations'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 604)

        sql += ' WHERE Name="Beaver Creek"'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 1)
        self.assertEqual(result_list[0][3], 39.604225)
        self.assertEqual(result_list[0][4], -106.516515)

        sql = 'SELECT * FROM Mountain_Locations WHERE State="California"'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 25)
        for c in result_list:
            if c[2] != 'California':
                california_test = False
            else:
                california_test = True
        self.assertTrue(california_test)

        conn.close()

    def test_Yelp(self):
        conn = sqlite3.connect('snowfall.db')
        cur = conn.cursor()

        sql = 'SELECT * FROM Yelp'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 604)

        for c in result_list:
            if c[3] == 'No Rating':
                 rating_test = True
            elif float(c[3]) >= 0 and float(c[3]) <= 5.0:
                rating_test = True
            else:
                rating_test = False
        self.assertTrue(rating_test)

        conn.close()


class TestGoogle(unittest.TestCase):
    def test_google(self):
        result = get_lat_and_long('Vail', 'Colorado')
        self.assertEqual(result, (39.6402638, -106.3741955))

        result = get_lat_and_long('Boyne Mountain', 'Michigan')
        self.assertEqual(result, (45.1628802, -84.93005989999999))

        result = get_lat_and_long('Mountain Creek', 'New Jersey')
        self.assertEqual(result, (41.1907552, -74.5051199))

        result = get_lat_and_long('Backcountry Snowcats', 'British Columbia')
        self.assertEqual(result, (50.31281, -122.729359))

        result = get_lat_and_long('Station Touristique Pin Rouge', 'Quebec')
        self.assertEqual(result, (48.313682, -65.730238))

class TestOpenSnow(unittest.TestCase):
    def test_openSnow(self):
        data = crawl_state('https://opensnow.com/state/CO')
        self.assertEqual(len(data[0]), 5)
        self.assertEqual(len(data[1]), 30)
        self.assertEqual(data[2], 'Colorado')

        data = crawl_state('https://opensnow.com/state/MI')
        self.assertEqual(len(data[0]), 5)
        self.assertEqual(len(data[1]), 32)
        self.assertEqual(data[2], 'Michigan')

        data = crawl_state('https://opensnow.com/state/CA')
        self.assertEqual(len(data[0]), 5)
        self.assertEqual(len(data[1]), 25)
        self.assertEqual(data[2], 'California')

class TestYelp(unittest.TestCase):
    def test_Yelp(self):
        yelp = yelp_individual_request('Vail', 39.6402638, -106.3741955)
        if yelp[1] == 'No Rating':
             yelp_test = True
        elif yelp[1] >= 0 and yelp[1] <= 5.0:
            yelp_test = True
        else:
            yelp_test = False
        self.assertTrue(yelp_test)

        yelp = yelp_individual_request('Boyne Mountain', 45.1628802, -84.93005989999999)
        if yelp[1] == 'No Rating':
             yelp_test = True
        elif yelp[1] >= 0 and yelp[1] <= 5.0:
            yelp_test = True
        else:
            yelp_test = False
        self.assertTrue(yelp_test)

        yelp = yelp_individual_request('Mountain Creek', 41.1907552, -74.5051199)
        if yelp[1] == 'No Rating':
             yelp_test = True
        elif yelp[1] >= 0 and yelp[1] <= 5.0:
            yelp_test = True
        else:
            yelp_test = False
        self.assertTrue(yelp_test)

        yelp = yelp_individual_request('Backcountry Snowcats', 50.31281, -122.729359)
        if yelp[1] == 'No Rating':
             yelp_test = True
        elif yelp[1] >= 0 and yelp[1] <= 5.0:
            yelp_test = True
        else:
            yelp_test = False
        self.assertTrue(yelp_test)

        yelp = yelp_individual_request('Station Touristique Pin Rouge', 48.313682, -65.730238)
        if yelp[1] == 'No Rating':
             yelp_test = True
        elif yelp[1] >= 0 and yelp[1] <= 5.0:
            yelp_test = True
        else:
            yelp_test = False
        self.assertTrue(yelp_test)


unittest.main()
