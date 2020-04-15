import cx_Freeze

executables = [cx_Freeze.Executable("Gsim.py")]

cx_Freeze.setup(
    name="A bit Racey",
    options={"build_exe": {"packages":["pygame","xlrd"],
                           "include_files":["Config.xlsx"]}},
    executables = executables

    )