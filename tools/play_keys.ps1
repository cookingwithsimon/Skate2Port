# Launch skate2.exe and play a key script, e.g. "35:Return,5:Space,60:snap" (wait seconds, then key or snap).
param([string]$Script = "35:Return,5:Space,60:snap", [string]$OutDir = "$PSScriptRoot\..\work\snaps", [switch]$KeepRunning)

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Win3 { [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  public struct RECT { public int Left, Top, Right, Bottom; } }
"@
$vk = @{ Return = 0x0D; Space = 0x20; Up = 0x26; Down = 0x28; Left = 0x25; Right = 0x27; Tab = 0x09; Escape = 0x1B; F1 = 0x70; F2 = 0x71; F3 = 0x72; F4 = 0x73; A = 0x41; Alt = 0x12; Control = 0x11; T = 0x54 }
New-Item -ItemType Directory -Force $OutDir | Out-Null
Set-Location (Join-Path $PSScriptRoot '..\out\build\win-amd64-relwithdebinfo')
$p = Start-Process .\skate2.exe -PassThru
$n = 0
foreach ($step in $Script.Split(',')) {
  $wait, $action = $step.Split(':')
  $end = (Get-Date).AddSeconds([double]$wait)
  while ((Get-Date) -lt $end -and -not $p.HasExited) { Start-Sleep -Milliseconds 200 }
  if ($p.HasExited) { "game exited before step '$step'"; exit 1 }
  $p.Refresh(); $h = $p.MainWindowHandle
  # Tapping Alt lets this process move focus; never send keys unless the game really has focus.
  if ([Win3]::GetForegroundWindow() -ne $h) { [Win3]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero); [Win3]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero) }
  [Win3]::ShowWindow($h, 9) | Out-Null; [Win3]::SetForegroundWindow($h) | Out-Null; Start-Sleep -Milliseconds 300
  if ([Win3]::GetForegroundWindow() -ne $h) { "could not focus the game window; stopping before '$step'"; Stop-Process -Id $p.Id -Force; exit 1 }
  if ($action -eq 'snap') {
    $r = New-Object Win3+RECT; [Win3]::GetWindowRect($h, [ref]$r) | Out-Null
    $bmp = New-Object System.Drawing.Bitmap ($r.Right - $r.Left), ($r.Bottom - $r.Top)
    [System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen($r.Left, $r.Top, 0, 0, $bmp.Size)
    $f = Join-Path $OutDir ("play_{0:D2}.png" -f $n++); $bmp.Save($f); "saved $f"
  } elseif ($action.StartsWith('type=')) {
    foreach ($ch in $action.Substring(5).ToUpper().ToCharArray()) {
      [Win3]::keybd_event([byte][char]$ch, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
      [Win3]::keybd_event([byte][char]$ch, 0, 2, [UIntPtr]::Zero); Start-Sleep -Milliseconds 60
    }
    "typed $($action.Substring(5))"
  } else {
    $code = [byte]$vk[$action]
    [Win3]::keybd_event($code, 0, 0, [UIntPtr]::Zero); Start-Sleep -Milliseconds 150
    [Win3]::keybd_event($code, 0, 2, [UIntPtr]::Zero); "pressed $action"
  }
}
if ($KeepRunning) { "still running (pid $($p.Id))" } else { Stop-Process -Id $p.Id -Force; "closed" }
