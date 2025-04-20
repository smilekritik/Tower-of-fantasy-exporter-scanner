# Scripts that scan Tower of Fantasy files
- `main_scanning_files.py` for scanning multiple buffs and generating JSON results
- `scanned_result_to_exel.py` for converting JSON results to Excel tables
- `patch_difference.py` for comparing JSON files between patches
> [!NOTE]
> This project is prepared for working with already exported game files.

## [To begin with](#start-export)
You need to export game files to JSON format using tools like:
- [FModel](https://fmodel.app/)
- [UnrealExporter](https://github.com/whotookzakum/UnrealExporter)

Set `UE_Version` to `"GAME_TowerOfFantasy"` and use the following AES keys:
- **Global AES Key**: `0x6E6B325B02B821BD46AF6B62B1E929DC89957DC6F8AA78210D5316798B7508F8`
- **CN AES Key**: `0x857C7D3936769F2CA4CDC8A1DEB1A2D8A61649ADE7192E2C51870A66850DF9AC`

Export the entire game to JSON in any folder. Be prepared, as this process may take time.

## [Using scripts](#script-use)
### [Scanning multiple buffs](#script-scan)
In `main_scanning_files.py`, replace the `directory` variable with your folder path.

For example, you can use the main game folder `Resources`, or scan the entire game by using the "Exports" folder.

Then, start the script and choose one of the following modes:
1. **Full scan**: Scans all files in the specified directory and its subdirectories.
2. **Scan only new files**: Scans only files that have not been scanned before.
3. **Rescan empty files**: Rescans files that were previously scanned but found to have no attributes.
4. **Rescan files with attributes found**: Rescans files where attributes were previously found.

Results will be in the `Exported` folder:
- `unique_attributes_sorted.json`: Contains all unique buffs found.
- `attribute_files_map1.json`: Maps `AttributeName` to `[file_name]`.
> [!NOTE]
> Some buffs have the same `AttributeName` but different `ModuleExtraType` headers, meaning they are multiplicative.
> For accurate information, use the following results:
- `attribute_to_module_mapping2.json`: Maps `AttributeName` to `ModuleExtraType` to `[file_name]`.
- `module_extra_to_files_mapping3.json`: Maps `ModuleExtraType` to `AttributeName` to `[file_name]`.

Additionally, log files will be stored in the `Logs` folder:
- `log_empty_files.txt`: Files scanned but found to have no attributes.
- `log_processed_files.txt`: Files where attributes were found.
- `log_scanned_files.txt`: All files scanned by the script.
- `log_info.txt`: Summary of the script's execution.

### [Converting results to Excel table](#script-excel)
After scanning with `main_scanning_files.py`, use `scanned_result_to_exel.py`.

Results will be in:
- `exported_v1.xlsx`: Contains all information from `module_extra_to_files_mapping3.json`.

### [Making a difference between patches](#script-difference)
1. Save the file from the previous patch in the `Exported` folder as `module_extra_to_files_mapping3_old.json`.
2. After scanning with `main_scanning_files.py`, use `patch_difference.py`.

Results will be in the `Exported` folder:
- `difference.json`: Contains all information added in the new file.

You can then use `scanned_result_to_exel.py` again by editing the path to the file.