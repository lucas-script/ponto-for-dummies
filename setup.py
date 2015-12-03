from cx_Freeze import setup, Executable


setup(
    name = "ponto_dor_dummies" ,
    version = "0.1" ,
    description = "ponto_for_dummies @ lucas.script@gmail.com" ,
    executables = [Executable("ponto_for_dummies.pyw", base = "Win32GUI")]  ,
)