def auto_adjust_column_width(sheet):
    print("Sheet name:", sheet.title)
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)) + 0.71)
            except:
                pass
        adjusted_width = max_length
        sheet.column_dimensions[column_letter].width = adjusted_width
        print("Column:", column_letter)
        print("Adjusted width:", max_length)