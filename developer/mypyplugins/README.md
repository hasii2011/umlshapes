# wx.lib.sized_controls Mypy Plugin

## Purpose
`wx.lib.sized_controls` monkey-patches several helper methods onto `wx.Window` and `wx.SizerItem` at runtime (such as `SetSizerProps`, `GetSizerProps`, `SetSizerProp`, `SetDefaultSizerProps`, `GetDefaultHIGBorder`, `GetDialogBorder`, `SetHGrow`, and `SetVGrow`). 

Because `wxPython`'s static `.pyi` stubs do not include these monkey-patched methods, modern `mypy` flags calls on sized controls with:
```
error: "<Control>" has no attribute "SetSizerProps"  [attr-defined]
```

This plugin teaches `mypy`'s semantic analyzer that these methods exist on `wx.core.Window` and `wx.core.SizerItem`, resolving all such errors across the project without requiring `# type: ignore` comments or manual casts.

---

## Migration Note: Move to `buildlackey`

> [!IMPORTANT]
> **This plugin is temporarily staged here.**
> To avoid duplicating this plugin across multiple wxPython repositories, move this plugin into the shared `buildlackey` package:
>
> 1. Copy `SizedControlsPlugin.py` to `buildlackey/src/buildlackey/mypy/sizedcontrols.py`.
> 2. Expose it via `buildlackey.mypy.sizedcontrols`.
> 3. In all wxPython repositories, update `.mypi.ini` to:
>    ```ini
>    [mypy]
>    plugins = buildlackey.mypy.sizedcontrols
>    ```
> 4. Once `buildlackey` is updated, remove this directory (``) from individual repositories.
