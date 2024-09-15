# Scripts that scanning Tower of Fantasy files
- `main_scanning_files.py` for scanning multype buffs and make json result
- `scanned_result_to_exel.py` for converting json result to exel table
> [!NOTE]
> Project prepared for working with already exported game files

## [To begin with](#start-export)
Need to export game files to json format
throw [FModel](https://fmodel.app/)
or [UnrealExporter](https://github.com/whotookzakum/UnrealExporter)

Set UE_Version to "GAME_TowerOfFantasy"
and use

- Global AES Key: 0x6E6B325B02B821BD46AF6B62B1E929DC89957DC6F8AA78210D5316798B7508F8
- CN AES Key: 0x857C7D3936769F2CA4CDC8A1DEB1A2D8A61649ADE7192E2C51870A66850DF9AC

Export entire game to json in any folder, but be ready, **this may take time**
## [Using scripts](#script-use)
### [Scanning multype buffs](#script-scan)
In `main_scanning_files.py` replace directory variable to yours.

For example was used main game folder Resources, but you can scan entire game by using "Exports" folder lvl.

Than start script and wait until it end.

Results will be in:
- `unique_attributes_sorted.json` with all multype buffs that was founded
- `attribute_files_map1.json`    -    AttributeName => [file_name] 
> [!NOTE]
> Some multype have same AttributeName but different ModuleExtraType header, which means that they will be multiplicative
> so for correct information use next results:
- `attribute_to_module_mapping2.json`    -    AttributeName => ModuleExtraType => [file_name]
- `module_extra_to_files_mapping3.json`    -    ModuleExtraType => AttributeName => [file_name]
### [Converting result to Exel table](#script-exel)
After scanning by `main_scanning_files.py` was completed u can use `scanned_result_to_exel.py`

Results will be in:
- `exported_v1.xlsx` with all information from `module_extra_to_files_mapping3.json`
