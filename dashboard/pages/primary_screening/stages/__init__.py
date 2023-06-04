from .s1_bmg_input import BMG_INPUT_STAGE
from .s2_outliers_purging import OUTLIERS_PURGING_STAGE
from .s3_filtered_plates_stats import FILTERED_PLATES_STATS_STAGE
from .s4_echo_input import ECHO_INPUT_STAGE
from .s5_summary import SUMMARY_STAGE
from .s6_report import REPORT_STAGE

STAGES = [
    BMG_INPUT_STAGE,
    OUTLIERS_PURGING_STAGE,
    FILTERED_PLATES_STATS_STAGE,
    ECHO_INPUT_STAGE,
    SUMMARY_STAGE,
    REPORT_STAGE,
]
