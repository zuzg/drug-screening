def read_stages_stats(
    outliers_preview_stage: dict, statistics_stage: dict, summary_stage: dict
) -> dict:
    return {
        "outliers_preview_stage": {
            "outliers_only_checklist": outliers_preview_stage["outliers_only_checklist"]
        },
        "statistics_stage": {"z_slider_value": statistics_stage["z_slider_value"]},
        "summary_stage": summary_stage,
    }
