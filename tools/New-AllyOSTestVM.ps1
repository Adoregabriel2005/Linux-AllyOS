param([ValidateSet('Full','Minimal')][string]$Profile)
$ErrorActionPreference = 'Stop'
$vbox = 'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe'
$workspace = 'G:\PROJETOS\LINUX'
$vmName = "AllyOS-Install-$Profile"
$firmware = if ($Profile -eq 'Minimal') { 'efi64' } else { 'bios' }
function Invoke-VBox {
    & $vbox @args
    if ($LASTEXITCODE -ne 0) { throw "VirtualBox falhou: $($args[0])" }
}
$existing = & $vbox list vms
if ($existing -match ('"' + [regex]::Escape($vmName) + '"')) { throw 'VM de teste já existe; não sobrescrever.' }
Invoke-VBox createvm --name $vmName --ostype Debian_64 --basefolder "$workspace\vms" --register
Invoke-VBox modifyvm $vmName --memory 4096 --cpus 2 --ioapic on --graphicscontroller vmsvga --vram 128 --accelerate-3d off --firmware $firmware --nic1 nat --boot1 dvd --boot2 disk --boot3 none --boot4 none --rtc-use-utc on --audio-controller hda --audio-enabled on --audio-out on --audio-in off --mouse usbtablet --usb-ohci on
Invoke-VBox storagectl $vmName --name SATA --add sata --controller IntelAhci --portcount 2
Invoke-VBox createmedium disk --filename "$workspace\vms\$vmName\AllyOS-$Profile.vdi" --size 32768 --format VDI
Invoke-VBox storageattach $vmName --storagectl SATA --port 0 --device 0 --type hdd --medium "$workspace\vms\$vmName\AllyOS-$Profile.vdi"
Invoke-VBox storageattach $vmName --storagectl SATA --port 1 --device 0 --type dvddrive --medium emptydrive
Invoke-VBox modifyvm $vmName --uart1 0x3F8 4 --uart-mode1 file "$workspace\iso\output\$vmName-serial.log"
Invoke-VBox sharedfolder add $vmName --name allyos-src --hostpath $workspace --readonly
Invoke-VBox sharedfolder add $vmName --name allyos-output --hostpath "$workspace\iso\output"
Write-Output "$vmName preparada: $firmware, 4 GB RAM, disco virtual novo 32 GB."
