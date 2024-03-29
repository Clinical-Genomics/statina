from typing import Dict, List

from statina.models.database import DataBaseSample
from statina.models.server.plots.coverage import CoveragePlotSampleData
from statina.models.server.sample import SampleValidator, SampleWarning


def get_scatter_data_for_coverage_plot(
    samples: List[SampleValidator],
) -> Dict["str", CoveragePlotSampleData]:
    """Coverage Ratio data for Coverage Plot.
    Only adding samples with a zscore war
    ning"""

    data = {}
    for sample in samples:
        sample_warnings: SampleWarning = sample.warnings
        zscore_warnings = [
            sample_warnings.z_score_13,
            sample_warnings.z_score_18,
            sample_warnings.z_score_21,
        ]
        if set(zscore_warnings) == {"default"}:
            continue

        x = []
        y = []
        for chromosome in range(1, 23):
            ratio = sample.dict().get(f"Chr{chromosome}_Ratio")
            if ratio is None:
                continue
            y.append(ratio)
            x.append(chromosome)
        data[sample.sample_id] = CoveragePlotSampleData(x_axis=x, y_axis=y)
    return data


def get_box_data_for_coverage_plot(
    validated_samples: List[DataBaseSample],
) -> Dict[int, List[float]]:
    """Coverage Ratio data for Coverage Plot."""

    box_data = {}
    for chromosome in range(1, 23):
        box_data[chromosome] = []
        for sample in validated_samples:
            ratio = sample.dict().get(f"Chr{chromosome}_Ratio")
            if ratio is None:
                continue
            box_data[chromosome].append(ratio)
    return box_data
