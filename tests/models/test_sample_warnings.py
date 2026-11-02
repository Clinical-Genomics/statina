from types import SimpleNamespace

import pytest

from statina.models.server.sample import SampleValidator

DATASET = SimpleNamespace(trisomy_hard_max=1.015, trisomy_soft_max=1.009, trisomy_hard_min=0.985)


@pytest.mark.parametrize(
    "ratio, expected_warning",
    [
        (None, "default"),
        (1.0, "default"),
        (1.0089, "default"),
        (1.009, "warning"),
        (1.0117, "warning"),
        (1.015, "danger"),
        (1.02, "danger"),
        (0.985, "danger"),
        (0.98, "danger"),
    ],
)
def test_get_tris_warning(ratio, expected_warning):
    # GIVEN a ratio and a dataset with trisomy thresholds

    # WHEN getting the trisomy warning
    warning: str = SampleValidator.get_tris_warning(ratio=ratio, dataset=DATASET)

    # THEN the warning is based on the ratio thresholds only, independent of fetal fraction
    assert warning == expected_warning
