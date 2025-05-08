# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('tools')
datas += collect_data_files('azure.devops')
datas += collect_data_files('pyfiglet', include_py_files=False)

hidden_imports = [
    'urllib3',
    'github',
    'github.MainClass',
    'github.GithubRetry',
    'azure.devops.v7_0.git',
    'pyfiglet.fonts',
    'requests',
    'boto3',
    'docker',
    'rich',
    'marshmallow',
    'ruamel.yaml',
    'Authlib',
    'PyJWT',
    'sympy',
    'packageurl',
    'distro',
    'pexpect',
    'requests_toolbelt',
    'python-decouple',
    'prettytable',
    'pyfiglet',
    'paramiko',
    'dateutil.tz.tzfile',
    'awscrt',
    'aiohttp',
    'multidict',
    'opentelemetry',
    'opentelemetry.trace',
    'opentelemetry.context',
    'opentelemetry.propagate',
    'azure.core.pipeline.transport.AioHttpTransportResponse',
    'azure.core.tracing.opentelemetry',
    'azure.core.tracing.ext.opentelemetry_span',
    'azure.core.tracing.ext.opencensus_span',
]

hidden_imports += collect_submodules('devsecops_engine_tools')

block_cipher = None

a = Analysis(
    ['engine_core/src/applications/runner_engine_core.py'],
    pathex=['tools'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="devsecops-engine-tools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,                  
    upx=True,
    upx_exclude=[],                   
    runtime_tmpdir=None,         
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None              
)
