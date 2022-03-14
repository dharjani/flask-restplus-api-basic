try:
    import unittest
    import json
    from app import api
except Exception as e:
    print("Some modules are missing {} ".format(e))

class CITest (unittest.TestCase):

    #Check if app is healthy i.e. response is 200
    def test_health(self):
        tester = api.test_client(self)
        response = tester.get('/public/healthz')
        statuscode = response.status_code
        self.assertEqual(200, statuscode)

if __name__ == "__main__":
    unittest.main()