import pytest
import os
import tempfile
from app.licensing.referral import ReferralManager

@pytest.fixture
def temp_referral_mgr():
    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tf.name
    tf.close()
    mgr = ReferralManager(db_path=db_path)
    yield mgr
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass

def test_referral_code_generation(temp_referral_mgr):
    code1 = temp_referral_mgr.get_or_create_referral_code("user_101", "fp_device_1")
    assert code1.startswith("REF-")
    code2 = temp_referral_mgr.get_or_create_referral_code("user_101", "fp_device_1")
    assert code1 == code2

def test_referral_redemption_success(temp_referral_mgr):
    code = temp_referral_mgr.get_or_create_referral_code("user_referrer", "fp_dev_A")
    res = temp_referral_mgr.redeem_referral(code, "user_referee", "fp_dev_B")
    assert res["success"] is True
    assert res["status"] == "ACTIVATED"

def test_self_referral_prevention(temp_referral_mgr):
    code = temp_referral_mgr.get_or_create_referral_code("user_referrer", "fp_dev_A")
    res = temp_referral_mgr.redeem_referral(code, "user_referrer", "fp_dev_B")
    assert res["success"] is False
    assert res["reason"] == "SELF_REFERRAL"

def test_same_device_referral_prevention(temp_referral_mgr):
    code = temp_referral_mgr.get_or_create_referral_code("user_referrer", "fp_dev_SAME")
    res = temp_referral_mgr.redeem_referral(code, "user_friend", "fp_dev_SAME")
    assert res["success"] is False
    assert res["reason"] == "SAME_DEVICE"

def test_duplicate_redemption_prevention(temp_referral_mgr):
    code1 = temp_referral_mgr.get_or_create_referral_code("user_ref_1", "fp_dev_1")
    code2 = temp_referral_mgr.get_or_create_referral_code("user_ref_2", "fp_dev_2")
    
    res1 = temp_referral_mgr.redeem_referral(code1, "user_referee_X", "fp_dev_X")
    assert res1["success"] is True
    
    res2 = temp_referral_mgr.redeem_referral(code2, "user_referee_X", "fp_dev_X")
    assert res2["success"] is False
    assert res2["reason"] == "ALREADY_REDEEMED"
