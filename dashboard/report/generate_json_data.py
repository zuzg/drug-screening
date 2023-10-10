def generate_json_data(
    second_stage: dict, third_stage: dict, fifth_stage: dict
) -> dict:
    second_stage.pop("plates_count")
    second_stage.pop("compounds_count")
    second_stage.pop("outliers_count")
    third_stage.pop("control_values_fig")
    return {
        "second_stage": second_stage,
        "third_stage": third_stage,
        "fifth_stage": fifth_stage,
    }
