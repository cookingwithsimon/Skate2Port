# Skate 2 PC Recompilation

An unofficial native Windows port of the Xbox 360 version of Skate 2, built by statically recompiling the game's `default.xex` with the [ReXGlue SDK](https://github.com/rexglue/rexglue-sdk) (via the [Skate 3 Recomp fork](https://github.com/mchughalex/rexglue-skate3)).

The game boots through the menus and idle movie into freeskate, and mission triggers work, at over 100 FPS on a Ryzen 7 7800X3D. It is early: expect bugs. It uses the SDK's emulated Xbox 360 GPU on Direct3D 12.

**No game files or recompiled game code are included.** You need your own Xbox 360 Skate 2 disc image. The build recompiles the code from your copy.

Tested with `Skate 2 (USA) (En,Fr)`, title ID `4541087F`, `default.xex` SHA-1 `a9b539c1acbc80aeaade3ffbe708e1fbd3a2dad7`. Other regions or title updates have different code addresses and need their own config.

## Requirements

- Windows 10/11, x86-64 CPU with AVX2
- [LLVM](https://releases.llvm.org/) (Clang 18 or newer): `winget install LLVM.LLVM`
- Visual Studio 2022 Build Tools with the C++ workload (MSVC libraries, CMake and Ninja)
- Python 3, Git

`tools/devenv.bat` runs a command with the VS 2022 Build Tools environment plus LLVM on the path. Edit the paths at the top if yours differ.

## Build

```bash
git clone https://github.com/cookingwithsimon/Skate2Recompiled.git
```

```bash
powershell -ExecutionPolicy Bypass -File tools/setup.ps1
```

`setup.ps1` fetches the SDK submodules and applies `patches/rexglue-sdk.patch`.

Extract your disc image into `game/`:

```bash
python tools/extract_iso.py "Skate 2 (USA) (En,Fr).iso" extract-all game
```

Configure, build the recompiler, generate the C++ from your `default.xex`, then build the game:

```bash
tools\devenv.bat cmake --preset win-amd64-relwithdebinfo
```

```bash
tools\devenv.bat cmake --build out/build/win-amd64-relwithdebinfo --target rexglue
```

```bash
third_party\rexglue-sdk\out\win-amd64\rexglue.exe codegen skate2_manifest.toml
```

```bash
tools\devenv.bat cmake --preset win-amd64-relwithdebinfo
```

```bash
tools\devenv.bat cmake --build out/build/win-amd64-relwithdebinfo
```

Copy `skate2.example.toml` to `out/build/win-amd64-relwithdebinfo/skate2.toml`, set `game_data_root` to your `game` folder, and run `skate2.exe` from that folder.

## Controls

An Xbox controller works out of the box. Keyboard controls (set in `skate2.toml`, `mnk_mode = true`):

| Controller | Key |
| --- | --- |
| Left stick | W / A / S / D |
| Left stick click | Z |
| A / B / X / Y | Space / Ctrl / Shift / T |
| D-pad | Arrow keys |
| Start / Back | Enter / Tab |
| LB / RB | Q / R |
| LT / RT | Right / left mouse button |

F2 toggles the FPS counter.

## What was needed for Skate 2

- `config/skate2_functions.toml`: native `setjmp`/`longjmp` (without them Lua never initialises), about 205 function entry points the analysis misses (found with `tools/scan_data_ptrs.py` and `tools/scan_code_ptrs.py`), and one jump table override.
- `patches/rexglue-sdk.patch`, applied to the SDK:
  - ImGui overlays (on-screen keyboard, FPS counter) never drew with the current imgui: the drawer read the obsolete `ImDrawData::CmdListsCount`.
  - A lone Alt press opened the window's system menu and froze input.
  - `vpkuhus`/`vpkuwus` produced wrong results when the destination register aliased a source.
  - Unregistered-call crashes log a guest backtrace.
  - One imgui font setting that only exists in the fork's imgui is disabled.
  - The frame-end refresh of GPU-written page flags always copies the whole table. The partial copy went into a buffer two frames stale and caused alternating-frame flicker once frames got faster.
- The presets build with `REXGLUE_ENABLE_PERF_COUNTERS=OFF`, which saves about 6% CPU on the GPU thread. Tested at 1x and 2x resolution scale.
- To update an SDK checkout that has an older patch applied, run `git -C third_party/rexglue-sdk checkout -- src` and then `setup.ps1` again.
- The SDK pins an imgui commit that no longer exists upstream; `setup.ps1` uses the nearest commit from the same day.

## Development helpers

- `tools/iterate.ps1`: regenerate, rebuild, run for a while and print the end of the log.
- `tools/play_keys.ps1`: launch the game, press keys on a schedule and take screenshots.
- `tools/peek.py`, `tools/find_refs.py`, `tools/func_strings.py`: inspect the decrypted image from `rexglue dump-xex`.

## Disclaimer

Not affiliated with or endorsed by Electronic Arts or Microsoft. Skate 2 is a trademark of Electronic Arts. Use only with a copy of the game you own.
