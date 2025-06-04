import unittest
from unittest.mock import patch, MagicMock
import functions  # Імпортуємо файл, де містяться функції, наприклад functions.py

# 1. add_numbers
class TestAddNumbers(unittest.TestCase):
    def test_add(self):
        self.assertEqual(functions.add_numbers(2, 3), 5)
        self.assertEqual(functions.add_numbers(-1, 1), 0)

# 2. is_even
class TestIsEven(unittest.TestCase):
    def test_even(self):
        self.assertTrue(functions.is_even(4))

    def test_odd(self):
        self.assertFalse(functions.is_even(5))

# 3. fetch_data (mock requests)
class TestFetchData(unittest.TestCase):
    @patch('functions.requests.get')
    def test_fetch_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'key': 'value'}
        result = functions.fetch_data("http://example.com")
        self.assertEqual(result, {'key': 'value'})

    @patch('functions.requests.get')
    def test_fetch_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        result = functions.fetch_data("http://example.com")
        self.assertIsNone(result)

# 4. process_mock_object
class TestProcessMockObject(unittest.TestCase):
    def test_positive_value(self):
        mock_obj = MagicMock()
        mock_obj.value = 10
        self.assertEqual(functions.process_mock_object(mock_obj), 20)

    def test_negative_value(self):
        mock_obj = MagicMock()
        mock_obj.value = -5
        self.assertIsNone(functions.process_mock_object(mock_obj))

# 5. run_data_pipeline
class TestRunDataPipeline(unittest.TestCase):
    def test_pipeline(self):
        mock_processor = MagicMock()
        mock_data = MagicMock()
        mock_processor.process_data.return_value.analyze_data.return_value = mock_data
        functions.run_data_pipeline(mock_processor)
        mock_data.save_result.assert_called_once()

# 6. divide_numbers
class TestDivideNumbers(unittest.TestCase):
    def test_division(self):
        self.assertEqual(functions.divide_numbers(10, 2), 5)

    def test_zero_division(self):
        self.assertIsNone(functions.divide_numbers(10, 0))

    def test_type_error(self):
        self.assertIsNone(functions.divide_numbers("10", 2))

# 7. check_even_odd
class TestCheckEvenOdd(unittest.TestCase):
    @patch('functions.requests.get')
    def test_even_odd(self, mock_get):
        mock_get.return_value.json.side_effect = [
            {"results": [{"value": 4}]},
            {"results": [{"value": 7}]}
        ]
        result = functions.check_even_odd([1, 2], "http://fakeurl.com")
        self.assertEqual(result, ["Even", "Odd"])

# 8. DataProcessor class
class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = functions.DataProcessor()

    def test_process_data(self):
        result = self.processor.process_data([1, 2, 3])
        self.assertEqual(result, [2, 4, 6])

    def test_analyze_data(self):
        result = self.processor.analyze_data([1, 2, 3])
        self.assertEqual(result, 12)
