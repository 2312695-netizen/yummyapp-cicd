import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (Moi chi dat ~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""
    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2 (TIET 3): SINH VIEN TU TAY LAP TRINH TEST CASE DUOI DAY
# (Sau khi da hoan thanh Ban thiet ke test case viet tay tren giay)
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai (4 test cases)"""
    def setUp(self):
        self.app = YummyApp()

    def test_promo_online_valid_code(self):
        """Test 1: Online va ma hop le GIAM10 tren OS 15 -> giam 10%"""
        self.app.network_status = "online"
        self.app.os_version = 15
        result = self.app.apply_promo_code(100000, "GIAM10")
        self.assertEqual(result, 90000.0)

    def test_promo_offline_raises_connection_error(self):
        """Test 2: Offline -> nem ngoai le ConnectionError"""
        self.app.network_status = "offline"
        with self.assertRaises(ConnectionError) as context:
            self.app.apply_promo_code(100000, "GIAM10")
        self.assertIn("Khong co ket noi mang de xac thuc ma.", str(context.exception))

    def test_promo_special_code_os15_success(self):
        """Test 3: Ma dac biet NEW_OS_ONLY tren OS 15 -> giam 20%"""
        self.app.network_status = "online"
        self.app.os_version = 15
        result = self.app.apply_promo_code(100000, "NEW_OS_ONLY")
        self.assertEqual(result, 80000.0)

    def test_promo_special_code_os14_raises_value_error(self):
        """Test 4: Ma dac biet NEW_OS_ONLY tren OS 14 -> nem ngoai le ValueError"""
        self.app.network_status = "online"
        self.app.os_version = 14
        with self.assertRaises(ValueError) as context:
            self.app.apply_promo_code(100000, "NEW_OS_ONLY")
        self.assertIn("Ma nay yeu cau HDH phien ban 15 tro len.", str(context.exception))


class TestHardLevel(unittest.TestCase):
    """Kiem thu chuc nang de xuat nha hang voi GPS Mocking (3 test cases)"""
    def setUp(self):
        self.app = YummyApp()

    @patch("yummy_app.gps_service.get_current_location")
    def test_gps_supported_location(self, mock_location):
        """Test 5: GPS trong vung ho tro (10.0, 105.0) -> tra ve 2 nha hang"""
        mock_location.return_value = (10.0, 105.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"])
        mock_location.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_gps_out_of_range_location(self, mock_location):
        """Test 6: GPS ngoai vung ho tro (20.0, 110.0) -> tra ve danh sach rong []"""
        mock_location.return_value = (20.0, 110.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, [])
        mock_location.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_gps_signal_lost(self, mock_location):
        """Test 7: GPS mat tin hieu -> bat GPSSignalLostError va tra ve thong bao"""
        mock_location.side_effect = gps_service.GPSSignalLostError()
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")
        mock_location.assert_called_once()


if __name__ == '__main__':
    unittest.main()
