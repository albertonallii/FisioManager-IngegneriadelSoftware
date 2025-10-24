import controllers.plan_controller as plc

def test_create_and_complete_plan(temp_data_dir):
    plan = plc.create_treatment_plan(1, "Riabilitazione ginocchio")
    assert hasattr(plan, "id") and isinstance(plan.id, int)
    ok = plc.complete_treatment_plan(plan.id)
    assert ok in (True, None)
