# Workspace Startup

Boot zinciri masaüstüne indikten sonra bu klasördeki startup sözleşmesi devreye girer.

Beklenen sıra:

1. Microsoft boot manager hazırlanmış workspace VHDX'i açar
2. Windows otomatik oturum açar
3. `Start-CigerToolWorkspace.ps1` çalışır
4. USB medya kökü tespit edilir
5. `workspace-status.json` ve `workspace-startup.log` yazılır
6. `CigerTool.exe` otomatik başlatılır

Başarısızlık halinde sistem kapanmaz. Masaüstü ayakta kalır ve kullanıcı log dosyalarına bakabilir.
