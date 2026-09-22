"""Isolated Flask contract tests; no board, live DB, camera, or cloud access."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class UnknownCaptureTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qsm_unknown_test_")
        self.addCleanup(self.temp.cleanup)
        copied = Path(self.temp.name) / "app.py"
        shutil.copy2(ROOT / "app.py", copied)
        spec = importlib.util.spec_from_file_location("isolated_retail", copied)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.app.config["TESTING"] = True
        self.module.init_db()
        self.module.set_state("latest_capture", "captures/old_product.jpg")
        self.audio = patch.object(self.module, "play_audio", return_value=False).start()
        self.addCleanup(patch.stopall)
        self.client = self.module.app.test_client()
        self.prediction = {"ok": True, "model_available": True, "backend": "rknn_cli",
                           "result": "predicted", "candidates": [
                               {"product_id": "SKU001", "product_name": "Test product", "confidence": 0.9}]}

    def post(self, body):
        response = self.client.post("/api/vision/candidates", json=body)
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def capture_response(self, data):
        return lambda: self.module.jsonify(data)

    def test_fresh_success_ignores_old_and_supplied_image(self):
        cap = {"ok": True, "image_path": "captures/new.jpg", "capture_id": "new", "latency_ms": 10}
        with patch.object(self.module, "api_capture_v265", side_effect=self.capture_response(cap)) as camera, \
                patch.object(self.module, "predict_vision_top3", return_value=self.prediction) as predict:
            before = self.module.cart_json()
            data = self.post({"capture": True, "image_path": "captures/old_product.jpg"})
            self.assertTrue(data["ok"])
            camera.assert_called_once()
            predict.assert_called_once_with("captures/new.jpg")
            self.assertEqual(data["capture"], cap)
            self.assertEqual(data["top1_product_id"], "SKU001")
            self.assertFalse(data["auto_add_cart"])
            self.assertEqual(before, self.module.cart_json())

    def test_capture_failures_do_not_predict_old_image(self):
        for reason in ("capture_busy", "capture_cooldown", "capture_timeout", "capture_failed"):
            with self.subTest(reason=reason), \
                    patch.object(self.module, "api_capture_v265", side_effect=self.capture_response(
                        {"ok": False, "error_reason": reason, "message": reason})), \
                    patch.object(self.module, "predict_vision_top3") as predict:
                data = self.post({"capture": True})
                self.assertFalse(data["ok"])
                self.assertEqual(data["error_reason"], reason)
                self.assertEqual(data["candidates"], [])
                self.assertEqual(data["image_path"], "")
                self.assertEqual(data["top1_product_id"], "")
                predict.assert_not_called()
                self.assertEqual(json.loads(self.module.get_state("latest_vision"))["candidates"], [])

    def test_missing_capture_path_is_not_success(self):
        with patch.object(self.module, "api_capture_v265", side_effect=self.capture_response({"ok": True})), \
                patch.object(self.module, "predict_vision_top3") as predict:
            self.assertFalse(self.post({"capture": True})["ok"])
            predict.assert_not_called()

    def test_unavailable_or_simulated_candidates_not_shown_as_real(self):
        for model, ok in ((False, False), (True, False), (False, True)):
            prediction = dict(self.prediction, model_available=model, ok=ok, result="predict_failed")
            with self.subTest(model=model, ok=ok), \
                    patch.object(self.module, "api_capture_v265", side_effect=self.capture_response(
                        {"ok": True, "image_path": "captures/new.jpg"})), \
                    patch.object(self.module, "predict_vision_top3", return_value=prediction):
                data = self.post({"capture": True})
                self.assertFalse(data["ok"])
                self.assertEqual(data["candidates"], [])
                self.assertEqual(data["top1_product_id"], "")
                self.assertTrue(data["capture"]["ok"])

    def test_empty_model_output_is_not_success(self):
        with patch.object(self.module, "api_capture_v265", side_effect=self.capture_response(
                {"ok": True, "image_path": "captures/new.jpg"})), \
                patch.object(self.module, "predict_vision_top3", return_value=dict(self.prediction, candidates=[])):
            self.assertFalse(self.post({"capture": True})["ok"])

    def test_legacy_explicit_image_still_works(self):
        with patch.object(self.module, "api_capture_v265") as camera, \
                patch.object(self.module, "predict_vision_top3", return_value=self.prediction) as predict:
            self.assertTrue(self.post({"image_path": "captures/supplied.jpg"})["ok"])
            camera.assert_not_called()
            predict.assert_called_once_with("captures/supplied.jpg")

    def test_legacy_latest_image_still_works(self):
        with patch.object(self.module, "api_capture_v265") as camera, \
                patch.object(self.module, "predict_vision_top3", return_value=self.prediction) as predict:
            self.assertTrue(self.post({})["ok"])
            camera.assert_not_called()
            predict.assert_called_once_with("captures/old_product.jpg")

    def test_unknown_scan_does_not_add_and_manual_add_is_explicit(self):
        before = self.module.cart_count()
        unknown = self.client.post("/api/scan", json={"barcode": "UNKNOWN_TEST_001"}).get_json()
        self.assertEqual(unknown["error_reason"], "unknown_barcode")
        self.assertEqual(before, self.module.cart_count())
        added = self.client.post("/api/cart/add", json={"product_id": "SKU001", "quantity": 1}).get_json()
        self.assertTrue(added["ok"])
        self.assertEqual(before + 1, self.module.cart_count())

    def test_known_scan_and_verification_do_not_double_add(self):
        scan = self.client.post("/api/scan", json={"barcode": "SKU001"}).get_json()
        self.assertTrue(scan["ok"])
        before = self.module.cart_json()
        with patch.object(self.module, "predict_vision_top3", return_value=self.prediction):
            data = self.client.post("/api/vision/verify_scan", json={"barcode": "SKU001"}).get_json()
            self.assertTrue(data["match_scan"])
        self.assertEqual(before, self.module.cart_json())

    def test_cart_total_remove_clear_regression(self):
        self.client.post("/api/scan", json={"barcode": "SKU006"})
        self.client.post("/api/scan", json={"barcode": "SKU007"})
        expected = self.module.get_product("SKU006")["price_cent"] + self.module.get_product("SKU007")["price_cent"]
        self.assertEqual(self.module.cart_json()["total_cent"], expected)
        self.assertTrue(self.client.post("/api/cart/remove_last").get_json()["ok"])
        self.assertEqual(self.module.cart_count(), 1)
        self.client.post("/api/cart/clear")
        self.assertEqual(self.module.cart_json()["total_cent"], 0)

    def test_empty_checkout_and_local_order_regression(self):
        self.assertEqual(self.client.post("/api/checkout").status_code, 400)
        self.client.post("/api/cart/add", json={"product_id": "SKU001", "quantity": 1})
        with patch.object(self.module, "cloud_create_order", return_value=None), \
                patch.object(self.module, "board_lan_ip_candidates", return_value=[]):
            response = self.client.post("/api/checkout")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["order"]["payment_status"], "unpaid")
        self.assertTrue(data["order"]["qr_exists"])
        self.assertEqual(data["order"]["total_cent"], self.module.get_product("SKU001")["price_cent"])

    def test_speech_query_and_checkout_correction_regression(self):
        queried = self.client.post("/api/speech/execute", json={"text": "一共多少钱"}).get_json()
        corrected = self.client.post("/api/speech/execute", json={"text": "我要截正"}).get_json()
        self.assertEqual(queried["intent"], "query_total_price")
        self.assertEqual(corrected["intent"], "checkout")
        self.assertTrue(corrected["corrected"])
        self.assertTrue(corrected["confirm_required"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
