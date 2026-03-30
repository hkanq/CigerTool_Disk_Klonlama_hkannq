# Release Plan

## Ana Build Girisi

- `build/build_cigertool_release.ps1`

Bu script tek resmi build entrypoint'tir.

## Build Modlari

Plan dogrulama:

- `build/build_cigertool_release.ps1 -PlanOnly`

Gercek artifact uretimi:

- `build/build_cigertool_release.ps1`

## Artifact'ler

Birincil artifact:

- `artifacts/CigerTool-Workspace.iso`

Ikincil artifact'ler:

- `artifacts/CigerTool-Workspace.iso.sha256`
- `artifacts/CigerTool-Workspace-debug.zip`
- `artifacts/CigerTool-Workspace.release.json`

## Dagitim Modeli

Birincil artifact dagitima uygun bir USB boot ISO'sudur.

- Kullanici ISO'yu USB'ye ISO/extract mode ile yazar
- USB yazildiktan sonra `/isos/windows`, `/isos/linux` ve `/isos/tools` dizinleri kullanici tarafinda doldurulabilir
- Workspace ve ISO Library ayni USB uzerinden kullanilir

## Startup Hook

Workspace oturumu icinde otomatik baslatma hook'u:

- `workspace/startup/Start-CigerToolWorkspace.ps1`

## Uretim Ozeti

1. WIM girdisi dogrulanir
2. uygulama paketlenir
3. workspace VHDX hazirlanir
4. boot katmani uretilir
5. USB layout staging tamamlanir
6. `CigerTool-Workspace.iso` olusturulur
