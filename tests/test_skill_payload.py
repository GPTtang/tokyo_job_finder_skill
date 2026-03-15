from job_finder.skill import run_job_finder


def test_run_job_finder_config_error():
    payload = run_job_finder("find jobs", config_path=None)
    assert payload["ok"] is True
