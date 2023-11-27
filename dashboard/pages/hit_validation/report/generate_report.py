import io
import os
from datetime import datetime

import jinja2
import pandas as pd
import xlsxwriter
from dash import dcc
from PIL import Image

from dashboard.visualization.plots import plot_ic50


def generate_jinja_report(content: dict):
    now = datetime.now()
    content["current_day"] = now.strftime("%d-%m-%y")
    content["current_time"] = now.strftime("%H:%M:%S")
    template_loader = jinja2.FileSystemLoader("dashboard/pages/hit_validation/report")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("report.html")
    return template.render(content)


def get_eos_img(eos: str, screening_df: pd.DataFrame, hit_df: pd.DataFrame) -> Image:
    """
    Returns the image of the IC50 plot for a given EOS

    :param eos: EOS to get the image for
    :param screening_df: Screening dataframe
    :param hit_df: Hit dataframe
    :return: Image of the IC50 plot
    """
    # NOTE: some of the values are hardcoded as there's a discrepancy in the Image and xlsxwritter scale
    IMG_WIDTH = 285
    IMG_HEIGHT = 145

    screening_data = screening_df.loc[lambda df: df["EOS"] == eos]
    concentrations = screening_data["CONCENTRATION"].to_numpy()
    values = screening_data["VALUE"].to_numpy()
    entry = hit_df[hit_df["EOS"] == eos].iloc[0].to_dict()
    fig = plot_ic50(entry, concentrations, values, showlegend=False)

    fig.update_layout(
        width=IMG_WIDTH,
        height=IMG_HEIGHT,
        margin=dict(l=1, r=1, t=1, b=1),
        xaxis=dict(tickfont=dict(size=8)),
        yaxis=dict(tickfont=dict(size=8)),
        xaxis_title_font=dict(size=10),
        yaxis_title_font=dict(size=10),
    )

    image_bytes = fig.to_image(format="png")
    img_resized = Image.open(io.BytesIO(image_bytes)).resize((IMG_WIDTH, IMG_HEIGHT))
    return img_resized


def generate_hit_valildation_report(
    filename: str, screening_df: pd.DataFrame, hit_df: pd.DataFrame
) -> dict:
    """
    Generates the hit validation report in the xlsx format (with images)

    :param filename: Name of the file to save the report as
    :param screening_df: Screening dataframe
    :param hit_df: Hit dataframe
    :return: Download link to the report
    """
    columns = [col for col in hit_df.columns if col != "EOS"]
    hit_df["Image"] = None
    columns_ordered = ["EOS", "Image"] + columns
    hit_df = hit_df[columns_ordered]

    excel_data = io.BytesIO()
    workbook = xlsxwriter.Workbook(excel_data, {"nan_inf_to_errors": True})
    worksheet = workbook.add_worksheet("hit_validation")
    worksheet.set_column("B:B", 40)

    for idx, col in enumerate(hit_df.columns):
        worksheet.write(0, idx, col)  # Write column headers
        for row_idx, value in enumerate(hit_df[col]):
            if col == "Image":
                eos = hit_df["EOS"][row_idx]
                eos_img = get_eos_img(eos, screening_df, hit_df)

                img_stream = io.BytesIO()
                eos_img.save(img_stream, format="PNG")
                img_stream.seek(0)

                worksheet.set_row(row_idx + 1, 110)
                worksheet.insert_image(
                    f"B{row_idx + 2}", "plot.png", {"image_data": img_stream}
                )
            else:
                worksheet.write(row_idx + 1, idx, value)

    workbook.close()
    temp_file_path = "temp_report.xlsx"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(excel_data.getvalue())

    download_link = dcc.send_file(temp_file_path, filename=filename)
    os.remove(temp_file_path)

    return download_link
